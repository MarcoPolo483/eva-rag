# EVA RAG Development Guide

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
│                     (main.py)                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer                                │
│              (api/ingest.py)                                │
│  - Request validation                                       │
│  - Response formatting                                      │
│  - Error handling                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Ingestion Service                              │
│         (services/ingestion_service.py)                     │
│  - Orchestrates full pipeline                               │
│  - Coordinates all services                                 │
└──┬───────┬─────────┬──────────┬──────────┬─────────────────┘
   │       │         │          │          │
   ▼       ▼         ▼          ▼          ▼
┌─────┐ ┌────┐  ┌────────┐ ┌────────┐ ┌──────────┐
│Load │ │Lang│  │Chunking│ │Embed   │ │Storage   │
│er   │ │uage│  │Service │ │Service │ │Services  │
└─────┘ └────┘  └────────┘ └────────┘ └──────────┘
  │                                       │
  ▼                                       ▼
┌──────────┐                         ┌──────────┐
│Loaders   │                         │Azure     │
│(PDF,DOCX,│                         │Services  │
│TXT)      │                         │(Blob,    │
└──────────┘                         │Cosmos,   │
                                     │OpenAI)   │
                                     └──────────┘
```

## 📁 Project Structure

```
eva-rag/
├── src/eva_rag/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (env vars, Azure config)
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   └── ingest.py          # Document ingestion endpoint
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── document.py        # Document metadata models
│   │   ├── chunk.py           # Chunk models
│   │   └── ingest.py          # API request/response models
│   │
│   ├── loaders/                # Document loaders
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract base loader
│   │   ├── factory.py         # Loader factory
│   │   ├── pdf_loader.py      # PDF extraction
│   │   ├── docx_loader.py     # DOCX extraction
│   │   └── text_loader.py     # TXT/MD extraction
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── ingestion_service.py    # Main orchestrator
│   │   ├── chunking_service.py     # Text chunking
│   │   ├── embedding_service.py    # Vector embeddings
│   │   ├── language_service.py     # Language detection
│   │   ├── metadata_service.py     # Cosmos DB operations
│   │   └── storage_service.py      # Azure Blob operations
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── datetime_utils.py  # Datetime helpers
│
├── tests/                      # Test suite (94.62% coverage!)
│   ├── test_*.py              # Unit tests
│   └── integration/           # Integration tests
│
├── docs/                       # Documentation
│   └── SPECIFICATION.md       # Technical specification
│
├── pyproject.toml             # Poetry dependencies
├── .env.example               # Environment template
├── README.md                  # Project overview
├── API-USAGE-GUIDE.md         # API documentation
└── TEST-COVERAGE-REPORT.md    # Coverage report
```

## 🚀 Getting Started

### 1. Clone and Setup

```powershell
# Clone repository
git clone https://github.com/MarcoPolo483/eva-rag.git
cd eva-rag

# Install dependencies
poetry install

# Setup environment
Copy-Item .env.example .env
code .env  # Configure Azure credentials
```

### 2. Environment Variables

Required in `.env`:

```bash
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
AZURE_STORAGE_CONTAINER_NAME="documents"

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT="https://your-account.documents.azure.com:443/"
AZURE_COSMOS_KEY="your_key"
AZURE_COSMOS_DATABASE="eva-rag"
AZURE_COSMOS_CONTAINER="documents"

# Azure OpenAI
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your_key"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"
AZURE_OPENAI_API_VERSION="2024-02-01"

# Application
MAX_FILE_SIZE_MB=50
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### 3. Run Development Server

```powershell
# Start server with auto-reload
poetry run uvicorn eva_rag.main:app --reload --host 127.0.0.1 --port 8000

# Access API docs
Start-Process "http://127.0.0.1:8000/api/v1/docs"
```

## 🧪 Testing

### Run All Tests

```powershell
# Unit tests only (fast)
poetry run pytest tests/ -m "not integration"

# With coverage report
poetry run pytest tests/ -m "not integration" --cov=src/eva_rag --cov-report=html

# View coverage report
Start-Process htmlcov/index.html
```

### Run Specific Tests

```powershell
# Test single module
poetry run pytest tests/test_embedding_service.py -v

# Test single function
poetry run pytest tests/test_pdf_loader.py::test_pdf_loader_extracts_text -v

# Run with markers
poetry run pytest tests/ -m "integration" -v
```

### Writing Tests

```python
# tests/test_your_feature.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

def test_simple_function():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await your_async_function()
    assert result is not None

def test_with_mock():
    """Test with mocked dependency."""
    with patch('your_module.DependencyClass') as MockDep:
        mock_instance = Mock()
        mock_instance.method.return_value = "mocked"
        MockDep.return_value = mock_instance
        
        result = your_function_using_dependency()
        assert result == "mocked"
```

## 🏭 Adding New Features

### Add New Document Loader

1. Create loader class in `loaders/`:

```python
# loaders/xlsx_loader.py
from io import BytesIO
from openpyxl import load_workbook
from .base import DocumentLoader, ExtractedDocument

class ExcelLoader(DocumentLoader):
    """Extract text from Excel files."""
    
    def load(self, file: BytesIO, filename: str) -> ExtractedDocument:
        """Extract text from XLSX file."""
        workbook = load_workbook(file, data_only=True)
        
        text_parts = []
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text_parts.append(f"[SHEET: {sheet_name}]")
            
            for row in sheet.iter_rows(values_only=True):
                row_text = " | ".join(str(cell) for cell in row if cell)
                if row_text:
                    text_parts.append(row_text)
        
        return ExtractedDocument(
            text="\n".join(text_parts),
            page_count=len(workbook.sheetnames),
            metadata={"sheets": workbook.sheetnames}
        )
```

2. Register in factory:

```python
# loaders/factory.py
from .xlsx_loader import ExcelLoader

class LoaderFactory:
    @staticmethod
    def get_loader(filename: str) -> DocumentLoader:
        ext = Path(filename).suffix.lower()
        
        if ext == ".pdf":
            return PDFLoader()
        elif ext == ".docx":
            return DOCXLoader()
        elif ext in [".txt", ".md"]:
            return TextLoader()
        elif ext in [".xlsx", ".xls"]:  # Add this
            return ExcelLoader()
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
```

3. Add tests:

```python
# tests/test_xlsx_loader.py
import pytest
from openpyxl import Workbook
from io import BytesIO
from eva_rag.loaders.xlsx_loader import ExcelLoader

def test_excel_loader_extracts_text():
    """Test Excel loader extracts cell data."""
    # Create test Excel file
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws['A1'] = "Header1"
    ws['B1'] = "Header2"
    ws['A2'] = "Value1"
    ws['B2'] = "Value2"
    
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    
    # Load with ExcelLoader
    loader = ExcelLoader()
    result = loader.load(excel_buffer, "test.xlsx")
    
    assert "[SHEET: Sheet1]" in result.text
    assert "Header1" in result.text
    assert "Value1" in result.text
    assert result.page_count == 1
```

### Add New API Endpoint

1. Create endpoint in `api/`:

```python
# api/search.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/rag", tags=["RAG"])

class SearchRequest(BaseModel):
    query: str
    space_id: str
    tenant_id: str
    limit: int = 10

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    document_id: str

@router.post("/search", response_model=list[SearchResult])
async def search_documents(request: SearchRequest):
    """Search for relevant document chunks."""
    # Implement search logic
    pass
```

2. Register router in `main.py`:

```python
from eva_rag.api import ingest, search

app.include_router(ingest.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
```

## 🔍 Debugging

### Enable Debug Logging

```python
# main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("eva_rag")
```

### VS Code Launch Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "eva_rag.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v",
        "-s"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

## 📊 Code Quality

### Run Linters

```powershell
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Type checking
poetry run mypy src/

# Linting
poetry run ruff check src/ tests/
```

### Pre-commit Checks

```powershell
# Run all quality checks
poetry run pytest tests/ -m "not integration" --cov=src/eva_rag
poetry run black --check src/ tests/
poetry run isort --check src/ tests/
poetry run mypy src/
```

## 🚢 Deployment

### Build Docker Image

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "eva_rag.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
# Build and run
docker build -t eva-rag:latest .
docker run -p 8000:8000 --env-file .env eva-rag:latest
```

## 📝 Contributing Guidelines

1. **Branch Naming**: `feature/description`, `bugfix/description`
2. **Commit Messages**: Follow conventional commits
3. **Tests Required**: All new code must have tests
4. **Coverage**: Maintain >90% coverage
5. **Documentation**: Update docs for API changes
6. **Type Hints**: All functions must have type hints
7. **Docstrings**: Required for public functions/classes

## 🐛 Common Issues

### Issue: Azure Connection Errors

```
Solution: Check .env file has correct credentials
Verify: Azure services are running in correct region
Test: Run poetry run python check_azure_connectivity.py
```

### Issue: ImportError after adding dependency

```
Solution: poetry install
Restart: VS Code Python language server
```

### Issue: Tests failing after merge

```
Solution: poetry update
Clean: Remove __pycache__ directories
Rebuild: poetry run pytest tests/ --cache-clear
```

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Poetry Docs**: https://python-poetry.org/docs/
- **Azure SDK**: https://learn.microsoft.com/azure/developer/python/
- **Pydantic**: https://docs.pydantic.dev/
- **Pytest**: https://docs.pytest.org/

## 🤝 Getting Help

- **GitHub Issues**: https://github.com/MarcoPolo483/eva-rag/issues
- **Discussions**: https://github.com/MarcoPolo483/eva-rag/discussions
- **Internal Wiki**: Link to internal documentation
