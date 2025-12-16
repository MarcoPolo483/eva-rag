# EVA RAG Engine

**Retrieval-Augmented Generation engine for the EVA Suite**

[![POD](https://img.shields.io/badge/POD-F-blue)](https://github.com/MarcoPolo483/eva-suite)
[![Owner](https://img.shields.io/badge/Owner-P04--LIB%20%2B%20P06--RAG-green)](https://github.com/MarcoPolo483/eva-suite)
[![Phase](https://img.shields.io/badge/Phase-1%3A%20Document%20Ingestion-yellow)](docs/SPECIFICATION.md)

## Overview

EVA-RAG provides document ingestion, chunking, vector embedding, hybrid search, and citation extraction for the EVA Suite.

### Features

- **Document Ingestion**: PDF, DOCX, TXT, HTML, XML, CSV, Excel, PowerPoint, MS Project
  - **Microsoft 365 Suite**: Full support for Excel (.xlsx, .xls), PowerPoint (.pptx), Project (.mpp XML)
  - **Kaggle Datasets**: Optimized CSV loader for large employment datasets (120MB+)
  - **XML & Folder Processing**: Automatic schema detection and recursive folder ingestion
- **Text Chunking**: Semantic chunking with LangChain (500 tokens, 50 overlap)
- **Vector Embedding**: Azure OpenAI text-embedding-3-small (1536 dims)
- **Hybrid Search**: Vector (cosine) + Keyword (BM25) with RRF fusion
- **Reranking**: Cross-encoder for precision improvement
- **Citation Extraction**: Link answers to source documents with page numbers
- **Bilingual**: EN-CA and FR-CA support with automatic language detection

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Azure services (Storage, Cosmos DB, OpenAI, AI Search)
- Redis

### Installation

```powershell
# Install dependencies
poetry install

# Copy environment file
Copy-Item .env.example .env

# Edit .env with your Azure credentials
code .env
```

### Run Server

```powershell
# Development
poetry run uvicorn eva_rag.main:app --reload --host 0.0.0.0 --port 8000

# Production
poetry run uvicorn eva_rag.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Visit http://localhost:8000/api/v1/docs for Swagger UI

## Project Structure

```
eva-rag/
├── src/eva_rag/           # Source code
│   ├── api/               # FastAPI endpoints
│   ├── loaders/           # Document loaders (13 formats supported)
│   │   ├── pdf_loader.py      # PDF documents
│   │   ├── docx_loader.py     # Microsoft Word
│   │   ├── csv_loader.py      # CSV with delimiter detection
│   │   ├── excel_loader.py    # Excel (.xlsx, .xls)
│   │   ├── pptx_loader.py     # PowerPoint presentations
│   │   ├── mpp_loader.py      # MS Project (XML format)
│   │   ├── xml_loader.py      # XML with schema detection
│   │   ├── folder_loader.py   # Recursive folder processing
│   │   └── ...                # HTML, TXT, MD loaders
│   ├── services/          # Business logic (chunking, embedding, search)
│   ├── models/            # Pydantic models
│   └── utils/             # Utilities
├── tests/                 # Tests (95%+ coverage required)
├── docs/                  # Documentation
│   ├── SPECIFICATION.md       # Complete specification (834 lines)
│   └── KAGGLE-INTEGRATION.md  # Kaggle employment datasets guide
└── pyproject.toml         # Poetry dependencies
```

## Development

### Run Tests

```powershell
# All tests with coverage
poetry run pytest

# Specific test file
poetry run pytest tests/test_loaders.py

# With coverage report
poetry run pytest --cov=src/eva_rag --cov-report=html
```

### Type Checking

```powershell
poetry run mypy src/
```

### Linting

```powershell
poetry run ruff check src/
poetry run black src/ --check
```

### Format Code

```powershell
poetry run black src/
poetry run ruff check src/ --fix
```

## API Endpoints

### POST /api/v1/rag/ingest

Upload document, extract text, chunk, embed, and index.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "space_id=uuid" \
  -F "tenant_id=uuid"
```

**Response**:
```json
{
  "document_id": "uuid",
  "status": "indexed",
  "chunk_count": 42,
  "processing_time_ms": 3500,
  "language_detected": "en"
}
```

### POST /api/v1/rag/search

Retrieve relevant chunks for a query.

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the eligibility criteria?",
    "space_id": "uuid",
    "tenant_id": "uuid",
    "top_k": 5
  }'
```

**Response**:
```json
{
  "results": [
    {
      "chunk_id": "uuid",
      "document_name": "policy.pdf",
      "page_number": 3,
      "content": "Eligibility criteria: ...",
      "relevance_score": 0.92
    }
  ]
}
```

## Implementation Phases

- ✅ **Phase 1** (Weeks 1-2): Document Ingestion - **COMPLETE**
  - ✅ 13 file formats supported: PDF, DOCX, TXT, MD, HTML, XML, CSV, Excel, PowerPoint, MS Project
  - ✅ CSV loader for Kaggle employment datasets (120MB+ files)
  - ✅ XML loader with automatic schema detection
  - ✅ Folder loader for recursive directory processing
  - ✅ Microsoft 365 suite support (Excel, PowerPoint, Project)
- ⏳ **Phase 2** (Weeks 3-4): Text Chunking & Embedding
- ⏳ **Phase 3** (Weeks 5-6): Vector Indexing & Search
- ⏳ **Phase 4** (Weeks 7-8): Reranking & Citation Extraction

## Quality Gates

All 12 quality gates must pass before production deployment:

- ✅ Test Coverage: 95%+
- ✅ Retrieval Accuracy: 90%+ (recall@5)
- ✅ Search Latency: <500ms (p95)
- ✅ Chunk Quality: 95%+ complete sentences
- ✅ Bilingual Support: EN-CA + FR-CA
- ✅ Type Safety: 100% type hints (mypy strict)

See [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for complete details.

## References

- [Azure AI Search Hybrid Search](https://learn.microsoft.com/azure/search/hybrid-search-overview)
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [OpenWebUI Retrieval](https://github.com/open-webui/open-webui)
- [PubSec Info Assistant](https://github.com/microsoft/PubSec-Info-Assistant)

## License

Proprietary - EVA Suite © 2025

## Contact

Marco Presta - marco@evasuite.com

<!-- Phase 3 enforcement system test -->

<!-- Quality gate smoke test -->

<!-- Trigger refresh -->

<!-- Trigger with fixed branch -->
