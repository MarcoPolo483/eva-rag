# EVA-RAG Phase 2: Chunking Strategy Analysis

**🏷️ FILE STAMP**  
**ID:** `EVA-RAG-CHUNK-STRAT-20241208-1830`  
**Type:** Technical Analysis | Phase 2 Specification  
**Tags:** `#chunking` `#phase2` `#rag-pipeline` `#context-engineering` `#embedding-strategy`  
**Owner:** Marco Presta + GitHub Copilot  
**Status:** 🔴 DRAFT - AWAITING APPROVAL  
**Created:** 2024-12-08 18:30 EST  
**Version:** 1.0 (Fresh Analysis)  

---

## 🎯 Executive Summary

**Problem:** 1,272 ingested documents (14 MB raw JSON) need to be chunked for RAG retrieval  
**Goal:** Design optimal chunking strategy balancing **search quality**, **context preservation**, and **cost**  
**Approach:** Apply **Context Engineering (CE)**, **Human Knowledge (HK)**, and **Working Memory (WM)** principles  
**Outcome:** Production-ready chunking specification for Phase 2 implementation

### Key Decisions Needed

| Data Source | Strategy | Chunks | Cost | Decision |
|-------------|----------|--------|------|----------|
| Canada.ca | Page-level with CE | 1,257 | $0.015 | ⚠️ Approve |
| Employment CSV | WM-aware time-series | 400 | $0.005 | ⚠️ Approve |
| Jurisprudence | Legal reasoning blocks | 24 | $0.001 | ⚠️ Approve |
| IT Agreement | Article-level with HK | 200 | $0.002 | ⚠️ Approve |
| **TOTAL** | **Mixed strategies** | **~1,900** | **$0.038** | 🔴 **BLOCKED** |

---

## 🧠 Theoretical Foundation

### Context Engineering (CE) Principles

**Definition:** Deliberate design of information boundaries to optimize LLM comprehension

**Applied to Chunking:**
1. **Context Windows**: LLMs have limited working memory (~8K-128K tokens)
2. **Retrieval Units**: Each chunk = one retrievable context unit
3. **Boundary Optimization**: Split at natural semantic boundaries, not arbitrary token limits
4. **Metadata Injection**: Augment chunks with structured context (headers, breadcrumbs, document type)

**Example (Good CE):**
```
Chunk: "Section 4.2 - Prescription Drug Coverage under PSHCP
The Public Service Health Care Plan covers eligible prescription drugs listed in the Drug Benefit List.
Coverage is 80% of eligible costs after $100 annual deductible per family.
Maximum annual benefit: $3,000 per person. [Page 42]"

Metadata: {
  "section": "4.2",
  "title": "Prescription Drug Coverage",
  "benefit_type": "PSHCP",
  "coverage_limit": "$3,000",
  "page": 42
}
```

**Example (Bad CE):**
```
Chunk: "...plan covers eligible prescription drugs listed in the Drug Benefit List. Coverage is 80% of eligible..."
Metadata: { "page": 42 }
```

### Human Knowledge (HK) Principles

**Definition:** Leverage domain expert understanding of content structure and usage patterns

**Applied to Chunking:**
1. **Domain Structure**: Legal documents ≠ Government websites ≠ CSV datasets
2. **Query Patterns**: How will humans actually ask questions?
3. **Expert Workflow**: What context do domain experts need to answer?
4. **Citation Requirements**: Legal/policy contexts need precise source attribution

**Example (Legal - HK-aware):**
```
Chunk: R. v. Smith, 2024 SCC 1 - Legal Issue
"The central issue is whether section 8 of the Charter protects digital privacy in the context of..."

Context needed by legal expert:
- Case citation (R. v. Smith, 2024 SCC 1)
- Legal issue (Charter s. 8)
- Court level (Supreme Court of Canada)
- Date (2024)
- Precedents cited (Hunter v. Southam)
```

### Working Memory (WM) Principles

**Definition:** Optimize for LLM's ability to "hold" and reason about retrieved chunks

**Applied to Chunking:**
1. **WM Capacity**: Most LLMs reason best with 3-5 retrieved chunks (3-5K tokens total)
2. **Chunk Size**: 600-1200 tokens per chunk = sweet spot for reasoning
3. **Redundancy**: Slight overlap (50-100 tokens) prevents context loss at boundaries
4. **Ranking**: Better to retrieve 5 relevant chunks than 50 marginally relevant ones

**Example (Time-Series - WM-aware):**
```
Bad: 5,700 individual CSV rows → LLM overwhelmed, can't spot trends
Good: 400 aggregated chunks (one per province-metric-year) → LLM can reason about trends

Query: "What's the unemployment trend in Ontario?"
Retrieved: 1 chunk = "Ontario unemployment 2020-2024: [8.5%, 8.3%, 7.9%, 7.2%, 6.8%]"
LLM reasoning: "Clear declining trend from 8.5% to 6.8% over 5 years..."
```

---

## 📊 Data Source Analysis (Fresh Look)

### 1️⃣ Canada.ca (632 EN + 625 FR = 1,257 pages, 11.3 MB)

**Ingested Structure:**
```json
{
  "source_url": "https://www.canada.ca/en/services/jobs.html",
  "content_preview": "Skip to main content...",
  "content_length": 3963,
  "page_count": 1,
  "metadata": {
    "title": "Jobs and the workplace - Canada.ca",
    "description": "Find a job, find student employment...",
    "crawl_depth": 1,
    "domain": "https://www.canada.ca"
  }
}
```

**Human Knowledge (HK) Insights:**
- **User Intent**: Citizens want procedural answers ("How do I apply for EI?")
- **Expert Pattern**: Government services are task-oriented (apply, register, report)
- **Navigation**: Breadcrumb context is critical (canada.ca → Services → Jobs → Find a job)

**Context Engineering (CE) Strategy:**

**Option A: Page-Level Chunking with CE (RECOMMENDED)**
- **Method**: One page = one chunk (or split if >2000 tokens)
- **Chunk Size**: 400-2000 tokens per page (avg ~600 tokens)
- **CE Enhancements**:
  - **Inject breadcrumbs** at start: `[Canada.ca > Services > Jobs > Find a job]`
  - **Preserve title + description** as chunk prefix
  - **Link bilingual**: Store `parallel_doc_id` for EN ↔ FR
  - **Add navigation context**: "This page is part of the Jobs and workplace services section"

**Working Memory (WM) Optimization:**
- **Retrieval**: Top 5 pages retrieved per query
- **Token Budget**: 5 pages × 600 tokens = 3,000 tokens in WM (well within capacity)
- **Reasoning**: LLM can synthesize info across multiple government pages

**Example Chunk (with CE):**
```markdown
[Breadcrumb: Canada.ca > Services > Jobs > Find a job]
[Page Title: Jobs and the workplace - Canada.ca]
[Description: Find a job, find student employment, funding programs for jobs and training, start a business and learn workplace standards]

# Jobs and the workplace

## Find a job
- Job Bank - Search for jobs across Canada
- Youth employment programs
- International students working in Canada

## Training and skills
- Funding for skills development
- Apprenticeship programs
...

[URL: https://www.canada.ca/en/services/jobs.html]
[Language: EN | FR version: /fr/services/emplois.html]
[Last crawled: 2024-12-08]
```

**Metadata Schema:**
```json
{
  "doc_id": "canada-ca-en-jobs-001",
  "source_url": "https://www.canada.ca/en/services/jobs.html",
  "language": "en",
  "parallel_doc_id": "canada-ca-fr-emplois-001",
  "breadcrumbs": ["Canada.ca", "Services", "Jobs"],
  "page_title": "Jobs and the workplace - Canada.ca",
  "page_description": "Find a job...",
  "topic": "employment",
  "department": "ESDC",
  "crawl_depth": 1,
  "last_updated": "2024-12-08"
}
```

**Estimated Chunks:** 1,257 (one per page)  
**Embedding Cost:** 1,257 chunks × 600 tokens avg × $0.00002/1K = **$0.015**  
**Decision:** ⚠️ **AWAITING APPROVAL**

---

### 2️⃣ Employment Analytics (2 CSV files, 5,700 rows, 10.8K chars)

**Ingested Structure:**
```json
{
  "dataset_name": "Employment by Industry (14-10-0355)",
  "content_length": 5433,
  "metadata": {
    "loader": "CSVLoader",
    "column_count": 7,
    "row_count": 3000,
    "columns": ["REF_DATE", "GEO", "NAICS", "Data_Type", "UOM", "VALUE", "STATUS"],
    "statistics": {
      "REF_DATE": { "unique_count": 60 },
      "GEO": { "unique_count": 5, "sample_values": ["British Columbia", "Canada", "Alberta", "Quebec", "Ontario"] },
      "NAICS": { "unique_count": 10 }
    }
  }
}
```

**Human Knowledge (HK) Insights:**
- **User Intent**: Policy analysts want **trends**, not individual data points
  - "What's the unemployment trend in Ontario?" ✓
  - "What was Ontario's unemployment rate on June 15, 2023?" ✗ (too granular)
- **Expert Pattern**: Time-series analysis requires **full year** for seasonality
- **Query Types**: Geographic comparisons, industry trends, demographic breakdowns

**Working Memory (WM) Problem:**
- **Bad approach**: 5,700 individual rows → LLM retrieves 50 rows → Can't see trends
- **Good approach**: 400 aggregated chunks → LLM retrieves 5 chunks → Immediately sees patterns

**Context Engineering (CE) Strategy:**

**Option A: Time-Series Aggregation (RECOMMENDED)**
- **Method**: Group by (Province + Industry + Full Year)
- **Chunk Structure**:
  ```markdown
  # Employment Analytics: Ontario - Healthcare - 2024
  
  **Dataset:** Employment by Industry (14-10-0355)
  **Province:** Ontario
  **Industry:** Health care and social assistance (NAICS)
  **Metric:** Employment (Persons x 1,000)
  **Time Period:** 2024 (12 months)
  
  ## Monthly Data
  | Month | Employment | Change |
  |-------|-----------|---------|
  | 2024-01 | 850,000 | +0.5% |
  | 2024-02 | 852,000 | +0.2% |
  | ... | ... | ... |
  | 2024-12 | 875,000 | +1.2% |
  
  ## Summary Statistics
  - Average: 862,500
  - Min: 848,000 (March 2024)
  - Max: 875,000 (December 2024)
  - Trend: +2.9% year-over-year
  - Seasonality: Peak in December (holiday hiring)
  
  [Source: Statistics Canada, Table 14-10-0355]
  ```

- **Chunk Size**: 500-800 tokens per aggregation
- **Overlap**: None (discrete time series)

**Metadata Schema:**
```json
{
  "doc_id": "statcan-14-10-0355-ON-healthcare-2024",
  "dataset": "14-10-0355",
  "province": "Ontario",
  "industry": "Healthcare and social assistance",
  "metric_type": "Employment",
  "unit": "Persons x 1,000",
  "time_period": "2024",
  "time_granularity": "monthly",
  "data_points": 12,
  "summary": {
    "average": 862500,
    "min": 848000,
    "max": 875000,
    "trend": "+2.9%",
    "yoy_change": "+25,000"
  }
}
```

**Working Memory Optimization:**
- Query: "Compare healthcare employment in Ontario vs Quebec in 2024"
- Retrieved: 2 chunks (ON-Healthcare-2024, QC-Healthcare-2024)
- LLM WM: 2 × 700 tokens = 1,400 tokens (easy comparison)

**Estimated Chunks:**
- Dataset 1 (Employment by Industry): 5 provinces × 10 industries × 5 years = 250 chunks
- Dataset 2 (Labour Force): 5 provinces × 6 demographics × 5 years = 150 chunks
- **Total: 400 chunks**

**Embedding Cost:** 400 chunks × 700 tokens × $0.00002/1K = **$0.0056**  
**Decision:** ⚠️ **AWAITING APPROVAL**

---

### 3️⃣ Jurisprudence (4 Supreme Court cases, 8.6K chars)

**Ingested Structure:**
```json
{
  "client": "jurisprudence",
  "document_type": "case_law",
  "content_preview": "# Smith v. Canada (Attorney General)\n2024 SCC 1\nDecision Date: January 15, 2024...",
  "content_length": 3252,
  "metadata": {
    "title": "Smith v. Canada - 2024 SCC 1",
    "jurisdiction": "Canada - Supreme Court",
    "target_users": "Legal researchers, Policy analysts"
  }
}
```

**Human Knowledge (HK) Insights:**
- **Legal Reasoning**: Cannot split mid-argument (breaks chain of logic)
- **Citation Requirements**: Lawyers need **exact** case citations + page numbers
- **Query Patterns**:
  - By legal issue: "Show me cases on Charter section 8"
  - By precedent: "Cases citing R. v. Hunter"
  - By outcome: "Cases where privacy rights were upheld"

**Context Engineering (CE) Strategy:**

**Option A: Legal Reasoning Blocks (RECOMMENDED)**
- **Method**: Split cases into logical sections preserving legal reasoning
- **Structure**:
  1. **Case Header** (1 chunk): Citation, court, date, judges, parties
  2. **Facts** (1 chunk): Background, procedural history
  3. **Legal Issue** (1 chunk): Question before the court, statutory provisions
  4. **Analysis** (2-3 chunks): Legal reasoning, precedent discussion, statutory interpretation
  5. **Ruling** (1 chunk): Decision, ratio decidendi, orders
  6. **Dissent** (if any): Minority opinion

**Example Chunk (Facts - with CE):**
```markdown
# R. v. Smith, 2024 SCC 1 - Facts

**Citation:** R. v. Smith, 2024 SCC 1  
**Court:** Supreme Court of Canada  
**Decision Date:** January 15, 2024  
**Coram:** Wagner C.J., Karakatsanis, Côté, Brown, Rowe, Martin, Kasirer, Jamal, O'Bonsawin JJ.

## Background

The appellant, John Smith, challenges his conviction for breach of probation arising from police surveillance of his digital communications. In 2022, police obtained a production order under s. 487.014 of the Criminal Code requiring the appellant's internet service provider to disclose metadata about his online activities without judicial pre-authorization.

## Procedural History

Trial Court: Convicted (2022 ONCJ 145)
Court of Appeal: Conviction upheld (2023 ONCA 89)
Supreme Court: Appeal allowed, new trial ordered

## Key Facts
- Police monitored appellant's IP address and browsing history for 6 months
- No warrant obtained (reliance on s. 487.014)
- Evidence showed appellant violated probation conditions
- Charter s. 8 challenge raised at trial

[Next section: Legal Issue]
[Case ID: scc-2024-001]
```

**Metadata Schema:**
```json
{
  "doc_id": "scc-2024-001-facts",
  "case_citation": "R. v. Smith, 2024 SCC 1",
  "case_name": "R. v. Smith",
  "court": "Supreme Court of Canada",
  "decision_date": "2024-01-15",
  "docket": "40123",
  "judges": ["Wagner C.J.", "Karakatsanis J.", "..."],
  "section_type": "facts",
  "section_order": 1,
  "legal_issues": ["Charter s. 8", "Digital privacy", "Production orders"],
  "precedents_cited": ["R. v. Hunter", "R. v. Edwards"],
  "outcome": "Appeal allowed",
  "jurisdiction": "Canada",
  "area_of_law": "Criminal law, Constitutional law"
}
```

**Working Memory Optimization:**
- Query: "What did the Supreme Court say about digital privacy?"
- Retrieved: 3 chunks (Facts, Legal Issue, Analysis section 1)
- LLM WM: 3 × 800 tokens = 2,400 tokens (can synthesize full legal reasoning)

**Estimated Chunks:**
- 4 cases × 6 sections avg = **24 chunks**

**Embedding Cost:** 24 chunks × 800 tokens × $0.00002/1K = **$0.00038**  
**Decision:** ⚠️ **AWAITING APPROVAL**

---

### 4️⃣ IT Collective Agreement (2 files EN/FR, 746K chars)

**Human Knowledge (HK) Insights:**
- **User Intent**: Employees need **specific** articles (pay scales, leave entitlement, overtime rules)
- **Citation Pattern**: Must preserve article numbers (Article 12.4)
- **Cross-references**: Articles reference other articles ("See Article 8.2 for definitions")

**Context Engineering (CE) Strategy:**

**Option A: Article-Level Chunking with Cross-Reference Linking (RECOMMENDED)**
- **Method**: Each article = 1 chunk (or split large articles at sub-sections)
- **CE Enhancements**:
  - **Article Header**: Inject article number + title at start
  - **Cross-Reference Metadata**: Store all referenced articles
  - **Bilingual Linking**: Link EN ↔ FR parallel articles
  - **Classification Tags**: Tag by employee group (IT-01, IT-02, IT-03, IT-04)

**Example Chunk:**
```markdown
# IT Collective Agreement - Article 12: Vacation Leave

**Article Number:** 12  
**Title:** Vacation Leave  
**Effective Date:** 2022-06-22  
**Applies To:** IT-01, IT-02, IT-03, IT-04  
**Language:** English

## 12.1 Entitlement

Employees earn vacation leave credits based on years of service:

| Years of Service | Vacation Days per Year |
|------------------|------------------------|
| 0-7 years        | 15 days                |
| 8-15 years       | 20 days                |
| 16-27 years      | 25 days                |
| 28+ years        | 30 days                |

## 12.2 Accumulation

Vacation leave credits accumulate at a rate of 1.25 days per month (0-7 years service).

## 12.3 Carry-Over

Up to 5 days may be carried over to the next fiscal year. Excess days are forfeited unless approved by management.

## 12.4 Cash-Out

Vacation leave may not be cashed out except upon retirement or separation. See Article 8.2 for definitions of retirement eligibility.

[Cross-references: Article 8.2 (Definitions), Article 13 (Sick Leave)]
[French version: Article 12 - Congé annuel]
[Source: Treasury Board - ACFO IT Collective Agreement]
```

**Metadata Schema:**
```json
{
  "doc_id": "it-agreement-en-art-12",
  "agreement_name": "IT Collective Agreement",
  "parties": ["Treasury Board", "ACFO"],
  "language": "en",
  "parallel_article_id": "it-agreement-fr-art-12",
  "article_number": "12",
  "article_title": "Vacation Leave",
  "classifications": ["IT-01", "IT-02", "IT-03", "IT-04"],
  "effective_date": "2022-06-22",
  "cross_references": ["Article 8.2", "Article 13"],
  "topic": "leave_entitlement",
  "section_type": "article"
}
```

**Estimated Chunks:**
- ~50 articles × 2 languages = **100 chunks**
- Large articles split into sub-sections: +100 chunks
- **Total: 200 chunks**

**Embedding Cost:** 200 chunks × 600 tokens × $0.00002/1K = **$0.0024**  
**Decision:** ⚠️ **AWAITING APPROVAL**

---

## 📊 Complete Chunking Specification Summary

### Total Cost & Chunk Breakdown

| Data Source | Method | Chunks | Avg Tokens | Total Tokens | Embedding Cost |
|-------------|--------|--------|------------|--------------|----------------|
| Canada.ca (EN/FR) | Page-level + CE | 1,257 | 600 | 754,200 | $0.015 |
| Employment Analytics | Time-series aggregation | 400 | 700 | 280,000 | $0.0056 |
| Jurisprudence | Legal reasoning blocks | 24 | 800 | 19,200 | $0.00038 |
| IT Agreement (EN/FR) | Article-level + HK | 200 | 600 | 120,000 | $0.0024 |
| Employment Equity Act | Section-level | 80 | 500 | 40,000 | $0.0008 |
| Employment Standards | Q&A pairs | 10 | 300 | 3,000 | $0.00006 |
| **TOTAL** | **Mixed strategies** | **1,971** | **~620** | **1,216,400** | **$0.024** |

### Principles Applied per Source

| Data Source | CE Applied | HK Applied | WM Applied |
|-------------|------------|------------|------------|
| Canada.ca | ✅ Breadcrumbs, navigation context | ✅ Task-oriented citizen queries | ✅ 5-page retrieval limit |
| Employment Analytics | ✅ Time-series structure | ✅ Trend analysis patterns | ✅ Aggregated chunks |
| Jurisprudence | ✅ Legal reasoning preservation | ✅ Citation requirements | ✅ 3-section retrieval |
| IT Agreement | ✅ Cross-reference linking | ✅ Article-based lookup | ✅ Single article focus |

---

## 🚀 Implementation Plan

### Phase 2.1: Chunking Pipeline (Week 1)

**Tasks:**
1. **Build Semantic Chunker** (Canada.ca, IT Agreement)
   - [ ] Load JSON ingestion files
   - [ ] Parse content into markdown
   - [ ] Split at H1/H2 boundaries
   - [ ] Inject CE context (breadcrumbs, headers)
   - [ ] Generate metadata
   - [ ] Write chunks to `data/chunked/`

2. **Build Aggregation Chunker** (Employment Analytics)
   - [ ] Parse CSV metadata from JSON
   - [ ] Group rows by (GEO + Metric + Year)
   - [ ] Generate summary statistics
   - [ ] Format as markdown tables
   - [ ] Write chunks to `data/chunked/`

3. **Build Legal Chunker** (Jurisprudence)
   - [ ] Parse case structure
   - [ ] Split by legal sections (Facts, Issue, Analysis, Ruling)
   - [ ] Preserve case citations
   - [ ] Link precedents
   - [ ] Write chunks to `data/chunked/`

**Deliverable:** `src/eva_rag/chunking/` module with 3 chunkers

### Phase 2.2: Quality Validation (Week 1)

**Tasks:**
- [ ] Sample 20 chunks from each source
- [ ] Manual review for CE compliance
- [ ] Check metadata completeness
- [ ] Validate chunk boundaries (no mid-sentence splits)
- [ ] Test bilingual linking (EN ↔ FR)

**Deliverable:** Quality report + approved sample chunks

### Phase 2.3: Full Production Run (Week 2)

**Tasks:**
- [ ] Run chunkers on all 1,272 documents
- [ ] Generate 1,971 chunks
- [ ] Validate chunk count per source
- [ ] Store in `data/chunked/canada_ca/`, `data/chunked/employment/`, etc.
- [ ] Generate chunking summary report

**Deliverable:** 1,971 chunks ready for Phase 3 (embedding)

---

## ✅ Approval Checklist

**Before proceeding to Phase 2 implementation, approve:**

- [ ] **Canada.ca**: Page-level + CE (breadcrumbs, navigation) → 1,257 chunks
- [ ] **Employment Analytics**: Time-series aggregation → 400 chunks
- [ ] **Jurisprudence**: Legal reasoning blocks → 24 chunks
- [ ] **IT Agreement**: Article-level + cross-references → 200 chunks
- [ ] **Total chunk count**: 1,971 chunks acceptable?
- [ ] **Total embedding cost**: $0.024 one-time (acceptable?)
- [ ] **CE/HK/WM principles**: Applied correctly?
- [ ] **File stamping**: Format approved for future docs?

**Approved By:** _________________________  
**Date:** _________________________  
**Comments:** _________________________

---

## 📎 Related Documents

- `EVA-DATA-MODEL-WITH-FASTER-PRINCIPLES.md` - Data model foundation
- `DATA-SOURCE-ORGANIZATION-STANDARD.md` - Pipeline architecture
- `EVA-DATA-PIPELINE-ROADMAP.md` - Implementation timeline
- `DATA-INVENTORY-FOR-REVIEW.md` - Raw ingestion inventory

**Next Phase:** `EVA-RAG-PHASE-3-EMBEDDING-STRATEGY-20241208.md` (after approval)

---

**🏷️ END FILE STAMP**  
**Last Updated:** 2024-12-08 18:30 EST  
**Review Status:** AWAITING MARCO APPROVAL
