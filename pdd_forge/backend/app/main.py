"""
PDD Forge - FastAPI Main Application

Implements the backend API as defined in the implementation plan:
- PDF upload endpoint
- PDD parsing and section extraction
- IR generation and review
- UiPath project generation
- ZIP download
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import tempfile
import shutil
import zipfile
import logging
from typing import List, Optional

from app.core.config import settings
from app.models.ir import IntermediateRepresentation
from app.services.pdd_parser import PDFParser
from app.services.llm_service import LLMService
from app.generators.uipath_generator import UiPathGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Generate UiPath projects from Process Design Documents (PDD)"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for session data (in production, use Redis/database)
session_data = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "PDD to UiPath Project Generator",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload")
async def upload_pdd(file: UploadFile = File(...)):
    """
    Upload a PDD PDF file for processing.
    
    Returns:
        Session ID and extracted sections for review
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit ({settings.max_file_size_mb}MB)"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(contents)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Parse PDF
        parser = PDFParser(max_pages=settings.max_pdf_pages)
        extracted = parser.extract(str(tmp_path))
        
        # Get statistics
        stats = parser.get_statistics(extracted)
        
        # Check page limit
        if stats["total_pages"] > settings.max_pdf_pages:
            raise HTTPException(
                status_code=400,
                detail=f"PDF exceeds maximum page limit ({settings.max_pdf_pages})"
            )
        
        # Get full text
        full_text = parser.get_full_text(extracted)
        
        # Classify sections using LLM service
        llm_service = LLMService()
        sections = llm_service.classify_sections(full_text)
        
        # Create session
        import uuid
        session_id = str(uuid.uuid4())
        session_data[session_id] = {
            "pdf_path": str(tmp_path),
            "full_text": full_text,
            "sections": [s.dict() for s in sections],
            "stats": stats,
            "extracted_pages": len(extracted)
        }
        
        logger.info(f"Uploaded PDD: {file.filename}, {stats['total_pages']} pages, session={session_id}")
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "statistics": stats,
            "sections": [s.dict() for s in sections],
            "message": "PDD uploaded and sections extracted. Please review sections before generating."
        }
    
    except Exception as e:
        logger.error(f"Error processing PDD: {str(e)}")
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/{session_id}")
async def generate_project(session_id: str):
    """
    Generate UiPath project from reviewed sections.
    
    Args:
        session_id: Session ID from upload response
        
    Returns:
        Path to generated project (for download)
    """
    if session_id not in session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = session_data[session_id]
    
    try:
        # Extract IR from sections
        llm_service = LLMService()
        
        # Convert sections back to objects
        from app.models.ir import PDDSection
        sections = [PDDSection(**s) for s in session["sections"]]
        
        ir = llm_service.extract_ir(sections)
        
        # Calculate quality score
        quality_score = llm_service.calculate_quality_score(sections, ir)
        ir.quality_score = quality_score
        
        # Generate UiPath project
        generator = UiPathGenerator()
        project_path = generator.generate(ir)
        
        # Store project path in session
        session["project_path"] = str(project_path)
        session["ir"] = ir.dict()
        session["quality_score"] = quality_score
        
        logger.info(f"Generated project for session {session_id}: {project_path}")
        
        return {
            "session_id": session_id,
            "project_name": ir.process.name,
            "project_path": str(project_path),
            "quality_score": quality_score,
            "steps_count": len(ir.steps),
            "warnings": ir.warnings,
            "message": "Project generated successfully. Ready for download."
        }
    
    except Exception as e:
        logger.error(f"Error generating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{session_id}")
async def download_project(session_id: str):
    """
    Download generated project as ZIP file.
    
    Args:
        session_id: Session ID from generate response
        
    Returns:
        ZIP file of the project
    """
    if session_id not in session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = session_data[session_id]
    
    if "project_path" not in session:
        raise HTTPException(status_code=400, detail="Project not generated yet. Call /generate first.")
    
    project_path = Path(session["project_path"])
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project folder not found")
    
    # Create ZIP file
    zip_path = project_path.parent / f"{project_path.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(project_path.parent)
                zipf.write(file_path, arcname)
    
    logger.info(f"Created ZIP for session {session_id}: {zip_path}")
    
    return FileResponse(
        path=str(zip_path),
        filename=f"{project_path.name}.zip",
        media_type="application/zip"
    )


@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information without triggering regeneration."""
    if session_id not in session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    session = session_data[session_id]
    
    return {
        "session_id": session_id,
        "filename": session.get("filename", "unknown"),
        "statistics": session.get("stats", {}),
        "sections_count": len(session.get("sections", [])),
        "project_generated": "project_path" in session,
        "quality_score": session.get("quality_score"),
        "project_name": session.get("ir", {}).get("process", {}).get("name")
    }


# Import os at module level for download function
import os


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
