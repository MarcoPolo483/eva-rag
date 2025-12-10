# P02 Overview: EVA Data Model with FASTER Principles

**Navigation Guide**: How to read this feature documentation  
**Audience**: Product Owners, Developers, Tech Leads, Security Reviewers, Compliance Auditors  
**Last Updated**: December 8, 2025

---

## 📚 Documentation Structure (P02 Pattern)

This feature follows the **P02 10-artifact pattern** - a self-contained documentation structure that eliminates "code vibing" (monolithic docs) and provides clear, navigable context for all stakeholders.

### The 10 P02 Artifacts

| # | Artifact | Purpose | Length | Primary Audience |
|---|----------|---------|--------|------------------|
| 1 | **README.md** | Quick start, architecture overview | 600 lines | Everyone (start here) |
| 2 | **P02-Overview.md** (this file) | Navigation guide, reading approaches | 400 lines | Everyone (read 2nd) |
| 3 | **requirements.md** | 35 requirements (20 FR, 15 NFR) | 1,200 lines | PO, Tech Lead, QA |
| 4 | **backlog.md** | 6 sprints, 199 story points, 33 user stories | 1,400 lines | PO, Scrum Master, Dev Team |
| 5 | **use-cases.md** | 8 scenarios (citizen query, admin upload, bias detection, etc.) | 2,800 lines | PO, UX, Dev Team |
| 6 | **risks.md** | 21 risks (1 critical, 8 high, 9 medium, 3 low) | 1,000 lines | PO, Tech Lead, Security |
| 7 | **architecture-notes.md** | Deployment, API design, data model, security, performance | 2,500 lines | Tech Lead, Architects, DevOps |
| 8 | **adr-eva-data-model-faster.md** | 6 architecture decisions (Cosmos DB, HPK, AI Search, etc.) | 1,800 lines | Architects, Tech Lead, CISO |
| 9 | **tests.md** | 345+ test cases (unit, integration, security, compliance, E2E) | 2,000 lines | QA, Dev Team, Compliance |
| 10 | **feature-map.md** | System diagram, 10 collections, hybrid search, RBAC, governance | 1,600 lines | Everyone (visual learners) |

**Total**: ~14,700 lines across 10 focused artifacts (vs 1 monolithic 24,000-line doc ❌)

---

## 🎯 Reading Approaches (Choose Your Journey)

### Approach 1: Quick Context (15 minutes)

**Goal**: Understand what EVA Data Model is, why it matters, and demo scope  
**Audience**: Executives, stakeholders, first-time readers

**Reading Path**:
1. **README.md** (Sections: Quick Start, What is EVA, Architecture Overview, Cost Breakdown, Demo Sandbox)
   - **Time**: 10 minutes
   - **Key Takeaways**: EVA = multi-tenant RAG for GC, FASTER principles, $500/month demo sandbox, 25 users, all OOTB features
2. **feature-map.md** (Section: System Architecture Overview, 10 Collections, Demo Sandbox Capabilities)
   - **Time**: 5 minutes
   - **Key Takeaways**: 10 Cosmos DB collections, hybrid search (60% vector + 40% BM25), 6-layer security, compliance mapping

**Exit Questions to Validate**:
- Can you explain EVA's FASTER principles in 1 sentence each?
- What are the 3 Azure services used and their monthly costs?
- What makes this a "demo sandbox" vs "production pilot"?

**Next Steps**: If interested, proceed to Approach 2 (PO Review) or Approach 3 (Developer Deep Dive)

---

### Approach 2: Product Owner Review (30 minutes)

**Goal**: Validate requirements, backlog, use cases, risks for sprint planning  
**Audience**: Product Owners, Scrum Masters, Business Analysts

**Reading Path**:
1. **README.md** (Full read)
   - **Time**: 10 minutes
   - **Focus**: Architecture overview, cost breakdown, evidence artifacts for stakeholders
2. **requirements.md** (All 35 requirements)
   - **Time**: 10 minutes
   - **Focus**: Functional requirements (FR-001 to FR-020), non-functional requirements (NFR-001 to NFR-015)
   - **Validation**: Check acceptance criteria, dependencies, FASTER principle alignment
3. **backlog.md** (Sprint overview + user stories)
   - **Time**: 5 minutes
   - **Focus**: 6 sprints (Dec 8 - Jan 18), story point distribution (199 SP total), critical path
4. **risks.md** (RISK-C01 critical risk + high-severity risks)
   - **Time**: 5 minutes
   - **Focus**: RISK-C01 (ITSG-33 ATO gap), mitigation roadmap, sprint-by-sprint risk reduction

**Exit Questions to Validate**:
- Are the 35 requirements self-explanatory? Any gaps?
- Is the 6-sprint timeline (42 days) realistic for 199 story points?
- What is the critical risk (RISK-C01) and how is it mitigated?

**Next Steps**: Use backlog.md for sprint planning, prioritize RISK-C01 mitigation in Sprint 1

---

### Approach 3: Developer Deep Dive (60 minutes)

**Goal**: Understand implementation details, API design, data model, testing strategy  
**Audience**: Software Developers, QA Engineers, DevOps Engineers

**Reading Path**:
1. **README.md** (Quick Start section)
   - **Time**: 5 minutes
   - **Action**: Clone repo, deploy demo sandbox, start FastAPI server locally
2. **architecture-notes.md** (Full read)
   - **Time**: 25 minutes
   - **Focus**: 
     - Deployment architecture (Azure resource topology, network security)
     - API design (RESTful endpoints, rate limiting, error handling)
     - Data model (10 Cosmos DB collections, HPK schemas, AI Search index)
     - Security architecture (6-layer defense, encryption, secrets management)
     - Performance optimization (Cosmos DB query tuning, caching, background jobs)
3. **use-cases.md** (UC-001, UC-002, UC-004, UC-006 - key flows)
   - **Time**: 15 minutes
   - **Focus**: Citizen query, admin upload, prompt injection defense, audit verification
4. **tests.md** (Unit tests section + integration tests section)
   - **Time**: 10 minutes
   - **Focus**: Test coverage targets (90%+ unit, 100% API), test frameworks (pytest, Locust), CI/CD gates
5. **feature-map.md** (Data flow diagrams)
   - **Time**: 5 minutes
   - **Focus**: User query path, document upload path, component relationships

**Exit Questions to Validate**:
- Can you implement a new API endpoint following the existing patterns?
- How would you add a new Cosmos DB collection with HPK?
- What are the 6 layers of security defense and their order?

**Next Steps**: Set up local dev environment, run tests (`poetry run pytest`), implement first user story from Sprint 1

---

### Approach 4: Technical Lead / Architect Review (90 minutes)

**Goal**: Validate architecture decisions, scaling strategy, compliance, disaster recovery  
**Audience**: Technical Leads, Solutions Architects, Enterprise Architects, CISO

**Reading Path**:
1. **README.md** (Full read)
   - **Time**: 10 minutes
   - **Focus**: Architecture overview, cost breakdown, scaling path
2. **adr-eva-data-model-faster.md** (All 6 architecture decisions)
   - **Time**: 30 minutes
   - **Focus**:
     - ADR-001.1: Why Cosmos DB over PostgreSQL/MySQL? (FedRAMP High, HPK, auto-scaling)
     - ADR-001.2: Why HPK `/spaceId/tenantId/userId`? (10x query performance, physical isolation)
     - ADR-001.3: Why 10 collections instead of monolithic schema? (optimized indexing, security boundaries)
     - ADR-001.4: Why Azure AI Search over native Cosmos DB vector search? (hybrid search, RBAC filters, GA maturity)
     - ADR-001.5: Why cryptographic hash chains? (tamper-evident, ITSG-33 AU-9, cost-effective)
     - ADR-001.6: Why write-once for AI interactions? (immutable audit trail, provenance)
3. **architecture-notes.md** (Sections: Deployment, Security, Performance, Monitoring, DR, Scaling)
   - **Time**: 25 minutes
   - **Focus**:
     - Azure resource topology (VNet, NSG, private endpoints)
     - Encryption at rest (CMK) + in transit (TLS 1.3)
     - Cosmos DB query optimization (HPK, composite indexes, continuation tokens)
     - Disaster recovery (RPO: 1 hour, RTO: 2 hours, point-in-time restore)
     - Scaling strategy (Demo $500 → Beta $2000 → Production $5000)
4. **risks.md** (All 21 risks + mitigation roadmap)
   - **Time**: 15 minutes
   - **Focus**: Technical risks (6), security risks (6), compliance risks (4), operational risks (5)
5. **tests.md** (Security tests + compliance tests sections)
   - **Time**: 10 minutes
   - **Focus**: Prompt injection tests, PII detection tests, ITSG-33 control tests, PIPEDA principle tests

**Exit Questions to Validate**:
- Why was Cosmos DB chosen over PostgreSQL? (Trade-offs: cost, vendor lock-in, learning curve)
- How does HPK provide 10x query performance? (Single-partition reads: 5 RU vs 50 RU cross-partition)
- What is the disaster recovery plan? (RPO, RTO, backup strategy)
- How does the architecture scale from 25 users → 1000+ users? (RU/s, AI Search tier, App Service instances)

**Next Steps**: Approve ADR, validate with enterprise architecture standards, sign off on ITSG-33 compliance strategy

---

### Approach 5: Compliance / Security Review (45 minutes)

**Goal**: Validate ITSG-33, PIPEDA, NIST AI RMF compliance, security controls  
**Audience**: Compliance Officers, Security Analysts, CISO, Privacy Officers, Auditors

**Reading Path**:
1. **README.md** (Section: Compliance - ITSG-33, PIPEDA, NIST AI RMF)
   - **Time**: 5 minutes
   - **Focus**: 52/60 ITSG-33 controls (87%), 10/10 PIPEDA principles, NIST AI RMF Level 2 maturity
2. **adr-eva-data-model-faster.md** (Sections: ADR-001.5 hash chains, ADR-001.6 write-once provenance)
   - **Time**: 10 minutes
   - **Focus**: Tamper-evident audit logging (ITSG-33 AU-9), immutable AI interactions (provenance)
3. **architecture-notes.md** (Section: Security Architecture)
   - **Time**: 15 minutes
   - **Focus**:
     - 6-layer defense (input validation, PII detection, prompt injection, RBAC, output filtering, audit logging)
     - Authentication flow (Azure AD OIDC, MFA, JWT validation)
     - Encryption at rest (CMK in Key Vault) + in transit (TLS 1.3)
     - Secrets management (Azure Key Vault, no hardcoded credentials)
4. **use-cases.md** (UC-004 Prompt Injection, UC-006 Audit Verification, UC-008 DSAR)
   - **Time**: 10 minutes
   - **Focus**: Security incident scenarios, hash chain verification, PIPEDA principle 9 (individual access)
5. **tests.md** (Sections: Security tests, Compliance tests)
   - **Time**: 5 minutes
   - **Focus**: 45 security tests (100% attack vectors), 35 compliance tests (ITSG-33, PIPEDA, NIST AI RMF)

**Exit Questions to Validate**:
- How are ITSG-33 AU-2 (audit events) and AU-9 (tamper protection) satisfied? (Hash chains + WORM Blob Storage)
- How is PIPEDA principle 4 (accuracy) enforced? (Bias detection + governance workflow)
- What is the process for a Data Subject Access Request (DSAR)? (UC-008: export all user data in 30 days)
- How are prompt injection attacks prevented? (6-layer defense, 100% block rate in tests)

**Next Steps**: Conduct security assessment, validate ITSG-33 control implementations, approve for Protected B data handling

---

## 🗺️ Cross-References (How Artifacts Link Together)

### Requirements → Backlog → Tests

```
requirements.md (FR-001: Multi-Tenant Isolation)
    ↓
backlog.md (Sprint 1, Story 1.1: "Implement HPK /spaceId/tenantId/userId")
    ↓
tests.md (Test ID: UT-001: "HPK query returns only Space data")
```

### Use Cases → Architecture → ADR

```
use-cases.md (UC-001: Citizen Query with Citations)
    ↓
architecture-notes.md (Section: API Design, Endpoint: POST /api/v1/spaces/{spaceId}/query)
    ↓
adr-eva-data-model-faster.md (ADR-001.4: Why Azure AI Search for hybrid search?)
```

### Risks → Backlog → Tests

```
risks.md (RISK-C01: ITSG-33 ATO gap blocks production deployment)
    ↓
backlog.md (Sprint 4, Story 4.3: "Implement hash chain verification for AU-9")
    ↓
tests.md (Test ID: CT-001: "Verify hash chain integrity for 100 logs")
```

---

## 📊 Artifact Dependency Matrix

| Artifact | Dependencies | Dependents |
|----------|--------------|------------|
| **README.md** | None (entry point) | All other artifacts |
| **P02-Overview.md** | README.md | All other artifacts (navigation) |
| **requirements.md** | README.md | backlog.md, tests.md, use-cases.md |
| **backlog.md** | requirements.md | tests.md, architecture-notes.md |
| **use-cases.md** | requirements.md | tests.md, architecture-notes.md |
| **risks.md** | requirements.md, backlog.md | tests.md, architecture-notes.md |
| **architecture-notes.md** | requirements.md, use-cases.md, adr.md | tests.md, feature-map.md |
| **adr-eva-data-model-faster.md** | requirements.md | architecture-notes.md, feature-map.md |
| **tests.md** | requirements.md, backlog.md, use-cases.md | None (validation artifact) |
| **feature-map.md** | architecture-notes.md, adr.md | None (visual summary) |

---

## ✅ Artifact Completeness Checklist

**Before Sprint 1 Begins**, validate all 10 artifacts are complete:

- [x] **README.md**: Quick start works (3 steps, 15 minutes)
- [x] **P02-Overview.md**: 5 reading approaches documented
- [x] **requirements.md**: 35 requirements with acceptance criteria, dependencies, test criteria
- [x] **backlog.md**: 6 sprints, 33 user stories, 199 story points, clear priorities
- [x] **use-cases.md**: 8 scenarios covering all FASTER principles (UC-001 to UC-008)
- [x] **risks.md**: 21 risks identified, mitigation roadmap mapped to sprints
- [x] **architecture-notes.md**: Deployment, API, data model, security, performance, monitoring, DR, scaling
- [x] **adr-eva-data-model-faster.md**: 6 decisions documented with rationale, consequences, mitigations
- [x] **tests.md**: 345+ test cases, 95%+ coverage target, CI/CD gates defined
- [x] **feature-map.md**: System diagram, 10 collections, hybrid search, RBAC, governance, compliance mapping

**Status**: ✅ 10/10 artifacts complete (100%)

---

## 🚀 How to Update P02 Artifacts

### When to Update

- **requirements.md**: When new requirements discovered or acceptance criteria refined
- **backlog.md**: After each sprint (update story status, adjust priorities)
- **use-cases.md**: When new user scenarios identified or flows change
- **risks.md**: When new risks discovered or mitigation strategies change
- **architecture-notes.md**: When infrastructure changes (new Azure resources, API endpoints)
- **adr-eva-data-model-faster.md**: When major architecture decisions made (rarely - ADRs are immutable after approval)
- **tests.md**: When new test cases added or coverage targets updated
- **feature-map.md**: When component relationships change (new collections, layers)

### Version Control

All P02 artifacts include **Revision History** table at the bottom:

```markdown
## 🔄 Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-08 | 1.0 | Marco Presta | Initial artifact |
| 2025-12-15 | 1.1 | Dev Team | Updated Sprint 1 results |
```

---

## 📞 Questions & Feedback

### Who to Ask

- **P02 Structure Questions**: Marco Presta (Product Owner)
- **Requirements Clarification**: Marco Presta
- **Architecture Questions**: Tech Lead (assign when project funded)
- **Security/Compliance Questions**: ESDC CISO office
- **API/Implementation Questions**: Dev Team (assign when project funded)

### How to Provide Feedback

1. **GitHub Issues**: Open issue in `eva-rag` repo with label `documentation`
2. **Direct Feedback**: Email Marco Presta (marco.presta@esdc.gc.ca)
3. **Sprint Retrospectives**: Discuss P02 artifact usefulness, suggest improvements

---

## 🎓 P02 Pattern Benefits (Why We Use This)

### Problem: Code Vibing ❌

**Before P02**: Single 24,000-line monolithic doc (`EVA-MULTI-TENANT-ARCHITECTURE.md`)
- Hard to navigate (no clear structure)
- Hard to maintain (changes ripple everywhere)
- Hard to understand (cognitive overload)
- Hard to validate (no clear acceptance criteria)

### Solution: P02 10-Artifact Pattern ✅

**After P02**: 10 focused artifacts (~14,700 lines total, 40% reduction)
- **Self-contained**: Each artifact standalone (can read in isolation)
- **Self-explanatory**: Requirements include acceptance criteria, dependencies, test criteria
- **Cross-referenced**: Clear links between artifacts (requirements → backlog → tests)
- **Role-specific**: Different stakeholders read different artifacts (PO vs Dev vs Security)
- **Navigable**: P02-Overview provides 5 reading approaches (Quick, PO, Dev, Tech Lead, Compliance)

### Evidence of Success

- ✅ README.md validates in 15 minutes (Quick Context approach)
- ✅ PO can plan Sprint 1 in 30 minutes (requirements.md + backlog.md)
- ✅ Dev can implement first story in 60 minutes (architecture-notes.md + use-cases.md)
- ✅ Security can approve in 45 minutes (compliance review approach)
- ✅ Zero "where do I start?" questions (P02-Overview solves this)

---

## 🔄 Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-08 | 1.0 | Marco Presta | Initial P02-Overview - 5 reading approaches, artifact dependencies, completeness checklist |

---

**Last Updated**: December 8, 2025  
**Maintainer**: Marco Presta (Product Owner)  
**Next Review**: After Sprint 1 completion (Dec 14, 2025)
