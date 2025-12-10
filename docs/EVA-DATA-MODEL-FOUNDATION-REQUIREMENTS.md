# EVA Data Model Foundation Requirements

**Status**: 🔍 DISCOVERED - PENDING IMPLEMENTATION  
**Priority**: 🔴 CRITICAL - BLOCKS EVA DATA PIPELINE  
**Date**: Dec 8, 2024  
**Source**: P02-AUTO-3fc7c655-p02-req-001-eva-data-model.md (400 lines, HIGH priority)

---

## 📋 Executive Summary

The **EVA Data Model** is the foundational architecture that must be established before proceeding with the **EVA Data Pipeline** implementation. This document summarizes what was discovered in the archive and what needs to be created.

**Why This Matters**:
- EVA Data Pipeline (approved, $500K ROI, 8-week roadmap) is ready to execute
- But pipeline needs defined Cosmos DB schemas, AI Search indexes, and RBAC patterns
- Without data model foundation, pipeline would build on undefined schemas
- User correctly identified this dependency: "there is another thing that needs to happen before"

---

## 🎯 What Was Found

### 1. EVA Data Model Intake Document (400 lines)
**Location**: `eva-orchestrator/docs/intake/processed/P02-AUTO-3fc7c655-p02-req-001-eva-data-model.md`

**Metadata**:
- **Intake Date**: 2025-12-06 (2 days ago)
- **Priority**: HIGH
- **Status**: PENDING P02 PROCESSING
- **Requested By**: Marco Presta (PO)
- **Urgency**: Required for onboarding new developers across 40+ EVA Suite products

**Problem Statement**:
After establishing workspace architecture zoning (LESSON-005), need to document how data flows through EVA system and how folder structures reflect architectural decisions.

**Value Proposition**:
- Enables developers/agents to place code correctly
- Provides authoritative reference for data architecture
- Enables efficient navigation across 40+ repos
- Reduces onboarding time by 50%

### 2. CDD Inventory Configuration (286 lines)
**Location**: `eva-orchestrator/agents/cdd-inventory.yaml`

**Purpose**: Defines Component Design Document (CDD) recursion depth and requirements for 14 EVA components

**Key Components**:
- **Level 1**: UI/UX (eva-ui, eva-i11y, eva-i18n) - Depth 3-4
- **Level 2**: Infrastructure (eva-infra, eva-utils) - Depth 4-5
- **Level 3**: Core Business (eva-core, eva-auth) - Depth 4-5
- **Level 4**: AI & Agents (eva-agent, eva-openai, **eva-rag**) - Depth 4-5
- **Level 5**: Integration (eva-api, eva-mcp, eva-safety) - Depth 4
- **Level 6**: Operations (eva-metering, eva-ops, eva-seed, eva-enterprise) - Depth 3-4

**eva-rag Requirements** (Target Depth: 5):
```yaml
eva-rag:
  targetDepth: 5
  requiredSections:
    - "RAG Pipeline Architecture"
    - "Document Processing & Chunking"
    - "Vector Search & Retrieval"
    - "Hybrid Search Strategies"
    - "Citation & Evaluation Systems"
  dependencies: ["eva-core", "eva-openai", "eva-utils"]
  recursiveRequirements:
    level1: "RAG framework overview"
    level2: "Document ingestion and processing"
    level3: "Search and retrieval mechanisms"
    level4: "Evaluation and optimization"
    level5: "Advanced scenarios and customization"
```

---

## 📦 What Needs to Be Created

### Required Deliverables (V1.0 - Sprint 1):

#### 1. `docs/architecture/eva-data-model.md`
**Estimated**: 800-1,200 lines

**Structure**:
```markdown
# EVA Data Model

## Overview
- High-level architecture diagram
- Key data flows (ingestion, retrieval, routing)

## Cosmos DB Collections
### documents
- **Purpose**: Store original documents and metadata
- **Schema**: 
  - id (string, unique)
  - documentId (string, unique identifier)
  - tenantId (string, HPK)
  - userId (string, HPK)
  - title (string)
  - content (string, full text)
  - documentType (enum: jurisprudence, policy, legislation, etc.)
  - sourceUrl (string)
  - language (enum: en, fr)
  - classification (enum: Protected B, Unclassified)
  - metadata (object, flexible schema)
  - createdAt (datetime)
  - updatedAt (datetime)
  - rbacGroups (array<string>, AD groups with access)
- **Hierarchical Partition Key**: /tenantId/userId
- **RBAC**: Filtered by rbacGroups matching user's AD group membership

### chunks
- **Purpose**: Store chunked document segments for RAG retrieval
- **Schema**:
  - id (string, unique)
  - chunkId (string, unique identifier)
  - documentId (string, foreign key to documents)
  - tenantId (string, HPK)
  - userId (string, HPK)
  - content (string, chunk text)
  - chunkIndex (int, 0-based position)
  - embedding (array<float>, 1536-dimensional vector)
  - metadata (object, inherited from document + chunk-specific)
  - rbacGroups (array<string>, inherited from document)
- **Hierarchical Partition Key**: /tenantId/userId
- **RBAC**: Filtered by rbacGroups

### users
- **Purpose**: Store user profiles and preferences
- **Schema**:
  - id (string, unique)
  - userId (string, Azure AD object ID)
  - tenantId (string, HPK)
  - email (string)
  - displayName (string)
  - preferredLanguage (enum: en, fr)
  - adGroups (array<string>, AD group memberships)
  - preferences (object, user settings)
  - createdAt (datetime)
  - lastLoginAt (datetime)
- **Hierarchical Partition Key**: /tenantId
- **RBAC**: User can only read their own profile

### sessions
- **Purpose**: Store chat session history and context
- **Schema**:
  - id (string, unique)
  - sessionId (string, unique identifier)
  - tenantId (string, HPK)
  - userId (string, HPK)
  - title (string, session name)
  - messages (array<object>, conversation history)
  - context (object, session metadata)
  - createdAt (datetime)
  - updatedAt (datetime)
- **Hierarchical Partition Key**: /tenantId/userId
- **RBAC**: User can only access their own sessions

## Azure AI Search Indexes

### jurisprudence-index
- **Purpose**: Legal case law and tribunal decisions
- **Fields**:
  - id (Edm.String, key)
  - documentId (Edm.String, filterable)
  - content (Edm.String, searchable)
  - contentVector (Collection(Edm.Single), 1536 dims)
  - title (Edm.String, searchable, filterable)
  - tribunal (Edm.String, filterable, facetable)
  - citation (Edm.String, filterable)
  - decisionDate (Edm.DateTimeOffset, filterable, sortable)
  - language (Edm.String, filterable)
  - rbacGroups (Collection(Edm.String), filterable)
- **Vectorization**: text-embedding-3-large (1536 dims)
- **Search Type**: Hybrid (keyword + vector)
- **Security Filters**: rbacGroups eq 'user-ad-group'

### assistme-index
- **Purpose**: General government assistance documents
- **Fields**:
  - id, documentId, content, contentVector
  - title, category, sourceUrl, language
  - rbacGroups
- **Vectorization**: text-embedding-3-large
- **Search Type**: Hybrid
- **Security Filters**: rbacGroups eq 'user-ad-group'

### canl-index
- **Purpose**: Canadian legislation and regulations
- **Fields**:
  - id, documentId, content, contentVector
  - title, legislationType, enactmentDate, status
  - rbacGroups
- **Vectorization**: text-embedding-3-large
- **Search Type**: Hybrid
- **Security Filters**: rbacGroups eq 'user-ad-group'

## Data Flow Diagrams

### Ingestion Pipeline (Mermaid)
[PDF/HTML] → [Fetch] → [Extract Text] → [Chunk] → [Embed] → [Store Cosmos DB] → [Index AI Search]
- Security: RBAC groups attached at fetch time
- Validation: Schema validation before storage
- Monitoring: Prometheus metrics at each stage

### Retrieval Flow (Mermaid)
[User Query] → [APIM Auth] → [AI Search] → [Security Filter] → [Hybrid Search] → [Rerank] → [LLM Context] → [Response]
- Security: User's AD groups used as filter
- Search: Keyword + vector hybrid with RRF
- Reranking: Semantic relevance scoring

### APIM Request Routing (Mermaid)
[Client] → [APIM Gateway] → [Auth (Azure AD)] → [Rate Limit] → [Eva Foundation] → [Cosmos DB/AI Search]
- Authentication: Bearer token validation
- Authorization: AD group extraction from token
- Metering: Usage tracking per tenant/user

## RBAC Enforcement

### Pattern
1. **Authentication**: Azure AD validates user identity
2. **Group Extraction**: Token contains user's AD group memberships
3. **Context Propagation**: Groups passed to all backend services
4. **Database Filtering**: Cosmos DB queries filter by rbacGroups
5. **Search Filtering**: AI Search applies security filters (rbacGroups eq 'group')
6. **Citation Validation**: Only return citations user has access to

### Example
User in group "legal-team" queries jurisprudence:
```sql
-- Cosmos DB Query
SELECT * FROM documents d
WHERE ARRAY_CONTAINS(d.rbacGroups, 'legal-team')

-- AI Search Filter
search.in(rbacGroups, 'legal-team', ',')
```
```

#### 2. `docs/architecture/folder-schemas.md`
**Estimated**: 600-800 lines

**Structure**:
```markdown
# EVA Suite Folder Schemas

## Core Trunks

### eva-orchestrator (SDLC Automation)
/docs/
  /architecture/ - Architecture documentation (THIS FILE)
  /eva-patterns/ - P00-P15 devtools patterns
  /gc-agentic-framework/ - C0-C3 autonomy levels
  /intake/ - P02 requirements intake
    /processed/ - Approved requirements
    /pending/ - Awaiting P02 processing
  /features/ - Feature specifications
  /sprint-plans/ - Agile sprint planning
  /compliance/ - INFxx/SECxx/UIxx requirements
/scripts/ - Automation scripts (bash, PowerShell, Python)
/agents/ - Agent configurations (governance-registry.yaml, cdd-inventory.yaml)
/_progress/ - Live task queue and metrics
/.github/workflows/ - GitHub Actions CI/CD
/cdds/ - Component Design Documents
/prompts/ - Agent prompt templates
/tools/ - Development tooling

### eva-rag (RAG Engine)
/docs/ - RAG-specific documentation
/src/ - Python source code
  /ingest/ - Document ingestion pipelines
  /chunking/ - Chunking strategies
  /embedding/ - Vector embedding utilities
  /search/ - Hybrid search implementation
  /evaluation/ - RAG evaluation metrics
/data-sources/ - P02-ready data source definitions
  /jurisprudence/ - Legal case law sources
  /assistme/ - Government assistance docs
  /_templates/ - Business analyst templates
/scripts/ - Ingestion automation scripts
/tests/ - Unit and integration tests

### eva-sovereign-ui (UI Components)
/packages/eva-sovereign-ui-wc/ - Lit web components library
/themes/ - Theme definitions (canada-gc)
/docs/ - Component documentation
/storybook/ - Component showcase
/.storybook/ - Storybook configuration

### eva-meta (Governance & Registry)
/docs/ - Governance documentation
/registry/ - Product and persona registry
/compliance/ - Compliance artifacts

### eva-matrix (Public Narrative)
/docs/ - Public-facing documentation
/website/ - Static site generator content

### eva-mcp (MCP Servers)
/servers/ - MCP server implementations
  /filesystem/ - Filesystem MCP server
  /github/ - GitHub MCP server
  /azure/ - Azure MCP server
/docs/ - MCP integration guides

## Supporting Repos

### eva-foundation (Azure Functions Backend)
/functions/ - Azure Function apps
  /documents/ - Document CRUD operations
  /search/ - Search API endpoints
  /auth/ - Authentication middleware
/shared/ - Shared utilities and models

### eva-infra (Infrastructure as Code)
/bicep/ - Azure Bicep templates
  /cosmos-db.bicep - Cosmos DB definitions
  /ai-search.bicep - AI Search definitions
  /apim.bicep - APIM gateway configuration
/terraform/ - Terraform modules (legacy)

## File Naming Conventions
- **Kebab-case**: File names (my-component.ts, user-service.py)
- **PascalCase**: TypeScript classes (UserService, DocumentModel)
- **camelCase**: Functions and variables (getUserById, documentCount)
- **UPPER_SNAKE_CASE**: Constants (MAX_CHUNK_SIZE, API_VERSION)

## Decision Tree: Where Should I Add...?

**SDLC Automation** → eva-orchestrator
- Sprint planning → docs/sprint-plans/
- Automation script → scripts/
- P02 requirement → docs/intake/
- Agent config → agents/

**RAG Engine** → eva-rag
- Ingestion pipeline → src/ingest/
- Data source definition → data-sources/[source-name]/
- Chunking strategy → src/chunking/
- Search optimization → src/search/

**UI Component** → eva-sovereign-ui
- Web component → packages/eva-sovereign-ui-wc/
- Theme customization → themes/canada-gc/
- Component docs → docs/

**Governance Doc** → eva-meta
- Product registry → registry/
- Compliance artifact → compliance/

**Public Narrative** → eva-matrix
- Marketing content → docs/
- Website page → website/

**MCP Server** → eva-mcp
- New MCP server → servers/[server-name]/
- Integration guide → docs/

**Backend Function** → eva-foundation
- API endpoint → functions/
- Shared model → shared/models/

**Infrastructure** → eva-infra
- Azure resource → bicep/[resource].bicep
- IaC module → terraform/modules/
```

#### 3. `docs/architecture/spxx-pxx-mapping.md`
**Estimated**: 400-600 lines

**Structure**:
```markdown
# SPxx vs Pxx Mapping

## Conceptual Split

### SPxx (Service Personas) - What Users See
Service Personas are live agents/bots operating within EVA products:
- Have C0-C3 autonomy levels per GC Agentic Framework
- Interact with end users (public servants, citizens)
- Governed by INFxx/SECxx/UIxx requirements
- Examples: SP01-EVA-Chat-Assistant, SP03-Jurisprudence-Research-Assistant

### Pxx (Devtools Patterns) - How We Build
Devtools Patterns are internal development workflows used by Agile Crew:
- Used for sprint-based delivery
- Enable agent-driven automation (P02, P03, P04)
- No end-user interaction
- Examples: P02-REQ (requirements), P03-SCR (scrum), P04-LIB (documentation)

## SPxx → Repo Mapping

| Service Persona | Code Repos | Data Collections (Cosmos DB) | AI Search Indexes |
|----------------|------------|------------------------------|-------------------|
| SP01-EVA-Chat-Assistant | eva-agent, eva-api, eva-foundation | sessions, messages, users | assistme-index |
| SP02-EVA-Data-Ingestion | eva-rag | documents, chunks | (publishes to all indexes) |
| SP03-Jurisprudence-Research-Assistant | eva-agent, eva-foundation | sessions, documents, chunks | jurisprudence-index |
| SP04-Legislation-Research-Assistant | eva-agent, eva-foundation | sessions, documents, chunks | canl-index |

## Pxx → Folder Mapping

| Devtools Pattern | Primary Repos | Key Folders | Deliverables |
|------------------|---------------|-------------|--------------|
| P02-REQ | eva-orchestrator | docs/intake/, cdds/ | requirements.json, P02 specs |
| P03-SCR | eva-orchestrator | _progress/, docs/sprint-plans/ | task-queue.json, sprint reports |
| P04-LIB | eva-orchestrator, all repos | docs/ | README.md, architecture docs |
| P05-SCA | eva-orchestrator | scripts/scaffolding/ | Project templates |
| P06-RAG | eva-rag | src/, data-sources/ | Ingestion pipelines |
| P12-UXA | eva-sovereign-ui | packages/, themes/ | UI components |

## Autonomy Levels (C0-C3)

### C0: Observation Only
- Agent observes but doesn't act
- Example: Monitoring dashboard

### C1: Assisted Action (Human Approval)
- Agent suggests, human approves
- Example: SP01 chat assistant (requires human to review responses)

### C2: Bounded Autonomy
- Agent acts within predefined boundaries
- Example: SP02 data ingestion (can run pipelines, cannot modify schemas)

### C3: Full Autonomy
- Agent acts independently
- Example: P02 requirements refinement (generates specs without approval)
```

---

## 📅 Implementation Timeline

### Sprint 1 (V1.0 - Core Data Model): 5-7 Days

**Day 1-2: Data Model Discovery**
- Analyze `eva-infra/bicep/` for Cosmos DB container definitions
- Analyze `eva-foundation/functions/` for document schemas
- Analyze `eva-rag/src/` for AI Search index configs
- Extract entity schemas and relationships

**Day 3-4: Data Flow Mapping**
- Map ingestion pipeline (PDF → chunking → embedding → indexing)
- Map retrieval flow (query → search → context → LLM → response)
- Map APIM routing (client → auth → rate limit → backend)
- Create Mermaid diagrams

**Day 5: Documentation**
- Write `docs/architecture/eva-data-model.md`
- Include schemas, diagrams, RBAC patterns
- Generate ER diagrams

**Day 6-7: Review & Refinement**
- Marco review and feedback
- Iterate based on clarifications

### Sprint 2 (V1.1 - Folder Schemas + Mapping): 5-7 Days

**Day 1-2: Folder Schema Analysis**
- Document core trunk folder structures (6 repos)
- Extract file naming conventions
- Identify module organization patterns

**Day 3-4: SPxx/Pxx Mapping**
- Map service personas to repos/collections
- Map devtools patterns to folders/deliverables
- Create reference tables

**Day 5: Documentation**
- Write `docs/architecture/folder-schemas.md`
- Write `docs/architecture/spxx-pxx-mapping.md`

**Day 6-7: Review & Refinement**
- Marco review and feedback
- Iterate based on clarifications

---

## 🎯 Success Criteria

### Must Have (V1.0):
- ✅ All Cosmos DB collections documented (documents, chunks, users, sessions)
- ✅ All AI Search indexes documented (jurisprudence, assistme, canl)
- ✅ Data flow diagrams (ingestion, retrieval, APIM)
- ✅ RBAC enforcement pattern documented
- ✅ ER diagrams showing entity relationships

### Should Have (V1.1):
- ✅ Core trunk folder schemas (6 repos)
- ✅ SPxx/Pxx conceptual split explained
- ✅ "Where should I add...?" decision tree

### Could Have (V2.0):
- ⏳ Automated folder schema validation
- ⏳ Visual architecture diagrams (draw.io/Figma)
- ⏳ Interactive data model explorer

---

## 🔗 Dependencies

**Blocks**:
- ❌ **EVA Data Pipeline** (Phase 1: P02 Generator) - Needs schemas to generate pipelines
- ❌ **New Data Source Ingestion** - Needs defined Cosmos DB and AI Search schemas
- ❌ **RAG Optimization** - Needs documented chunking and indexing strategies

**Depends On**:
- ✅ LESSON-001 (Folder trees 1600x faster) - Can use for discovery
- ✅ LESSON-005 (Workspace architecture zoning) - Foundation already established
- ✅ CDD Inventory (agents/cdd-inventory.yaml) - Defines eva-rag depth requirements

**References**:
- `eva-infra/bicep/` - IaC templates with schema definitions
- `eva-foundation/functions/` - Backend code with entity models
- `eva-rag/src/` - RAG implementation with indexing logic
- `agents/governance-registry.yaml` - SPxx/Pxx definitions
- `docs/gc-agentic-framework/` - C0-C3 autonomy levels

---

## 🚀 Next Steps

1. **Immediate** (Today):
   - [ ] Marco approval to proceed with Sprint 1
   - [ ] Create task in `_progress/TASK-QUEUE.json`
   - [ ] Assign P04-LIB agent for documentation work

2. **Sprint 1 Kickoff** (Dec 9-15):
   - [ ] Analyze eva-infra bicep templates for schemas
   - [ ] Analyze eva-foundation functions for models
   - [ ] Analyze eva-rag for indexing configs
   - [ ] Create eva-data-model.md with complete schemas

3. **After V1.0 Completion**:
   - [ ] Unblock EVA Data Pipeline Phase 1
   - [ ] Resume P02 Generator implementation
   - [ ] Update Copilot instructions with new data model docs
   - [ ] Socialize with Agile Crew

---

## 📊 Impact

**EVA Data Pipeline** (Waiting on This):
- $500K annual savings blocked
- 8-week implementation paused
- 10 data sources by Week 8 delayed
- 50+ sources by Month 3 at risk

**Developer Onboarding** (Waiting on This):
- New developers across 40+ products cannot navigate efficiently
- 50% onboarding time reduction blocked
- "Where should I add...?" questions unanswered

**Agile Crew** (Waiting on This):
- P02/P03/P04 agents need schemas to generate correct code
- CDD recursion depth 5 (eva-rag) cannot be achieved without data model

**Estimated ROI of Foundation Work**:
- Investment: 10-14 days ($15K-$20K)
- Unblocks: $500K annual savings (EVA Data Pipeline)
- Reduces: 50% onboarding time across 40+ products
- Enables: Agent-driven development with correct schemas

---

## 🎓 Related Documentation

- **Source Intake**: `eva-orchestrator/docs/intake/processed/P02-AUTO-3fc7c655-p02-req-001-eva-data-model.md` (400 lines)
- **CDD Requirements**: `eva-orchestrator/agents/cdd-inventory.yaml` (eva-rag: depth 5)
- **EVA Data Pipeline**: `eva-rag/docs/features/EVA-DATA-PIPELINE.md` (1,000 lines, APPROVED)
- **Implementation Roadmap**: `eva-rag/docs/EVA-DATA-PIPELINE-ROADMAP.md` (800 lines, PAUSED)
- **Data Inventory**: `eva-rag/docs/DATA-INVENTORY-FOR-REVIEW.md` (1,272 documents)
- **Organization Standard**: `eva-rag/docs/DATA-SOURCE-ORGANIZATION-STANDARD.md` (P02-ready structure)

---

**CONVERSATION STATUS**: ⏸️ PAUSED - TO BE PROGRESSED  
**BLOCKING ITEM**: EVA Data Model Foundation (this document)  
**RESUME WHEN**: V1.0 deliverables complete (Cosmos DB schemas, AI Search indexes, data flows documented)

---

**Prepared by**: GitHub Copilot  
**Date**: December 8, 2024  
**Review Required**: Marco Presta (PO)
