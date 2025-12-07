# EVA RAG Engine (eva-rag)

**Comprehensive Specification for Autonomous Implementation**

---

## 1. Vision & Business Value

### What This Service Delivers

EVA-RAG is the **Retrieval-Augmented Generation engine** for the EVA Suite. It provides:

- **Document Ingestion**: Upload PDF/DOCX/TXT files, extract text, detect language
- **Text Chunking**: Split documents into semantic chunks (500 tokens, 50 token overlap)
- **Vector Embedding**: Generate embeddings using Azure OpenAI (text-embedding-3-small, 1536 dimensions)
- **Vector Storage**: Store embeddings in Azure AI Search with metadata (filename, page, language)
- **Semantic Search**: Retrieve relevant chunks using cosine similarity
- **Hybrid Search**: Combine vector search + keyword search (BM25) for better recall
- **Citation Extraction**: Link answers to source documents with page numbers and snippets
- **Reranking**: Use cross-encoder to rerank results for better precision

### Success Metrics

- **Retrieval Accuracy**: 90%+ relevance (measured by manual evaluation of top-3 results)
- **Latency**: < 500ms (p95) for retrieval (embedding + search + reranking)
- **Throughput**: 100+ queries/second (concurrent retrieval operations)
- **Chunk Quality**: 95%+ of chunks contain complete sentences (no mid-sentence splits)

### Business Impact

- **Accurate Answers**: Citations prove answers come from source documents (no hallucinations)
- **Bilingual Support**: EN-CA and FR-CA document processing (automatic language detection)
- **Multi-Tenant**: Complete isolation between organizations (tenant_id on all operations)
- **Compliance**: Document retention policies, audit trails, PII masking in logs

---

## 2. Architecture Overview

### System Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EVA Suite Services                          │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ eva-api  │  │ eva-ui   │  │ eva-auth │  │ eva-mcp  │  ...       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │             │             │                   │
│       └─────────────┴─────────────┴─────────────┘                   │
│                           │                                         │
│                           ▼                                         │
│       ┌───────────────────────────────────────────┐                │
│       │      eva-rag (This Service)               │                │
│       │  Ingestion │ Chunking │ Embedding │ Search│                │
│       └───────────┬───────────────────────────────┘                │
│                   │                                                 │
└───────────────────┼─────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌────────────────┐     ┌────────────────────┐
│ Azure AI Search│     │  Azure Blob Storage│
│ (Vector Index) │     │  (Original Files)  │
└────────────────┘     └────────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │Azure OpenAI  │
                       │(Embeddings)  │
                       └──────────────┘
```

### RAG Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          eva-rag Service                            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 1. Document Ingestion                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ Upload   │→│ Language │→│ Text     │→│ Metadata │     │  │
│  │  │ Handler  │  │ Detect   │  │ Extract  │  │ Extract  │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │                 2. Text Chunking                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │  │
│  │  │Recursive │→│ Sentence │→│ Overlap  │                   │  │
│  │  │ Split    │  │ Boundary │  │ Handler  │                   │  │
│  │  └──────────┘  └──────────┘  └──────────┘                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │                 3. Vector Embedding                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │  │
│  │  │ Batch    │→│ Azure    │→│ Cache    │                   │  │
│  │  │ Processor│  │ OpenAI   │  │ (Redis)  │                   │  │
│  │  └──────────┘  └──────────┘  └──────────┘                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │                 4. Semantic Search                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ Query    │→│ Hybrid   │→│ Rerank   │→│ Citation │     │  │
│  │  │ Embed    │  │ Search   │  │(CrossEnc)│  │ Extract  │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Stack

### Primary Technologies

- **Language**: Python 3.11+ (async/await for concurrent operations)
- **Framework**: FastAPI 0.100+ (async API endpoints, OpenAPI docs)
- **Vector Database**: Azure AI Search (hybrid search, semantic reranker, filters)
- **Embeddings**: Azure OpenAI text-embedding-3-small (1536 dimensions, $0.02/1M tokens)
- **Document Processing**: PyPDF2, python-docx, UnstructuredIO (text extraction)
- **Text Splitting**: LangChain RecursiveCharacterTextSplitter (semantic chunking)
- **Reranking**: Sentence Transformers cross-encoder (ms-marco-MiniLM-L-6-v2)
- **Storage**: Azure Blob Storage (original documents), Azure Cosmos DB (metadata)
- **Caching**: Redis (embedding cache to reduce OpenAI costs)

### RAG Pipeline Components

1. **Document Loaders**:
   - PDF: PyPDF2 (extract text + page numbers)
   - DOCX: python-docx (extract text + preserve formatting)
   - TXT/MD: Plain text (UTF-8)
   - OCR: Azure Document Intelligence (scanned documents)

2. **Chunking Strategies**:
   - **Recursive**: Split by paragraphs → sentences → words (LangChain)
   - **Sentence-Aware**: Never split mid-sentence (NLTK sentence tokenizer)
   - **Overlap**: 50 tokens overlap for context continuity
   - **Size**: 500 tokens per chunk (optimal for Azure OpenAI)

3. **Embedding Models**:
   - **Primary**: text-embedding-3-small (1536 dims, $0.02/1M tokens)
   - **Fallback**: text-embedding-ada-002 (1536 dims, legacy support)
   - **Batch Size**: 100 chunks per API call (rate limit: 3000 RPM)

4. **Search Strategies**:
   - **Vector Search**: Cosine similarity on embeddings (top-K=20)
   - **Keyword Search**: BM25 on text fields (boost filename 2x)
   - **Hybrid Search**: Combine vector + keyword (RRF fusion)
   - **Semantic Reranker**: Azure AI Search semantic search (GPT-4 reranking)

5. **Reranking Models**:
   - **Cross-Encoder**: ms-marco-MiniLM-L-6-v2 (fast, accurate)
   - **Input**: Query + candidate chunk → relevance score (0-1)
   - **Threshold**: 0.5 minimum relevance (filter low-quality results)

---

## 4. API Specification

### 4.1 Ingest Document

**POST** `/api/v1/rag/ingest`

Upload document, extract text, chunk, embed, and index.

**Request**:
```json
{
  "file": "multipart/form-data",
  "space_id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "metadata": {
    "document_type": "policy",
    "language": "en",
    "tags": ["benefits", "eligibility"]
  }
}
```

**Response**:
```json
{
  "document_id": "uuid",
  "status": "indexed",
  "chunk_count": 42,
  "processing_time_ms": 3500,
  "embedding_tokens": 21000,
  "language_detected": "en"
}
```

**Business Logic**:
1. Validate user has access to space (call eva-api)
2. Upload file to Azure Blob Storage (tenant isolation)
3. Extract text with PyPDF2/python-docx/OCR
4. Detect language with langdetect (en/fr)
5. Chunk text with RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
6. Generate embeddings in batches (100 chunks, check Redis cache)
7. Index in Azure AI Search with metadata (space_id, tenant_id, filename, page, language)
8. Update eva-core Document entity (status=indexed, chunk_count)
9. Emit DocumentIndexed event

**Error Handling**:
- 400: Invalid file format (only PDF/DOCX/TXT supported)
- 413: File too large (max 50MB)
- 429: Rate limit exceeded (Azure OpenAI throttling)
- 503: Azure AI Search unavailable (retry with exponential backoff)

---

### 4.2 Search Documents

**POST** `/api/v1/rag/search`

Retrieve relevant chunks for a query.

**Request**:
```json
{
  "query": "What are the eligibility criteria for parental benefits?",
  "space_id": "uuid",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "top_k": 5,
  "search_mode": "hybrid",
  "rerank": true,
  "filters": {
    "document_type": "policy",
    "language": "en"
  }
}
```

**Response**:
```json
{
  "query_id": "uuid",
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_name": "parental-benefits-policy.pdf",
      "page_number": 3,
      "content": "Eligibility criteria: 1) Employed for 600+ hours...",
      "relevance_score": 0.92,
      "language": "en",
      "metadata": {
        "document_type": "policy",
        "section": "Eligibility"
      }
    }
  ],
  "processing_time_ms": 450,
  "search_mode_used": "hybrid",
  "reranked": true
}
```

**Business Logic**:
1. Validate user has access to space
2. Generate query embedding (Azure OpenAI)
3. Execute hybrid search:
   - Vector search: Cosine similarity on embeddings (top-K=20)
   - Keyword search: BM25 on content field (boost filename)
   - RRF fusion: Combine rankings (k=60)
4. Apply filters: space_id, tenant_id, language, document_type
5. Rerank with cross-encoder (if enabled): Top-20 → relevance scores → filter < 0.5
6. Return top-K results with citations
7. Emit QueryExecuted event

**Error Handling**:
- 400: Missing required fields (query, space_id, tenant_id)
- 403: User does not have access to space
- 429: Rate limit exceeded (Azure OpenAI)
- 503: Azure AI Search unavailable

---

### 4.3 Delete Document

**DELETE** `/api/v1/rag/documents/{document_id}`

Remove document and all chunks from index.

**Request**:
```json
{
  "tenant_id": "uuid",
  "user_id": "uuid"
}
```

**Response**:
```json
{
  "document_id": "uuid",
  "chunks_deleted": 42,
  "status": "deleted"
}
```

**Business Logic**:
1. Validate user has permission to delete (owner or admin)
2. Delete from Azure AI Search (filter by document_id + tenant_id)
3. Delete from Azure Blob Storage
4. Update eva-core Document entity (status=deleted, soft delete)
5. Emit DocumentDeleted event

---

## 5. Domain Models

### 5.1 DocumentChunk

```python
# src/eva_rag/domain/models/document_chunk.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentChunk(BaseModel):
    """Document chunk with vector embedding and metadata."""
    
    # Identity
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    space_id: str
    tenant_id: str
    
    # Content
    content: str = Field(min_length=10, max_length=2000)
    chunk_index: int = Field(ge=0)  # Position in document (0-indexed)
    page_number: Optional[int] = None
    
    # Embedding
    embedding: List[float] = Field(min_items=1536, max_items=1536)
    embedding_model: str = "text-embedding-3-small"
    
    # Metadata
    document_name: str
    language: str = "en"  # en, fr
    document_type: str = "other"  # policy, jurisprudence, guidance, faq
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit
    indexed_at: datetime = Field(default_factory=datetime.utcnow)
```

### 5.2 SearchRequest

```python
# src/eva_rag/domain/models/search_request.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class SearchMode(str, Enum):
    VECTOR = "vector"       # Pure vector search
    KEYWORD = "keyword"     # BM25 keyword search
    HYBRID = "hybrid"       # Vector + keyword (RRF fusion)

class SearchRequest(BaseModel):
    """Search request parameters."""
    
    query: str = Field(min_length=1, max_length=2000)
    space_id: str
    tenant_id: str
    user_id: str
    
    # Search parameters
    top_k: int = Field(default=5, ge=1, le=50)
    search_mode: SearchMode = SearchMode.HYBRID
    rerank: bool = True
    
    # Filters
    filters: Optional[Dict[str, Any]] = None
```

### 5.3 SearchResult

```python
# src/eva_rag/domain/models/search_result.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ChunkResult(BaseModel):
    """Single search result chunk."""
    
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    language: str
    metadata: Dict[str, Any]

class SearchResult(BaseModel):
    """Search results with metadata."""
    
    query_id: str
    results: List[ChunkResult]
    processing_time_ms: int
    search_mode_used: SearchMode
    reranked: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

---

## 6. Business Rules & Validation

### Document Ingestion Rules

1. **File Size Limits**:
   - PDF/DOCX: Max 50MB
   - TXT: Max 10MB
   - Reason: Avoid long processing times, control costs

2. **Supported Formats**:
   - PDF: PyPDF2 (text-based), Azure Document Intelligence (OCR for scanned)
   - DOCX: python-docx
   - TXT/MD: Plain text
   - Reject: Images alone, videos, executables

3. **Language Detection**:
   - Use `langdetect` library (97% accuracy)
   - Supported: EN, FR
   - If confidence < 0.8, default to EN and log warning

4. **Tenant Isolation**:
   - All operations filter by `tenant_id`
   - Cross-tenant access blocked at database level (Azure AI Search filters)
   - Blob storage: Separate containers per tenant

5. **Duplicate Detection**:
   - Compute SHA-256 hash of file content
   - If hash exists in space, reject with 409 Conflict
   - Allow same file in different spaces (different contexts)

### Chunking Rules

1. **Chunk Size**:
   - Target: 500 tokens (OpenAI tokenizer)
   - Max: 800 tokens (hard limit for Azure OpenAI)
   - Min: 50 tokens (avoid meaningless fragments)

2. **Overlap**:
   - 50 tokens overlap between adjacent chunks
   - Ensures context continuity (question spanning chunk boundaries)

3. **Sentence Boundaries**:
   - Never split mid-sentence (use NLTK sentence tokenizer)
   - If sentence > 800 tokens, split at clause boundaries (commas, semicolons)

4. **Page Number Preservation**:
   - Extract page numbers during PDF parsing
   - Attach to each chunk for citation purposes
   - Handle multi-page chunks (store range: "3-4")

### Search Rules

1. **Top-K Limits**:
   - Min: 1 result
   - Max: 50 results (avoid overwhelming UI, reduce costs)
   - Default: 5 results

2. **Reranking Threshold**:
   - Cross-encoder score >= 0.5 to include result
   - Filters out irrelevant results (improves precision)

3. **Hybrid Search Fusion**:
   - RRF (Reciprocal Rank Fusion) with k=60
   - Formula: `score = sum(1 / (k + rank_i))` for each result list
   - Combines vector and keyword rankings

4. **Access Control**:
   - User must be member of space (checked via eva-api)
   - Filter all searches by `space_id` + `tenant_id`
   - No cross-space search (privacy requirement)

---

## 7. Performance & Scalability

### Latency Targets

- **Document Ingestion**: < 5s for 10-page PDF (p95)
  - Text extraction: 1s
  - Chunking: 0.5s
  - Embedding (100 chunks): 2s (batch API)
  - Indexing: 1.5s

- **Search**: < 500ms (p95)
  - Query embedding: 100ms
  - Hybrid search: 200ms
  - Reranking (20 chunks): 150ms
  - Citation extraction: 50ms

### Throughput Targets

- **Ingestion**: 10 documents/minute (per worker)
- **Search**: 100 queries/second (concurrent)

### Optimization Strategies

1. **Embedding Cache (Redis)**:
   - Cache embeddings by content hash (deduplication)
   - TTL: 7 days
   - Reduces OpenAI costs by 60%+ (common queries)

2. **Batch Processing**:
   - Embed 100 chunks per API call (vs 1 at a time)
   - Reduces latency from 10s to 2s for 100 chunks

3. **Async Operations**:
   - All Azure OpenAI calls use async/await
   - FastAPI async endpoints (non-blocking)

4. **Connection Pooling**:
   - Azure AI Search: 10 concurrent connections
   - Azure OpenAI: 50 concurrent requests (rate limit: 3000 RPM)

5. **Indexing Strategy**:
   - Azure AI Search: Vector index (HNSW algorithm)
   - Build parameters: m=4, ef_construction=400 (balance speed/accuracy)

---

## 8. Quality Gates (All Must Pass)

### 1. Test Coverage: 95%+
- **Tool**: pytest + Coverage.py
- **Command**: `pytest --cov=eva_rag --cov-report=html --cov-fail-under=95`
- **Target**: 95% line coverage, 90% branch coverage
- **Evidence**: Coverage report showing all modules

### 2. Retrieval Accuracy: 90%+
- **Test Set**: 100 question-answer pairs with known documents
- **Metric**: Recall@5 (correct document in top-5 results)
- **Tool**: Custom evaluation script
- **Evidence**: Accuracy report (90/100 questions answered correctly)

### 3. Latency Benchmarks
- **Ingestion**: < 5s (p95) for 10-page PDF
- **Search**: < 500ms (p95) for query
- **Tool**: pytest-benchmark, Locust load testing
- **Evidence**: Latency distribution charts

### 4. API Documentation
- **OpenAPI Spec**: Auto-generated from FastAPI
- **Examples**: curl commands for each endpoint
- **Tool**: Swagger UI (auto-served by FastAPI)
- **Evidence**: Published OpenAPI JSON

### 5. Chunk Quality
- **Metric**: 95%+ chunks end with complete sentences
- **Tool**: NLTK sentence tokenizer validation
- **Evidence**: Chunk quality report (sampling 1000 chunks)

### 6. Embedding Cost Control
- **Metric**: < $10/1M tokens (Azure OpenAI pricing)
- **Cache Hit Rate**: 60%+ (Redis cache)
- **Tool**: Cost tracking in Azure Cost Management
- **Evidence**: Monthly cost report

### 7. Tenant Isolation
- **Test**: Cross-tenant access attempts must fail
- **Tool**: Pytest security tests
- **Evidence**: 100% of cross-tenant queries return 403 Forbidden

### 8. Bilingual Support
- **Languages**: EN-CA, FR-CA
- **Test**: Upload French document, search in French
- **Tool**: Langdetect + manual validation
- **Evidence**: Language detection accuracy report

### 9. Error Handling
- **Scenarios**: Azure OpenAI timeout, Azure AI Search unavailable, invalid file format
- **Behavior**: Graceful degradation, retry with exponential backoff
- **Tool**: Chaos engineering tests (kill Azure services)
- **Evidence**: Error handling test suite passing

### 10. Security
- **Authentication**: JWT validation (via eva-auth)
- **Authorization**: Space access control (via eva-api)
- **Input Validation**: Pydantic models (reject malformed requests)
- **Evidence**: Security audit checklist, penetration test report

### 11. Observability
- **Logging**: Structured JSON logs (Azure Application Insights)
- **Metrics**: Latency, throughput, error rate (Prometheus)
- **Tracing**: Distributed tracing (OpenTelemetry)
- **Evidence**: Grafana dashboards, trace examples

### 12. Developer Experience
- **Setup Time**: < 5 minutes (poetry install)
- **Local Testing**: Mock Azure services with LocalStack
- **Type Hints**: 100% coverage (mypy strict)
- **Evidence**: Developer onboarding time tracking

---

## 9. Implementation Phases (4 Phases, 8 Weeks)

### Phase 1: Document Ingestion (Weeks 1-2)

**Goal**: Upload documents, extract text, generate metadata

**Tasks**:
1. FastAPI project setup: Poetry, pytest, mypy, ruff
2. Document loader: PyPDF2 (PDF), python-docx (DOCX), plain text
3. Text extraction: Handle multi-page, preserve page numbers
4. Language detection: langdetect integration
5. Blob storage: Azure Blob client, upload with tenant isolation
6. Cosmos DB integration: Store document metadata (eva-core Document entity)
7. API endpoint: POST /api/v1/rag/ingest (multipart file upload)
8. Tests: Unit tests for loaders, integration tests with Azure Blob

**Deliverables**:
- Documents uploadable via API
- Text extracted and stored in Blob Storage
- Metadata stored in Cosmos DB
- 95% test coverage for Phase 1 modules

**Evidence**:
- Swagger UI showing /ingest endpoint
- Sample PDF uploaded successfully
- Blob Storage screenshot showing uploaded file
- Test report: pytest passing

---

### Phase 2: Text Chunking & Embedding (Weeks 3-4)

**Goal**: Split text into chunks, generate embeddings, cache results

**Tasks**:
1. Text chunking: LangChain RecursiveCharacterTextSplitter (500 tokens, 50 overlap)
2. Sentence boundary detection: NLTK sentence tokenizer
3. Chunk validation: Ensure complete sentences, no truncation
4. Azure OpenAI integration: text-embedding-3-small (1536 dims)
5. Batch embedding: Process 100 chunks per API call (rate limit handling)
6. Redis cache: Store embeddings by content hash (7-day TTL)
7. Error handling: Retry with exponential backoff (Azure OpenAI throttling)
8. Tests: Chunking quality tests, embedding tests with mocked Azure OpenAI

**Deliverables**:
- Documents chunked into semantic segments
- Embeddings generated and cached
- Batch processing implemented
- 95% test coverage for Phase 2 modules

**Evidence**:
- Chunk quality report (95%+ complete sentences)
- Redis cache hit rate (60%+ on repeated queries)
- Test report: pytest passing
- Sample embeddings (1536 dimensions verified)

---

### Phase 3: Vector Indexing & Search (Weeks 5-6)

**Goal**: Index chunks in Azure AI Search, implement hybrid search

**Tasks**:
1. Azure AI Search integration: Create index schema (fields: chunk_id, content, embedding, space_id, tenant_id, metadata)
2. Index creation: Vector field (1536 dims, cosine similarity), keyword fields (content, document_name)
3. Batch indexing: Upload chunks in batches (100 chunks/request)
4. Vector search: Cosine similarity on embeddings (top-K=20)
5. Keyword search: BM25 on content field (boost filename 2x)
6. Hybrid search: RRF fusion (k=60) combining vector + keyword rankings
7. Filters: space_id, tenant_id, language, document_type
8. API endpoint: POST /api/v1/rag/search
9. Tests: Search accuracy tests (recall@5 on test set)

**Deliverables**:
- Chunks indexed in Azure AI Search
- Hybrid search working (vector + keyword)
- Filters applied (tenant isolation)
- 95% test coverage for Phase 3 modules

**Evidence**:
- Azure AI Search index screenshot
- Search results for sample queries
- Recall@5 accuracy report (90%+)
- Test report: pytest passing

---

### Phase 4: Reranking & Citation Extraction (Weeks 7-8)

**Goal**: Rerank results with cross-encoder, extract citations

**Tasks**:
1. Cross-encoder integration: ms-marco-MiniLM-L-6-v2 (Sentence Transformers)
2. Reranking: Score top-20 results, filter < 0.5, return top-K
3. Citation extraction: Extract document_name, page_number, content snippet
4. API endpoint updates: Add rerank parameter to /search
5. Performance optimization: Parallel reranking (async)
6. End-to-end tests: Upload document → search → verify citations
7. Documentation: OpenAPI spec, usage examples, architecture diagrams
8. Deployment: Dockerfile, Kubernetes manifests, Azure deployment

**Deliverables**:
- Reranking implemented with cross-encoder
- Citations extracted with page numbers
- All 12 quality gates passed
- Production deployment ready

**Evidence**:
- Reranking accuracy report (precision improvement)
- Citation extraction tests passing
- OpenAPI spec published
- Kubernetes deployment successful
- Grafana dashboards showing metrics

---

## 10. References

### RAG Architecture
- **Microsoft RAG Pattern**: https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview
- **LangChain RAG**: https://python.langchain.com/docs/use_cases/question_answering/
- **Azure AI Search Hybrid**: https://learn.microsoft.com/azure/search/hybrid-search-overview

### Reference Implementations
- **OpenWebUI Retrieval**: `OpenWebUI/backend/open_webui/retrieval/` (vector search, loaders, utils)
- **PubSec Info Assistant**: `PubSec-Info-Assistant/app/backend/approaches/chatreadretrieveread.py` (Azure AI Search + reranking)
- **EVA Jurispipeline**: `eva-orchestrator/jurispipeline/jurispipeline/publish/to_vector_chunks.py` (chunking strategy)

### Azure Services
- **Azure AI Search**: https://learn.microsoft.com/azure/search/
- **Azure OpenAI Embeddings**: https://learn.microsoft.com/azure/ai-services/openai/concepts/models#embeddings
- **Azure Blob Storage**: https://learn.microsoft.com/azure/storage/blobs/

### Python Libraries
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **Sentence Transformers**: https://www.sbert.net/
- **PyPDF2**: https://pypdf2.readthedocs.io/
- **python-docx**: https://python-docx.readthedocs.io/

---

## 11. Autonomous Implementation Model

### Context Engineering Principles

This specification follows the **Three Concepts Pattern**:

1. **Context Engineering**: Complete specification (no gaps), reference implementations analyzed (OpenWebUI retrieval, PubSec Info Assistant), Azure patterns documented
2. **Complete SDLC**: TDD (95% coverage), async FastAPI, CI/CD (GitHub Actions), observability (OpenTelemetry)
3. **Execution Evidence Rule**: All deliverables must include evidence (test reports, accuracy metrics, latency benchmarks, deployed endpoints)

### Implementation Approach

Marco will **NOT** be available for incremental approvals during the 8-week implementation. The agent must:

1. **Follow Requirements TO THE LETTER**: No shortcuts, no approximations, no "close enough"
2. **Use Reference Implementations**: OpenWebUI retrieval patterns, PubSec Info Assistant Azure AI Search integration
3. **Apply All 12 Quality Gates**: 95% coverage, 90% retrieval accuracy, < 500ms latency, bilingual support
4. **Test Continuously**: TDD approach (write tests first), run tests after every change, validate accuracy on test set
5. **Document Everything**: OpenAPI spec, usage examples, architecture diagrams, deployment guides
6. **Generate Evidence**: Test reports, accuracy reports, latency benchmarks, deployed endpoint screenshots

### Binary Final Review

After 8 weeks, Marco will perform a **binary review**:

- ✅ **All 12 quality gates PASS** → Ship to production
- ❌ **Any gate FAILS** → List specific failures, agent fixes, resubmit for review

There is NO partial credit. All gates must pass.

### Success Criteria

**IF** this specification is followed completely **AND** all reference patterns are applied **AND** all 12 quality gates pass **THEN** eva-rag will be production-ready without Marco's incremental involvement.

This is the **proven model from EVA-API, EVA-AUTH, and EVA-CORE** (comprehensive spec → autonomous implementation → all gates passed).

---

## 12. Next Steps

1. **Marco Opens eva-rag Workspace**:
   ```powershell
   cd "C:\Users\marco\Documents\_AI Dev\EVA Suite"
   code eva-rag
   ```

2. **Run Startup Script**:
   ```powershell
   .\_MARCO-use-this-to-tell_copilot-to-read-repo-specific-instructions.ps1
   ```

3. **Copy Output to Copilot**:
   - Copy green text (5 bullet points)
   - Paste as FIRST message to GitHub Copilot
   - Wait for Copilot to confirm it read `docs/SPECIFICATION.md`

4. **Give Task**:
   ```
   Implement Phase 1: Document Ingestion (upload, extract text, store metadata).
   Follow specification TO THE LETTER.
   Use OpenWebUI loader patterns (PyPDF2, python-docx).
   Use PubSec Info Assistant Azure Blob patterns.
   Achieve 95% test coverage.
   Show test report + uploaded file screenshot when done.
   ```

5. **Check In Biweekly** (NOT Weekly):
   - Week 2: Phase 1 complete? (Documents uploadable, text extracted, tests passing)
   - Week 4: Phase 2 complete? (Chunking working, embeddings generated, cache hit rate 60%+)
   - Week 6: Phase 3 complete? (Hybrid search working, accuracy 90%+, filters applied)
   - Week 8: Phase 4 complete? (Reranking working, citations extracted, all gates PASSED)

6. **Final Review** (Week 9):
   - Marco validates all 12 quality gates
   - Binary decision: Ship OR Fix

---

**END OF SPECIFICATION**

This document contains ALL requirements for autonomous eva-rag implementation. No additional context needed. Follow TO THE LETTER. Good luck! 🚀
