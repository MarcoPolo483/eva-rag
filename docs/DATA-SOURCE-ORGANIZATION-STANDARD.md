# EVA-RAG Data Source Organization Standard

**Version:** 1.0  
**Date:** December 8, 2024  
**Purpose:** Define the canonical structure for organizing data sources, ingestion specifications, and business analyst prompts in EVA-RAG

---

## 🎯 Vision

Enable **business analysts** to define data ingestion requirements using **structured, agent-ready formats** that can be automatically processed by EVA's orchestration layer (P02 Requirements Engine) to generate complete ingestion pipelines.

### Inspired By

1. **Jurispipeline Architecture:** Discover → Fetch → Normalize → Publish
2. **P02 Requirements Pattern:** JSON-based, agent-consumable specifications
3. **Multi-tenant Design:** Client-specific metadata and segregation

---

## 📁 Directory Structure

```
eva-rag/
├── data-sources/                    # Root for all data source definitions
│   ├── _templates/                  # Templates for business analysts
│   │   ├── ingestion-requirements.json
│   │   ├── ingestion-prompt.md
│   │   └── README.md
│   │
│   ├── jurisprudence/               # Example: Legal research client
│   │   ├── requirements.json        # P02-style requirements
│   │   ├── constraints.json         # Safety boundaries
│   │   ├── ingestion-spec.md        # Detailed specification
│   │   ├── config/
│   │   │   └── pipeline-config.yaml
│   │   ├── discover/                # Discovery logic (URLs, APIs, files)
│   │   │   ├── sources.yaml
│   │   │   └── discovery_rules.py
│   │   ├── fetch/                   # Fetching configuration
│   │   │   ├── rate_limits.yaml
│   │   │   └── auth_config.yaml
│   │   ├── normalize/               # Transformation rules
│   │   │   ├── metadata_schema.json
│   │   │   ├── cleaning_rules.yaml
│   │   │   └── parsers/
│   │   ├── publish/                 # Output configuration
│   │   │   ├── chunking_strategy.yaml
│   │   │   ├── vector_config.yaml
│   │   │   └── index_schema.json
│   │   ├── scripts/                 # Generated/manual scripts
│   │   │   ├── ingest_jurisprudence.py
│   │   │   └── validate_ingestion.py
│   │   └── docs/                    # Documentation
│   │       ├── overview.md
│   │       └── troubleshooting.md
│   │
│   ├── canada-ca/                   # Example: Government services
│   │   ├── requirements.json
│   │   ├── constraints.json
│   │   └── ... (same structure)
│   │
│   ├── employment-analytics/        # Example: Statistics datasets
│   │   └── ...
│   │
│   └── assistme/                    # Example: Legal guidance client
│       └── ...
│
├── data/                            # Actual data (existing)
│   ├── raw/                         # Raw source data
│   │   ├── jurisprudence/
│   │   ├── canada-ca/
│   │   └── ...
│   ├── processed/                   # Cleaned/transformed
│   └── ingested/                    # RAG-ready (existing)
│
└── src/eva_rag/
    └── pipelines/                   # Auto-generated pipeline code
        ├── jurisprudence_pipeline.py
        ├── canada_ca_pipeline.py
        └── ...
```

---

## 📋 Core Files in Each Data Source

### 1. `requirements.json` — P02-Ready Requirements

**Purpose:** Machine-readable specification for automated pipeline generation

**Schema:**
```json
{
  "project_name": "string",
  "project_space": "string",
  "project_owner": "string",
  "classification": "string",
  "objective": "string",
  "expected_outputs": ["string"],
  
  "data_sources": [
    {
      "name": "string",
      "source_url_en": "string",
      "source_url_fr": "string (optional)",
      "source_type": "HTML|PDF|API|CSV|Excel|XML",
      "update_frequency": "Daily|Weekly|Monthly|One-time",
      "expected_volume": "string"
    }
  ],
  
  "document_formats": ["string"],
  "metadata_required": ["string"],
  
  "rag_pipeline_requirements": {
    "chunking": {
      "method": "semantic|structural|fixed",
      "max_tokens": "number",
      "overlap": "number",
      "structure_awareness": ["string"]
    },
    "embedding_model": "text-embedding-3-small|text-embedding-3-large",
    "vector_store": "Azure AI Search|Qdrant",
    "hybrid_search": "boolean",
    "filters": ["string"],
    "citations_mandatory": "boolean"
  },
  
  "language_requirements": {
    "bilingual_output": "boolean",
    "detect_language": "boolean",
    "link_parallel_docs": "boolean",
    "normalize_accents": "boolean"
  },
  
  "compliance": {
    "privacy": "string",
    "security": "string",
    "a11y": "string",
    "ola": "string"
  },
  
  "success_criteria": ["string"]
}
```

**Example:** See `data-sources/jurisprudence/requirements.json`

---

### 2. `constraints.json` — Safety Boundaries

**Purpose:** Define autonomy level and allowed/disallowed operations

**Schema:**
```json
{
  "autonomy_level": "L1_supervised|L2_bounded|L3_autonomous|L4_full",
  "allowed_tools": ["string"],
  "disallowed_actions": ["string"],
  "mandatory_safe_steps": ["string"],
  "human_approval_required": ["string"],
  "rollback_strategy": "string"
}
```

**Example:**
```json
{
  "autonomy_level": "L2_bounded",
  "allowed_tools": [
    "html_extractor",
    "pdf_extractor",
    "metadata_parser",
    "semantic_chunker",
    "vector_uploader"
  ],
  "disallowed_actions": [
    "no_external_internet",
    "no_deletion_of_source_data",
    "no_policy_changes",
    "no_legal_interpretation"
  ],
  "mandatory_safe_steps": [
    "retrieval_only",
    "citation_enforcement",
    "human_review_before_publish"
  ]
}
```

---

### 3. `ingestion-spec.md` — Human-Readable Blueprint

**Purpose:** Detailed specification for developers and analysts

**Template:**
```markdown
# [Data Source Name] Ingestion Specification

## Overview
- **Client:** Name
- **Use Case:** Primary use case
- **Priority:** HIGH|MEDIUM|LOW
- **Status:** DRAFT|APPROVED|IN-PROGRESS|COMPLETE

## Data Sources
### Source 1: [Name]
- **URL:** https://...
- **Type:** HTML|PDF|API|...
- **Language:** EN|FR|Bilingual
- **Update Frequency:** Daily|Weekly|...
- **Authentication:** None|API Key|OAuth|...

## Pipeline Stages

### 1. Discover
- **Method:** Web crawl|API query|File scan
- **Entry Points:** [URLs or paths]
- **Depth:** [Number of levels]
- **Filters:** [Inclusion/exclusion rules]

### 2. Fetch
- **Rate Limiting:** [Requests per second]
- **Retry Strategy:** [Max retries, backoff]
- **Caching:** [Yes/No]
- **Authentication:** [Details]

### 3. Normalize
- **HTML Parsing:** [BeautifulSoup selectors]
- **PDF Extraction:** [PyMuPDF, OCR settings]
- **Metadata Extraction:** [Fields to extract]
- **Content Cleaning:** [Rules]
- **Language Detection:** [Method]

### 4. Publish
- **Chunking:** [Strategy, size, overlap]
- **Embeddings:** [Model, dimensions]
- **Vector Store:** [Azure AI Search, index name]
- **Metadata Schema:** [Required fields]
- **Output Format:** [JSON structure]

## Metadata Schema
```json
{
  "required": ["field1", "field2"],
  "optional": ["field3"],
  "types": { ... }
}
```

## Quality Checks
- [ ] Completeness: All expected documents ingested
- [ ] Accuracy: Metadata correctly extracted
- [ ] Bilingual: EN/FR documents linked
- [ ] Citations: Source URLs preserved
- [ ] Privacy: No PII detected

## Success Criteria
1. [Criterion 1]
2. [Criterion 2]
```

---

### 4. `config/pipeline-config.yaml` — Pipeline Configuration

**Purpose:** Runtime configuration for the ingestion pipeline

**Example:**
```yaml
pipeline:
  name: jurisprudence-scc
  version: "1.0.0"
  description: "Supreme Court of Canada ingestion"

discover:
  source: "scc-lexum"
  mode: "online"  # online|offline|hybrid
  endpoint: "https://scc-csc.lexum.com/api"
  rate_limit_per_second: 2

fetch:
  mode: "online"
  timeout_seconds: 30
  max_retries: 3
  backoff_factor: 2
  user_agent: "EVA-RAG/1.0"

normalize:
  parser: "html"
  extract_citations: true
  extract_metadata: true
  detect_language: true
  remove_navigation: true
  remove_headers_footers: true

publish:
  filesystem:
    enabled: true
    output_dir: "data/processed/jurisprudence"
  
  vector_chunks:
    enabled: true
    chunk_size: 800
    chunk_overlap: 120
  
  azure_search:
    enabled: true
    index_name: "eva-jurisprudence-prod"
    create_if_missing: true

logging:
  level: "INFO"
  file: "logs/jurisprudence_pipeline.log"
```

---

### 5. `discover/sources.yaml` — Source Catalog

**Purpose:** Catalog of all source URLs, files, or APIs

**Example:**
```yaml
sources:
  supreme_court:
    name: "Supreme Court of Canada"
    type: "web_crawl"
    entry_points:
      - url: "https://www.scc-csc.ca/judgments-jugements/index-eng.aspx"
        language: "en"
      - url: "https://www.scc-csc.ca/jugements-judgments/index-fra.aspx"
        language: "fr"
    crawl_depth: 2
    include_patterns:
      - "/judgments-jugements/*/index-eng.aspx"
      - "/jugements-judgments/*/index-fra.aspx"
    exclude_patterns:
      - "/contact/"
      - "/about/"
    
  federal_court:
    name: "Federal Court"
    type: "api"
    endpoint: "https://decisions.fct-cf.gc.ca/api/v1/decisions"
    authentication:
      type: "api_key"
      key_env_var: "FC_API_KEY"
    pagination:
      type: "offset"
      page_size: 100
```

---

### 6. `normalize/metadata_schema.json` — Metadata Schema

**Purpose:** Define required and optional metadata fields

**Example:**
```json
{
  "schema_version": "1.0",
  "required_fields": [
    {
      "name": "tribunal",
      "type": "string",
      "description": "Name of the court or tribunal",
      "examples": ["Supreme Court of Canada", "Federal Court"]
    },
    {
      "name": "case_name",
      "type": "string",
      "description": "Full case name",
      "examples": ["R. v. Smith", "ABC Corp. v. Minister"]
    },
    {
      "name": "docket_number",
      "type": "string",
      "pattern": "^\\d{5}$",
      "description": "Court docket number"
    },
    {
      "name": "decision_date",
      "type": "date",
      "format": "YYYY-MM-DD",
      "description": "Date decision was rendered"
    },
    {
      "name": "language",
      "type": "string",
      "enum": ["en", "fr"],
      "description": "Document language"
    },
    {
      "name": "url_source",
      "type": "url",
      "description": "Original source URL"
    }
  ],
  "optional_fields": [
    {
      "name": "hearing_date",
      "type": "date",
      "format": "YYYY-MM-DD"
    },
    {
      "name": "judge_panel",
      "type": "array",
      "items": "string",
      "description": "List of judges"
    },
    {
      "name": "legal_issues",
      "type": "array",
      "items": "string",
      "description": "Main legal issues addressed"
    },
    {
      "name": "linked_document_fr",
      "type": "url",
      "description": "Link to French version"
    },
    {
      "name": "linked_document_en",
      "type": "url",
      "description": "Link to English version"
    }
  ],
  "computed_fields": [
    {
      "name": "hash_fingerprint",
      "type": "string",
      "description": "SHA-256 hash of content",
      "computed_from": "content"
    },
    {
      "name": "ingestion_timestamp",
      "type": "datetime",
      "description": "When document was ingested",
      "auto_generated": true
    },
    {
      "name": "chunk_count",
      "type": "integer",
      "description": "Number of chunks created",
      "auto_generated": true
    }
  ]
}
```

---

### 7. `publish/chunking_strategy.yaml` — Chunking Rules

**Purpose:** Define how documents are split for RAG

**Example:**
```yaml
chunking:
  primary_strategy: "semantic"
  fallback_strategy: "structural"
  
  semantic_chunking:
    model: "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: 0.7
    max_tokens: 800
    min_tokens: 100
    
  structural_chunking:
    preserve_boundaries:
      - "heading"
      - "paragraph"
      - "table"
      - "list"
    hierarchy_aware: true
    
  overlap:
    tokens: 120
    method: "sliding_window"
    
  special_handling:
    tables:
      method: "preserve_structure"
      format: "markdown"
    
    citations:
      preserve_in_chunk: true
      link_to_source: true
    
    headings:
      include_in_chunk: true
      use_as_anchor: true

chunk_metadata:
  include:
    - "chunk_index"
    - "total_chunks"
    - "heading_path"
    - "section_type"
    - "parent_document_id"
    - "language"
```

---

## 🎨 Template for Business Analysts

### File: `data-sources/_templates/ingestion-prompt.md`

Business analysts can copy this template and fill it out to request a new ingestion pipeline.

```markdown
# Data Ingestion Request

**Submitted By:** [Your Name]  
**Date:** [YYYY-MM-DD]  
**Priority:** HIGH | MEDIUM | LOW  
**Target Completion:** [YYYY-MM-DD]

---

## 1. Project Information

**Project Name:** [e.g., "Jurisprudence Legal Research"]  
**Client/Stakeholder:** [e.g., "AICOE Knowledge Management Team"]  
**Use Case:** [e.g., "Enable legal researchers to find relevant case law"]

**Business Objective:**  
[Describe in 2-3 sentences what business problem this solves]

---

## 2. Data Sources

### Source 1: [Name]
- **URL or Location:** https://...
- **Type:** Web pages | PDF documents | Excel files | API | Database | ...
- **Language:** English | French | Bilingual
- **How Often Updated:** Daily | Weekly | Monthly | One-time
- **Estimated Volume:** [e.g., "20,000 documents", "5 GB of PDFs"]
- **Access Requirements:** Public | API Key | Login | Database credentials

### Source 2: [Name] (if applicable)
[Same structure as above]

---

## 3. What Should Be Extracted

### Required Information (Must Have)
- [ ] [Field 1, e.g., "Case name"]
- [ ] [Field 2, e.g., "Decision date"]
- [ ] [Field 3, e.g., "Full text"]
- [ ] ...

### Optional Information (Nice to Have)
- [ ] [Field 1, e.g., "Judge names"]
- [ ] [Field 2, e.g., "Keywords"]
- [ ] ...

### Content to Exclude
- [ ] [e.g., "Navigation menus"]
- [ ] [e.g., "Advertisements"]
- [ ] ...

---

## 4. Language Requirements

- [ ] English only
- [ ] French only
- [ ] Bilingual (both languages needed)
- [ ] Automatically detect language
- [ ] Link English and French versions of same document

---

## 5. How Should Data Be Organized

**Chunking Preference:**
- [ ] By document section (recommended for long documents)
- [ ] Fixed size chunks (simpler, faster)
- [ ] Intelligent/semantic chunks (best for Q&A)

**Chunk Size:** [e.g., "500-1000 words per chunk"]

**Special Handling:**
- [ ] Preserve tables
- [ ] Keep citations linked
- [ ] Maintain heading hierarchy
- [ ] Extract images (if applicable)

---

## 6. Security & Privacy

**Data Classification:** Public | Protected A | Protected B  
**Privacy Concerns:** [Any personal information that must be redacted?]  
**Access Control:** [Who should be able to access this data?]

---

## 7. Success Criteria

What does "good" look like for this ingestion?

- [ ] [Criterion 1, e.g., "95% of documents successfully ingested"]
- [ ] [Criterion 2, e.g., "All metadata fields populated"]
- [ ] [Criterion 3, e.g., "English and French versions linked"]
- [ ] ...

---

## 8. Timeline & Resources

**Target Start Date:** [YYYY-MM-DD]  
**Target Completion:** [YYYY-MM-DD]  
**Recurring Ingestion:** Yes | No  
**If Yes, Frequency:** Daily | Weekly | Monthly

**Resources Available:**
- [ ] API credentials (if needed)
- [ ] Database access (if needed)
- [ ] Sample documents for testing
- [ ] Subject matter expert for validation

---

## 9. Additional Notes

[Any other context, constraints, or requirements]

---

## Submission

Once completed, save this file as:
```
data-sources/[project-name]/ingestion-request.md
```

Then notify the EVA-RAG team via:
- Slack: #eva-rag-ingestion
- Email: eva-rag-team@example.gc.ca
- GitHub Issue: [Create issue in eva-rag repo]

The team will review and create the technical specification within 2 business days.
```

---

## 🔄 Workflow: From Analyst Prompt to Pipeline

### Step 1: Business Analyst Fills Template
- Copies `_templates/ingestion-prompt.md`
- Fills in business requirements
- Submits to EVA-RAG team

### Step 2: Technical Team Creates Specification
- Creates folder: `data-sources/[project-name]/`
- Generates `requirements.json` (P02-ready)
- Writes `ingestion-spec.md` (detailed blueprint)
- Defines `constraints.json` (safety boundaries)

### Step 3: P02 Agent Generates Pipeline
- Reads `requirements.json`
- Creates folder structure
- Generates pipeline code in `src/eva_rag/pipelines/`
- Generates configuration files
- Creates validation scripts

### Step 4: Human Review & Approval
- P03 Reviewer validates generated code
- Security team reviews constraints
- Business analyst confirms specifications
- Approvals documented

### Step 5: Pipeline Execution
- Manual test run with sample data
- Validation against success criteria
- Production run (if test passes)
- Monitoring and logging

### Step 6: Continuous Updates
- Scheduled runs (if recurring)
- Monitoring for source changes
- Incremental ingestion
- Quality metrics tracking

---

## 📊 Example: Jurisprudence Data Source

See complete example in:
```
data-sources/jurisprudence/
├── requirements.json              ✅ P02-ready requirements
├── constraints.json               ✅ Safety boundaries
├── ingestion-spec.md              ✅ Detailed blueprint
├── config/
│   └── pipeline-config.yaml       ✅ Runtime configuration
├── discover/
│   └── sources.yaml               ✅ Source catalog
├── normalize/
│   ├── metadata_schema.json       ✅ Metadata definition
│   └── cleaning_rules.yaml        ✅ Content cleaning rules
├── publish/
│   ├── chunking_strategy.yaml     ✅ Chunking configuration
│   └── vector_config.yaml         ✅ Vector store settings
└── docs/
    └── overview.md                ✅ Human-readable docs
```

---

## 🎯 Benefits of This Organization

### For Business Analysts
- ✅ Simple template to request ingestion
- ✅ No technical knowledge required
- ✅ Clear expectations and timeline

### For Developers
- ✅ Standardized structure across all data sources
- ✅ Automated pipeline generation via P02
- ✅ Reusable components and patterns
- ✅ Easy to maintain and update

### For Operations
- ✅ Consistent monitoring and logging
- ✅ Clear ownership and documentation
- ✅ Audit trail for compliance
- ✅ Scalable to 100+ data sources

### For Security
- ✅ Defined constraints per source
- ✅ Privacy controls built-in
- ✅ Access control enforcement
- ✅ Compliance with GC standards

---

## 🚀 Next Steps

1. **Create Template Library:** Build `data-sources/_templates/` with all files
2. **Migrate Existing Sources:** Move current ingestion scripts to new structure
3. **Build P02 Integration:** Connect requirements.json → pipeline generation
4. **Document for Analysts:** Create user guide and video tutorial
5. **Pilot with Jurisprudence:** Migrate jurispipeline as proof-of-concept

---

**Status:** DRAFT — Ready for Marco's review and approval
