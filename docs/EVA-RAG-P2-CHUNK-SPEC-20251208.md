# EVA-RAG Phase 2: Chunking Strategy & Implementation Specification

**🏷️ FILE STAMP**  
**ID:** `EVA-RAG-P2-CHUNK-SPEC-20251208-1845`  
**Feature Key:** `EVA-RAG-P2-001`  
**Type:** Requirements | Phase 2 Specification  
**Tags:** `#chunking` `#phase2` `#rag-pipeline` `#production-ready`  
**Owner:** POD-F (P04-LIB + P06-RAG)  
**Status:** 🔴 AWAITING APPROVAL  
**Generated:** 2025-12-08 18:45 EST  
**Version:** 2.0 (P02-Compliant)  
**Run ID:** `P02-RAG-CHUNK-20251208-1845`

---

## 📋 Functional Requirements

### What We're Building

**Phase 2 Objective:** Transform 1,272 ingested documents (14 MB JSON) into ~1,900 search-optimized chunks ready for embedding and RAG retrieval.

**Success Criteria:**
- ✅ All ingested documents processed without data loss
- ✅ Chunk boundaries preserve semantic meaning (no mid-sentence splits)
- ✅ Metadata schema enables precise filtering (by language, source, date, topic)
- ✅ Bilingual linking (EN ↔ FR parallel documents)
- ✅ Cost optimization: <$0.05 total embedding cost
- ✅ Quality validation: 95%+ chunk quality score (manual sample review)

### Data Sources & Target Chunks

| Source | Input Docs | Input Size | Strategy | Output Chunks | Embedding Cost |
|--------|------------|------------|----------|---------------|----------------|
| Canada.ca (EN/FR) | 1,257 | 11.3 MB | Page-level + CE | 1,257 | $0.015 |
| Employment Analytics | 2 CSV | 10.8 KB | Time-series aggregation | 400 | $0.0056 |
| **Jurisprudence (4 tribunals)** | **800** | **~8 MB** | **Hybrid semantic + structural** | **2,400** | **$0.48** |
| IT Collective Agreement | 2 (EN/FR) | 746 KB | Article-level | 200 | $0.0024 |
| Employment Equity Act | 5 | 1.9 MB | Section-level | 80 | $0.0008 |
| Employment Standards | 2 | 2.5 KB | Q&A pairs | 10 | $0.00006 |
| **TOTAL** | **2,068** | **~22 MB** | **Mixed** | **4,347** | **$0.51** |

---

## 🧩 Context Engineering Constraints

**⚠️ CRITICAL**: All chunking implementations MUST respect these constraints. These are **NON-NEGOTIABLE** EVA-RAG requirements.

### 1. Semantic Boundary Preservation
- [ ] **No Mid-Sentence Splits**: Chunks must end at sentence/paragraph boundaries
- [ ] **Structure Awareness**: Respect H1/H2/H3 headings, list items, table rows
- [ ] **Legal/Policy Integrity**: For legal docs, keep complete reasoning chains together
- [ ] **Table Handling**: Keep tables intact or split by logical row groups (not mid-table)

**Why**: Broken context = poor LLM comprehension = incorrect answers to users

### 2. Bilingual Linking (Official Languages Act Compliance)
- [ ] **Parallel Document IDs**: EN ↔ FR documents linked via `parallel_doc_id` metadata
- [ ] **Language Detection**: Every chunk tagged with `language: "en"|"fr"` 
- [ ] **Query Routing**: EVA must retrieve both languages when user query is ambiguous
- [ ] **No Translation Gaps**: If EN doc exists, FR version must also be chunked (or flagged as missing)

**Reference**: Official Languages Act (R.S.C., 1985, c. 31), `eva-i18n/README.md`

### 3. WCAG 2.1 AA Metadata (Accessibility)
- [ ] **Alt Text Preservation**: If source doc has image descriptions, preserve in metadata
- [ ] **Reading Level**: Tag complex documents with reading level (grade 8-12)
- [ ] **Plain Language Flag**: Mark documents available in plain language version
- [ ] **Screen Reader Compatibility**: Markdown formatting compatible with TTS engines

**Reference**: [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/), GC Digital Standards

### 4. Citation & Audit Trail (RBAC-Aware)
- [ ] **Source Attribution**: Every chunk links back to original doc (URL, filename, page number)
- [ ] **Timestamp Metadata**: Store ingestion date + last modified date
- [ ] **Access Control Tags**: Tag chunks with classification (Unclassified, Protected B)
- [ ] **Audit Logging**: Log chunk generation to EVA Audit Trail (run_id, timestamp, chunk count)

**Reference**: `eva-audit-trail/README.md`, Treasury Board Directive on Security Management

### 5. Protected B Data Handling
- [ ] **No PII in Chunks**: Redact PII (names, SINs, emails) before chunking
- [ ] **Encryption at Rest**: Chunked JSON files encrypted in Azure Blob Storage
- [ ] **No External Logging**: Debug logs stay local, no chunk content to third-party services
- [ ] **Data Minimization**: Only chunk fields needed for RAG (content + essential metadata)

**Reference**: PIPEDA, ITSG-33

### 6. Anti-Vibe-Coding Pattern (Spec Anchoring)
- [ ] **4-Block Prompts**: When using Copilot to write chunking code, anchor to this spec
- [ ] **Test First**: Write test cases BEFORE implementation (TDD approach)
- [ ] **Sample Validation**: Manually review 20 chunks per source type before full run
- [ ] **No Assumptions**: If spec unclear, ask for clarification (don't guess behavior)

**Reference**: `docs/context-engineering.md`, `docs/eva-patterns/P16-DMP.md`

---

## 🧹 Housekeeping Checklist

**Post-Implementation Cleanup** (complete before marking Phase 2 as done):

### Code Quality
- [ ] **Remove Debug Code**: Delete `print()`, `console.log()`, temporary test scripts
- [ ] **Type Hints**: All Python functions have type annotations
- [ ] **Docstrings**: Public functions have Google-style docstrings
- [ ] **Linting**: Run `ruff check src/`, fix all errors
- [ ] **Formatting**: Run `black src/` for consistent style

### Documentation
- [ ] **Update README**: Add Phase 2 completion status to `eva-rag/README.md`
- [ ] **Chunking Guide**: Create `docs/CHUNKING-GUIDE.md` explaining strategies
- [ ] **API Documentation**: Update `docs/SPECIFICATION.md` with chunk schema
- [ ] **ADR if Needed**: If major decision made (e.g., "why page-level for Canada.ca?"), create ADR

### Testing
- [ ] **Unit Tests**: 80%+ coverage for chunking functions (`tests/test_chunking.py`)
- [ ] **Integration Tests**: End-to-end test (ingest → chunk → verify output)
- [ ] **Quality Tests**: Sample 20 chunks per source, validate boundaries and metadata
- [ ] **Regression Tests**: Re-run Phase 1 ingestion, ensure compatibility

### Security & Compliance
- [ ] **No Secrets in Code**: Connection strings in `.env`, not hardcoded
- [ ] **Dependency Audit**: Run `pip-audit`, fix vulnerabilities
- [ ] **License Compliance**: Check new packages (Pandas, NLTK) have compatible licenses

### Directory Map & Working Memory
- [ ] **Update Repo Tree**: Refresh `.eva-cache/repo-tree.txt`
  ```powershell
  .\scripts\Quick-WorkspaceTree.ps1 -RepoPath "C:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"
  ```
- [ ] **Commit Tree Map**: `git add -f .eva-cache/repo-tree.txt`
- [ ] **Verify .gitignore**: Ensure `data/chunked/` tracked, but `data/raw/` ignored

**Reference**: `docs/DEFINITION-OF-DONE.md`, `docs/eva-patterns/P16-DMP.md`

---

## 📊 Chunking Strategies (Detailed)

### Strategy 1: Page-Level + Context Engineering (Canada.ca)

**Input:** 1,257 HTML pages (632 EN + 625 FR)  
**Output:** 1,257 chunks (one per page, or split if >2000 tokens)

**CE Enhancements:**
1. **Inject Breadcrumbs**: Prepend navigation path to chunk
   ```markdown
   [Canada.ca > Services > Jobs > Find a job]
   ```
2. **Preserve Metadata**: Title, description, URL, language
3. **Link Bilingual**: Store `parallel_doc_id` for EN ↔ FR

**Example Chunk:**
````markdown
[Breadcrumb: Canada.ca > Services > Jobs > Find a job]
[Title: Jobs and the workplace - Canada.ca]
[Description: Find a job, find student employment, funding programs...]

# Jobs and the workplace

## Find a job
- Job Bank - Search for jobs across Canada
- Youth employment programs
- International students working in Canada

[URL: https://www.canada.ca/en/services/jobs.html]
[Language: EN | FR: /fr/services/emplois.html]
[Last updated: 2024-12-08]
````

**Metadata Schema:**
```json
{
  "chunk_id": "canada-ca-en-jobs-001",
  "source_url": "https://www.canada.ca/en/services/jobs.html",
  "language": "en",
  "parallel_chunk_id": "canada-ca-fr-emplois-001",
  "breadcrumbs": ["Canada.ca", "Services", "Jobs"],
  "page_title": "Jobs and the workplace",
  "topic": "employment",
  "chunk_tokens": 587,
  "ingestion_date": "2024-12-08T11:52:23Z"
}
```

---

### Strategy 2: Time-Series Aggregation (Employment Analytics)

**Input:** 2 CSV files, 5,700 rows  
**Output:** 400 chunks (grouped by Province + Metric + Year)

**Rationale:** Users ask trend questions ("What's the unemployment trend in Ontario?"), not point-in-time ("What was ON unemployment on June 15, 2023?")

**Aggregation Logic:**
- Group by: (GEO, Metric, Year)
- Calculate: Average, Min, Max, Trend, YoY Change
- Include: All 12 monthly data points

**Example Chunk:**
```markdown
# Employment Analytics: Ontario - Healthcare - 2024

**Dataset:** 14-10-0355 (Employment by Industry)
**Province:** Ontario
**Industry:** Health care and social assistance
**Metric:** Employment (Persons × 1,000)

## Monthly Data (2024)
| Month | Employment | MoM Change |
|-------|-----------|-----------|
| Jan | 850,000 | - |
| Feb | 852,000 | +0.2% |
| ... | ... | ... |
| Dec | 875,000 | +1.2% |

## Summary
- Average: 862,500
- Trend: ↗ +2.9% YoY
- Seasonality: Peak in December

[Source: Statistics Canada, Table 14-10-0355]
```

**Metadata Schema:**
```json
{
  "chunk_id": "statcan-14-10-0355-ON-healthcare-2024",
  "dataset_id": "14-10-0355",
  "province": "Ontario",
  "industry": "Healthcare",
  "year": 2024,
  "data_points": 12,
  "summary": {
    "average": 862500,
    "trend": "+2.9%",
    "seasonality": "December peak"
  }
}
```

---

### Strategy 3: Hybrid Semantic + Structural (Jurisprudence - 4 Tribunals)

**Input:** 800 cases (100 samples × 4 tribunals × 2 languages = 800 cases, ~8 MB)  
**Output:** 2,400 chunks (avg 3 chunks per case)  
**Embedding Model:** `text-embedding-3-large` (3072 dimensions) - **Higher cost but required for legal precision**

**Data Sources:**
1. **Supreme Court of Canada (SCC)** - 100 EN + 100 FR = 200 cases
2. **Federal Court (FC)** - 100 EN + 100 FR = 200 cases
3. **Federal Court of Appeal (FCA)** - 100 EN + 100 FR = 200 cases
4. **Social Security Tribunal (SST)** - 100 EN + 100 FR = 200 cases

**Rationale:** Legal documents require **semantic integrity**. Can't split mid-argument (breaks precedent chains). Hybrid approach: structural sectioning + semantic similarity for long sections.

**Pipeline Integration:**
- Uses existing `jurispipeline` package (`eva-orchestrator/jurispipeline/`)
- Case model schema: `Case(id, neutral_citation, style_of_cause, decision_date, full_text, judges, citations, metadata)`
- Pydantic v2 models with validation

**Chunking Method:**

**Phase 1: Structural Sectioning**
1. Parse case HTML/PDF to extract sections:
   - **Header:** Citation, date, judges, docket
   - **Headnote:** Summary (if available)
   - **Facts:** Background and procedural history
   - **Issue(s):** Legal questions presented
   - **Analysis:** Court's reasoning (may split if >1500 tokens)
   - **Holding/Ruling:** Decision and disposition
   - **Dissent:** Minority opinion (if any)

2. Each section = baseline chunk

**Phase 2: Semantic Subdivision (for long sections)**
- If section >1500 tokens:
  - Use `sentence-transformers/all-MiniLM-L6-v2`
  - Similarity threshold: 0.7
  - Max chunk: 800 tokens, Min chunk: 100 tokens
  - Overlap: 120 tokens (sliding window)
  - Preserve paragraph boundaries

**Special Handling:**
- **Citations:** Extract and store as metadata (`citations: ["2019 SCC 65", "Criminal Code s. 8"]`)
- **Precedents:** Link to other cases via neutral citation
- **Tables:** Keep intact (e.g., sentencing guidelines, statutory interpretation tables)
- **Footnotes:** Include inline with markers `[^1]`
- **Bilingual Linking:** EN ↔ FR versions linked via `linked_document_fr/en` field

**Example Chunk:**
```markdown
# R. v. Smith, 2024 SCC 1 - Analysis (Part 1)

**Neutral Citation:** 2025 SCC 1  
**Style of Cause:** R. v. Smith  
**Court:** Supreme Court of Canada  
**Decision Date:** 2025-01-15  
**Docket:** 39876  
**Judges:** Wagner C.J., Karakatsanis, Côté, Brown, Rowe, Martin, Kasirer, Jamal, O'Bonsawin JJ.

## Section: Analysis

### I. Reasonable Expectation of Privacy in Location Data

[1] The central issue in this appeal is whether individuals retain a reasonable expectation 
of privacy in historical location data obtained from mobile telecommunications providers. 
This Court has previously recognized that privacy interests extend to informational content 
that reveals intimate details of an individual's lifestyle and personal choices 
(R. v. Spencer, 2014 SCC 43, at para. 51).

[2] Location data, by its nature, chronicles a person's movements over time. When aggregated, 
such data reveals patterns of behavior, associations, and activities that engage core privacy 
values protected by s. 8 of the Charter. As this Court stated in R. v. Marakah, 2017 SCC 59, 
at para. 32, "[t]he question is whether the claimant had a reasonable expectation of privacy 
in the subject matter of the alleged search."

[3] In the digital age, mobile devices have become ubiquitous. Location data generated by 
these devices is retained by telecommunications providers for business purposes and can be 
accessed by law enforcement. The question becomes whether individuals, by using mobile 
technology, have relinquished their privacy in their physical movements.

[Citations: R. v. Spencer (2014 SCC 43), R. v. Marakah (2017 SCC 59), Charter s. 8]
[Continued in: R. v. Smith, 2024 SCC 1 - Analysis (Part 2)]
[FR version: R. c. Smith, 2024 CSC 1 - Analyse (Partie 1)]
```

**Metadata Schema:**
```json
{
  "doc_id": "scc-2024-001-en",
  "source": "jurisprudence",
  "document_type": "case_law",
  "tribunal": "Supreme Court of Canada",
  "language": "en",
  "linked_document_fr": "scc-2024-001-fr",
  "chunk_id": "scc-2024-001-en-chunk-003",
  "chunk_index": 3,
  "total_chunks": 6,
  "neutral_citation": "2025 SCC 1",
  "style_of_cause": "R. v. Smith",
  "docket_number": "39876",
  "decision_date": "2025-01-15",
  "judges": ["Wagner C.J.", "Karakatsanis J.", "Côté J.", "Brown J.", "Rowe J.", "Martin J.", "Kasirer J.", "Jamal J.", "O'Bonsawin J."],
  "section_type": "analysis",
  "heading_path": "I. Reasonable Expectation of Privacy in Location Data",
  "legal_issues": ["Charter s. 8", "Digital privacy", "Reasonable expectation of privacy"],
  "citations_referenced": ["2014 SCC 43", "2017 SCC 59"],
  "outcome": "Appeal allowed",
  "url_source": "https://www.scc-csc.ca/case-dossier/info/...",
  "hash_fingerprint": "sha256:abc123...",
  "ingestion_timestamp": "2025-12-08T15:30:00Z",
  "embedding_model": "text-embedding-3-large",
  "embedding_dimensions": 3072
}
```

**Quality Assurance:**
- [ ] **Completeness:** All 800 cases chunked (95%+ success rate)
- [ ] **Bilingual Parity:** EN/FR pairs correctly linked (400 pairs)
- [ ] **Metadata Validation:** No null required fields (tribunal, citation, date)
- [ ] **Citation Extraction:** Precedents captured in 90%+ of cases
- [ ] **Chunk Boundaries:** No mid-paragraph splits (manual review of 20 samples per tribunal)

**Data Acquisition Plan:**
1. **Week 1:** Ingest 100 SCC cases (EN + FR) using `jurispipeline` discovery + fetch stages
2. **Week 2:** Ingest 100 FC cases (EN + FR)
3. **Week 3:** Ingest 100 FCA cases (EN + FR)
4. **Week 4:** Ingest 100 SST cases (EN + FR)
5. **Week 5:** Quality validation + chunking execution

**Reference:** See `eva-rag/data-sources/jurisprudence/ingestion-spec.md` for full pipeline details

---

### Strategy 4: Article-Level (IT Collective Agreement)

**Input:** 2 files (EN/FR), 746 KB  
**Output:** 200 chunks (~50 articles × 2 languages, some split)

**Example Chunk:**
```markdown
# IT Collective Agreement - Article 12: Vacation Leave

**Article:** 12
**Title:** Vacation Leave
**Language:** English

## 12.1 Entitlement
| Years of Service | Vacation Days |
|------------------|---------------|
| 0-7 years | 15 days |
| 8-15 years | 20 days |
| 16-27 years | 25 days |
| 28+ years | 30 days |

## 12.2 Accumulation
Credits accumulate at 1.25 days/month (0-7 years service).

## 12.3 Carry-Over
Up to 5 days may carry over to next fiscal year.

[Cross-refs: Article 8.2 (Definitions)]
[FR version: Article 12 - Congé annuel]
```

---

## 🚀 Implementation Plan

### Week 1: Build Chunking Pipeline

**Day 1-2: Semantic Chunker (Canada.ca, IT Agreement)**
- [ ] Load JSON ingestion files
- [ ] Parse HTML to Markdown
- [ ] Split at H2/H3 boundaries
- [ ] Inject CE context (breadcrumbs)
- [ ] Generate metadata
- [ ] Write to `data/chunked/`

**Day 3-4: Aggregation Chunker (Employment Analytics)**
- [ ] Parse CSV metadata from JSON
- [ ] Group rows by (GEO, Metric, Year)
- [ ] Calculate summary statistics
- [ ] Format as Markdown tables
- [ ] Write to `data/chunked/`

**Day 5: Legal Chunker (Jurisprudence)**
- [ ] Parse case structure
- [ ] Split by legal sections
- [ ] Preserve citations
- [ ] Link precedents
- [ ] Write to `data/chunked/`

**Deliverable:** `src/eva_rag/chunking/` module with 3 chunkers

### Week 2: Quality Validation & Production Run

**Day 6-7: Quality Validation**
- [ ] Sample 20 chunks per source
- [ ] Manual review for CE compliance
- [ ] Check metadata completeness
- [ ] Validate bilingual linking
- [ ] Test chunk boundaries

**Day 8-9: Full Production Run**
- [ ] Run chunkers on all 1,272 documents
- [ ] Verify 1,971 chunks generated
- [ ] Validate chunk count per source
- [ ] Store in `data/chunked/`
- [ ] Generate summary report

**Day 10: Housekeeping & Documentation**
- [ ] Update README with Phase 2 status
- [ ] Create CHUNKING-GUIDE.md
- [ ] Run linting/formatting
- [ ] Update repo tree map
- [ ] Commit all changes

**Deliverable:** 1,971 chunks ready for Phase 3 (embedding)

---

## ✅ Approval Checklist

**Before proceeding to implementation, approve:**

- [ ] **Canada.ca Strategy**: Page-level + breadcrumbs → 1,257 chunks
- [ ] **Employment Strategy**: Time-series aggregation → 400 chunks
- [ ] **Jurisprudence Strategy**: Legal reasoning blocks → 24 chunks
- [ ] **IT Agreement Strategy**: Article-level → 200 chunks
- [ ] **Total Chunks**: 1,971 chunks acceptable?
- [ ] **Total Cost**: $0.024 one-time embedding cost approved?
- [ ] **CE Constraints**: All 6 constraints understood and agreed?
- [ ] **Housekeeping**: Checklist will be completed before Phase 2 done?

**Approved By:** _________________________  
**Date:** _________________________  
**Comments:** _________________________

---

## 📎 Related Documents

- `DATA-INVENTORY-FOR-REVIEW.md` - Phase 1 ingestion inventory
- `EVA-DATA-MODEL-WITH-FASTER-PRINCIPLES.md` - Data model foundation
- `DATA-SOURCE-ORGANIZATION-STANDARD.md` - Pipeline architecture
- `EVA-DATA-PIPELINE-ROADMAP.md` - 8-week implementation plan

**Next Phase:** `EVA-RAG-PHASE-3-EMBEDDING-STRATEGY-20241208.md` (after approval)

---

**🏷️ END FILE STAMP**  
**Generated By:** P02 Requirements Engine v2.0  
**Template:** `eva-orchestrator/templates/requirements.md.template`  
**Last Updated:** 2024-12-08 18:45 EST  
**Review Status:** 🔴 AWAITING MARCO APPROVAL
