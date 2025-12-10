# Sprint 2 Quick Reference Card

**Status**: ✅ COMPLETE | **Story Points**: 32/32 (100%) | **Date**: Dec 15-21, 2025

---

## 🚀 Quick Commands

### Migration
```bash
# Dry run
python scripts/migrate_to_hpk.py --dry-run --batch-size 100

# Execute
python scripts/migrate_to_hpk.py --batch-size 100

# Verify
python scripts/migrate_to_hpk.py --verify-only
```

### Testing
```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=src/eva_rag --cov-report=html

# Run specific service tests
pytest tests/unit/test_chunk_service.py -v
```

### Deployment
```bash
# Preview deployment
.\infra\deploy.ps1 -Environment dev -WhatIf

# Deploy to Azure
.\infra\deploy.ps1 -Environment dev

# Verify containers
python scripts/verify_containers.py --detailed
```

### Benchmarking
```bash
# Run all benchmarks
python scripts/benchmark_hpk.py

# Specific scenarios
python scripts/benchmark_hpk.py --scenarios single,cross --iterations 500

# Save results
python scripts/benchmark_hpk.py --output results.json
```

---

## 📦 Deliverables Summary

| Story | Files | Lines | Key Features |
|-------|-------|-------|--------------|
| **2.1 Migration** | 3 | 600+ | Dry-run, rollback, SHA-256 validation |
| **2.2 Tests** | 4 | 900+ | >80% coverage, mocked Cosmos DB |
| **2.3 Deployment** | 5 | 800+ | Bicep IaC, automated scripts, verification |
| **2.4 Benchmarking** | 2 | 700+ | Latency metrics, RU tracking, optimization guide |
| **2.5 Auth** | 2 | 500+ | Azure AD, JWT, RBAC, space isolation |
| **2.6 Logging** | 2 | 550+ | 20+ exceptions, structured logs, correlation IDs |

**Total**: 18 files | 4,050+ lines | 5 comprehensive guides

---

## 📁 File Locations

### Scripts
- `scripts/migrate_to_hpk.py` - Data migration with safety controls
- `scripts/rollback_migration.py` - Emergency rollback
- `scripts/benchmark_hpk.py` - Performance benchmarking
- `scripts/verify_containers.py` - Container validation

### Infrastructure
- `infra/cosmos_db.bicep` - Azure Cosmos DB template (7 containers)
- `infra/cosmos_db.parameters.json` - Environment config
- `infra/deploy.ps1` - Deployment automation

### Source Code
- `src/eva_rag/auth.py` - Authentication & RBAC
- `src/eva_rag/exceptions.py` - Custom exceptions (20+ types)
- `src/eva_rag/logging_config.py` - Structured logging

### Tests
- `tests/unit/test_chunk_service.py` - ChunkService tests
- `tests/unit/test_ai_interaction_service.py` - AIInteractionService tests
- `tests/unit/test_audit_service.py` - AuditService tests
- `tests/unit/test_metadata_service.py` - MetadataService tests

### Documentation
- `docs/MIGRATION-GUIDE.md` - Migration procedures
- `docs/AZURE-DEPLOYMENT.md` - Infrastructure deployment
- `docs/BENCHMARKING.md` - Performance testing
- `docs/AUTHENTICATION.md` - Auth setup & security
- `docs/features/eva-data-model-faster/SPRINT-2-COMPLETION.md` - Full report

---

## 🔑 Environment Variables

```bash
# Azure Cosmos DB
COSMOS_CONNECTION_STRING="AccountEndpoint=https://...;AccountKey=...;"
COSMOS_DATABASE_NAME="eva-rag"

# Authentication
AUTH_ENABLED=true
AZURE_AD_TENANT_ID=<tenant-id>
AZURE_AD_CLIENT_ID=<client-id>
JWT_ALGORITHM=RS256
JWT_AUDIENCE=eva-rag-api

# Logging
LOG_LEVEL=INFO
JSON_LOGS=true
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

---

## 🎯 Key Features

### Data Migration
- ✅ Batch processing (configurable size)
- ✅ Dry-run mode (preview changes)
- ✅ SHA-256 checksums (integrity verification)
- ✅ HPK validation
- ✅ Rollback capability
- ✅ Detailed logging

### Testing
- ✅ >80% code coverage
- ✅ Mocked Cosmos DB (fast, isolated)
- ✅ 4 core services tested
- ✅ CI/CD compatible

### Deployment
- ✅ 7 containers (4 HPK + 3 single-key)
- ✅ Autoscale throughput
- ✅ Continuous backup (7 days)
- ✅ Environment-specific configs
- ✅ Automated verification

### Benchmarking
- ✅ Latency percentiles (p50, p95, p99)
- ✅ RU consumption tracking
- ✅ 3 scenarios (single, cross, batch)
- ✅ JSON export for analysis

### Authentication
- ✅ Azure AD integration
- ✅ JWT validation
- ✅ 4 roles (admin, user, viewer, system)
- ✅ Space-level isolation
- ✅ Tenant isolation
- ✅ Development mode

### Error Handling
- ✅ 20+ custom exceptions
- ✅ HTTP status mapping
- ✅ Structured logging (JSON)
- ✅ Correlation IDs
- ✅ Azure App Insights ready

---

## 📊 Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Single-partition p50 | <20ms | 20-50ms | >50ms |
| Cross-partition p50 | <100ms | 100-200ms | >200ms |
| Batch p50 | <50ms | 50-150ms | >150ms |
| Single-partition RU | <5 RU | 5-10 RU | >10 RU |

---

## 🔒 Security Checklist

- [x] Azure AD authentication configured
- [x] JWT validation implemented
- [x] Role-based access control (RBAC)
- [x] Space-level isolation
- [x] Tenant isolation
- [x] Token expiration enforced
- [x] HTTPS required (production)
- [x] Audit logging enabled

---

## 🐛 Common Issues & Solutions

### Migration fails with "Missing HPK fields"
```bash
# Ensure all documents have space_id, tenant_id, user_id
python scripts/migrate_to_hpk.py --dry-run  # Preview issues
```

### Container deployment fails
```bash
# Check resource group exists
az group show --name eva-rag-dev

# Verify Bicep syntax
az bicep build --file infra/cosmos_db.bicep
```

### High RU consumption
```bash
# Run benchmarks to identify bottlenecks
python scripts/benchmark_hpk.py --scenarios cross

# Optimize: Add partition keys to queries
```

### Authentication errors
```bash
# Verify token format
curl -H "Authorization: Bearer <token>" https://api.eva-rag.com/health

# Check environment variables
echo $AUTH_ENABLED
echo $AZURE_AD_TENANT_ID
```

---

## 📚 Documentation Index

| Guide | Topic | Lines |
|-------|-------|-------|
| [MIGRATION-GUIDE.md](../MIGRATION-GUIDE.md) | Data migration procedures | 200+ |
| [AZURE-DEPLOYMENT.md](../AZURE-DEPLOYMENT.md) | Infrastructure deployment | 300+ |
| [BENCHMARKING.md](../BENCHMARKING.md) | Performance testing | 300+ |
| [AUTHENTICATION.md](../AUTHENTICATION.md) | Auth & security | 200+ |
| [SPRINT-2-COMPLETION.md](SPRINT-2-COMPLETION.md) | Full sprint report | 400+ |

---

## 🎓 Next Steps

### Immediate (Sprint 3)
1. Integration tests with real Cosmos DB
2. CI/CD pipeline (GitHub Actions)
3. API endpoints with auth decorators
4. Vector search optimization

### Short-term
1. Multi-region deployment
2. Performance tuning based on benchmarks
3. Monitoring dashboards
4. Load testing

### Long-term
1. Advanced RBAC policies
2. Rate limiting implementation
3. Caching layer
4. Documentation site

---

**Quick Links**:
- 📖 [Full Sprint Report](SPRINT-2-COMPLETION.md)
- 🚀 [Migration Guide](../MIGRATION-GUIDE.md)
- ☁️ [Azure Deployment](../AZURE-DEPLOYMENT.md)
- 📊 [Benchmarking](../BENCHMARKING.md)
- 🔐 [Authentication](../AUTHENTICATION.md)

**Version**: 1.0 | **Last Updated**: Dec 21, 2025
