# EVA Multi-Tenant Architecture: Sandbox to Production

**Status**: 🎯 VISION DOCUMENT  
**Priority**: 🔴 CRITICAL - FOUNDATION FOR EVA DATA MODEL  
**Date**: December 8, 2024  
**Context**: Extends EVA Data Model with multi-tenant isolation and cost governance

---

## 📋 Executive Summary

**Vision**: Enable AICOE Business Analysts to create isolated EVA Domain Assistant (EVA DA) "Spaces" as sandboxes for clients to trial the service, then seamlessly promote to production with full customization while maintaining cost segregation and security isolation.

**Key Principle**: **Everything is a Space**
- Each Space = Isolated tenant with dedicated resources
- Sandboxes share infrastructure but are logically isolated
- Production Spaces get dedicated indexes and infrastructure
- Business Analysts control all configuration (no code changes)

**Differentiation from Today**:
- **Current**: 50 hard-coded indexes in EVA Domain Assistant, RBAC-segregated (single-tier, monolithic)
- **EVA 2.0**: N Spaces (dynamic), each with configurable indexes, RAG parameters, UI/UX, system prompts, data sources

---

## 🎯 Vision: The Space Lifecycle

### Stage 1: Sandbox (Trial)
**Duration**: 30-90 days  
**Owner**: AICOE Business Analyst  
**Purpose**: Client evaluation, proof-of-concept, requirements discovery

**Characteristics**:
- ✅ Shared infrastructure (cost-effective)
- ✅ Logical isolation (RBAC + partition keys)
- ✅ Basic UI/UX (EVA DA Accelerator template)
- ✅ Starter data sources (10-20 curated documents)
- ✅ Standard system prompts
- ✅ Usage quotas (10K tokens/month, 100 queries/day)

**Cost Model**: $200-$500/month (shared infrastructure, metered usage)

### Stage 2: Production Support
**Duration**: Ongoing subscription  
**Owner**: Client IT team + AICOE Business Analyst (co-managed)  
**Purpose**: Production-grade service with SLA, performance guarantees, full customization

**Characteristics**:
- ✅ Dedicated infrastructure (isolated indexes, compute, storage)
- ✅ Physical + logical isolation (separate AI Search indexes, Cosmos DB partitions)
- ✅ Custom UI/UX (client branding, colors, layouts, components)
- ✅ Client-specific data sources (100-1000+ documents)
- ✅ Custom system prompts (tone, persona, guardrails)
- ✅ Advanced RAG tuning (chunking, embedding models, reranking)
- ✅ Performance SLA (99.9% uptime, <2s response time)
- ✅ Usage quotas (1M tokens/month, unlimited queries)

**Cost Model**: $5K-$50K/month (dedicated infrastructure, enterprise SLA)

---

## 🏗️ Architecture: Data Segregation by Space

### Isolation Levels

#### Level 1: Logical Isolation (Sandbox)
**Shared Infrastructure, Logical Boundaries**

```
Azure AI Search (Shared)
├── sandbox-index (all sandboxes)
│   ├── spaceId: "sandbox-client-a" (RBAC filter)
│   ├── spaceId: "sandbox-client-b" (RBAC filter)
│   └── spaceId: "sandbox-client-c" (RBAC filter)

Cosmos DB (Shared)
├── documents (container)
│   ├── /spaceId=sandbox-client-a/userId=... (HPK)
│   ├── /spaceId=sandbox-client-b/userId=... (HPK)
│   └── /spaceId=sandbox-client-c/userId=... (HPK)
├── chunks (container)
│   ├── /spaceId=sandbox-client-a/userId=... (HPK)
│   └── ...
└── sessions (container)
    ├── /spaceId=sandbox-client-a/userId=... (HPK)
    └── ...
```

**Security**:
- Hierarchical Partition Key (HPK): `/spaceId/userId`
- AI Search filters: `spaceId eq 'sandbox-client-a'`
- RBAC: User token includes `spaceId` claim, backend enforces filtering
- Network: Shared APIM gateway, shared Azure Functions

**Cost Savings**:
- Shared AI Search index (no dedicated index costs)
- Shared Cosmos DB containers (pay per RU/s consumed)
- Shared compute (Azure Functions with consumption plan)
- **Estimated**: $200-$500/month per sandbox (10x cheaper than dedicated)

#### Level 2: Physical Isolation (Production)
**Dedicated Infrastructure, Physical Boundaries**

```
Azure AI Search (Dedicated per Space)
├── prod-client-a-jurisprudence-index
├── prod-client-a-assistme-index
├── prod-client-b-legal-index
└── prod-client-b-hr-index

Cosmos DB (Dedicated per Space)
├── prod-client-a-documents (container)
│   └── /userId=... (HPK, single tenant)
├── prod-client-a-chunks (container)
├── prod-client-b-documents (container)
└── prod-client-b-chunks (container)

Azure Functions (Dedicated per Space)
├── prod-client-a-functions (isolated app)
└── prod-client-b-functions (isolated app)

APIM (Shared Gateway, Dedicated APIs per Space)
├── /api/v1/client-a/... (rate limit: 1M tokens/month)
└── /api/v1/client-b/... (rate limit: 500K tokens/month)
```

**Security**:
- Dedicated AI Search indexes (no cross-contamination)
- Dedicated Cosmos DB containers (physical isolation)
- Optional: Dedicated Azure subscription (billing isolation)
- Network isolation: Virtual Network (VNet) with private endpoints
- Advanced: Azure Private Link for backend-to-backend communication

**Cost Transparency**:
- AI Search: $250-$2,500/month per index (S1-S3 tier)
- Cosmos DB: $500-$5,000/month (autoscale, 4,000-400,000 RU/s)
- Azure Functions: $200-$2,000/month (Premium plan for VNet support)
- Storage: $50-$500/month (Azure Blob for raw documents)
- **Estimated**: $5K-$50K/month per production Space

---

## 🎨 Customization Dimensions

### 1. UI/UX (Business Analyst Configurable)

**Sandbox Template** (EVA DA Accelerator):
```json
{
  "spaceId": "sandbox-client-a",
  "ui": {
    "theme": "canada-gc",
    "branding": {
      "logo": "https://eva-assets.blob.core.windows.net/default-logo.svg",
      "primaryColor": "#26374a",
      "accentColor": "#335075",
      "fontFamily": "Noto Sans"
    },
    "layout": {
      "chatInterface": "standard",
      "sidebar": "collapsible",
      "headerHeight": "64px"
    },
    "components": {
      "enableCitations": true,
      "enableFeedback": true,
      "enableExport": false,
      "enableHistory": true
    },
    "i18n": {
      "defaultLanguage": "en",
      "supportedLanguages": ["en", "fr"]
    }
  }
}
```

**Production Customization**:
```json
{
  "spaceId": "prod-client-a",
  "ui": {
    "theme": "custom-client-a",
    "branding": {
      "logo": "https://client-a.com/logo.svg",
      "primaryColor": "#003366",
      "accentColor": "#ff6b35",
      "fontFamily": "Client A Corporate Font"
    },
    "layout": {
      "chatInterface": "multi-pane",
      "sidebar": "always-visible",
      "headerHeight": "80px",
      "customHeader": "<custom-header-component />"
    },
    "components": {
      "enableCitations": true,
      "enableFeedback": true,
      "enableExport": true,
      "enableHistory": true,
      "enableAnnotations": true,
      "customComponents": [
        "client-a-case-tracker",
        "client-a-document-viewer"
      ]
    },
    "i18n": {
      "defaultLanguage": "fr",
      "supportedLanguages": ["en", "fr", "es"]
    }
  }
}
```

**Configuration Management**:
- Storage: Cosmos DB `spaces` collection
- API: `PUT /api/v1/spaces/{spaceId}/ui-config`
- UI: Business Analyst portal at `https://eva-admin.gc.ca/spaces/{spaceId}/configure`
- Validation: JSON schema validation before save
- Rollback: Version history (last 10 configs)

### 2. RAG Configuration (Business Analyst Configurable)

**Sandbox Template**:
```json
{
  "spaceId": "sandbox-client-a",
  "rag": {
    "chunking": {
      "strategy": "semantic",
      "chunkSize": 1000,
      "chunkOverlap": 200,
      "minChunkSize": 100
    },
    "embedding": {
      "model": "text-embedding-3-large",
      "dimensions": 1536,
      "batchSize": 16
    },
    "search": {
      "type": "hybrid",
      "vectorWeight": 0.5,
      "keywordWeight": 0.5,
      "topK": 10,
      "minScore": 0.7
    },
    "reranking": {
      "enabled": false
    },
    "context": {
      "maxTokens": 4000,
      "includeMetadata": true,
      "citationFormat": "numbered"
    }
  }
}
```

**Production Customization**:
```json
{
  "spaceId": "prod-client-a",
  "rag": {
    "chunking": {
      "strategy": "hybrid-semantic-structural",
      "chunkSize": 1500,
      "chunkOverlap": 300,
      "minChunkSize": 200,
      "respectHeadings": true,
      "respectParagraphs": true
    },
    "embedding": {
      "model": "text-embedding-3-large",
      "dimensions": 3072,
      "batchSize": 32
    },
    "search": {
      "type": "hybrid-rrf",
      "vectorWeight": 0.6,
      "keywordWeight": 0.4,
      "topK": 20,
      "minScore": 0.6,
      "semanticConfiguration": "client-a-legal-semantic"
    },
    "reranking": {
      "enabled": true,
      "model": "cohere-rerank-v3",
      "topN": 10
    },
    "context": {
      "maxTokens": 8000,
      "includeMetadata": true,
      "citationFormat": "inline-with-preview",
      "contextWindow": "adaptive"
    }
  }
}
```

**Advanced RAG Tuning** (Production Only):
- **Chunking Strategies**: Fixed-size, semantic, structural, hybrid
- **Embedding Models**: ada-002 (1536), text-embedding-3-large (3072), multilingual
- **Search Modes**: Vector-only, keyword-only, hybrid (RRF), hybrid (weighted)
- **Reranking**: Cohere, Azure AI, custom models
- **Context Assembly**: Token-based, document-based, sliding window, adaptive

### 3. System Prompts (Business Analyst Configurable)

**Sandbox Template**:
```json
{
  "spaceId": "sandbox-client-a",
  "prompts": {
    "systemPrompt": "You are EVA, a Government of Canada assistant. Provide accurate, helpful answers based on retrieved documents. Always cite your sources.",
    "persona": {
      "tone": "professional",
      "style": "formal",
      "language": "clear and concise"
    },
    "guardrails": {
      "refusals": [
        "I cannot provide legal advice",
        "I cannot disclose personal information",
        "I can only answer based on official documents"
      ],
      "contentSafety": {
        "enabled": true,
        "categories": ["hate", "violence", "sexual", "self-harm"]
      }
    }
  }
}
```

**Production Customization**:
```json
{
  "spaceId": "prod-client-a",
  "prompts": {
    "systemPrompt": "You are EVA-Legal, a specialized legal research assistant for Client A Legal Department. You provide analysis of jurisprudence, legislation, and internal legal policies. Your answers must be precise, well-cited, and aligned with Client A's legal framework.",
    "persona": {
      "tone": "authoritative",
      "style": "analytical",
      "language": "technical legal terminology",
      "expertise": ["employment law", "administrative law", "privacy law"]
    },
    "guardrails": {
      "refusals": [
        "I cannot provide advice that contradicts Client A Legal Policy 2024-03",
        "I cannot disclose privileged attorney-client communications",
        "I can only cite approved legal sources (SCC, FCA, Client A internal policies)"
      ],
      "contentSafety": {
        "enabled": true,
        "categories": ["hate", "violence", "sexual", "self-harm", "legal-compliance"]
      },
      "customChecks": [
        "Verify citation against approved sources list",
        "Flag outdated jurisprudence (>5 years)",
        "Require supervisor approval for novel legal interpretations"
      ]
    },
    "responseTemplates": {
      "legalOpinion": "## Legal Analysis\n\n**Issue**: {issue}\n\n**Applicable Law**: {law}\n\n**Analysis**: {analysis}\n\n**Conclusion**: {conclusion}\n\n**Citations**: {citations}",
      "caseComparison": "## Case Comparison\n\n**Current Case**: {current}\n\n**Precedents**: {precedents}\n\n**Distinguishing Factors**: {factors}\n\n**Recommendation**: {recommendation}"
    }
  }
}
```

### 4. Data Sources (Business Analyst + Data Pipeline)

**Sandbox Template** (Starter Pack):
```json
{
  "spaceId": "sandbox-client-a",
  "dataSources": [
    {
      "sourceId": "starter-jurisprudence",
      "type": "jurisprudence",
      "scope": "curated-top-100-cases",
      "count": 100,
      "languages": ["en", "fr"],
      "classification": "Unclassified"
    },
    {
      "sourceId": "starter-assistme",
      "type": "government-assistance",
      "scope": "top-50-programs",
      "count": 50,
      "languages": ["en", "fr"],
      "classification": "Unclassified"
    }
  ],
  "totalDocuments": 150,
  "totalChunks": 3000,
  "storageUsed": "500 MB"
}
```

**Production Customization**:
```json
{
  "spaceId": "prod-client-a",
  "dataSources": [
    {
      "sourceId": "client-a-jurisprudence",
      "type": "jurisprudence",
      "scope": "all-employment-law-cases",
      "tribunals": ["SCC", "FCA", "FC", "SST"],
      "count": 5000,
      "languages": ["en", "fr"],
      "classification": "Protected B",
      "updateFrequency": "weekly"
    },
    {
      "sourceId": "client-a-internal-policies",
      "type": "internal-policies",
      "scope": "legal-department-policies",
      "count": 200,
      "languages": ["en", "fr"],
      "classification": "Protected B",
      "updateFrequency": "on-demand"
    },
    {
      "sourceId": "client-a-legislation",
      "type": "legislation",
      "scope": "employment-related-acts",
      "count": 50,
      "languages": ["en", "fr"],
      "classification": "Unclassified",
      "updateFrequency": "daily"
    },
    {
      "sourceId": "client-a-external-research",
      "type": "external-research",
      "scope": "subscribed-legal-journals",
      "count": 1000,
      "languages": ["en"],
      "classification": "Protected A",
      "updateFrequency": "monthly"
    }
  ],
  "totalDocuments": 6250,
  "totalChunks": 125000,
  "storageUsed": "50 GB"
}
```

**Data Pipeline Integration**:
- Each Space has dedicated data source definitions in `data-sources/{spaceId}/`
- Business Analyst submits ingestion request via template (no coding)
- P02 generates pipeline with Space-specific configuration
- P03 reviews and approves
- Pipeline runs on schedule, data written to Space-specific partition

---

## 💰 Cost Governance Model

### Cost Tracking by Space

**Cosmos DB**:
```json
{
  "spaceId": "sandbox-client-a",
  "costs": {
    "cosmosDb": {
      "requestUnits": 10000,
      "storage": 500,
      "unit": "MB",
      "costPerMonth": 150
    }
  }
}
```

**AI Search**:
- **Sandbox**: Shared index, metered by query count
- **Production**: Dedicated index, fixed monthly cost

**Azure Functions**:
- **Sandbox**: Consumption plan (pay per execution)
- **Production**: Premium plan (fixed monthly + execution)

**Total Cost Rollup**:
```json
{
  "spaceId": "prod-client-a",
  "monthlyBilling": {
    "aiSearch": 1500,
    "cosmosDb": 3000,
    "azureFunctions": 800,
    "storage": 200,
    "apim": 500,
    "monitoring": 100,
    "total": 6100,
    "currency": "USD"
  },
  "quotas": {
    "tokenLimit": 1000000,
    "tokensUsed": 450000,
    "queryLimit": -1,
    "queriesUsed": 12000
  }
}
```

### Billing Models

#### Sandbox (Trial)
- **Flat Rate**: $200-$500/month (all-inclusive)
- **Quotas**: 10K tokens/month, 100 queries/day
- **Overage**: $0.01/token, $0.10/query

#### Production Support
- **Base Subscription**: $5K/month (includes infrastructure, support, SLA)
- **Metered Usage**: 
  - AI Search queries: $0.50/1000 queries
  - Cosmos DB storage: $0.25/GB/month
  - Cosmos DB RU/s: $0.008/RU/s/hour
  - Azure OpenAI tokens: $0.0001/token
- **Overage**: Same rates as base
- **Custom**: Negotiated for enterprise clients (>$50K/month)

---

## 🚀 Business Analyst Workflow

### Creating a New Sandbox Space

**Step 1: Space Creation Request**
```
Business Analyst navigates to: https://eva-admin.gc.ca/spaces/new

Form:
- Space Name: "Client A Legal Trial"
- Space Type: Sandbox
- Duration: 90 days
- Owner: client-a-legal-lead@example.gc.ca
- Budget: $500/month
- Template: EVA DA Accelerator

[Submit]
```

**Step 2: Automated Provisioning** (5 minutes)
- Create Space record in Cosmos DB `spaces` collection
- Initialize RBAC permissions (owner + Business Analyst)
- Copy EVA DA Accelerator template (UI config, RAG config, system prompts)
- Provision starter data sources (100 jurisprudence cases, 50 assistme docs)
- Generate Space URL: `https://eva-da.gc.ca/spaces/sandbox-client-a`
- Send invitation email to owner

**Step 3: Customization** (2-4 hours)
Business Analyst configures via admin portal:
- Upload client logo
- Adjust color scheme
- Customize system prompt ("You are EVA-Legal for Client A...")
- Tune RAG parameters (chunk size, search mode)
- Add additional data sources (via ingestion request template)

**Step 4: Client Trial** (30-90 days)
- Client users access `https://eva-da.gc.ca/spaces/sandbox-client-a`
- Business Analyst monitors usage (queries, feedback, costs)
- Iterate on configuration based on client feedback
- Decision point: Proceed to production or discontinue

### Promoting to Production

**Step 5: Production Upgrade Request**
```
Business Analyst navigates to: https://eva-admin.gc.ca/spaces/sandbox-client-a/upgrade

Form:
- Confirm: Proceed to Production
- Estimated Monthly Budget: $10,000
- Desired Go-Live Date: 2025-02-01
- SLA Requirements: 99.9% uptime, <2s response time
- Data Sources: [Review and approve 10 proposed sources]
- Custom UI: [Upload design specs]

[Submit for Approval]
```

**Step 6: Infrastructure Provisioning** (1-2 weeks)
- Terraform/Bicep: Provision dedicated AI Search indexes
- Terraform/Bicep: Provision dedicated Cosmos DB containers
- Terraform/Bicep: Provision Premium Azure Functions plan
- Migrate sandbox data to production partitions
- Configure custom domain: `https://eva-legal.client-a.gc.ca`
- Run load testing (validate <2s response time)

**Step 7: Production Launch**
- Final Business Analyst review
- Client IT approval
- Cutover: Redirect users from sandbox URL to production URL
- Monitor for 7 days (24/7 support)
- Handoff to client IT + AICOE support team

---

## 📊 Comparison: Current vs EVA 2.0

### Current EVA Domain Assistant (50 Hard-Coded Indexes)

**Architecture**:
```
Single Azure AI Search Instance
├── Index 01: Legal (RBAC: legal-team)
├── Index 02: HR (RBAC: hr-team)
├── Index 03: Finance (RBAC: finance-team)
├── ...
└── Index 50: Operations (RBAC: ops-team)

All indexes share:
- Same UI/UX (fixed)
- Same system prompts (fixed)
- Same RAG parameters (fixed)
- Same Cosmos DB containers (RBAC-filtered)
```

**Limitations**:
- ❌ Cannot create new index without code deployment
- ❌ Cannot customize UI per client
- ❌ Cannot tune RAG per use case
- ❌ Cannot isolate costs per client
- ❌ Cannot trial new clients easily
- ❌ RBAC only (no physical isolation for sensitive clients)

### EVA 2.0 (Dynamic Spaces)

**Architecture**:
```
N Spaces (Dynamic)
├── Space: sandbox-client-a
│   ├── Shared infrastructure (logical isolation)
│   ├── Configurable UI (Canada GC template)
│   ├── Configurable RAG (standard params)
│   ├── Configurable prompts
│   └── Starter data sources (150 docs)
├── Space: prod-client-a
│   ├── Dedicated infrastructure (physical isolation)
│   ├── Custom UI (client branding)
│   ├── Advanced RAG tuning
│   ├── Custom prompts + guardrails
│   └── Full data sources (6,250 docs)
└── Space: prod-client-b
    └── ...
```

**Advantages**:
- ✅ Create new Space in 5 minutes (no code)
- ✅ Full UI/UX customization per Space
- ✅ Advanced RAG tuning per use case
- ✅ Transparent cost tracking per Space
- ✅ Sandbox-to-production lifecycle
- ✅ Physical isolation for sensitive clients (production)
- ✅ RBAC + HPK + dedicated resources (defense in depth)

---

## 🔒 Security & Compliance

### Defense-in-Depth by Space Type

#### Sandbox (Logical Isolation)
**Layers**:
1. **Network**: Shared APIM gateway, Azure AD authentication
2. **API**: spaceId claim in JWT token, validated by backend
3. **Database**: Hierarchical Partition Key (`/spaceId/userId`)
4. **Search**: Security filter (`spaceId eq 'sandbox-client-a'`)
5. **Monitoring**: Azure Monitor (detect cross-Space access attempts)

**Risk**: Low (suitable for Unclassified data only)

#### Production (Physical + Logical Isolation)
**Layers**:
1. **Network**: VNet with private endpoints, NSG rules
2. **API**: Dedicated APIM API per Space, custom domain
3. **Database**: Dedicated Cosmos DB containers, optional dedicated account
4. **Search**: Dedicated AI Search indexes, optional dedicated service
5. **Subscription**: Optional dedicated Azure subscription (billing + RBAC isolation)
6. **Monitoring**: Dedicated Log Analytics workspace, Security Center

**Risk**: Very Low (suitable for Protected B, Protected A with encryption)

### Compliance Patterns

**Protected B Data**:
- Production Spaces only (physical isolation required)
- Encryption at rest (Cosmos DB, AI Search, Blob Storage)
- Encryption in transit (TLS 1.2+)
- Private endpoints (no public internet access)
- Audit logging (all queries, all data access)
- Data residency: Canada Central (Azure region)

**RBAC Enforcement**:
- Azure AD groups define Space membership
- JWT token includes `spaceId` + AD groups
- Backend validates user can access Space
- Database queries filter by `spaceId` + `userId` (HPK)
- AI Search applies security filter (`spaceId eq 'X' and rbacGroups/any(g: g eq 'user-group')`)

---

## 🛠️ Technical Implementation

### Data Model Extensions (Cosmos DB)

#### New Collection: `spaces`
```json
{
  "id": "space-001",
  "spaceId": "prod-client-a",
  "spaceName": "Client A Legal Research",
  "spaceType": "production",
  "status": "active",
  "owner": {
    "userId": "user-123",
    "email": "lead@client-a.gc.ca"
  },
  "billing": {
    "subscriptionTier": "production-standard",
    "monthlyBudget": 10000,
    "currentSpend": 6100
  },
  "infrastructure": {
    "isolationLevel": "physical",
    "aiSearchService": "eva-search-client-a",
    "aiSearchIndexes": ["prod-client-a-jurisprudence", "prod-client-a-policies"],
    "cosmosDbContainers": ["prod-client-a-documents", "prod-client-a-chunks"],
    "azureFunctionsApp": "eva-functions-client-a"
  },
  "configuration": {
    "ui": { /* UI config */ },
    "rag": { /* RAG config */ },
    "prompts": { /* Prompts config */ }
  },
  "dataSources": [
    { /* Data source 1 */ },
    { /* Data source 2 */ }
  ],
  "quotas": {
    "tokenLimit": 1000000,
    "queryLimit": -1
  },
  "createdAt": "2024-12-01T00:00:00Z",
  "updatedAt": "2024-12-08T15:30:00Z"
}
```

#### Updated Collection: `documents` (with spaceId)
```json
{
  "id": "doc-001",
  "documentId": "doc-001",
  "spaceId": "prod-client-a",
  "tenantId": "client-a",
  "userId": "user-123",
  "title": "Smith v. Canada Employment Case",
  "content": "...",
  "documentType": "jurisprudence",
  "rbacGroups": ["client-a-legal-team"],
  /* ... other fields ... */
}
```

**Hierarchical Partition Key**: `/spaceId/tenantId/userId`

### AI Search Index Schema (with spaceId)

```json
{
  "name": "prod-client-a-jurisprudence-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    },
    {
      "name": "spaceId",
      "type": "Edm.String",
      "filterable": true,
      "facetable": false
    },
    {
      "name": "documentId",
      "type": "Edm.String",
      "filterable": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "contentVector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "default"
    },
    {
      "name": "rbacGroups",
      "type": "Collection(Edm.String)",
      "filterable": true
    }
  ]
}
```

**Search Query with Space Filter**:
```http
POST https://eva-search-client-a.search.windows.net/indexes/prod-client-a-jurisprudence-index/docs/search
Content-Type: application/json

{
  "search": "employment dismissal",
  "vectorQueries": [{
    "kind": "vector",
    "vector": [...],
    "fields": "contentVector",
    "k": 20
  }],
  "filter": "spaceId eq 'prod-client-a' and rbacGroups/any(g: g eq 'client-a-legal-team')",
  "top": 10
}
```

### API Endpoints (Space-Aware)

```
GET    /api/v1/spaces
POST   /api/v1/spaces
GET    /api/v1/spaces/{spaceId}
PUT    /api/v1/spaces/{spaceId}
DELETE /api/v1/spaces/{spaceId}

GET    /api/v1/spaces/{spaceId}/ui-config
PUT    /api/v1/spaces/{spaceId}/ui-config

GET    /api/v1/spaces/{spaceId}/rag-config
PUT    /api/v1/spaces/{spaceId}/rag-config

GET    /api/v1/spaces/{spaceId}/prompts
PUT    /api/v1/spaces/{spaceId}/prompts

GET    /api/v1/spaces/{spaceId}/data-sources
POST   /api/v1/spaces/{spaceId}/data-sources

POST   /api/v1/spaces/{spaceId}/chat/completions
GET    /api/v1/spaces/{spaceId}/chat/sessions
GET    /api/v1/spaces/{spaceId}/chat/sessions/{sessionId}

GET    /api/v1/spaces/{spaceId}/billing
GET    /api/v1/spaces/{spaceId}/usage
```

**Authentication**:
- Bearer token (Azure AD)
- Token includes `spaceId` claim (if user belongs to Space)
- Backend validates user can access `/spaces/{spaceId}` endpoints

### Infrastructure as Code (Bicep/Terraform)

#### Sandbox Provisioning (5 minutes)
```bicep
// sandbox-space.bicep
param spaceId string
param spaceName string

// Logical isolation only (no dedicated resources)
resource spaceRecord 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: evaCosmosDb
  name: 'spaces'
  properties: {
    resource: {
      id: spaceId
      partitionKey: {
        paths: ['/spaceId']
        kind: 'Hash'
      }
    }
  }
}

// RBAC assignment (Business Analyst + Owner)
resource rbacAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(spaceId, 'Contributor')
  properties: {
    principalId: ownerPrincipalId
    roleDefinitionId: contributorRoleId
  }
}
```

#### Production Provisioning (1-2 weeks)
```bicep
// prod-space.bicep
param spaceId string
param spaceName string

// Dedicated AI Search Service
resource aiSearchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: 'eva-search-${spaceId}'
  location: 'canadacentral'
  sku: {
    name: 'standard' // S1
  }
  properties: {
    replicaCount: 2
    partitionCount: 1
  }
}

// Dedicated Cosmos DB Containers
resource documentsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: evaCosmosDb
  name: '${spaceId}-documents'
  properties: {
    resource: {
      id: '${spaceId}-documents'
      partitionKey: {
        paths: ['/tenantId', '/userId']
        kind: 'MultiHash'
      }
    }
    options: {
      autoscaleMaxThroughput: 10000 // RU/s
    }
  }
}

resource chunksContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: evaCosmosDb
  name: '${spaceId}-chunks'
  properties: {
    resource: {
      id: '${spaceId}-chunks'
      partitionKey: {
        paths: ['/tenantId', '/userId']
        kind: 'MultiHash'
      }
    }
    options: {
      autoscaleMaxThroughput: 40000
    }
  }
}

// Dedicated Azure Functions App (Premium Plan)
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: 'eva-functions-${spaceId}'
  location: 'canadacentral'
  kind: 'functionapp'
  properties: {
    serverFarmId: premiumAppServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'SPACE_ID'
          value: spaceId
        },
        {
          name: 'COSMOS_CONNECTION_STRING'
          value: cosmosDb.connectionStrings[0].connectionString
        }
      ]
    }
  }
}
```

---

## 📈 Success Metrics

### Business KPIs
- **Sandbox Conversions**: 60% of sandbox clients convert to production (target)
- **Time-to-Trial**: <1 day from request to sandbox live (target: 5 minutes automated)
- **Time-to-Production**: <2 weeks from approval to production live
- **Client Satisfaction**: NPS >40 (target: >50)
- **Cost Predictability**: 95% of production clients stay within budget ±10%

### Technical KPIs
- **Isolation Violations**: 0 (critical security metric)
- **Cross-Space Data Leakage**: 0 (critical security metric)
- **Sandbox Performance**: <3s average response time (acceptable, best-effort)
- **Production Performance**: <2s average response time (SLA)
- **Production Uptime**: 99.9% (SLA)

### Operational KPIs
- **Business Analyst Efficiency**: 1 BA can manage 20 sandbox Spaces + 5 production Spaces
- **Configuration Changes**: 95% of changes done via admin portal (no code deployments)
- **Data Source Onboarding**: <2 days from request to ingestion (via EVA Data Pipeline)
- **Support Tickets**: <10 tickets/Space/month (production Spaces)

---

## 🎯 Roadmap Integration

### Phase 0: Foundation (NOW - Dec 8, 2024)
- ✅ EVA Data Model requirements discovered
- ⏳ EVA Data Model documentation (Sprint 1, 5-7 days)
- ⏳ Multi-tenant architecture design (THIS DOCUMENT)

### Phase 1: Sandbox MVP (Weeks 1-4, Dec 9-Jan 5)
- Build `spaces` collection and API
- Implement logical isolation (HPK, RBAC filters)
- Create EVA DA Accelerator template (UI + RAG + prompts)
- Business Analyst admin portal (basic: create/configure Space)
- Deploy 3 pilot sandboxes (internal testing)

### Phase 2: Production Support (Weeks 5-8, Jan 6-Feb 2)
- Implement physical isolation (Bicep templates for dedicated resources)
- Build promotion workflow (sandbox → production)
- Advanced admin portal (full customization, cost tracking)
- Deploy 2 pilot production Spaces (early adopter clients)

### Phase 3: EVA Data Pipeline Integration (Weeks 9-12, Feb 3-Mar 1)
- Integrate Space-aware data ingestion
- Business Analyst can request data source ingestion per Space
- P02 generates pipelines with Space-specific config
- Deploy 5 new production Spaces with custom data sources

### Phase 4: Scale (Months 4-6, Mar-May 2025)
- Onboard 20 sandbox Spaces
- Convert 10 sandbox → production
- Build self-service portal (clients can create sandboxes)
- Automated cost optimization (recommend tier changes)

### Phase 5: Enterprise (Months 7-12, Jun-Dec 2025)
- 50+ production Spaces
- Advanced features: Custom RAG models, A/B testing, analytics
- Enterprise SLA: 99.99% uptime, <1s response time
- White-label support (clients can fully rebrand)

---

## 🚧 Open Questions & Decisions

### Architectural Decisions

**Q1: Sandbox → Production Migration Strategy**
- **Option A**: In-place upgrade (add dedicated resources, keep spaceId)
- **Option B**: Create new production Space, migrate data (new spaceId)
- **Recommendation**: Option A (simpler for users, maintain URLs)

**Q2: Cosmos DB Isolation for Production**
- **Option A**: Dedicated containers in shared account (HPK isolation)
- **Option B**: Dedicated Cosmos DB account per Space (full isolation)
- **Recommendation**: Option A for <Protected B, Option B for Protected B (cost vs security tradeoff)

**Q3: AI Search Isolation for Production**
- **Option A**: Dedicated indexes in shared service (logical isolation)
- **Option B**: Dedicated AI Search service per Space (physical isolation)
- **Recommendation**: Option A for standard tier, Option B for enterprise tier (>$20K/month)

**Q4: Azure Subscription Boundary**
- **Option A**: All Spaces in single EVA subscription (shared billing)
- **Option B**: Dedicated subscription per production Space (isolated billing)
- **Recommendation**: Option A for <50 Spaces, Option B for enterprise clients (>$50K/month)

### Business Decisions

**Q5: Sandbox Trial Duration**
- **Recommendation**: 30-90 days (configurable), with 30-day extension option

**Q6: Sandbox Quotas**
- **Recommendation**: 10K tokens/month, 100 queries/day (adjustable per Space)

**Q7: Production Pricing Model**
- **Option A**: Flat monthly subscription ($5K-$50K) + metered overage
- **Option B**: Pure metered pricing ($0.0001/token + infra costs)
- **Recommendation**: Option A (predictable costs for clients)

**Q8: Business Analyst Permissions**
- **Recommendation**: 
  - Sandbox: Full control (create, configure, delete)
  - Production: Create/configure only, delete requires manager approval

---

## 📚 Related Documentation

**Foundation**:
- `EVA-DATA-MODEL-FOUNDATION-REQUIREMENTS.md` - Data model schemas (BLOCKS THIS)
- `EVA-DATA-PIPELINE.md` - Data ingestion automation (INTEGRATES WITH THIS)
- `EVA-DATA-PIPELINE-ROADMAP.md` - Implementation timeline (ALIGNS WITH THIS)

**Architecture**:
- `docs/architecture/eva-data-model.md` - To be created (Sprint 1)
- `docs/architecture/folder-schemas.md` - To be created (Sprint 1)
- `docs/gc-deployment-patterns/` - INFxx/SECxx patterns (reference)

**Governance**:
- `agents/governance-registry.yaml` - SPxx personas, C0-C3 autonomy
- `agents/cdd-inventory.yaml` - CDD depth requirements (eva-rag: depth 5)

---

## ✅ Next Steps

1. **Immediate** (Dec 8, 2024):
   - [ ] Marco review and approval of multi-tenant vision
   - [ ] Prioritize: Data model foundation (Sprint 1) vs multi-tenant architecture (Phase 1)
   - [ ] Decision: Proceed with data model first (RECOMMENDED - unblocks everything)

2. **Sprint 1** (Dec 9-15, 2024):
   - [ ] Complete EVA Data Model documentation (schemas, data flows, RBAC)
   - [ ] Extend data model with `spaces` collection schema
   - [ ] Document multi-tenant isolation patterns (logical vs physical)

3. **Phase 1** (Weeks 1-4, Dec 9-Jan 5):
   - [ ] Build Sandbox MVP (logical isolation, EVA DA Accelerator template)
   - [ ] Business Analyst admin portal (create/configure Spaces)
   - [ ] Deploy 3 pilot sandboxes

4. **Phase 2** (Weeks 5-8, Jan 6-Feb 2):
   - [ ] Build Production Support (physical isolation, Bicep templates)
   - [ ] Promotion workflow (sandbox → production)
   - [ ] Deploy 2 pilot production Spaces

---

**CONVERSATION STATUS**: 🎯 VISION DEFINED - READY FOR REVIEW  
**BLOCKING ITEM**: EVA Data Model Foundation (Sprint 1, 5-7 days)  
**ESTIMATED IMPACT**: $500K+ annual savings (EVA Data Pipeline) + $2M+ new revenue (production Spaces)  
**DIFFERENTIATION**: Current EVA DA (50 fixed indexes) → EVA 2.0 (N dynamic Spaces, full customization)

---

**Prepared by**: GitHub Copilot  
**Date**: December 8, 2024  
**Review Required**: Marco Presta (PO)
