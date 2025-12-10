# EVA-RAG Ingested Data Inventory

**Date:** December 8, 2024  
**Purpose:** Detailed breakdown of all ingested data for review and categorization

---

## 📊 Overview Statistics

| Category | Documents | Characters | Format | Language | Status |
|----------|-----------|------------|--------|----------|--------|
| Employment Data | 2 | 10,853 | CSV | EN | ✅ Ingested |
| Legal - Jurisprudence | 4 | 8,607 | HTML | EN | ✅ Ingested |
| Legal - AssistMe | 2 | 2,490 | HTML | EN | ✅ Ingested |
| Canada.ca - English | 632 | 5,233,538 | HTML | EN | ✅ Ingested |
| Canada.ca - French | 625 | 6,063,367 | HTML | FR | ✅ Ingested |
| Legislation | 5 | 1,922,732 | HTML/PDF/XML | EN/FR | ✅ Ingested |
| Collective Agreement | 2 | 746,250 | HTML | EN/FR | ✅ Ingested |
| **TOTAL** | **1,272** | **13,987,837** | Mixed | Bilingual | ✅ Complete |

---

## 1️⃣ Employment Analytics Data

**Use Case:** Employment Analytics for Policy Analysts  
**Client:** N/A (Public datasets)  
**Source:** Statistics Canada (sample data)  
**Location:** `data/ingested/employment/employment_data_20251208_114430.json`

### Dataset 1: Employment by Industry (14-10-0355)
- **File:** `sample_employment_by_industry.csv`
- **Rows:** 3,000
- **Columns:** 7 (REF_DATE, GEO, NAICS, Data_Type, UOM, VALUE, STATUS)
- **Characters:** 5,433
- **Date Range:** 2020-2024 (5 years, monthly)
- **Geographic Coverage:** Canada, Ontario, Quebec, British Columbia, Alberta (5 provinces)
- **Industries:** 10 NAICS categories
  - Total employed, all industries
  - Goods-producing sector
  - Manufacturing
  - Services-producing sector
  - Health care and social assistance
  - Educational services
  - Retail trade
  - Professional, scientific and technical services
  - Finance and insurance
  - Information and cultural industries

**Content Quality:**
- ✅ Clean structure
- ✅ Consistent formatting
- ✅ Complete metadata
- ⚠️ Sample data (not production-scale)

**Proposed Actions:**
- [ ] Review industry categories relevance
- [ ] Decide if real Kaggle data needed
- [ ] Define chunking strategy (by province? by industry? by time period?)
- [ ] Specify embedding approach

### Dataset 2: Labour Force Characteristics by Province (14-10-0287)
- **File:** `sample_unemployment_by_province.csv`
- **Rows:** 2,700
- **Columns:** 8 (REF_DATE, GEO, Sex, Age_group, Labour_force_characteristics, UOM, VALUE, STATUS)
- **Characters:** 5,420
- **Date Range:** 2020-2024 (5 years, monthly)
- **Geographic Coverage:** Same 5 provinces
- **Metrics:** 9 labour force characteristics
  - Population
  - Labour force
  - Employment
  - Full-time employment
  - Part-time employment
  - Unemployment
  - Participation rate
  - Unemployment rate
  - Employment rate

**Content Quality:**
- ✅ Clean structure
- ✅ Rate metrics + absolute counts
- ✅ Complete metadata
- ⚠️ Sample data (not production-scale)

**Proposed Actions:**
- [ ] Review metrics relevance
- [ ] Decide if demographic breakdowns needed (age, sex)
- [ ] Define time-series chunking strategy
- [ ] Specify query patterns to support

---

## 2️⃣ Legal Documents - Jurisprudence Client

**Use Case:** Legal Research (Case Law)  
**Client:** Jurisprudence  
**Source:** Supreme Court of Canada + local samples  
**Location:** `data/ingested/legal/jurisprudence_legal_docs_20251208_115158.json`

### Document 1: sample_case_1.html
- **Characters:** 3,252
- **Source:** `eva-orchestrator/jurispipeline/data/raw-samples/`
- **Content Type:** Supreme Court case
- **Language:** EN
- **Quality:** ✅ Good

**Visible Content Preview:**
- Case citation and metadata
- Legal issues and holdings
- Court reasoning
- Disposition

**Proposed Actions:**
- [ ] Extract case citation as metadata
- [ ] Identify legal issues for tagging
- [ ] Preserve paragraph structure for citations
- [ ] Link to related cases if available

### Document 2: sample_case_2.html
- **Characters:** 3,197
- **Source:** `eva-orchestrator/jurispipeline/data/raw-samples/`
- **Content Type:** Supreme Court case
- **Language:** EN
- **Quality:** ✅ Good

**Proposed Actions:**
- [ ] Same as Document 1
- [ ] Check for duplicate content with Document 1

### Document 3: sample_scc_case_2024_001.html
- **Characters:** 1,431
- **Title:** R. v. Smith, 2024 SCC 1
- **Topic:** Privacy rights (s. 8 Charter)
- **Content Type:** Supreme Court case (created sample)
- **Language:** EN
- **Quality:** ✅ Good structure

**Key Elements:**
- Case citation: R. v. Smith, 2024 SCC 1
- Date: January 15, 2024
- Judges listed
- Issues, Decision, Key passages, Disposition

**Proposed Actions:**
- [ ] Extract structured metadata (citation, date, judges, issues)
- [ ] Tag with legal topics (Charter, privacy, search & seizure)
- [ ] Preserve section structure (Summary, Issues, Decision, Key Passages)
- [ ] Enable citation-based retrieval

### Document 4: sample_scc_case_2024_002.html
- **Characters:** 727
- **Title:** ABC Corp. v. Minister of Finance, 2024 SCC 2
- **Topic:** Administrative law (tax assessments)
- **Content Type:** Supreme Court case (created sample)
- **Language:** EN
- **Quality:** ✅ Good structure

**Key Elements:**
- Case citation: ABC Corp. v. Minister of Finance, 2024 SCC 2
- Date: March 8, 2024
- Topic: Reasonableness standard, taxation

**Proposed Actions:**
- [ ] Extract structured metadata
- [ ] Tag with legal topics (administrative law, taxation, judicial review)
- [ ] Cross-reference with related cases

**Client Metadata Applied:**
```json
{
  "client": "jurisprudence",
  "use_case": "Legal Research",
  "document_type": "case_law",
  "jurisdiction": "Canada - Supreme Court",
  "target_users": "Legal researchers, Policy analysts",
  "content_focus": "Supreme Court decisions, Case law precedents"
}
```

**Overall Assessment:**
- ✅ Clean HTML structure
- ✅ Consistent formatting
- ✅ Client-specific metadata applied
- ⚠️ Small sample size (4 cases)
- ⏳ Need more real case data for production

---

## 3️⃣ Legal Documents - AssistMe Client

**Use Case:** Legal Guidance (FAQ & Guides)  
**Client:** AssistMe  
**Source:** Created samples  
**Location:** `data/ingested/legal/assistme_legal_docs_20251208_115158.json`

### Document 1: employment_standards_guide.html
- **Characters:** 1,078
- **Title:** Employment Standards - Quick Reference Guide
- **Content Type:** Legal guidance document
- **Language:** EN
- **Topics Covered:**
  - Hours of work (standard, maximum, overtime)
  - Minimum wage ($17.30/hr for 2024)
  - Vacation entitlements (2-3 weeks)
  - Statutory holidays (10 paid days)
  - Termination notice (tiered by tenure)
  - Resources and contact info

**Content Quality:**
- ✅ Well-structured (headings, lists)
- ✅ Practical information
- ✅ Current rates and rules
- ✅ Clear formatting

**Proposed Actions:**
- [ ] Extract specific values as metadata (min wage, vacation rates)
- [ ] Tag with topics (hours, wages, holidays, termination)
- [ ] Enable FAQ-style retrieval
- [ ] Link to relevant legislation (Employment Standards Act)
- [ ] Update rates annually

### Document 2: workplace_rights_faq.html
- **Characters:** 1,412
- **Title:** Workplace Rights - Frequently Asked Questions
- **Content Type:** FAQ document
- **Language:** EN
- **Topics Covered:**
  - Overtime pay entitlement
  - Schedule change notice requirements (96 hours)
  - Discrimination complaints (CHRC)
  - Maternity/parental leave (17 + 63 weeks)
  - Termination without cause
  - Workplace safety rights (3 rights: refuse, know, participate)

**Content Structure:**
- Q&A format (6 questions)
- Clear questions with detailed answers
- References to legislation and agencies
- Practical guidance

**Proposed Actions:**
- [ ] Extract Q&A pairs as separate chunks
- [ ] Tag each Q&A with topic
- [ ] Enable question-based retrieval
- [ ] Cross-reference with employment_standards_guide
- [ ] Link to complaint processes

**Client Metadata Applied:**
```json
{
  "client": "assistme",
  "use_case": "Legal Guidance",
  "document_type": "guidance",
  "jurisdiction": "Canada - Federal",
  "target_users": "Legal staff, Citizens, Service providers",
  "content_focus": "Legal guidance, FAQs, Policy explanations"
}
```

**Overall Assessment:**
- ✅ User-friendly content
- ✅ Practical, actionable information
- ✅ FAQ format ideal for RAG
- ✅ Client-specific metadata applied
- ⏳ Need more topic coverage (health & safety, discrimination, contracts, etc.)

---

## 4️⃣ Canada.ca Government Information - English

**Use Case:** Government Services Assistant  
**Client:** N/A (Public service)  
**Source:** https://www.canada.ca/en.html (2-layer crawl)  
**Location:** `data/ingested/canada_ca/canada_ca_en_20251208_115223.json`

### Overview
- **Pages:** 632
- **Characters:** 5,233,538 (~5.2 MB)
- **Language:** EN
- **Crawl Depth:** 2 layers (homepage → direct links → their links)
- **Domain:** canada.ca only

### Top Sections Crawled
Based on URL patterns, primary sections include:

1. **/services/jobs/** - Employment and workplace
   - Job search resources
   - Training programs
   - Workplace rights
   - EI benefits
   
2. **/services/immigration-citizenship/** - Immigration
   - Passports
   - Visit Canada
   - Citizenship applications
   - Refugee services
   
3. **/services/business/** - Business services
   - Starting a business
   - Grants and funding
   - Regulations
   - Export/import
   
4. **/services/benefits/** - Benefits and programs
   - EI benefits
   - Public pensions (CPP, OAS)
   - Disability benefits
   - Dental care plan
   
5. **/services/health/** - Health services
   - Public health
   - Diseases and conditions
   - Healthy living
   - Food and nutrition
   
6. **/services/taxes/** - Tax information
   - Personal income tax
   - Business taxes
   - Filing deadlines
   - Tax credits
   
7. **/services/environment/** - Environment
   - Climate change
   - Conservation
   - Pollution
   - Weather
   
8. **/services/defence/** - National security
   - Military
   - Veterans services
   - Emergency preparedness
   
9. **/government/dept/** - Departments
   - ~62 department pages
   - Contact information
   - Organizational structure
   
10. **/contact/** - Contact government
    - ~57 contact pages
    - Service delivery channels

### Content Characteristics
- ✅ Clean HTML structure
- ✅ Consistent government formatting
- ✅ Bilingual metadata (title, description)
- ✅ Navigation preserved
- ⚠️ May contain duplicate navigation elements
- ⚠️ May contain non-content (headers, footers, menus)

### Proposed Actions
- [ ] **Content Cleaning:** Remove navigation, headers, footers
- [ ] **Deduplication:** Identify and merge duplicate pages
- [ ] **Section Tagging:** Tag each page with primary service area
- [ ] **Depth Analysis:** Analyze content quality by crawl depth (0, 1, 2)
- [ ] **Link Extraction:** Extract internal links for relationship mapping
- [ ] **Form Detection:** Identify pages with forms/applications
- [ ] **Contact Info:** Extract service contact information
- [ ] **Chunking Strategy:** Define by section (services, forms, policies)

### Known Issues to Address
- [ ] Homepage content may be minimal (navigation-heavy)
- [ ] Department listing pages may be redundant
- [ ] Contact pages may have similar structure
- [ ] Some pages may be seasonal/outdated
- [ ] Breadcrumb navigation needs removal

---

## 5️⃣ Canada.ca Government Information - French

**Use Case:** Government Services Assistant  
**Client:** N/A (Public service)  
**Source:** https://www.canada.ca/fr.html (2-layer crawl)  
**Location:** `data/ingested/canada_ca/canada_ca_fr_20251208_115223.json`

### Overview
- **Pages:** 625
- **Characters:** 6,063,367 (~6.1 MB)
- **Language:** FR
- **Crawl Depth:** 2 layers
- **Domain:** canada.ca only

### Comparison with English
- **Page Count:** 625 FR vs 632 EN (98.9% parity)
- **Content Size:** 6.1 MB FR vs 5.2 MB EN (17% more characters in French)
- **Coverage:** Parallel structure to English

### Top Sections Crawled (French equivalents)
1. **/services/emplois/** - Emploi et milieu de travail
2. **/services/immigration-citoyennete/** - Immigration et citoyenneté
3. **/services/entreprises/** - Entreprises et industrie
4. **/services/prestations/** - Prestations
5. **/services/sante/** - Santé
6. **/services/impots/** - Impôts
7. **/services/environnement/** - Environnement
8. **/services/defense/** - Défense
9. **/gouvernement/min/** - Ministères
10. **/contact/** - Coordonnées

### Bilingual Quality Assessment
- ✅ Near-complete parity (625 FR vs 632 EN)
- ✅ Parallel URL structure
- ✅ Equivalent content coverage
- ⚠️ Slightly longer French text (normal for FR translation)

### Proposed Actions
- [ ] **Bilingual Alignment:** Map EN pages to FR equivalents
- [ ] **Translation Quality:** Verify content accuracy
- [ ] **Terminology Consistency:** Check for consistent FR terminology
- [ ] **Same Cleaning Rules:** Apply identical cleaning to both languages
- [ ] **Bilingual Chunking:** Align chunks for cross-language retrieval
- [ ] **Language Detection:** Verify language tagging accuracy

---

## 6️⃣ Legislation - Employment Equity Act

**Use Case:** Legal Reference / HR Compliance  
**Client:** N/A (Public legislation)  
**Source:** laws-lois.justice.gc.ca/eng/acts/e-5.6/  
**Location:** `data/ingested/specific_urls/specific_urls_20251208_132325.json`

### Document 1: Employment Equity Act - HTML (EN)
- **URL:** https://laws-lois.justice.gc.ca/eng/acts/e-5.6/page-1.html
- **Characters:** 47,235
- **Format:** HTML
- **Language:** EN
- **Act Code:** S.C. 1995, c. 44

**Content Structure:**
- Preamble
- Purpose section
- Definitions
- Part I: Employment Equity
- Part II: Implementation
- Part III: Enforcement
- Schedules

**Proposed Actions:**
- [ ] Extract section numbers and titles as metadata
- [ ] Tag with topics (equity, employment, designated groups)
- [ ] Enable section-based retrieval
- [ ] Cross-reference with regulations
- [ ] Link to related acts

### Document 2: Employment Equity Act - HTML (FR)
- **URL:** https://laws-lois.justice.gc.ca/fra/lois/e-5.6/page-1.html
- **Characters:** 50,224
- **Format:** HTML
- **Language:** FR
- **Act Code:** L.C. 1995, ch. 44

**Bilingual Quality:**
- ✅ Official translation
- ✅ Parallel structure to English
- ✅ Slightly longer (normal for French)

**Proposed Actions:**
- [ ] Align with English version by section
- [ ] Same tagging and metadata as English
- [ ] Enable bilingual legal search

### Document 3: Employment Equity Act - PDF (Bilingual)
- **URL:** https://laws-lois.justice.gc.ca/PDF/E-5.6.pdf
- **Characters:** 1,824,831 (~1.8 MB)
- **Format:** PDF
- **Language:** EN/FR (bilingual document)

**Content Characteristics:**
- ✅ Official consolidation
- ✅ Both languages in one document
- ⚠️ May include cover page, headers, page numbers
- ⚠️ PDF extraction may have formatting artifacts

**Proposed Actions:**
- [ ] Clean PDF extraction artifacts (headers, footers, page numbers)
- [ ] Separate EN and FR sections if possible
- [ ] Compare with HTML versions for accuracy
- [ ] Use as reference, prefer HTML for indexing

### Document 4: Employment Equity Act - XML (EN)
- **URL:** https://laws-lois.justice.gc.ca/eng/XML/E-5.6.xml
- **Characters:** 221
- **Format:** XML
- **Language:** EN

**Note:** Very short content suggests possible redirect or metadata file, not full act text.

**Proposed Actions:**
- [ ] Investigate XML content
- [ ] Verify if structural metadata only
- [ ] May not need for RAG if only metadata

### Document 5: Employment Equity Act - XML (FR)
- **URL:** https://laws-lois.justice.gc.ca/fra/XML/E-5.6.xml
- **Characters:** 221
- **Format:** XML
- **Language:** FR

**Same as EN XML** - likely metadata only.

**Overall Assessment:**
- ✅ Official government legislation
- ✅ Multiple formats available
- ✅ Bilingual coverage
- ⚠️ PDF needs cleaning
- ⚠️ XML may not be useful (too short)
- ✅ HTML versions are best for RAG

---

## 7️⃣ Collective Agreement - Information Technology (IT) Group

**Use Case:** HR / Labour Relations / Compensation  
**Client:** N/A (Public sector HR)  
**Source:** Treasury Board Secretariat  
**Location:** `data/ingested/specific_urls/specific_urls_20251208_132325.json`

### Document 1: IT Collective Agreement - HTML (EN)
- **URL:** https://www.canada.ca/en/treasury-board-secretariat/topics/pay/collective-agreements/it.html
- **Characters:** 346,203 (~346 KB)
- **Format:** HTML
- **Language:** EN

**Content Coverage:**
- Agreement parties (Treasury Board + ACFO)
- Effective dates
- Pay rates and scales
- Working conditions
- Benefits
- Leave provisions
- Grievance procedures
- Duration and renewal

**Proposed Actions:**
- [ ] Extract pay scale tables
- [ ] Tag sections by topic (compensation, benefits, leave, etc.)
- [ ] Extract effective dates as metadata
- [ ] Enable query by job classification
- [ ] Cross-reference with employment standards

### Document 2: IT Collective Agreement - HTML (FR)
- **URL:** https://www.canada.ca/fr/secretariat-conseil-tresor/sujets/remuneration/conventions-collectives/it.html
- **Characters:** 400,047 (~400 KB)
- **Format:** HTML
- **Language:** FR

**Bilingual Quality:**
- ✅ Official translation
- ✅ Complete parity with English
- ✅ Slightly longer in French (normal)

**Proposed Actions:**
- [ ] Align with English version by section
- [ ] Extract same structured data (pay scales, dates)
- [ ] Enable bilingual compensation queries

**Overall Assessment:**
- ✅ Comprehensive collective agreement
- ✅ Large, detailed document
- ✅ Structured content (sections, tables)
- ✅ Bilingual parity
- ✅ Official government source
- ⚠️ May contain large tables requiring special handling
- ⚠️ Pay scales need structured extraction

---

## 🎯 Segregation & Classification

### By Use Case
| Use Case | Documents | Characters | Priority |
|----------|-----------|------------|----------|
| Government Services | 1,257 | 11,296,905 | **HIGH** |
| Legislation | 5 | 1,922,732 | **HIGH** |
| HR / Labour | 2 | 746,250 | **MEDIUM** |
| Legal Research | 4 | 8,607 | **MEDIUM** |
| Legal Guidance | 2 | 2,490 | **LOW** |
| Employment Analytics | 2 | 10,853 | **LOW** |

### By Client (Multi-Tenant)
| Client | Documents | Use Case | Metadata Tag |
|--------|-----------|----------|--------------|
| **Jurisprudence** | 4 | Legal Research | `client: jurisprudence` |
| **AssistMe** | 2 | Legal Guidance | `client: assistme` |
| **Public / Unassigned** | 1,266 | Various | No client tag |

### By Language
| Language | Documents | Characters | % of Total |
|----------|-----------|------------|------------|
| English | ~640 | ~7.4 MB | 53% |
| French | ~627 | ~6.5 MB | 46% |
| Bilingual (PDF) | 1 | ~1.8 MB (counted above) | N/A |

### By Format
| Format | Documents | Use Case |
|--------|-----------|----------|
| HTML | 1,265 | Web pages, legal docs, guides |
| CSV | 2 | Employment datasets |
| PDF | 1 | Legislation (bilingual) |
| XML | 2 | Legislation metadata (?) |

### By Content Type
| Type | Documents | Characteristics |
|------|-----------|-----------------|
| **Web Pages** | 1,257 | Government services, navigation-heavy |
| **Legal Cases** | 4 | Structured, citations, precedents |
| **Guidance Docs** | 2 | FAQ format, practical advice |
| **Legislation** | 5 | Formal, sectioned, referenced |
| **Collective Agreement** | 2 | Detailed, tables, schedules |
| **Datasets** | 2 | Tabular, time-series, statistics |

---

## 📋 Next Steps - Review Checklist

### Marco's Review Tasks
- [ ] **Verify Use Case Assignments** - Are documents assigned to correct use cases?
- [ ] **Confirm Client Segregation** - Is Jurisprudence vs AssistMe separation correct?
- [ ] **Set Priorities** - Which use cases to process first?
- [ ] **Identify Missing Content** - What additional data sources needed?
- [ ] **Define Chunking Strategy** - How to split each content type?
- [ ] **Approve Cleaning Rules** - What to remove/keep in each category?
- [ ] **Metadata Enrichment** - What additional metadata to extract?
- [ ] **Cross-References** - Which documents should link to each other?

### Analysis Phase (Next)
After your review and updates, we'll proceed with:
1. **Content Quality Analysis** - Detailed examination of each document type
2. **Cleaning Proposal** - Specific rules for each category
3. **Transformation Plan** - Chunking strategy, metadata extraction
4. **Approval Document** - Formal proposal for your sign-off

---

**Instructions for Marco:**
1. Review each section above
2. Update priorities, classifications, proposed actions
3. Add notes in each section about specific requirements
4. Flag any content that should be excluded
5. Identify gaps or additional sources needed
6. Save and return for analysis phase

---

## 🗂️ New Organization System

All ingested data is now being organized using the **P02-ready data source structure**:

### Location
```
data-sources/
├── _templates/              # Templates for business analysts
├── jurisprudence/           # ✅ COMPLETE EXAMPLE
│   ├── requirements.json    # P02-consumable requirements
│   ├── constraints.json     # Safety boundaries  
│   ├── ingestion-spec.md    # Human-readable blueprint
│   ├── config/
│   │   └── pipeline-config.yaml
│   ├── discover/
│   │   └── sources.yaml
│   ├── normalize/
│   │   └── metadata_schema.json
│   └── publish/
│       └── chunking_strategy.yaml
├── canada-ca/               # TODO: Migrate from ingested data
├── employment/              # TODO: Migrate from ingested data
└── assistme/                # TODO: Migrate from ingested data
```

### Benefits
- ✅ **Agent-ready:** P02 can auto-generate pipelines from requirements.json
- ✅ **Business-friendly:** Analysts use simple templates to request ingestion
- ✅ **Standardized:** Same structure for all 1,272+ documents
- ✅ **Scalable:** Easy to add new sources (100+ planned)
- ✅ **Discoverable:** Clear documentation and metadata

### Documentation
- **[Organization Standard](DATA-SOURCE-ORGANIZATION-STANDARD.md)** - Complete specification
- **[Jurisprudence Example](../data-sources/jurisprudence/)** - Working implementation
- **[Pipeline Architecture](../data-sources/jurisprudence/ingestion-spec.md)** - Discover → Fetch → Normalize → Publish

### Next Steps
1. Review jurisprudence example as template
2. Decide which data sources to migrate first
3. Create requirements.json for canada-ca, employment, assistme
4. Generate pipelines using P02 pattern

---

**File Location:** `docs/DATA-INVENTORY-FOR-REVIEW.md`
