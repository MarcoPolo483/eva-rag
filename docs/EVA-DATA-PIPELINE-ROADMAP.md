# EVA Data Pipeline - Implementation Roadmap

**Start Date:** December 9, 2024  
**Target Launch:** January 31, 2025 (8 weeks)  
**Status:** APPROVED - READY TO EXECUTE  
**Owner:** EVA-RAG Team + P02 Agent

---

## 🎯 Implementation Phases

### ✅ Phase 0: Foundation (Week 0) — COMPLETE

**Status:** ✅ COMPLETE (December 8, 2024)

**Deliverables:**
- ✅ Architecture defined (Discover → Fetch → Normalize → Publish)
- ✅ Data source structure created (`data-sources/`)
- ✅ Jurisprudence complete example (10 files)
- ✅ Documentation complete (3 major docs)
- ✅ Feature specification approved (EVA-DATA-PIPELINE.md)
- ✅ Business analyst template created

**Artifacts:**
- `docs/DATA-SOURCE-ORGANIZATION-STANDARD.md` (700 lines)
- `docs/DATA-INVENTORY-FOR-REVIEW.md` (1000 lines)
- `docs/features/EVA-DATA-PIPELINE.md` (1000 lines)
- `data-sources/jurisprudence/` (10 files)
- `data-sources/_templates/ingestion-request.md`

---

### 🔨 Phase 1: P02 Generator (Weeks 1-2)

**Goal:** Build P02 agent that generates pipelines from requirements.json

**Timeline:** December 9-20, 2024 (2 weeks)

#### Week 1: Core Generator

**Tasks:**
1. **P02 Requirements Parser** (2 days)
   - [ ] Read and validate requirements.json schema
   - [ ] Parse data_sources array
   - [ ] Parse rag_pipeline_requirements
   - [ ] Parse compliance and success criteria
   - [ ] Error handling for invalid requirements

2. **Config Generator** (2 days)
   - [ ] Generate `config/pipeline-config.yaml`
   - [ ] Map requirements → discover/fetch/normalize/publish settings
   - [ ] Set rate limits, timeouts, retry logic
   - [ ] Configure embeddings and vector store

3. **Source Catalog Generator** (1 day)
   - [ ] Generate `discover/sources.yaml`
   - [ ] Parse entry points from data_sources
   - [ ] Set crawl depth, patterns, filters
   - [ ] Configure update frequency and schedule

**Deliverables:**
- `src/eva_rag/p02/requirements_parser.py`
- `src/eva_rag/p02/config_generator.py`
- `src/eva_rag/p02/source_generator.py`
- Unit tests (90%+ coverage)

#### Week 2: Schema & Script Generation

**Tasks:**
1. **Metadata Schema Generator** (2 days)
   - [ ] Generate `normalize/metadata_schema.json`
   - [ ] Map metadata_required → field definitions
   - [ ] Add validation rules (required, optional, computed)
   - [ ] Generate field examples and types

2. **Chunking Strategy Generator** (1 day)
   - [ ] Generate `publish/chunking_strategy.yaml`
   - [ ] Map chunking method (semantic/structural/fixed)
   - [ ] Set token limits and overlap
   - [ ] Configure special handling (tables, citations, etc.)

3. **Ingestion Script Generator** (2 days)
   - [ ] Generate `scripts/ingest_[source].py`
   - [ ] Implement 4 stages (Discover, Fetch, Normalize, Publish)
   - [ ] Add error handling and logging
   - [ ] Generate validation script

**Deliverables:**
- `src/eva_rag/p02/schema_generator.py`
- `src/eva_rag/p02/chunking_generator.py`
- `src/eva_rag/p02/script_generator.py`
- Generated script templates
- Unit tests

**Week 1-2 Exit Criteria:**
- ✅ P02 can generate all 7 config files from requirements.json
- ✅ Generated files pass validation (YAML/JSON syntax)
- ✅ Unit tests pass (90%+ coverage)
- ✅ Jurisprudence example regenerated successfully

---

### 🔍 Phase 2: P03 Reviewer (Weeks 3-4)

**Goal:** Build P03 agent that validates generated pipelines

**Timeline:** December 23, 2024 - January 3, 2025 (2 weeks)

#### Week 3: Code Quality & Security Validation

**Tasks:**
1. **Code Quality Checker** (2 days)
   - [ ] Lint generated Python code (pylint, black)
   - [ ] Check YAML/JSON syntax
   - [ ] Validate file structure (all required files present)
   - [ ] Check for TODO/FIXME markers

2. **Security Validator** (2 days)
   - [ ] Scan for hardcoded secrets (bandit)
   - [ ] Validate no external network access in disallowed list
   - [ ] Check constraints.json compliance
   - [ ] Validate authentication patterns (env vars only)

3. **Compliance Checker** (1 day)
   - [ ] Validate Privacy Act compliance (PII detection rules)
   - [ ] Check Official Languages Act (bilingual support)
   - [ ] Validate WCAG 2.2 AA (accessibility metadata)
   - [ ] Check Protected B classification rules

**Deliverables:**
- `src/eva_rag/p03/code_quality.py`
- `src/eva_rag/p03/security_validator.py`
- `src/eva_rag/p03/compliance_checker.py`
- Validation report template

#### Week 4: Testing & Approval Workflow

**Tasks:**
1. **Sample Execution Tester** (2 days)
   - [ ] Run generated pipeline with 10 sample documents
   - [ ] Validate output format (JSON structure)
   - [ ] Check metadata completeness
   - [ ] Verify error handling works

2. **Approval Workflow** (2 days)
   - [ ] Create approval request format
   - [ ] Implement human-in-loop approval step
   - [ ] Generate approval report (pass/fail + reasons)
   - [ ] Email notification to stakeholders

3. **Integration** (1 day)
   - [ ] Connect P02 → P03 pipeline
   - [ ] Test end-to-end (requirements.json → approved pipeline)
   - [ ] Error handling and retry logic

**Deliverables:**
- `src/eva_rag/p03/sample_tester.py`
- `src/eva_rag/p03/approval_workflow.py`
- `src/eva_rag/p03/reviewer_main.py`
- Integration tests

**Week 3-4 Exit Criteria:**
- ✅ P03 validates all security and compliance rules
- ✅ Sample execution test passes for jurisprudence
- ✅ Approval workflow sends email notifications
- ✅ P02 → P03 integration works end-to-end

---

### 🚀 Phase 3: Pilot (Weeks 5-6)

**Goal:** Migrate 4 existing sources to new structure and validate

**Timeline:** January 6-17, 2025 (2 weeks)

#### Week 5: Migrate Existing Sources

**Tasks:**
1. **Jurisprudence (20,000 decisions)** (2 days)
   - [ ] Create requirements.json from existing specs
   - [ ] Run P02 generator
   - [ ] P03 review and approve
   - [ ] Execute full ingestion
   - [ ] Validate against existing output

2. **Canada.ca (1,257 pages)** (2 days)
   - [ ] Create requirements.json
   - [ ] Map existing WebCrawlerLoader logic
   - [ ] Generate pipeline
   - [ ] Execute and validate

3. **Employment Analytics (2 datasets)** (1 day)
   - [ ] Create requirements.json
   - [ ] Generate CSV pipeline
   - [ ] Execute and validate

**Deliverables:**
- `data-sources/jurisprudence/requirements.json` (validated)
- `data-sources/canada-ca/requirements.json`
- `data-sources/employment/requirements.json`
- Migration validation report

#### Week 6: AssistMe + Testing

**Tasks:**
1. **AssistMe (2 guides)** (1 day)
   - [ ] Create requirements.json
   - [ ] Generate pipeline
   - [ ] Execute and validate

2. **Analyst Training** (2 days)
   - [ ] Create training materials (slides + video)
   - [ ] Train 5 pilot analysts
   - [ ] Have analysts fill out ingestion-request.md
   - [ ] Collect feedback

3. **Documentation** (2 days)
   - [ ] Quick start guide for analysts
   - [ ] Developer guide for P02/P03
   - [ ] Troubleshooting guide
   - [ ] FAQ document

**Deliverables:**
- `data-sources/assistme/requirements.json`
- Training materials (slides, video)
- Documentation (4 guides)
- Analyst feedback report

**Week 5-6 Exit Criteria:**
- ✅ All 4 existing sources migrated successfully
- ✅ Output matches existing ingestion (validation passes)
- ✅ 5 analysts trained and can use template
- ✅ Documentation complete and published

---

### 📈 Phase 4: Scale (Weeks 7-8)

**Goal:** Onboard 10 new data sources and automate scheduling

**Timeline:** January 20-31, 2025 (2 weeks)

#### Week 7: New Data Sources

**Priority Data Sources (10 sources):**

1. **Federal Court** (Legal)
   - [ ] Analyst submits ingestion-request.md
   - [ ] Dev creates requirements.json
   - [ ] P02 generates pipeline
   - [ ] P03 reviews and approves
   - [ ] Execute ingestion

2. **Federal Court of Appeal** (Legal)
   - [ ] Same workflow as above

3. **Social Security Tribunal** (Legal)
   - [ ] Same workflow as above

4. **Immigration & Citizenship** (Government Services)
   - [ ] Same workflow as above

5. **Benefits Programs** (Government Services)
   - [ ] Same workflow as above

6. **Tax Information** (Government Services)
   - [ ] Same workflow as above

7. **Public Service Collective Agreements** (HR)
   - [ ] Same workflow as above

8. **Employment Standards** (HR)
   - [ ] Same workflow as above

9. **PowerBI Dashboards** (Analytics)
   - [ ] Same workflow as above

10. **Internal Policy Documents** (Corporate)
    - [ ] Same workflow as above

**Target:** 2 sources per day

**Deliverables:**
- 10 new requirements.json files
- 10 generated pipelines
- 10 execution reports
- Quality metrics dashboard

#### Week 8: Automation & Monitoring

**Tasks:**
1. **Scheduling System** (2 days)
   - [ ] Implement APScheduler integration
   - [ ] Configure daily/weekly/monthly jobs
   - [ ] Add job queue management
   - [ ] Error handling and retry logic

2. **Monitoring Dashboard** (2 days)
   - [ ] Build Grafana dashboards
   - [ ] Track: documents processed, failures, duration
   - [ ] Alert on: failure rate > 5%, missing metadata > 1%
   - [ ] Email reports (daily summary)

3. **Performance Tuning** (1 day)
   - [ ] Optimize rate limiting
   - [ ] Tune batch sizes
   - [ ] Cache frequently accessed pages
   - [ ] Parallel processing where safe

**Deliverables:**
- `src/eva_rag/scheduler/scheduler_main.py`
- Grafana dashboard JSON
- Monitoring alert rules
- Performance tuning report

**Week 7-8 Exit Criteria:**
- ✅ 10 new data sources ingested successfully
- ✅ Scheduling system runs daily/weekly jobs
- ✅ Monitoring dashboard shows real-time metrics
- ✅ Average ingestion success rate > 95%

---

### 🎉 Phase 5: Production Launch (Week 9+)

**Goal:** Open to all analysts and scale to 50+ sources

**Timeline:** February 1, 2025 onwards

**Launch Plan:**

1. **Week 9 (Feb 3-7): Soft Launch**
   - [ ] Open to 20 analysts (early adopters)
   - [ ] Announce via Slack, email, town hall
   - [ ] Office hours daily (support questions)
   - [ ] Monitor closely for issues

2. **Week 10 (Feb 10-14): Full Launch**
   - [ ] Open to all GC analysts (50+ users)
   - [ ] Publish blog post and video demo
   - [ ] Weekly office hours (Thursdays 2-3 PM)
   - [ ] Track usage metrics

3. **Month 2 (February): Scale to 30 sources**
   - [ ] Process 20 new ingestion requests
   - [ ] Optimize based on feedback
   - [ ] Add common patterns to templates

4. **Month 3 (March): Scale to 50 sources**
   - [ ] Process 20 more requests
   - [ ] Build self-service web UI (V1.1)
   - [ ] Advanced features (incremental updates)

5. **Q2 2025: Scale to 100+ sources**
   - [ ] Enterprise-scale deployment
   - [ ] Multi-tenant isolation
   - [ ] Federated ingestion across departments

---

## 📊 Success Metrics & Tracking

### Business Metrics

| Metric | Baseline | Target | Q1 | Q2 | Status |
|--------|----------|--------|----|----|--------|
| Time to Pipeline | 2-4 weeks | < 2 days | - | - | 📈 Track |
| Analyst Requests | 0% | 80% | - | - | 📈 Track |
| Data Sources | 6 | 100+ | 20 | 50 | 📈 Track |
| Ingestion Success | 85% | 95%+ | - | - | 🎯 Target |

### Weekly KPIs (Track from Week 5)

**Week 5-8 Targets:**
- Pipeline generation time: < 30 min
- P03 approval time: < 1 day
- Full ingestion time: < 2 days
- Success rate: > 95%
- Analyst satisfaction: > 4.0/5

**Tracking Method:**
- Weekly team sync (Fridays 10 AM)
- Grafana dashboards (real-time)
- Bi-weekly stakeholder report

---

## 💰 Budget & Resources

### Development Effort (Weeks 1-8)

| Phase | Dev Hours | Cost Estimate |
|-------|-----------|---------------|
| Phase 1: P02 Generator | 160 hours | $16,000 |
| Phase 2: P03 Reviewer | 160 hours | $16,000 |
| Phase 3: Pilot | 120 hours | $12,000 |
| Phase 4: Scale | 120 hours | $12,000 |
| **Total** | **560 hours** | **$56,000** |

### Operational Costs (Monthly, Starting Feb 2025)

| Item | Cost |
|------|------|
| Azure AI Search | $500/mo |
| Azure OpenAI | $1,000/mo |
| Compute (VMs) | $400/mo |
| Storage | $50/mo |
| **Total** | **$1,950/mo** |

### ROI Calculation

**Annual Savings:**
- Developer time savings: $400K/year (90% reduction)
- Analyst time savings: $100K/year (80% reduction)
- **Total Savings: $500K/year**

**Total Investment:**
- Development (one-time): $56,000
- Operations (Year 1): $23,400
- **Total: $79,400**

**Break-even:** ~2 months  
**Year 1 ROI:** 530%

---

## 🎓 Training Plan

### Analyst Training (Week 6)

**Session 1: Introduction (1 hour)**
- What is EVA Data Pipeline?
- How it works (Discover → Fetch → Normalize → Publish)
- When to use it
- Live demo

**Session 2: Template Walkthrough (1 hour)**
- Fill out ingestion-request.md
- Common examples (web pages, PDFs, APIs)
- Best practices
- Q&A

**Session 3: Hands-on Practice (1 hour)**
- Participants fill out real request
- Dev team provides feedback
- Submit first request

**Materials:**
- Slides (30 pages)
- Video tutorial (15 min)
- Quick reference card (1 page)

### Developer Training (Week 4)

**Session 1: Architecture Deep Dive (2 hours)**
- 4-stage pipeline pattern
- P02 generator internals
- P03 reviewer process
- Extension points

**Session 2: Troubleshooting (2 hours)**
- Common errors and fixes
- Debugging techniques
- Performance tuning
- Security best practices

**Materials:**
- Architecture guide (50 pages)
- API documentation
- Troubleshooting guide

---

## 🚧 Risk Mitigation

### Top 5 Risks

**1. P02 Generates Incorrect Code**
- **Mitigation:** P03 mandatory review, extensive testing, gradual rollout
- **Owner:** Dev Team
- **Status:** ✅ Addressed in Phase 2

**2. Source Websites Change**
- **Mitigation:** Monitor for errors, version control parsers, manual review queue
- **Owner:** Ops Team
- **Status:** 🔄 Monitoring system in Phase 4

**3. Analyst Requests Impossible Requirements**
- **Mitigation:** Template validation, dev review, examples, office hours
- **Owner:** Support Team
- **Status:** ✅ Template designed with validation

**4. Scale Exceeds Azure Limits**
- **Mitigation:** Rate limiting, batch processing, cost monitoring
- **Owner:** Infrastructure Team
- **Status:** 🔄 Monitor in Phase 4

**5. Adoption Lower Than Expected**
- **Mitigation:** Training, office hours, success stories, executive sponsorship
- **Owner:** Product Team
- **Status:** 🔄 Measure in Phase 5

---

## 📅 Key Milestones & Checkpoints

| Date | Milestone | Status | Owner |
|------|-----------|--------|-------|
| Dec 8, 2024 | Phase 0 Complete | ✅ Done | Marco |
| Dec 20, 2024 | P02 Generator Complete | 🔄 In Progress | Dev Team |
| Jan 3, 2025 | P03 Reviewer Complete | ⏳ Pending | Dev Team |
| Jan 17, 2025 | Pilot Complete | ⏳ Pending | Project Team |
| Jan 31, 2025 | Production Launch | ⏳ Pending | All |
| Mar 31, 2025 | 50 Sources Live | ⏳ Pending | All |
| Jun 30, 2025 | 100 Sources Live | ⏳ Pending | All |

---

## ✅ Next Actions (Week 1 - Starting Dec 9)

### Monday, Dec 9
- [ ] Kickoff meeting (team + stakeholders)
- [ ] Setup dev environment (P02 generator)
- [ ] Create GitHub project board
- [ ] Start requirements parser

### Tuesday-Wednesday, Dec 10-11
- [ ] Complete requirements parser
- [ ] Unit tests for parser
- [ ] Start config generator

### Thursday-Friday, Dec 12-13
- [ ] Complete config generator
- [ ] Unit tests
- [ ] Start source generator
- [ ] Weekly checkpoint meeting

---

## 📝 Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Product Owner | Marco Presta | Dec 8, 2024 | ✅ Approved |
| Tech Lead | EVA-RAG Team | Dec 8, 2024 | ✅ Approved |
| Project Manager | TBD | Pending | ⏳ Pending |

---

**Document:** EVA Data Pipeline - Implementation Roadmap  
**Version:** 1.0  
**Status:** APPROVED - READY TO EXECUTE  
**Location:** `docs/EVA-DATA-PIPELINE-ROADMAP.md`
