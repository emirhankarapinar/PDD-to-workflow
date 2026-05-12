"""
PDD Parser Service - Extracts text and sections from PDF documents.

Uses PyMuPDF for fast text extraction and pdfplumber for table extraction.
Implements multi-pass parsing pipeline as defined in the implementation plan.
"""
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedText:
    """Extracted text with metadata."""
    text: str
    page_number: int
    has_tables: bool = False
    has_images: bool = False
    tables: List[List[List[str]]] = None  # List of tables (each table is list of rows)


@dataclass
class PDDSection:
    """Extracted PDD section."""
    name: str
    content: str
    pages: str
    confidence: float


class PDFParser:
    """
    PDF Parser for PDD documents.
    
    Implements Pass 1 of the parsing pipeline:
    - Text extraction with page numbers
    - Table detection and extraction
    - Image flagging
    """
    
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
    
    def extract(self, pdf_path: str) -> List[ExtractedText]:
        """
        Extract text and tables from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of ExtractedText objects per page
        """
        extracted = []
        
        # Extract text with PyMuPDF
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            if page_num >= self.max_pages:
                logger.warning(f"Reached max pages limit ({self.max_pages})")
                break
            
            # Extract text
            text = page.get_text("text")
            
            # Check for images
            images = page.get_images(full=True)
            has_images = len(images) > 0
            
            # Extract tables with pdfplumber
            tables = []
            has_tables = False
            
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    pdf_page = pdf.pages[page_num]
                    pdf_tables = pdf_page.extract_tables()
                    if pdf_tables:
                        tables = pdf_tables
                        has_tables = True
            
            extracted.append(ExtractedText(
                text=text,
                page_number=page_num + 1,  # 1-indexed
                has_tables=has_tables,
                has_images=has_images,
                tables=tables or []
            ))
        
        doc.close()
        return extracted
    
    def get_full_text(self, extracted: List[ExtractedText]) -> str:
        """Combine all extracted text into a single string."""
        return "\n\n".join([
            f"[Page {e.page_number}]\n{e.text}"
            for e in extracted
        ])
    
    def get_statistics(self, extracted: List[ExtractedText]) -> Dict:
        """Get extraction statistics."""
        total_pages = len(extracted)
        pages_with_tables = sum(1 for e in extracted if e.has_tables)
        pages_with_images = sum(1 for e in extracted if e.has_images)
        total_words = sum(len(e.text.split()) for e in extracted)
        
        return {
            "total_pages": total_pages,
            "pages_with_tables": pages_with_tables,
            "pages_with_images": pages_with_images,
            "total_words": total_words,
            "avg_words_per_page": total_words / total_pages if total_pages > 0 else 0
        }
