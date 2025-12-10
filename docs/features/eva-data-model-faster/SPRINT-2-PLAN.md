# Sprint 2 Planning: Data Migration + Testing Infrastructure

**Sprint**: Sprint 2 (Dec 15-21, 2025)  
**Status**: 🔵 In Planning  
**Previous Sprint**: Sprint 1 ✅ COMPLETE (Dec 8, 2025)

---

## 🎯 Sprint 2 Goals

Based on Sprint 1 completion, Sprint 2 focuses on:

1. **Technical Debt Paydown** - Unit tests, data migration scripts
2. **Azure Deployment** - Create HPK containers in Cosmos DB
3. **Performance Validation** - HPK query benchmarks, RU optimization
4. **API Hardening** - Authentication, rate limiting, error handling

**Story Points**: 35 / 40 capacity (leaving buffer for production issues)

---

## 📋 Sprint 2 Backlog

### STORY-2.1: Data Migration Script (Legacy → HPK)
**Priority**: P0 | **Points**: 8 | **Status**: 📋 To Do

**Description**: Create migration script to move existing documents from legacy `/tenant_id` partition to new HPK `/spaceId/tenantId/userId` containers.

**Tasks**:
- [ ] Create `scripts/migrate_to_hpk.py` migration script
- [ ] Implement batch migration (100 docs at a time)
- [ ] Add retry logic for transient failures
- [ ] Verify data integrity (checksums, row counts)
- [ ] Create rollback script in case of issues
- [ ] Document migration procedure in `docs/MIGRATION-GUIDE.md`

**Acceptance Criteria**:
- Migration script runs without errors
- All documents accessible via new HPK partition keys
- Zero data loss verified
- Migration completes in <1 hour for 10K documents

**Testing**:
- Migrate 100 test documents
- Verify all fields copied correctly
- Query via old and new partition keys
- Rollback test (restore from backup)

---

### STORY-2.2: Unit Tests for Services
**Priority**: P1 | **Points**: 8 | **Status**: 📋 To Do

**Description**: Add comprehensive unit tests for MetadataService, ChunkService, AIInteractionService, AuditService with mocked Cosmos DB.

**Tasks**:
- [ ] Create `tests/unit/test_metadata_service.py`
- [ ] Create `tests/unit/test_chunk_service.py`
- [ ] Create `tests/unit/test_ai_interaction_service.py`
- [ ] Create `tests/unit/test_audit_service.py`
- [ ] Mock Cosmos DB operations (pytest-mock or unittest.mock)
- [ ] Achieve >80% code coverage for services

**Acceptance Criteria**:
- All services have >80% line coverage
- Tests run in <10 seconds
- No external dependencies (mocked Cosmos DB)
- CI/CD compatible (GitHub Actions)

**Testing**:
- Run: `pytest tests/unit/ --cov=src/eva_rag/services --cov-report=html`
- Verify coverage report: `open htmlcov/index.html`

---

### STORY-2.3: Azure Cosmos DB Deployment
**Priority**: P0 | **Points**: 5 | **Status**: 📋 To Do

**Description**: Deploy HPK containers to Azure Cosmos DB (dev/staging/prod environments).

**Tasks**:
- [ ] Create Terraform/Bicep scripts for Cosmos DB provisioning
- [ ] Define containers: `spaces`, `documents_hpk`, `chunks`, `ai_interactions`, `audit_logs`, `audit_counters`
- [ ] Configure partition keys (MultiHash for HPK containers)
- [ ] Set throughput (RU/s): 400 RU/s per container (autoscale)
- [ ] Enable point-in-time restore (35 days)
- [ ] Configure backup policy (continuous backup)
- [ ] Document connection strings in Azure Key Vault

**Acceptance Criteria**:
- All 6 containers created successfully
- HPK partition keys verified
- Services can connect to Azure Cosmos DB
- Backup policy configured

**Testing**:
- Create test document via API
- Verify document stored in Azure portal
- Query document via HPK partition key
- Test failover to secondary region

---

### STORY-2.4: Performance Benchmarking
**Priority**: P1 | **Points**: 5 | **Status**: 📋 To Do

**Description**: Benchmark HPK query performance and optimize RU consumption.

**Tasks**:
- [ ] Create `scripts/benchmark_hpk.py` benchmark script
- [ ] Test scenarios:
  - Single document query (with HPK)
  - Cross-partition query (space-level list)
  - Batch operations (10/100/1000 chunks)
- [ ] Measure:
  - Latency (p50, p95, p99)
  - RU consumption per operation
  - Throughput (operations/second)
- [ ] Optimize queries based on results
- [ ] Document findings in `docs/PERFORMANCE.md`

**Acceptance Criteria**:
- Single doc query: <50ms latency, <5 RU
- Cross-partition query: <200ms latency, <50 RU
- Batch insert (100 chunks): <500ms, <100 RU
- Recommendations documented

**Testing**:
- Run benchmark with 1K/10K/100K documents
- Compare HPK vs legacy partition performance
- Verify autoscale triggers correctly

---

### STORY-2.5: API Authentication & RBAC
**Priority**: P0 | **Points**: 8 | **Status**: 📋 To Do

**Description**: Implement Azure AD authentication and role-based access control for API endpoints.

**Tasks**:
- [ ] Add FastAPI dependency: `fastapi-azure-auth`
- [ ] Configure Azure AD app registration
- [ ] Implement JWT token validation middleware
- [ ] Create RBAC decorators: `@require_role("admin")`, `@require_space_access(space_id)`
- [ ] Update API endpoints with auth requirements
- [ ] Document authentication flow in OpenAPI/Swagger
- [ ] Add example: `docs/API-AUTHENTICATION.md`

**Acceptance Criteria**:
- Unauthenticated requests return 401 Unauthorized
- Users can only access their Space data (403 for cross-Space)
- Admin endpoints require "admin" role
- JWT token validated with Azure AD

**Testing**:
- Get JWT token from Azure AD
- Call API with valid token (200 OK)
- Call API with invalid token (401)
- User A tries to access Space B (403)
- Admin accesses all spaces (200 OK)

---

### STORY-2.6: Error Handling & Logging
**Priority**: P1 | **Points**: 3 | **Status**: 📋 To Do

**Description**: Standardize error handling and structured logging across all services.

**Tasks**:
- [ ] Create custom exception classes: `CosmosDBError`, `HPKValidationError`, `AuthorizationError`
- [ ] Add structured logging with `structlog`
- [ ] Log correlation IDs for request tracing
- [ ] Add error responses with RFC 7807 Problem Details
- [ ] Configure log levels (DEBUG/INFO/WARN/ERROR)
- [ ] Send logs to Azure Application Insights

**Acceptance Criteria**:
- All errors return consistent JSON format
- Logs include correlation IDs
- Sensitive data not logged (redacted)
- Application Insights dashboard shows error rates

**Testing**:
- Trigger validation error (verify 400 response)
- Trigger auth error (verify 401/403 response)
- Trigger Cosmos DB error (verify 500 response + retry)
- Check Application Insights for log entries

---

## 📊 Sprint 2 Capacity

| Developer | Capacity (SP) | Assigned | Remaining |
|-----------|---------------|----------|-----------|
| Backend Dev 1 | 20 | 16 (2.1, 2.3, 2.5) | 4 |
| Backend Dev 2 | 20 | 16 (2.2, 2.4, 2.6) | 4 |
| **Total** | **40** | **32** | **8** |

**Buffer**: 8 story points (20%) for production support, bug fixes, or scope changes.

---

## 🚀 Sprint 2 Success Criteria

**Must Have** (P0):
- ✅ Data migration script tested and documented
- ✅ Azure Cosmos DB containers deployed (dev + staging)
- ✅ API authentication working with Azure AD

**Should Have** (P1):
- ✅ Unit tests achieving >80% coverage
- ✅ Performance benchmarks documented
- ✅ Error handling standardized

**Nice to Have** (P2):
- ⏸️ CI/CD pipeline with automated tests
- ⏸️ API rate limiting
- ⏸️ Monitoring dashboards (Grafana/Application Insights)

---

## 📅 Sprint 2 Timeline

**Day 1-2 (Dec 15-16)**: Setup & Infrastructure
- Deploy Cosmos DB containers
- Configure Azure AD authentication
- Setup Application Insights

**Day 3-4 (Dec 17-18)**: Testing & Migration
- Write unit tests
- Create migration script
- Run performance benchmarks

**Day 5-6 (Dec 19-20)**: Validation & Documentation
- Run integration tests
- Document APIs
- Performance tuning

**Day 7 (Dec 21)**: Sprint Review & Planning
- Demo to stakeholders
- Retrospective
- Plan Sprint 3

---

## 🔗 Related Documents

- [Sprint 1 Complete](./SPRINT-1-COMPLETE.md)
- [Full Backlog](./backlog.md)
- [Requirements](./requirements.md)
- [Architecture](../../ARCHITECTURE.md)

---

## 📝 Notes

**Risks**:
- Azure Cosmos DB quotas/throttling during migration
- Authentication complexity with Azure AD
- Performance issues with cross-partition queries

**Mitigations**:
- Test migration with small batches first
- Use Azure AD samples/templates from FastAPI community
- Implement query result caching for common queries

**Dependencies**:
- Azure subscription with Cosmos DB access
- Azure AD tenant for authentication
- Application Insights workspace
