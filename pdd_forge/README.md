# PDD Forge

**Generate UiPath projects from Process Design Documents (PDD)**

PDD Forge is a developer tooling platform that ingests PDF-based Process Design Documents and produces structurally valid, template-aware UiPath project scaffolds — including XAML workflows, configuration files, and connected components.

## Features

- **PDF Parsing**: Extract text and tables from PDD PDFs using PyMuPDF and pdfplumber
- **LLM-Powered Analysis**: Semantic analysis for section classification, step extraction, and business rule identification
- **REFramework Generation**: Generate complete REFramework (Queue-based) project structures
- **Template-Based XAML**: Safe, validated XAML generation using templates (not LLM-generated)
- **Config.xlsx Generation**: Automatic population of Settings, Constants, and Assets sheets
- **Quality Scoring**: PDD quality assessment with actionable feedback
- **Traceability**: Link generated artifacts back to PDD sections

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend API    │────▶│   Generator     │
│   (React)       │     │   (FastAPI)      │     │   Engine        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   LLM Service    │
                       │   (GPT-4o/Mock)  │
                       └──────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- UiPath Studio 2023.10+ (to open generated projects)

### Backend Setup

```bash
cd pdd_forge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Run server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd pdd_forge/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Docker (Alternative)

```bash
docker-compose up --build
```

## Usage

1. **Upload PDD**: Upload a PDF Process Design Document (max 100 pages)
2. **Review Sections**: Review and edit extracted sections
3. **Generate**: Click generate to create UiPath project
4. **Download**: Download ZIP file with complete project structure
5. **Open in Studio**: Open generated project in UiPath Studio

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/upload` | POST | Upload PDD PDF |
| `/api/generate/{session_id}` | POST | Generate UiPath project |
| `/api/download/{session_id}` | GET | Download project ZIP |
| `/api/session/{session_id}` | GET | Get session info |

## Project Structure

```
pdd_forge/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration
│   │   ├── generators/    # UiPath project generator
│   │   ├── models/        # Pydantic models (IR schema)
│   │   ├── services/      # Business logic (parser, LLM)
│   │   └── main.py        # FastAPI application
│   └── tests/
├── frontend/
│   └── src/
├── templates/
│   └── reframework-queue/
└── pyproject.toml
```

## Configuration

Create a `.env` file:

```env
# Application
APP_NAME=PDD Forge
DEBUG=false

# LLM (optional - mock mode works without API key)
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
LLM_MOCK=true

# Processing limits
MAX_PDF_PAGES=100
MAX_FILE_SIZE_MB=50

# Paths
TEMPLATE_DIR=templates
OUTPUT_DIR=output
```

## Testing

```bash
# Run tests
pytest backend/tests -v

# Run with coverage
pytest backend/tests --cov=backend/app
```

## Limitations (MVP)

- **Mock LLM Mode**: Default installation uses mock responses. For real extraction, configure OpenAI API key.
- **Single Template**: Only REFramework (Queue) template supported in MVP.
- **No Selector Generation**: Selectors require live application access; generated as TODO placeholders.
- **Human Review Required**: Generated projects are scaffolds, not production-ready automations.

## Roadmap

### v1.1 (Next Release)
- [ ] REFramework (Tabular) template
- [ ] Linear Process template
- [ ] IR review/edit UI
- [ ] Existing project injection

### v2.0
- [ ] Flowchart image extraction (vision models)
- [ ] Orchestrator API integration
- [ ] User accounts and project history
- [ ] Multi-language support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Based on the [implementation plan](implementation_plan.md) following best practices for PDD-to-code generation
- Uses UiPath REFramework template structure
- Inspired by modern code-generation platforms
