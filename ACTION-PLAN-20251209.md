# Action Plan: eva-rag

**Date**: December 9, 2025  
**Current Score**: 48/100  
**Target Score**: 90/100  
**Priority**: 🚨 CRITICAL (NOT a RAG engine, only file loaders)

---

## Executive Summary

**Status**: 🔴 CRITICAL - NOT A RAG ENGINE (48/100)  
**Gap**: -42 points (worst gap in EVA Suite)  
**Effort**: 6-9 weeks (180-270 hours)  
**Blocker**: Phases 2-4 completely missing (75% of functionality)

eva-rag is **NOT production-ready**. This is **NOT a RAG engine** - it's only file loaders. Cannot perform semantic search, vector search, or context augmentation. Phases 2-4 (Chunking, Embedding, Vector Search, Reranking, Citation) are **completely missing**.

---

## Gap Analysis (from DEEP-ASSESSMENT-20251209.md)

### Gap 1: NOT A RAG ENGINE (CRITICAL)
- **Issue**: Only Phase 1 (document loaders) implemented
- **Missing**: Phases 2-4 (Chunking, Embedding, Vector Search, Reranking, Citation)
- **Impact**: **CANNOT perform RAG** (no semantic search, no context retrieval)
- **Priority**: CRITICAL
- **Effort**: 6-9 weeks (180-270 hours)

### Gap 2: Coverage Misrepresentation (CRITICAL)
- **Claimed**: 94.62% coverage
- **Actual**: 32% coverage
- **Gap**: -62.62 points (worst in EVA Suite)
- **Impact**: Test suite inadequate, many code paths untested
- **Priority**: CRITICAL
- **Effort**: Included in Phase 2-4 implementation

### Gap 3: Broken Test Suite
- **Passing**: 63/93 tests (68%)
- **Failing**: 30 tests (32%)
- **Errors**: 3 test errors
- **Impact**: Cannot verify functionality
- **Priority**: HIGH
- **Effort**: 2-4 hours (fix tests)

### Gap 4: False "Production Ready" Claims
- **README**: Claims "Production Ready" (line 7)
- **DEPLOYMENT-COMPLETE.md**: Claims "✅ Production Ready"
- **Reality**: Only loaders work, RAG pipeline missing
- **Impact**: Misleading documentation, credibility loss
- **Priority**: IMMEDIATE
- **Effort**: 1 hour (update documentation)

---

## Action Items

### Phase 0: Immediate Fixes (Sprint 5 - Day 1)

**Task 0.1: Fix Documentation (IMMEDIATE)** (1 hour)
- [ ] Update README status: "🟡 Phase 1 Complete (Loaders Only)"
- [ ] Remove "Production Ready" claims
- [ ] Add warning: "⚠️ Phases 2-4 (RAG pipeline) not implemented"
- [ ] Update DEPLOYMENT-COMPLETE.md: "Phase 1 complete, Phases 2-4 pending"
- [ ] Update coverage claim: 32% actual (not 94.62%)

**Task 0.2: Fix Broken Tests** (2-4 hours)
- [ ] Run pytest and identify 30 failing tests
- [ ] Fix import errors (likely cause of failures)
- [ ] Fix broken fixtures (database connections, file paths)
- [ ] Achieve 90%+ tests passing (83+/93 tests)
- [ ] Document remaining failures (if any)

---

### Phase 2: Chunking + Embedding (Sprint 6-7 - Weeks of Dec 16-29)

**Task 2.1: Implement Text Chunking** (2-3 weeks, 80-120 hours)
- [ ] Read SPECIFICATION.md Phase 2 requirements (lines TBD)
- [ ] Install `langchain` or `llama-index` for chunking utilities
- [ ] Implement chunking strategies:
  - Fixed-size chunking (512, 1024, 2048 tokens)
  - Semantic chunking (sentence boundaries, paragraph boundaries)
  - Sliding window chunking (overlap for context preservation)
  - Recursive chunking (hierarchical documents)
- [ ] Implement chunk metadata:
  - `chunk_id`, `document_id`, `chunk_index`
  - `start_char`, `end_char`, `token_count`
  - `parent_chunk_id` (for recursive chunking)
- [ ] Add unit tests for chunking (30-40 tests)
- [ ] Add integration tests with sample documents (10-15 tests)
- [ ] Document chunking strategies in README

**Expected Outcome**:
```python
from eva_rag.chunking import ChunkingStrategy

chunker = ChunkingStrategy(
    strategy="semantic",
    chunk_size=1024,
    overlap=128,
    token_counter="tiktoken"
)

chunks = chunker.chunk_document(
    document=document,
    metadata={"document_id": "doc-123"}
)

# chunks = [
#     Chunk(id="chunk-1", text="...", token_count=1024, metadata={}),
#     Chunk(id="chunk-2", text="...", token_count=1024, metadata={}),
# ]
```

**Task 2.2: Implement Embedding Generation** (1-2 weeks, 40-80 hours)
- [ ] Install `openai` SDK (for text-embedding-3-small)
- [ ] Install `sentence-transformers` (for local embeddings)
- [ ] Implement embedding providers:
  - Azure OpenAI (text-embedding-3-small, 1536 dimensions)
  - Sentence Transformers (all-MiniLM-L6-v2, 384 dimensions)
  - HuggingFace (BAAI/bge-large-en-v1.5, 1024 dimensions)
- [ ] Implement batch embedding generation (32-128 chunks per batch)
- [ ] Add rate limiting for Azure OpenAI (1000 TPM limit)
- [ ] Add caching for embeddings (Redis)
- [ ] Add unit tests for embedding generation (20-30 tests)
- [ ] Add integration tests with Azure OpenAI (5-10 tests)

**Expected Outcome**:
```python
from eva_rag.embeddings import EmbeddingProvider

embedder = EmbeddingProvider(
    provider="azure_openai",
    model="text-embedding-3-small",
    batch_size=64
)

embeddings = embedder.embed_chunks(chunks)

# embeddings = [
#     Embedding(chunk_id="chunk-1", vector=[0.1, 0.2, ...], dimensions=1536),
#     Embedding(chunk_id="chunk-2", vector=[0.3, 0.4, ...], dimensions=1536),
# ]
```

---

### Phase 3: Vector Search + Reranking (Sprint 8-9 - Weeks of Dec 30 - Jan 12)

**Task 3.1: Implement Azure AI Search Integration** (2-3 weeks, 80-120 hours)
- [ ] Read SPECIFICATION.md Phase 3 requirements (lines TBD)
- [ ] Install `azure-search-documents` SDK
- [ ] Configure Azure AI Search connection (eva-suite-search-dev)
- [ ] Implement index management:
  - Create vector index (1536 dimensions for text-embedding-3-small)
  - Configure vector search algorithm (HNSW)
  - Configure hybrid search (vector + keyword)
  - Add semantic ranking (Azure Semantic Search)
- [ ] Implement document indexing:
  - Index chunks with embeddings
  - Index chunk metadata (document_id, chunk_index, etc.)
  - Batch indexing (100-1000 chunks per batch)
- [ ] Implement vector search:
  - K-nearest neighbors (KNN) search
  - Hybrid search (vector + keyword, weighted)
  - Semantic search (Azure Semantic Ranker)
  - Filtered search (metadata filters: document_id, date, etc.)
- [ ] Add unit tests for vector search (30-40 tests)
- [ ] Add integration tests with Azure AI Search (10-15 tests)

**Expected Outcome**:
```python
from eva_rag.vector_search import VectorSearchEngine

search_engine = VectorSearchEngine(
    provider="azure_ai_search",
    index_name="dev-index",
    search_mode="hybrid"
)

results = search_engine.search(
    query="What are the key findings?",
    top_k=10,
    filters={"document_id": "doc-123"}
)

# results = [
#     SearchResult(chunk_id="chunk-5", score=0.95, text="...", metadata={}),
#     SearchResult(chunk_id="chunk-12", score=0.89, text="...", metadata={}),
# ]
```

**Task 3.2: Implement Reranking** (1 week, 40 hours)
- [ ] Install `sentence-transformers` for cross-encoder reranking
- [ ] Implement reranking strategies:
  - Cross-encoder reranking (ms-marco-MiniLM-L-12-v2)
  - LLM-based reranking (GPT-4o with relevance prompt)
  - Hybrid reranking (combine cross-encoder + LLM scores)
- [ ] Add unit tests for reranking (15-20 tests)
- [ ] Add integration tests with sample search results (5-10 tests)

**Expected Outcome**:
```python
from eva_rag.reranking import Reranker

reranker = Reranker(
    strategy="cross_encoder",
    model="ms-marco-MiniLM-L-12-v2",
    top_k=5
)

reranked_results = reranker.rerank(
    query="What are the key findings?",
    results=results
)

# reranked_results = [
#     SearchResult(chunk_id="chunk-12", score=0.97, text="...", metadata={}),
#     SearchResult(chunk_id="chunk-5", score=0.94, text="...", metadata={}),
# ]
```

---

### Phase 4: Citation + Production Hardening (Sprint 10 - Week of Jan 13-19)

**Task 4.1: Implement Citation Generation** (1 week, 40 hours)
- [ ] Read SPECIFICATION.md Phase 4 requirements (lines TBD)
- [ ] Implement citation extraction:
  - Extract source document references
  - Extract page numbers, section titles
  - Extract URLs, publication dates
- [ ] Implement citation formatting:
  - APA format
  - MLA format
  - Chicago format
  - Custom format (configurable)
- [ ] Add inline citations to RAG responses
- [ ] Add unit tests for citation generation (15-20 tests)
- [ ] Add integration tests with full RAG pipeline (5-10 tests)

**Expected Outcome**:
```python
from eva_rag.citation import CitationGenerator

citation_gen = CitationGenerator(format="APA")

response = rag_pipeline.generate_response(
    query="What are the key findings?",
    include_citations=True
)

# response = {
#     "answer": "The key findings are... [1][2]",
#     "citations": [
#         {"id": 1, "text": "Smith, J. (2024). Research Report. Page 5."},
#         {"id": 2, "text": "Johnson, K. (2024). Analysis. Page 12."}
#     ]
# }
```

**Task 4.2: Production Hardening** (1 week, 40 hours)
- [ ] Add error handling (Azure service failures, rate limits)
- [ ] Add retry logic (exponential backoff)
- [ ] Add monitoring (Application Insights telemetry)
- [ ] Add performance optimization (caching, batching)
- [ ] Add configuration management (environment variables)
- [ ] Add deployment guide (Azure App Service or Functions)
- [ ] Add load testing (100+ concurrent users)
- [ ] Achieve 80%+ test coverage (currently 32%)
- [ ] Update README: "✅ Production Ready (Phases 1-4 Complete)"

---

## Testing Strategy

### Unit Tests
- Add 150-200 new tests (Phases 2-4)
- Target: 80%+ coverage (currently 32%)
- Mock Azure services for unit tests

### Integration Tests
- Test full RAG pipeline with dev Azure resources
- Test with sample documents (PDF, DOCX, TXT, etc.)
- Test with sample queries (factual, analytical, generative)

### End-to-End Tests
- Test document upload → chunking → embedding → indexing
- Test query → vector search → reranking → citation
- Test with 10+ diverse documents (government reports, technical papers, etc.)

### Performance Tests
- Load test with 100+ concurrent users
- Throughput test (100+ queries per minute)
- Latency test (p50, p95, p99 latency)

---

## Deployment Plan

### Prerequisites
- ✅ eva-infra deployed (Azure AI Search operational)
- ✅ Azure OpenAI deployed (text-embedding-3-small, gpt-4o)
- ⏳ Phases 2-4 implemented (Task 2.1-4.2)
- ⏳ Test coverage 80%+ (currently 32%)

### Deployment Steps
1. **Dev Environment** (Azure Functions or App Service)
   - Deploy Phase 2-4 implementation
   - Test with sample documents
   - Verify Azure AI Search integration

2. **Test Environment** (separate Azure resources)
   - Deploy via Terraform
   - Run end-to-end tests
   - Performance testing (100+ concurrent users)

3. **Prod Environment** (production Azure resources)
   - Deploy after test validation
   - Enable monitoring (Application Insights)
   - Set up alerts (error rate, latency, Azure service health)

---

## Success Criteria

### Definition of Done (Phase 2-4)
- ✅ Task 2.1-2.2: Chunking + Embedding implemented (3-5 weeks)
- ✅ Task 3.1-3.2: Vector Search + Reranking implemented (3-4 weeks)
- ✅ Task 4.1-4.2: Citation + Production Hardening implemented (2 weeks)
- ✅ 150-200 new tests added (total 243+ tests)
- ✅ Test coverage 80%+ (currently 32%)
- ✅ All integration tests passing with dev Azure resources
- ✅ End-to-end RAG pipeline functional (upload → query → citation)
- ✅ README updated: "✅ Production Ready (Phases 1-4 Complete)"
- ✅ DEEP-ASSESSMENT score: 90/100 target

### Quality Gates
- Coverage: 80%+ (target: 85%, verified via htmlcov/index.html)
- Tests: All passing (243+ tests)
- RAG Pipeline: Fully functional (chunking → embedding → search → reranking → citation)
- Azure AI Search: Operational (vector + hybrid + semantic search)
- Linting: No errors (flake8, mypy)
- Security: No vulnerabilities (bandit scan)

---

## Dependencies

### Internal
- ✅ eva-infra: Azure AI Search operational (eva-suite-search-dev)
- ✅ eva-infra: Azure OpenAI operational (text-embedding-3-small, gpt-4o)
- ✅ eva-api: API endpoints for document upload (optional)

### External
- ✅ Azure AI Search: eva-suite-search-dev (Basic SKU, operational)
- ✅ Azure OpenAI: eva-suite-openai-dev (gpt-4o, text-embedding-3-small)
- ✅ Azure Blob Storage: evasuitestoragedev (for document storage)
- ⏳ LangChain or LlamaIndex: Chunking utilities
- ⏳ Sentence Transformers: Embedding + reranking models

---

## Rollback Plan

**If deployment fails:**
1. Revert to Phase 1 (loaders only) - git tag: `eva-rag-phase1-v1.0.0`
2. Disable RAG endpoints (return 503 Service Unavailable)
3. Notify users: "RAG service temporarily unavailable"
4. Investigate logs (Application Insights)

**Rollback triggers:**
- Azure AI Search connection errors
- Azure OpenAI rate limit exceeded
- Test coverage drops below 80%
- Integration tests fail

---

## Recommendations

### Immediate (Sprint 5 - Week of Dec 9-15)
1. 🚨 **IMMEDIATE**: Task 0.1 (fix documentation) - 1 hour
   - Remove false "Production Ready" claims
   - Update README status: "Phase 1 Complete (Loaders Only)"
   - Timeline: Dec 9 (today)

2. 🚨 **HIGH**: Task 0.2 (fix broken tests) - 2-4 hours
   - Achieve 90%+ tests passing (83+/93 tests)
   - Timeline: Dec 9-10

### Sprint 6-10 (Weeks of Dec 16 - Jan 19)
3. 🚨 **CRITICAL**: Implement Phases 2-4 (6-9 weeks, 180-270 hours)
   - **Phase 2**: Chunking + Embedding (3-5 weeks)
   - **Phase 3**: Vector Search + Reranking (3-4 weeks)
   - **Phase 4**: Citation + Production Hardening (2 weeks)
   - **Target Score**: 90/100
   - **Timeline**: Jan 19, 2026 (estimated)

### Post-Phase 4 (Sprint 11+)
4. ⏳ **OPTIONAL**: Add multi-modal RAG (images, audio, video)
5. ⏳ **OPTIONAL**: Add query optimization (query expansion, query rewriting)
6. ⏳ **OPTIONAL**: Add RAG evaluation metrics (retrieval precision, answer accuracy)

---

## Risk Assessment

### High Risks
1. **Timeline Risk**: 6-9 weeks is aggressive for Phases 2-4
   - **Mitigation**: Prioritize Phase 2-3 (core RAG), defer Phase 4 (citation) if needed
   
2. **Azure AI Search Complexity**: Vector search + hybrid search integration complex
   - **Mitigation**: Use LangChain or LlamaIndex wrappers (simplifies integration)

3. **Test Coverage Gap**: 32% → 80%+ coverage requires 150-200 new tests
   - **Mitigation**: Write tests incrementally during implementation (TDD)

### Medium Risks
1. **Azure OpenAI Rate Limits**: 1000 TPM limit for embeddings
   - **Mitigation**: Batch embeddings (64-128 per batch), add caching (Redis)

2. **Broken Test Suite**: 30 failing tests may indicate deeper issues
   - **Mitigation**: Fix immediately (Task 0.2), investigate root causes

---

## Owner

**POD**: POD-F (Foundation Layer)  
**Team**: P04-LIB + P06-RAG  
**Primary Contact**: Marco Presta  
**Repository**: https://github.com/MarcoPolo483/eva-rag

---

**Created**: 2025-12-09  
**Status**: 🔴 CRITICAL - NOT A RAG ENGINE (Phase 1 only)  
**Next Review**: After Task 0.1-0.2 completion (Dec 10, 2025)  
**Estimated Completion**: Jan 19, 2026 (Phases 2-4, 6-9 weeks)  
**URGENT**: Update documentation today (remove false "Production Ready" claims)
