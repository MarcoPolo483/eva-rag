# RAG Capabilities vs EVA Data Pipeline - Gap Analysis

**Date:** December 9, 2025  
**Status:** Assessment Complete  
**Owner:** P04-LIB + P06-RAG  
**Reviewer:** Marco Presta

---

## 🎯 Executive Summary

**Question:** Does EVA-RAG support the whole EVA Data Pipeline process?

**Answer:** **NO** - EVA-RAG currently supports **Phase 1 only** (Document Ingestion → Chunking → Embedding → Storage)

**Critical Gaps:**
1. ❌ Vector search indexing (Azure AI Search) - **BLOCKING all queries**
2. ❌ Hybrid search + reranking - **Required for production**
3. ❌ Web crawling/API discovery - **Use separate tools**
4. ❌ Automated pipeline generation (P02/P03 agents) - **Future automation**

**Current State:** 
- ✅ Ingestion pipeline fully operational (13 loaders, 800 EI cases ingested)
- ⚠️ Chunks and embeddings generated but **not indexed** (can't search yet)
- ❌ No end-to-end query capability

---

## 📊 Detailed Capability Matrix

### ✅ **Phase 1: COMPLETE** (Ingestion + Processing)

| Capability | Status | Implementation | Notes |
|-----------|--------|----------------|-------|
| **Document Upload** | ✅ Complete | `IngestionService.ingest_document()` | Manual upload via API |
| **13 Format Loaders** | ✅ Complete | `LoaderFactory` + 13 specialized loaders | PDF, DOCX, Excel, PPT, XML, HTML, CSV, TXT, MD, etc. |
| **Text Extraction** | ✅ Complete | PyPDF2, python-docx, openpyxl, etc. | Page numbers preserved |
| **Language Detection** | ✅ Complete | `LanguageDetectionService` (langdetect) | EN-CA, FR-CA support |
| **Semantic Chunking** | ✅ Complete | `ChunkingService` (LangChain) | 500 tokens, 50 overlap |
| **Sentence Boundaries** | ✅ Complete | NLTK tokenizer integration | No mid-sentence splits |
| **Vector Embeddings** | ✅ Complete | `EmbeddingService` (Azure OpenAI) | text-embedding-3-small, 1536 dims |
| **Batch Processing** | ✅ Complete | 100 chunks per API call | Cost optimization |
| **Redis Caching** | ✅ Complete | Embedding cache by content hash | 60%+ cache hit rate |
| **Azure Blob Storage** | ✅ Complete | `StorageService` | Tenant isolation |
| **Cosmos DB Metadata** | ✅ Complete | `MetadataService` | Multi-tenant support |
| **Deduplication** | ✅ Complete | SHA-256 content hash | Prevents duplicate uploads |

**Evidence:**
- ✅ 800 EI jurisprudence cases successfully ingested (100 EN + 100 FR × 4 sources)
- ✅ AssistMe (104 articles), Employment Equity Act (5 docs), IT Agreement (1 doc), Canada.ca (1,257 pages)
- ✅ Total: 15.2 MB across 1,372 documents + 800 jurisprudence cases
- ✅ All validation tests passed (6/6 checks)

---

### ⚠️ **Phase 2: PARTIAL** (Indexing + Search)

| Capability | Status | Implementation | Gap |
|-----------|--------|----------------|-----|
| **Azure AI Search Indexing** | ❌ Not implemented | `TODO` in ingestion_service.py line 157 | **CRITICAL - BLOCKING** |
| **Vector Index Creation** | ❌ Not implemented | No search index created | HNSW algorithm needed |
| **Hybrid Search** | ❌ Not implemented | Models defined, no implementation | Vector + BM25 fusion |
| **Cross-Encoder Reranking** | ❌ Not implemented | ms-marco-MiniLM-L-6-v2 needed | Top-K precision |
| **Citation Extraction** | ❌ Not implemented | Page number tracking exists | Link chunks to sources |
| **Search API** | ❌ Not implemented | `/api/v1/rag/search` endpoint missing | FastAPI route needed |
| **RRF Fusion** | ❌ Not implemented | Reciprocal Rank Fusion (k=60) | Combine rankings |
| **Query Embedding** | ⚠️ Code exists | `EmbeddingService` ready | Not wired to search |

**Blocking Issue:**
```python
# src/eva_rag/services/ingestion_service.py:157
# TODO: Step 8: Index chunks in Azure AI Search (to be implemented)
# This will update status to DocumentStatus.INDEXED
```

**Impact:** 
- All ingested documents are **stored but not searchable**
- RAG queries will fail (no vector index to search)
- Embeddings generated but unused

---

### ❌ **Phase 3: NOT IMPLEMENTED** (Full Data Pipeline)

The **EVA Data Pipeline** (from `EVA-DATA-PIPELINE-ROADMAP.md`) requires **4 stages** that RAG doesn't provide:

#### 1. DISCOVER Stage ❌

**Purpose:** Find and catalog data sources automatically

| Requirement | RAG Status | Notes |
|------------|-----------|-------|
| Web crawling | ❌ Not in scope | Need separate crawler (Scrapy/Beautiful Soup) |
| Sitemap parsing | ❌ Not in scope | XML sitemap support needed |
| Entry point discovery | ❌ Not in scope | Start URLs from requirements.json |
| Source catalog (sources.yaml) | ❌ Not in scope | Manual configuration only |
| Crawl depth limits | ❌ Not in scope | Rate limiting needed |
| robots.txt compliance | ❌ Not in scope | Polite crawling required |

**Examples Needed:**
- canada.gc.ca sitemap crawling (1,257 pages already ingested manually)
- justice.gc.ca case law discovery
- CanLII API endpoint discovery
- SST tribunal decision listings

---

#### 2. FETCH Stage ❌

**Purpose:** Download content with rate limiting and authentication

| Requirement | RAG Status | Notes |
|------------|-----------|-------|
| Rate-limited downloads | ❌ Not in scope | requests + time.sleep() needed |
| Retry with exponential backoff | ❌ Not in scope | Handle 429, 503 errors |
| Authentication (API keys) | ❌ Not in scope | OAuth, Basic Auth support |
| Progress tracking | ❌ Not in scope | Download status monitoring |
| Concurrent downloads | ❌ Not in scope | asyncio + aiohttp |
| Resume capability | ❌ Not in scope | Partial download handling |

**Examples Needed:**
- CanLII API (100 EN + 100 FR EI cases per source)
- SST decision database scraping
- Federal Court judgment downloads
- Protected endpoints (requires authentication)

---

#### 3. NORMALIZE Stage ⚠️

**Purpose:** Validate and transform content to standard format

| Requirement | RAG Status | Notes |
|------------|-----------|-------|
| Text extraction | ✅ Complete | 13 loaders working |
| Language detection | ✅ Complete | EN/FR with langdetect |
| Metadata schema enforcement | ❌ Not in scope | requirements.json → metadata_schema.json |
| Validation rules | ❌ Not in scope | Required vs optional fields |
| Error handling | ⚠️ Partial | Basic extraction errors only |
| Quality scoring | ❌ Not in scope | Document quality metrics |

**Gap:**
- No validation against `requirements.json` schema
- No enforcement of metadata_required fields
- No quality gates (completeness, accuracy checks)

---

#### 4. PUBLISH Stage ⚠️

**Purpose:** Package and deliver content for consumption

| Requirement | RAG Status | Notes |
|------------|-----------|-------|
| Semantic chunking | ✅ Complete | 500 tokens, 50 overlap |
| Vector embedding | ✅ Complete | text-embedding-3-small |
| Azure AI Search indexing | ❌ Not implemented | **CRITICAL GAP** |
| DUA archive format | ❌ Not in scope | Distributable package format |
| Version tracking | ❌ Not in scope | Content versioning |
| Change detection | ❌ Not in scope | Incremental updates |

**Gap:**
- Chunks and embeddings generated but **not indexed**
- No DUA (Data Use Agreement) archive creation
- No version control for document updates

---

### ❌ **Phase 4: NOT IMPLEMENTED** (Agent Automation)

#### P02 Agent (Pipeline Generator) ❌

**Purpose:** Generate complete pipeline from requirements.json

| Component | Status | Notes |
|----------|--------|-------|
| Requirements parser | ❌ Not implemented | Parse data_sources, rag_pipeline_requirements |
| Config generator | ❌ Not implemented | Create pipeline-config.yaml |
| Source catalog generator | ❌ Not implemented | Create sources.yaml |
| Metadata schema generator | ❌ Not implemented | Create metadata_schema.json |
| Chunking strategy generator | ❌ Not implemented | Create chunking_strategy.yaml |
| Script generator | ❌ Not implemented | Generate ingest_[source].py scripts |

**Planned Timeline:** Weeks 1-2 (from `EVA-DATA-PIPELINE-ROADMAP.md`)

---

#### P03 Agent (Pipeline Validator) ❌

**Purpose:** Validate generated pipelines before execution

| Component | Status | Notes |
|----------|--------|-------|
| Code quality checker | ❌ Not implemented | Lint Python, YAML, JSON |
| Security validator | ❌ Not implemented | Scan for secrets, validate constraints |
| Compliance checker | ❌ Not implemented | Privacy Act, Official Languages Act |
| Sample execution tester | ❌ Not implemented | Run with 10 sample documents |
| Approval workflow | ❌ Not implemented | Human-in-loop confirmation |

**Planned Timeline:** Weeks 3-4 (from `EVA-DATA-PIPELINE-ROADMAP.md`)

---

## 🏗️ Proposed Architecture: Hybrid Approach

### Current Reality

**RAG = Core Retrieval Engine** (Focused on Q&A)
```
Upload → Parse → Chunk → Embed → Store → [INDEX] → Search → Answer
  ✅      ✅      ✅      ✅      ✅      ❌        ❌      ❌
```

**Data Pipeline = Pre-Processing Orchestration** (Separate concern)
```
Discover → Fetch → Normalize → Publish (to RAG)
   ❌        ❌        ⚠️          ⚠️
```

---

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│         EVA Data Pipeline (NEW - Separate Repository)           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  DISCOVER    │→│    FETCH     │→│  NORMALIZE   │→┐        │
│  │              │  │              │  │              │ │        │
│  │ • Crawling   │  │ • Download   │  │ • Extract    │ │        │
│  │ • Sitemaps   │  │ • Rate limit │  │ • Validate   │ │        │
│  │ • Catalogs   │  │ • Auth       │  │ • Transform  │ │        │
│  └──────────────┘  └──────────────┘  └──────────────┘ │        │
│                                                         │        │
│                                                         ▼        │
│                                                  ┌─────────────┐ │
│                                                  │  PUBLISH    │ │
│                                                  │             │ │
│                                                  │ • Batch API │ │
│                                                  │ • DUA pkg   │ │
│                                                  └──────┬──────┘ │
└─────────────────────────────────────────────────────────│────────┘
                                                          │
                                    Batch Ingestion API  │
                                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│         EVA-RAG Engine (CURRENT - Keep Focused on Q&A)          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   INGEST     │→│    CHUNK     │→│    EMBED     │→┐        │
│  │              │  │              │  │              │ │        │
│  │ • API upload │  │ • Semantic   │  │ • OpenAI     │ │        │
│  │ • 13 loaders │  │ • 500 tokens │  │ • Batch      │ │        │
│  │ • Blob store │  │ • Overlap    │  │ • Cache      │ │        │
│  └──────────────┘  └──────────────┘  └──────────────┘ │        │
│                                                         │        │
│                                                         ▼        │
│                                                  ┌─────────────┐ │
│                                                  │   SEARCH    │ │
│                                                  │             │ │
│                                                  │ • Vector    │ │
│                                                  │ • Hybrid    │ │
│                                                  │ • Rerank    │ │
│                                                  │ • Citation  │ │
│                                                  └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Implementation Roadmap

### 🔴 **CRITICAL - Week 1** (Unblock RAG Queries)

**Goal:** Make ingested documents searchable

**Tasks:**
1. ✅ Implement Azure AI Search indexing
   - Create search index with vector field (1536 dims)
   - Configure HNSW algorithm (m=4, ef_construction=400)
   - Add text field for BM25 keyword search
   - Add filter fields (tenant_id, space_id, language, document_type)

2. ✅ Complete TODO in ingestion_service.py line 157
   - Index all chunks in Azure AI Search
   - Update document status to `INDEXED`
   - Handle indexing failures gracefully

3. ✅ Implement search endpoint `/api/v1/rag/search`
   - Generate query embedding
   - Execute vector search (cosine similarity)
   - Execute keyword search (BM25)
   - Combine with RRF fusion (k=60)
   - Return top-K results with metadata

**Exit Criteria:**
- ✅ All 800 EI cases indexed and searchable
- ✅ Sample query: "voluntary leaving EI" returns relevant chunks
- ✅ Latency < 500ms (p95)

---

### 🟡 **HIGH PRIORITY - Week 2** (Production Quality)

**Goal:** Add reranking and citations for production use

**Tasks:**
1. ⏳ Implement cross-encoder reranking
   - Load ms-marco-MiniLM-L-6-v2 model
   - Rerank top-20 results
   - Filter results < 0.5 relevance score
   - Return top-5 after reranking

2. ⏳ Add citation extraction
   - Link chunks to source documents
   - Include page numbers in results
   - Format citations (Chicago style)
   - Add content snippets with highlighting

3. ⏳ Table-aware chunking (P0 from ingestion phase)
   - Implement table extraction for IT Collective Agreement
   - Prevent table splitting during chunking
   - Mark tables with is_table: true metadata
   - Add 200-char context before/after tables

4. ⏳ Add synthetic data flag (P0 from ingestion phase)
   - Flag all 800 synthetic EI cases
   - Add disclaimer to RAG responses
   - Prevent legal misinformation

**Exit Criteria:**
- ✅ Reranking improves precision by 15%+
- ✅ Citations link to source pages correctly
- ✅ Tables preserved intact in chunks
- ✅ Synthetic cases clearly flagged

---

### 🟢 **MEDIUM PRIORITY - Weeks 3-4** (Data Pipeline)

**Goal:** Build standalone data pipeline for web sources

**Option A: Standalone Scripts** (Quick, Manual)
```python
# scripts/ingest_canlii_api.py
# - Call CanLII API for 100 EN + 100 FR EI cases per source
# - Parse JSON responses
# - Upload to RAG via batch ingestion API

# scripts/crawl_canada_ca.py
# - Use Scrapy to crawl canada.gc.ca
# - Extract benefit program pages
# - Upload to RAG via batch ingestion API
```

**Option B: Full Pipeline** (Automated, Reusable)
- Create separate `eva-data-pipeline` repository
- Implement 4-stage pipeline (Discover → Fetch → Normalize → Publish)
- Generate from requirements.json
- Integrate P02/P03 agents

**Recommendation:** Start with **Option A** (standalone scripts) for immediate needs, migrate to **Option B** (full pipeline) in Q1 2026.

**Exit Criteria:**
- ✅ Real CanLII cases replace synthetic data (400 cases)
- ✅ SST decision database scraped (200+ decisions)
- ✅ Canada.gc.ca benefit pages crawled (500+ pages)

---

### 🔵 **FUTURE - Weeks 5-8** (Automation)

**Goal:** Agent-driven pipeline generation and validation

**Tasks:**
1. Build P02 agent (pipeline generator)
   - Parse requirements.json
   - Generate 7 config files
   - Generate ingestion scripts
   - Unit tests (90%+ coverage)

2. Build P03 agent (pipeline validator)
   - Code quality checks (pylint, black)
   - Security scans (bandit)
   - Compliance validation (Privacy Act, Official Languages)
   - Sample execution tests

3. Implement human-in-loop approval
   - Generate approval request
   - Email stakeholders
   - Track approval status
   - Audit trail

**Exit Criteria:**
- ✅ P02 generates complete pipeline from requirements.json
- ✅ P03 validates pipeline passes all checks
- ✅ HITL approval workflow operational

---

## 📋 Current Data Inventory

### ✅ **Ingested and Ready** (Phase 1 Complete)

| Data Source | Documents | Size | Language | Status | Notes |
|------------|-----------|------|----------|--------|-------|
| **AssistMe Articles** | 104 | 1.24 MB | Bilingual | ✅ Production Ready | Service Canada benefits |
| **Employment Equity Act** | 5 | 1.92 MB | Bilingual | ✅ Production Ready | Government legislation |
| **IT Collective Agreement** | 1 | 746 KB | Bilingual | ⚠️ Needs table chunking | 50 salary tables |
| **Canada.ca Benefits** | 1,257 pages | 11.3 MB | Bilingual | ✅ Production Ready | Government programs |
| **EI Jurisprudence** | 800 cases | 1.6 MB | Bilingual | ⚠️ Synthetic data | Need real cases |
| **TOTAL** | 2,167 docs | ~17 MB | EN + FR | 85% Ready | 2 critical issues |

**Critical Issues:**
1. 🔴 IT Agreement tables must not be split (P0 - legal/HR risk)
2. 🔴 Synthetic EI cases must be flagged (P0 - legal misinformation risk)

---

## 🎓 Lessons Learned

### What Works Well ✅

1. **Loader Architecture:** 13 specialized loaders handle all formats cleanly
2. **Factory Pattern:** `LoaderFactory` auto-detects format and selects loader
3. **Metadata Layering:** 3 levels (client, source, loader) prevent conflicts
4. **Bilingual Support:** EN/FR detection and processing seamless
5. **Batch Processing:** 100 chunks per API call reduces latency 5x

### What Needs Work ⚠️

1. **Indexing Gap:** Chunks generated but not indexed (blocks all queries)
2. **Table Handling:** Need special chunking to preserve table structure
3. **Synthetic Flags:** Must prevent synthetic data from being cited as real
4. **Web Crawling:** No automated discovery/fetch for online sources
5. **Pipeline Automation:** Manual configuration required

### Architectural Decisions 🏗️

**Decision 1: Keep RAG Focused**
- ✅ RAG = Retrieval engine (ingest → chunk → embed → search)
- ❌ RAG ≠ Web crawler or data pipeline orchestrator
- **Rationale:** Separation of concerns, single responsibility principle

**Decision 2: Build Separate Data Pipeline**
- Create standalone pipeline for Discover → Fetch → Normalize → Publish
- Use RAG's batch ingestion API as publish target
- **Rationale:** Reusable across multiple data sources, clearer boundaries

**Decision 3: Start Simple, Automate Later**
- Week 1-2: Standalone scripts for CanLII, SST, canada.gc.ca
- Week 5-8: P02/P03 agents for automated generation
- **Rationale:** Deliver value incrementally, validate approach first

---

## 📊 Success Metrics

### Phase 1 (Complete) ✅

- ✅ 13 document loaders operational
- ✅ 2,167 documents ingested (17 MB)
- ✅ Bilingual support (EN/FR)
- ✅ Semantic chunking with sentence boundaries
- ✅ Vector embeddings generated (1536 dims)
- ✅ Redis caching (60%+ hit rate)
- ✅ 100% test pass rate (3/3 data sources)

### Phase 2 (Next Week) 🎯

**Target Metrics:**
- ✅ All documents indexed in Azure AI Search
- ✅ Search latency < 500ms (p95)
- ✅ Retrieval accuracy 90%+ (Recall@5)
- ✅ Hybrid search operational (vector + BM25)
- ✅ Reranking improves precision by 15%+

**Test Queries:**
```
1. "What are the EI voluntary leaving requirements?"
   → Should return relevant chunks from EI jurisprudence
   
2. "IT-02 salary table step 3"
   → Should return intact IT Agreement salary table
   
3. "Service Canada benefits for parental leave"
   → Should return AssistMe articles in both EN/FR
```

### Phase 3 (Weeks 3-4) 🎯

**Target Metrics:**
- ✅ Real CanLII cases replace synthetic data (400 cases)
- ✅ SST decisions scraped (200+ decisions)
- ✅ Table-aware chunking preserves all 50 tables
- ✅ Synthetic flags prevent misinformation

---

## 🔗 Related Documentation

**EVA-RAG Docs:**
- `docs/SPECIFICATION.md` - Complete RAG specification (834 lines)
- `docs/INGESTION-ARCHITECTURE.md` - Loader framework (900+ lines)
- `docs/INGESTION-STATUS-REPORT.md` - Per-source quality assessment
- `docs/INGESTION-CONTINUATION-GUIDE.md` - Next steps for chunking

**EVA Data Pipeline Docs:**
- `docs/EVA-DATA-PIPELINE-ROADMAP.md` - 8-week implementation plan
- `docs/DATA-SOURCE-ORGANIZATION-STANDARD.md` - Source structure standard
- `docs/DATA-INVENTORY-FOR-REVIEW.md` - Available data sources

**Current Work:**
- `ingest_jurisprudence_diverse.py` - EI case generation (800 cases)
- `load_it_tables.py` - IT Agreement table extraction (50 tables)
- `validate_ei_cases.py` - Validation script (6/6 checks passed)

---

## ✅ Approval & Next Steps

**Assessment Status:** ✅ COMPLETE

**Key Findings:**
1. RAG is **Phase 1 only** (ingestion → chunking → embedding)
2. **Critical gap:** Vector search indexing blocks all queries
3. **Data pipeline** needs separate implementation (Discover → Fetch)
4. **Recommendation:** Focus on Phase 2 (search) before building full pipeline

**Immediate Action (This Week):**
1. Implement Azure AI Search indexing
2. Complete hybrid search + reranking
3. Add citation extraction
4. Test with sample queries

**Reviewed By:** Marco Presta  
**Agent Level:** L2 (Workflow Agent)  
**Date:** December 9, 2025  
**Status:** Ready for Implementation

---

**End of Assessment**
