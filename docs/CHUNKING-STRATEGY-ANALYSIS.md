# EVA-RAG Chunking Strategy Analysis

**Date:** December 8, 2024  
**Purpose:** Define optimal chunking strategies for each ingested data source before Phase 2 execution  
**Status:** 🔴 CRITICAL DECISION REQUIRED  
**Blocks:** Phase 2 (Chunking), Phase 3 (Embeddings), Phase 4 (Search)

---

## 📊 Overview

**Total Documents:** 1,272  
**Total Characters:** 13,987,837 (~14 MB)  
**Data Sources:** 7 categories

**Chunking Impact:**
- **Search Quality**: Chunks too large → poor precision, chunks too small → lost context
- **Embedding Cost**: More chunks = higher Azure OpenAI embedding costs
- **Query Performance**: More chunks = slower search (but better recall)
- **User Experience**: Chunk boundaries affect answer coherence

---

## 🎯 Chunking Decision Framework

For each data source, analyze:

1. **Document Structure**: How is information organized?
2. **Query Patterns**: How will users ask questions?
3. **Context Requirements**: How much context needed to answer?
4. **Metadata Preservation**: What must be retained?
5. **Cost vs Quality Trade-off**: Optimal chunk count?

---

## 1️⃣ Canada Life Benefits (4 docs, 810K chars, 521 pages)

### Current State
- **PSHCP Member Booklet**: 84 pages, 548K chars (health coverage)
- **PSDCP Member Booklet**: 40 pages, 238K chars (dental coverage)
- **200 Questions FAQ**: 256 pages, 14K chars (Q&A format)
- **EVA Scenario Document**: 141 pages, 11K chars (implementation guide)

### Document Structure Analysis

**PSHCP/PSDCP Booklets:**
- Hierarchical: Sections → Sub-sections → Paragraphs
- Key sections: Coverage limits, Eligibility, Claims process, Drug formulary (tables), Vision care
- Special content: Tables (drug lists, coverage grids), Bullet lists, Cross-references

**200 Questions FAQ:**
- Q&A pairs: Question → Answer
- Topics: Claims, Coverage, Eligibility, Appeals
- Cross-references to booklet sections

**EVA Scenario:**
- Implementation guide structure
- Step-by-step procedures
- Example queries

### Expected Query Patterns

**User Questions:**
- "What prescription drugs are covered under PSHCP?"
- "What's the vision care coverage limit?"
- "How do I submit a dental claim?"
- "Is physiotherapy covered?"
- "What's the deductible for PSDCP?"

**Required Context:**
- Benefit type (health vs dental)
- Coverage limits (dollar amounts, percentages)
- Eligibility criteria
- Cross-references (e.g., "See Section 4.2 for details")

### Recommended Chunking Strategy

**Option A: Semantic Chunking (RECOMMENDED)**
- **Method**: Split by section headings + semantic boundaries
- **Chunk Size**: 800-1200 tokens (~3-5 paragraphs)
- **Overlap**: 100 tokens
- **Structure Awareness**: 
  - Preserve section hierarchy (H1 → H2 → H3)
  - Keep tables intact (don't split mid-table)
  - Preserve Q&A pairs together
- **Special Handling**:
  - Drug formulary tables: Chunk by drug category
  - Coverage grids: Keep complete table as one chunk
  - Cross-references: Store section IDs in metadata

**Option B: Structural Chunking (Alternative)**
- **Method**: Split by PDF sections (bookmarks, TOC)
- **Chunk Size**: Variable (section-based)
- **Overlap**: None (section boundaries are natural)
- **Pros**: Cleaner boundaries, easier navigation
- **Cons**: Some sections too large (>2000 tokens)

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:**
- PSHCP: ~60 chunks (548K / 1000 tokens avg)
- PSDCP: ~30 chunks (238K / 1000 tokens avg)
- FAQ: ~14 chunks (one per Q&A group)
- EVA Scenario: ~11 chunks
- **Total: ~115 chunks**

**Metadata to Preserve:**
```json
{
  "benefit_type": "PSHCP|PSDCP",
  "section_number": "4.2",
  "section_title": "Prescription Drug Coverage",
  "page_number": 42,
  "coverage_category": "drugs|dental|vision|claims",
  "document_type": "booklet|faq|guide"
}
```

---

## 2️⃣ Supreme Court Jurisprudence (4 cases, 8,607 chars)

### Current State
- **sample_case_1.html**: 3,252 chars
- **sample_case_2.html**: 3,197 chars
- **R. v. Smith (privacy)**: 1,431 chars
- **ABC Corp. v. Minister (tax)**: 727 chars

### Document Structure Analysis

**Legal Cases:**
- **Header**: Case citation, court, date, judges
- **Facts**: Background of the case
- **Issue**: Legal question
- **Analysis**: Legal reasoning
- **Ruling**: Decision and ratio decidendi
- **Dissent** (if any): Minority opinion

### Expected Query Patterns

**User Questions:**
- "What Supreme Court cases deal with privacy rights?"
- "Show me recent tax law precedents"
- "What's the ruling in R. v. Smith?"
- "Cases where Charter Section 8 was cited"

**Required Context:**
- Full legal reasoning (can't split analysis mid-argument)
- Case citations (precedent references)
- Judge names
- Charter sections cited

### Recommended Chunking Strategy

**Option A: Structural Chunking by Legal Section (RECOMMENDED)**
- **Method**: Split by legal structure (Facts, Issue, Analysis, Ruling)
- **Chunk Size**: Variable (keep each section intact)
- **Overlap**: None (legal sections are discrete)
- **Structure Awareness**:
  - Facts = 1 chunk
  - Issue = 1 chunk
  - Analysis = 1 chunk (or split if >1500 tokens)
  - Ruling = 1 chunk
- **Special Handling**:
  - Preserve case citations as metadata
  - Keep precedent references linked
  - Store judge names, date, court level

**Option B: One Case = One Chunk (Alternative)**
- **Method**: Entire case as single chunk
- **Chunk Size**: 700-3200 tokens per case
- **Pros**: Maintains complete legal context
- **Cons**: May be too granular for specific legal issues

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:**
- **Option A (Structural)**: 4 cases × 4 sections avg = ~16 chunks
- **Option B (Full Case)**: 4 chunks

**Metadata to Preserve:**
```json
{
  "case_citation": "R. v. Smith, 2024 SCC 001",
  "court": "Supreme Court of Canada",
  "date": "2024-03-15",
  "judges": ["McLachlin C.J.", "Abella J.", "..."],
  "legal_issue": "Charter Section 8 - Unreasonable search",
  "outcome": "Appeal dismissed",
  "precedents_cited": ["R. v. Hunter", "R. v. Edwards"],
  "section_type": "facts|issue|analysis|ruling"
}
```

---

## 3️⃣ Canada.ca Government Content (1,257 pages, 11.3 MB, Bilingual)

### Current State
- **English**: 632 pages, 5.2 MB
- **French**: 625 pages, 6.1 MB
- **Coverage**: Jobs, immigration, business, benefits, health, taxes, environment

### Document Structure Analysis

**Government Web Pages:**
- **Breadcrumbs**: canada.ca → Services → Jobs → Find a job
- **Page Title**: H1 heading
- **Sections**: H2 → H3 → Paragraphs
- **Lists**: Steps, Requirements, Eligibility
- **Tables**: Comparison tables, Fee schedules
- **Links**: Internal (canada.ca), External

### Expected Query Patterns

**User Questions:**
- "How do I apply for EI benefits?"
- "What's the process to sponsor my parents to Canada?"
- "How do I register a business in Canada?"
- "What are the tax deadlines for 2025?"

**Required Context:**
- Step-by-step procedures (must be complete)
- Eligibility criteria (all conditions)
- Contact information (phone, email, office locations)
- Bilingual linking (EN ↔ FR equivalent pages)

### Recommended Chunking Strategy

**Option A: Page-Level Chunking (RECOMMENDED FOR MVP)**
- **Method**: Each page = 1 chunk (or split if >2000 tokens)
- **Chunk Size**: Variable (400-2000 tokens per page)
- **Overlap**: None (page boundaries are natural)
- **Structure Awareness**:
  - Preserve breadcrumbs (navigation context)
  - Keep bilingual page IDs linked
  - Store URL, last-modified date
- **Special Handling**:
  - Multi-step procedures: Keep all steps together
  - Tables: Keep intact or chunk by row group
  - EN/FR linking: Store parallel document ID

**Option B: Section-Level Chunking (Alternative)**
- **Method**: Split by H2 sections within each page
- **Chunk Size**: 500-1000 tokens per section
- **Pros**: Finer granularity for long pages
- **Cons**: May lose page-level context

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:**
- **Option A (Page)**: 1,257 chunks (one per page)
- **Option B (Section)**: ~3,000 chunks (2.5 sections avg per page)

**Metadata to Preserve:**
```json
{
  "url": "https://www.canada.ca/en/services/jobs/opportunities.html",
  "language": "en|fr",
  "parallel_document_id": "doc-fr-456",
  "breadcrumbs": ["Canada.ca", "Services", "Jobs", "Find a job"],
  "page_title": "Find a job",
  "topic": "employment|immigration|business|benefits",
  "last_modified": "2024-11-15",
  "department": "ESDC"
}
```

---

## 4️⃣ Employment Analytics (2 CSV files, 10,853 chars, 5,700 rows)

### Current State
- **Dataset 1**: Employment by Industry (3,000 rows, 14-10-0355)
- **Dataset 2**: Labour Force by Province (2,700 rows, 14-10-0287)

### Document Structure Analysis

**CSV Structure:**
- **Columns**: REF_DATE, GEO, NAICS/Age/Sex, Data_Type, UOM, VALUE, STATUS
- **Time Range**: 2020-2024 (monthly)
- **Geographic**: Canada, Ontario, Quebec, BC, Alberta

### Expected Query Patterns

**User Questions:**
- "What's the unemployment rate in Ontario in 2024?"
- "Show employment trends in healthcare sector"
- "Compare employment rates by province"
- "What's the labour force participation rate for women?"

**Required Context:**
- Time period (date range)
- Geographic location
- Industry or demographic
- Metric type (rate vs absolute count)

### Recommended Chunking Strategy

**Option A: Time-Series Aggregation (RECOMMENDED)**
- **Method**: Aggregate by (GEO + Metric + Year)
- **Example Chunk**: "Ontario unemployment rate 2024" = 12 rows (monthly data)
- **Chunk Size**: 12-60 rows per chunk
- **Overlap**: None (time-series are discrete)
- **Structure Awareness**:
  - Keep all months together for trend analysis
  - Store entire row as metadata (filterable)
  - Generate summary statistics (avg, min, max)

**Option B: Row-Level Chunking (Alternative)**
- **Method**: Each row = 1 document
- **Chunk Size**: 1 row per chunk
- **Pros**: Maximum granularity, easy filtering
- **Cons**: 5,700 chunks, expensive embeddings, poor for trend questions

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:**
- **Option A (Aggregated)**: ~400 chunks (5 provinces × 10 industries × 5 years + demographics)
- **Option B (Row-level)**: 5,700 chunks

**Metadata to Preserve:**
```json
{
  "dataset_id": "14-10-0355",
  "province": "Ontario",
  "industry": "Healthcare and social assistance",
  "metric": "Employment rate",
  "time_period": "2024",
  "data_points": [
    {"month": "2024-01", "value": 8.5},
    {"month": "2024-02", "value": 8.3}
  ],
  "summary_stats": {
    "average": 8.2,
    "min": 7.8,
    "max": 8.9,
    "trend": "declining"
  }
}
```

---

## 5️⃣ IT Collective Agreement (2 files, 746K chars, EN/FR)

### Current State
- **English**: 346K chars (Treasury Board + ACFO)
- **French**: 400K chars (parallel structure)

### Document Structure Analysis

**Agreement Structure:**
- **Articles**: Numbered clauses (Article 1, 2, 3...)
- **Sections**: Sub-clauses (1.1, 1.2, 1.3...)
- **Appendices**: Pay scales, Classifications
- **Cross-references**: "See Article 12.4"

### Expected Query Patterns

**User Questions:**
- "What's the pay scale for IT-03?"
- "How many vacation days for IT-02 with 5 years service?"
- "What's the grievance process?"
- "Overtime rules for IT employees"

**Required Context:**
- Article number (for citation)
- Classification level (IT-01, IT-02, IT-03, IT-04)
- Cross-referenced articles (must be retrievable)
- Bilingual equivalence (EN ↔ FR articles)

### Recommended Chunking Strategy

**Option A: Article-Level Chunking (RECOMMENDED)**
- **Method**: Each article = 1 chunk (or split if >1500 tokens)
- **Chunk Size**: Variable (200-1500 tokens per article)
- **Overlap**: None (articles are discrete)
- **Structure Awareness**:
  - Preserve article number and title
  - Link EN/FR parallel articles
  - Store cross-references as metadata
- **Special Handling**:
  - Pay scale tables: Keep entire table as one chunk
  - Appendices: Chunk by section
  - Definitions: Keep all definitions together

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:**
- **Estimated**: ~100 articles × 2 languages = ~200 chunks

**Metadata to Preserve:**
```json
{
  "article_number": "12.4",
  "article_title": "Vacation Leave Entitlement",
  "language": "en|fr",
  "parallel_article_id": "doc-fr-art-12-4",
  "classifications": ["IT-01", "IT-02", "IT-03", "IT-04"],
  "cross_references": ["Article 8.2", "Appendix A"],
  "effective_date": "2022-06-22"
}
```

---

## 6️⃣ Employment Equity Act (5 files, 1.9 MB, EN/FR)

### Current State
- **HTML EN**: 47K chars (S.C. 1995, c. 44)
- **HTML FR**: 50K chars (L.C. 1995, ch. 44)
- **PDF Bilingual**: 1.8 MB (consolidated)

### Recommended Chunking Strategy

**Option A: Section-Level (by statute section)**
- **Method**: Split by section number (s. 1, s. 2, s. 3...)
- **Chunk Size**: Variable (100-800 tokens per section)
- **Similar to IT Agreement approach**

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:** ~80 chunks (40 sections × 2 languages)

---

## 7️⃣ Employment Standards & Workplace Rights (2 files, 2,490 chars)

### Current State
- **Employment Standards Guide**: 1,078 chars
- **Workplace Rights FAQ**: 1,412 chars

### Recommended Chunking Strategy

**Option A: Q&A Chunking**
- **Method**: One question-answer pair = 1 chunk
- **Chunk Size**: 200-400 tokens per Q&A
- **Similar to Canada Life FAQ approach**

**Decision:** ⚠️ **NEEDS APPROVAL**

**Estimated Chunks:** ~10 chunks

---

## 📊 Summary Table

| Data Source | Documents | Size | Recommended Strategy | Est. Chunks | Cost Impact |
|-------------|-----------|------|---------------------|-------------|-------------|
| Canada Life Benefits | 4 | 810K | Semantic (section) | 115 | Low |
| Jurisprudence | 4 | 8.6K | Structural (legal sections) | 16 | Very Low |
| Canada.ca | 1,257 | 11.3 MB | Page-level | 1,257 | High |
| Employment Analytics | 2 CSV | 10.8K | Time-series aggregation | 400 | Low |
| IT Agreement | 2 | 746K | Article-level | 200 | Medium |
| Employment Equity Act | 5 | 1.9 MB | Section-level | 80 | Low |
| Employment Standards | 2 | 2.5K | Q&A pairs | 10 | Very Low |
| **TOTAL** | **1,276** | **14 MB** | **Mixed strategies** | **~2,078** | **Medium** |

---

## 💰 Cost Estimation

### Embedding Costs (Azure OpenAI text-embedding-3-small)

- **Model**: text-embedding-3-small ($0.00002 per 1K tokens)
- **Average chunk**: 600 tokens
- **Total chunks**: 2,078
- **Total tokens**: 2,078 × 600 = 1,246,800 tokens
- **Cost**: 1,246.8 × $0.00002 = **$0.025** (one-time)

### Storage Costs (Azure AI Search)

- **Vector dimensions**: 1536 per chunk
- **Storage per chunk**: ~10 KB (vector + metadata)
- **Total storage**: 2,078 × 10 KB = ~20 MB
- **Cost**: Negligible (~$0.01/month)

### Re-embedding Costs (if chunks change)

- **Scenario**: 10% of chunks change monthly
- **Monthly cost**: 208 chunks × 600 tokens × $0.00002 = **$0.0025/month**

---

## ✅ Next Steps

### 1. **Review & Approve Strategies** (THIS WEEK)
- [ ] Review each data source chunking decision
- [ ] Approve or modify recommendations
- [ ] Document final decisions

### 2. **Create Chunking Configurations** (NEXT)
- [ ] Generate `publish/chunking_strategy.yaml` for each source
- [ ] Define metadata schemas
- [ ] Set overlap and token limits

### 3. **Build Chunking Pipeline** (Phase 2)
- [ ] Implement semantic chunker
- [ ] Implement structural chunker
- [ ] Implement CSV aggregator
- [ ] Add special handling (tables, Q&A, legal sections)

### 4. **Test with Samples** (Before Full Run)
- [ ] Chunk 10 sample documents from each source
- [ ] Validate chunk quality (boundaries, context preservation)
- [ ] Test search quality with sample queries
- [ ] Adjust strategies if needed

---

## 🚨 Critical Decisions Needed

**BEFORE proceeding to Phase 2, Marco must approve:**

1. **Canada Life**: Semantic vs Structural chunking?
2. **Jurisprudence**: Structural (legal sections) vs Full case?
3. **Canada.ca**: Page-level vs Section-level?
4. **Employment Analytics**: Time-series aggregation vs Row-level?
5. **IT Agreement**: Article-level chunking approved?
6. **Total chunk count**: 2,078 chunks acceptable? (Cost: $0.025 one-time)

**Sign-off Required:** ___________________  
**Date:** ___________________

---

**STATUS:** 🔴 **AWAITING APPROVAL** - Blocks Phase 2 execution
