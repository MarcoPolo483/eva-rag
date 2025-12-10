---
name: EVA Multi-Tenant Architecture Implementation
about: Implement Space-based multi-tenant architecture with sandbox-to-production lifecycle
title: '[EPIC] EVA Multi-Tenant Architecture: Sandbox to Production Spaces'
labels: ['epic', 'architecture', 'high-priority', 'enhancement']
assignees: ''
---

## 📋 Epic Overview

**Objective**: Enable AICOE Business Analysts to create isolated EVA Domain Assistant "Spaces" that clients can trial (sandbox) and promote to production with full customization, cost segregation, and security isolation.

**Priority**: 🔴 CRITICAL - Foundation for EVA 2.0 business model  
**Estimated Effort**: 12-16 weeks (4 phases)  
**Estimated Value**: $2M+ annual revenue from production Spaces + $500K savings from automation

---

## 🎯 Business Context

### Current State (EVA Domain Assistant)
- 50 hard-coded AI Search indexes
- RBAC-only segregation (shared infrastructure)
- Fixed UI/UX, RAG parameters, system prompts
- Cannot trial new clients easily
- Cannot isolate costs per client
- Requires code deployment for new indexes

### Desired State (EVA 2.0)
- **N Dynamic Spaces** (sandbox + production)
- **Business Analyst Self-Service**: Create Space in 5 minutes via admin portal
- **Full Customization**: UI/UX, RAG parameters, system prompts, data sources
- **Cost Segregation**: Track and bill per Space
- **Security Isolation**: Logical (sandbox) or physical (production)
- **Lifecycle Management**: Sandbox → Production promotion

---

## 🏗️ Architecture Overview

### Space Types

#### Sandbox (Trial)
- **Purpose**: 30-90 day client evaluation
- **Isolation**: Logical (shared infrastructure, RBAC + HPK filtering)
- **Cost**: $200-$500/month
- **Data**: 150 starter documents (curated)
- **Quotas**: 10K tokens/month, 100 queries/day
- **UI**: EVA DA Accelerator template (configurable)

#### Production Support
- **Purpose**: Production service with SLA
- **Isolation**: Physical (dedicated AI Search indexes, Cosmos DB containers)
- **Cost**: $5K-$50K/month (based on usage)
- **Data**: 1,000-10,000+ custom documents
- **Quotas**: 1M+ tokens/month, unlimited queries
- **UI**: Fully customized (client branding)
- **SLA**: 99.9% uptime, <2s response time

### Key Components

```
Space
├── spaceId (unique identifier)
├── Infrastructure
│   ├── Sandbox: Shared (Cosmos HPK, AI Search filter)
│   └── Production: Dedicated (indexes, containers, functions)
├── Configuration (Business Analyst editable)
│   ├── UI/UX (logo, colors, layout, components)
│   ├── RAG (chunking, embedding, search, reranking)
│   ├── Prompts (system prompt, persona, guardrails)
│   └── Data Sources (ingestion pipelines)
├── Billing (cost tracking per Space)
└── Users (RBAC with Azure AD)
```

---

## 📦 Implementation Phases

### Phase 1: Foundation & Sandbox MVP (Weeks 1-4)

**Goal**: Enable Business Analysts to create sandbox Spaces with logical isolation

#### Tasks

**1.1 Data Model Extension**
- [ ] Create `spaces` collection in Cosmos DB
  - Schema: spaceId, spaceName, spaceType (sandbox/production), status, owner, billing, infrastructure, configuration
  - Partition key: `/spaceId`
- [ ] Add `spaceId` field to existing collections (documents, chunks, sessions)
  - Update Hierarchical Partition Key: `/spaceId/tenantId/userId`
- [ ] Migration script: Assign existing data to default Space
- [ ] **Acceptance**: `spaces` collection created, existing collections updated, migration tested

**1.2 Backend API (Space Management)**
- [ ] `POST /api/v1/spaces` - Create new sandbox Space
  - Input: spaceName, owner email, duration (days)
  - Output: spaceId, Space URL, configuration
  - Logic: Create Space record, initialize default config (EVA DA Accelerator), provision RBAC
- [ ] `GET /api/v1/spaces` - List Spaces (filtered by user permissions)
- [ ] `GET /api/v1/spaces/{spaceId}` - Get Space details
- [ ] `PUT /api/v1/spaces/{spaceId}` - Update Space metadata
- [ ] `DELETE /api/v1/spaces/{spaceId}` - Soft delete Space (archive data)
- [ ] **Acceptance**: All CRUD endpoints functional, RBAC enforced, integration tests pass

**1.3 Configuration Management**
- [ ] `GET /api/v1/spaces/{spaceId}/ui-config` - Get UI configuration
- [ ] `PUT /api/v1/spaces/{spaceId}/ui-config` - Update UI configuration
  - JSON schema validation (logo URL, colors, layout, components, i18n)
- [ ] `GET /api/v1/spaces/{spaceId}/rag-config` - Get RAG configuration
- [ ] `PUT /api/v1/spaces/{spaceId}/rag-config` - Update RAG configuration
  - JSON schema validation (chunking, embedding, search, reranking, context)
- [ ] `GET /api/v1/spaces/{spaceId}/prompts` - Get system prompts
- [ ] `PUT /api/v1/spaces/{spaceId}/prompts` - Update system prompts
  - JSON schema validation (systemPrompt, persona, guardrails, responseTemplates)
- [ ] **Acceptance**: Configuration endpoints functional, validation working, configs persisted

**1.4 Space-Aware Query Filtering**
- [ ] Update Cosmos DB queries to filter by `spaceId`
  - Example: `SELECT * FROM documents d WHERE d.spaceId = @spaceId AND ...`
- [ ] Update AI Search queries to filter by `spaceId`
  - Example: `filter: "spaceId eq 'sandbox-client-a' and rbacGroups/any(...)"`
- [ ] Add `spaceId` claim to JWT token (from Azure AD or Space membership)
- [ ] Backend middleware: Extract `spaceId` from token, validate user access
- [ ] **Acceptance**: Cross-Space data leakage tests pass (100% isolation)

**1.5 EVA DA Accelerator Template**
- [ ] Define default UI configuration (canada-gc theme, standard layout)
- [ ] Define default RAG configuration (semantic chunking, hybrid search, no reranking)
- [ ] Define default system prompt ("You are EVA, a Government of Canada assistant...")
- [ ] Provision starter data sources (100 jurisprudence cases, 50 assistme docs)
- [ ] **Acceptance**: New sandbox Space has working UI, RAG, prompts out-of-box

**1.6 Business Analyst Admin Portal (Basic)**
- [ ] Create Space form (spaceName, owner, duration)
- [ ] Space list view (filter by status: active, trial, archived)
- [ ] Space detail view (metadata, users, usage stats)
- [ ] Basic configuration UI (logo upload, color picker, prompt editor)
- [ ] **Acceptance**: BA can create and configure sandbox Space via UI

**1.7 Testing & Pilot**
- [ ] Deploy 3 pilot sandbox Spaces (internal users)
- [ ] Test isolation: Verify users in Space A cannot see data from Space B
- [ ] Test configuration: Verify UI/RAG/prompt changes apply correctly
- [ ] Performance testing: Measure query latency with 10 concurrent Spaces
- [ ] **Acceptance**: 3 sandboxes operational, isolation verified, performance acceptable

---

### Phase 2: Production Support (Weeks 5-8)

**Goal**: Enable promotion to production with dedicated infrastructure

#### Tasks

**2.1 Infrastructure as Code (Bicep Templates)**
- [ ] `prod-space-ai-search.bicep` - Provision dedicated AI Search service
  - Parameters: spaceId, tier (S1/S2/S3), replicas, partitions
  - Resources: Azure AI Search service, indexes (jurisprudence, assistme, custom)
- [ ] `prod-space-cosmos-db.bicep` - Provision dedicated Cosmos DB containers
  - Parameters: spaceId, autoscale RU/s (4K-400K)
  - Resources: documents, chunks, sessions, users containers with HPK
- [ ] `prod-space-functions.bicep` - Provision dedicated Azure Functions app
  - Parameters: spaceId, plan (Premium P1/P2/P3)
  - Resources: Function app with VNet integration, private endpoints
- [ ] **Acceptance**: Bicep templates deploy successfully, resources created with correct naming

**2.2 Promotion Workflow (Sandbox → Production)**
- [ ] `POST /api/v1/spaces/{spaceId}/promote` - Initiate promotion
  - Input: productionTier (standard/enterprise), estimatedBudget, goLiveDate
  - Output: promotionRequestId, estimated timeline
  - Logic: Create infrastructure provisioning task, queue Bicep deployment
- [ ] Background job: Execute Bicep templates (10-30 minutes)
- [ ] Data migration: Copy documents, chunks, sessions from sandbox to production containers
  - Use Cosmos DB bulk operations (optimize for <1 hour migration)
- [ ] DNS/URL update: Redirect sandbox URL to production URL
- [ ] `GET /api/v1/spaces/{spaceId}/promotion-status` - Check promotion progress
- [ ] **Acceptance**: Sandbox promotes to production in <2 hours, data migrated, users can access

**2.3 Cost Tracking & Billing**
- [ ] Implement cost metering per Space
  - Track: AI Search queries, Cosmos DB RU/s, Azure Functions executions, Storage GB
- [ ] `GET /api/v1/spaces/{spaceId}/billing` - Get monthly billing summary
  - Output: aiSearch, cosmosDb, azureFunctions, storage, total (USD)
- [ ] `GET /api/v1/spaces/{spaceId}/usage` - Get usage metrics
  - Output: tokensUsed, queriesUsed, documentsCount, chunksCount
- [ ] Quota enforcement: Block queries if Space exceeds token/query limits
- [ ] **Acceptance**: Billing API returns accurate costs, quotas enforced

**2.4 Advanced Admin Portal**
- [ ] Promote Space UI (initiate promotion, track progress)
- [ ] Cost dashboard (monthly spend, usage trends, quota status)
- [ ] Infrastructure view (AI Search tier, Cosmos RU/s, Functions plan)
- [ ] Advanced configuration UI (RAG tuning sliders, custom prompt templates)
- [ ] **Acceptance**: BA can promote Space and monitor costs via UI

**2.5 Testing & Pilot**
- [ ] Deploy 2 pilot production Spaces (early adopter clients)
- [ ] Load testing: Validate <2s response time under 100 concurrent queries
- [ ] Failover testing: Validate 99.9% uptime (simulate region outage)
- [ ] Cost validation: Compare billed costs to Azure Cost Management
- [ ] **Acceptance**: 2 production Spaces meet SLA, costs accurate

---

### Phase 3: EVA Data Pipeline Integration (Weeks 9-12)

**Goal**: Enable Space-specific data source ingestion via EVA Data Pipeline

#### Tasks

**3.1 Space-Aware Data Ingestion**
- [ ] Update ingestion scripts to accept `spaceId` parameter
  - Example: `python ingest.py --space-id sandbox-client-a --source jurisprudence`
- [ ] Update Cosmos DB writes to include `spaceId` field
- [ ] Update AI Search indexing to include `spaceId` field
- [ ] **Acceptance**: Ingestion writes data to correct Space partition/index

**3.2 P02 Generator Enhancement**
- [ ] Extend `requirements.json` schema to include `spaceId`
- [ ] P02 generates ingestion pipelines with Space-specific config
  - Read Space's RAG config (chunking, embedding)
  - Read Space's data source definitions
  - Generate `ingest_[source]_[spaceId].py` script
- [ ] **Acceptance**: P02 generates Space-aware pipelines

**3.3 Business Analyst Data Source Requests**
- [ ] `GET /api/v1/spaces/{spaceId}/data-sources` - List data sources
- [ ] `POST /api/v1/spaces/{spaceId}/data-sources` - Request new data source
  - Input: sourceName, sourceType, sourceUrl, schedule
  - Output: dataSourceId, ingestion pipeline spec
  - Logic: Create P02 requirements.json, trigger P02 generation
- [ ] Admin portal: Data source request form
- [ ] **Acceptance**: BA can request data source ingestion via UI

**3.4 Testing & Pilot**
- [ ] Ingest 5 new data sources across 3 Spaces
- [ ] Validate: Data appears in correct Space only
- [ ] Validate: RAG config applied correctly (chunking, embedding)
- [ ] **Acceptance**: 5 data sources ingested, isolated per Space

---

### Phase 4: Scale & Polish (Weeks 13-16)

**Goal**: Production-ready system, onboard 20+ Spaces

#### Tasks

**4.1 Self-Service Sandbox Creation**
- [ ] Public-facing form: Clients can request sandbox (no BA required)
  - Input: Organization name, use case, contact email
  - Output: Sandbox provisioned in 5 minutes, invitation email sent
- [ ] Automated approval workflow (review requests, auto-approve low-risk)
- [ ] **Acceptance**: Clients can request sandboxes, 80% auto-approved

**4.2 Analytics & Monitoring**
- [ ] Space health dashboard (uptime, query latency, error rate)
- [ ] Usage analytics (most queried topics, user engagement, feedback scores)
- [ ] Cost optimization recommendations (suggest tier downgrades, optimize RU/s)
- [ ] **Acceptance**: Dashboard shows real-time metrics for all Spaces

**4.3 Advanced Features**
- [ ] A/B testing: Compare RAG configurations within same Space
- [ ] Custom RAG models: Upload fine-tuned embedding models
- [ ] White-label support: Custom domains (eva.client-a.gc.ca)
- [ ] **Acceptance**: Advanced features functional for enterprise Spaces

**4.4 Documentation & Training**
- [ ] Business Analyst guide: Creating and managing Spaces
- [ ] Client guide: Using EVA in your Space
- [ ] Developer guide: Adding Space-aware features
- [ ] **Acceptance**: Guides published, 5 BAs trained

**4.5 Production Launch**
- [ ] Onboard 10 sandbox Spaces (real clients)
- [ ] Convert 5 sandbox → production
- [ ] Monitor for 30 days (24/7 support)
- [ ] **Acceptance**: 15 Spaces operational, <5 P1 incidents/month

---

## 🔒 Security & Compliance Requirements

### Sandbox (Logical Isolation)
- [ ] Hierarchical Partition Key (HPK): `/spaceId/tenantId/userId`
- [ ] AI Search filter: `spaceId eq '{spaceId}'` on every query
- [ ] RBAC: JWT token includes `spaceId` claim, backend validates access
- [ ] Isolation testing: 100% pass rate (no cross-Space data leakage)
- [ ] **Data Classification**: Unclassified only

### Production (Physical Isolation)
- [ ] Dedicated AI Search indexes per Space
- [ ] Dedicated Cosmos DB containers per Space
- [ ] VNet integration with private endpoints (no public internet)
- [ ] Encryption at rest: Cosmos DB, AI Search, Blob Storage
- [ ] Encryption in transit: TLS 1.2+
- [ ] Audit logging: All queries, all data access (Azure Monitor)
- [ ] **Data Classification**: Protected B supported

### Compliance
- [ ] RBAC aligned with GC Agentic Framework (C0-C3 autonomy)
- [ ] Data residency: Canada Central (Azure region)
- [ ] Regular security audits (quarterly)
- [ ] Penetration testing before production launch

---

## 📊 Success Metrics

### Business KPIs
- [ ] **Sandbox Conversion Rate**: 60% convert to production (target)
- [ ] **Time-to-Trial**: <1 day from request to sandbox live
- [ ] **Time-to-Production**: <2 weeks from approval to production live
- [ ] **Client Satisfaction**: NPS >50
- [ ] **Revenue**: $2M+ annual from production Spaces

### Technical KPIs
- [ ] **Isolation**: 0 cross-Space data leakage incidents
- [ ] **Performance**: <2s average response time (production), <3s (sandbox)
- [ ] **Uptime**: 99.9% (production SLA)
- [ ] **Cost Predictability**: 95% of Spaces within budget ±10%

### Operational KPIs
- [ ] **BA Efficiency**: 1 BA manages 20 sandboxes + 5 production Spaces
- [ ] **Configuration**: 95% of changes via admin portal (no code)
- [ ] **Data Source Onboarding**: <2 days from request to ingestion

---

## 🧩 Dependencies

### Blocks
- ❌ EVA Data Model Foundation (REQ-001, Sprint 1) - **MUST COMPLETE FIRST**
  - Need: Cosmos DB schemas with `spaceId` HPK
  - Need: AI Search index schemas with `spaceId` field
  - Need: RBAC patterns documented

### Integrates With
- 🔗 EVA Data Pipeline (P06-RAG) - Space-aware ingestion
- 🔗 EVA Sovereign UI - Space-aware UI components
- 🔗 EVA Foundation (Azure Functions) - Space filtering middleware

---

## 📚 Reference Documentation

**Architecture**:
- `eva-rag/docs/EVA-MULTI-TENANT-ARCHITECTURE.md` (12,000 lines, complete vision)
- `eva-rag/docs/EVA-DATA-MODEL-FOUNDATION-REQUIREMENTS.md` (prerequisite)

**Related Features**:
- `eva-rag/docs/features/EVA-DATA-PIPELINE.md` (data ingestion automation)
- `eva-rag/docs/EVA-DATA-PIPELINE-ROADMAP.md` (implementation timeline)

**Governance**:
- `eva-orchestrator/agents/governance-registry.yaml` (SPxx personas, autonomy levels)
- `eva-orchestrator/agents/cdd-inventory.yaml` (CDD depth requirements)

---

## 🚀 Getting Started

### For GitHub Team

1. **Review Prerequisites**:
   - Read `EVA-MULTI-TENANT-ARCHITECTURE.md` (full vision)
   - Verify EVA Data Model Foundation (REQ-001) is complete
   - Confirm Cosmos DB + AI Search schemas include `spaceId`

2. **Phase 1 Kickoff** (Week 1):
   - Assign tasks 1.1-1.7 to team members
   - Create feature branches: `feature/multi-tenant-phase-1`
   - Daily standups to track progress

3. **Development Environment**:
   - Clone `eva-rag` repo
   - Set up local Cosmos DB emulator + AI Search service (or use dev environment)
   - Run existing tests: `pytest --cov`

4. **Testing Strategy**:
   - Unit tests: 90%+ coverage for new code
   - Integration tests: All API endpoints
   - Isolation tests: Verify cross-Space data leakage prevention
   - Performance tests: <3s response time with 10 concurrent Spaces

5. **Code Review & Merge**:
   - All PRs require 2 approvals
   - Merge to `develop` branch after tests pass
   - Deploy to staging for BA testing
   - Merge to `main` after BA approval

---

## ✅ Definition of Done

### Phase 1 Complete When:
- [ ] `spaces` collection created and tested
- [ ] All Space management APIs functional
- [ ] Configuration APIs functional (UI, RAG, prompts)
- [ ] Space-aware query filtering working (100% isolation)
- [ ] EVA DA Accelerator template deployed
- [ ] BA admin portal deployed
- [ ] 3 pilot sandboxes operational
- [ ] All tests pass (unit, integration, isolation, performance)
- [ ] Documentation complete (API docs, BA guide)

### Entire Epic Complete When:
- [ ] All 4 phases complete
- [ ] 10 sandbox Spaces + 5 production Spaces operational
- [ ] Success metrics achieved (conversion rate, uptime, performance)
- [ ] Security audit passed
- [ ] Client satisfaction >50 NPS
- [ ] BA training complete (5 BAs certified)

---

## 🎓 Questions & Support

**For Architecture Questions**: Tag @marco-presta or reference `EVA-MULTI-TENANT-ARCHITECTURE.md`  
**For Implementation Help**: Comment on this issue or create sub-tasks  
**For EVA Data Model**: See REQ-001 (prerequisite, must complete first)  

---

**Prepared by**: Marco Presta (PO) + GitHub Copilot  
**Date**: December 8, 2024  
**Epic Owner**: GitHub Team (to be assigned)  
**Estimated Timeline**: 12-16 weeks (4 phases)  
**Estimated Value**: $2M+ annual revenue + $500K savings
