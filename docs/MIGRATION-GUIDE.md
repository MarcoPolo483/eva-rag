# Data Migration Guide: Legacy → HPK

**Version**: 1.0  
**Date**: December 8, 2025  
**Sprint**: Sprint 2 - STORY-2.1

---

## Overview

This guide explains how to migrate existing documents from legacy partition key (`/tenant_id`) to new Hierarchical Partition Keys (`/spaceId/tenantId/userId`).

**Migration Strategy**: Dual-write approach
- Legacy container: `documents` (keep for backward compatibility)
- HPK container: `documents_hpk` (new applications)

---

## Prerequisites

### Required Information
- ✅ Azure Cosmos DB connection string
- ✅ Database name (default: `eva-rag`)
- ✅ Source container: `documents` (legacy)
- ✅ Target container: `documents_hpk` (will be created if missing)

### Required Fields
All documents must have:
- `id` (UUID)
- `space_id` (UUID)
- `tenant_id` (UUID)
- `user_id` (UUID)

**⚠️ Documents missing these fields will be skipped.**

---

## Migration Scripts

### 1. Preview Migration (Dry Run)

```bash
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"

# Set environment variable
$env:COSMOS_CONNECTION_STRING = "AccountEndpoint=https://...;AccountKey=..."

# Preview migration (no changes)
python scripts/migrate_to_hpk.py --dry-run --batch-size 100
```

**Expected Output**:
```
2025-12-08 10:00:00 - INFO - Starting migration (batch_size=100, skip=0, dry_run=True)
2025-12-08 10:00:01 - INFO - Found 100 documents to migrate
2025-12-08 10:00:01 - INFO - DRY RUN - No documents will be migrated
2025-12-08 10:00:01 - INFO -   ✓ Would migrate: 550e8400-e29b-41d4-a716-446655440000
2025-12-08 10:00:01 - INFO -   ✓ Would migrate: 660e8400-e29b-41d4-a716-446655440001
...
2025-12-08 10:00:02 - INFO - ============================================================
2025-12-08 10:00:02 - INFO - MIGRATION REPORT
2025-12-08 10:00:02 - INFO - ============================================================
2025-12-08 10:00:02 - INFO - Total documents: 100
2025-12-08 10:00:02 - INFO - Successfully migrated: 0 (dry run)
2025-12-08 10:00:02 - INFO - Skipped (validation errors): 0
2025-12-08 10:00:02 - INFO - ============================================================
```

### 2. Migrate Small Batch (Test)

```bash
# Migrate first 10 documents
python scripts/migrate_to_hpk.py --batch-size 10

# Check logs
cat migration.log
```

### 3. Verify Migration

```bash
# Verify migrated documents
python scripts/migrate_to_hpk.py --verify-only --batch-size 10
```

**Expected Output**:
```
2025-12-08 10:05:00 - INFO - Verifying migration (sample_size=10)
2025-12-08 10:05:01 - DEBUG - ✓ Verified: 550e8400-e29b-41d4-a716-446655440000
2025-12-08 10:05:01 - DEBUG - ✓ Verified: 660e8400-e29b-41d4-a716-446655440001
...
2025-12-08 10:05:02 - INFO - Verification complete: 10 verified, 0 errors
```

### 4. Full Migration

```bash
# Migrate all documents (100 at a time)
python scripts/migrate_to_hpk.py --batch-size 100
```

**For Large Datasets** (>10K documents):
```bash
# Migrate in chunks
python scripts/migrate_to_hpk.py --batch-size 100 --skip 0     # First 100
python scripts/migrate_to_hpk.py --batch-size 100 --skip 100   # Next 100
python scripts/migrate_to_hpk.py --batch-size 100 --skip 200   # Next 100
# ... repeat until complete
```

---

## Verification Checklist

After migration, verify:

### ✅ Data Integrity
```bash
# Compare document counts
# Azure Portal → Cosmos DB → Documents

# Legacy container: documents
SELECT COUNT(1) FROM c

# HPK container: documents_hpk
SELECT COUNT(1) FROM c
```

**Expected**: Both counts should match.

### ✅ Query by HPK
```bash
# Test HPK query via API
curl http://localhost:8000/api/v1/spaces/{space_id}/documents/{document_id}?tenant_id=...&user_id=...
```

**Expected**: 200 OK with document data.

### ✅ Metadata Added
```bash
# Check migration metadata in Azure Portal
SELECT c._migration_metadata FROM c
```

**Expected**:
```json
{
  "_migration_metadata": {
    "migrated_at": "2025-12-08T10:00:00Z",
    "source_hash": "abc123...",
    "migration_version": "1.0"
  }
}
```

---

## Rollback Procedure

### ⚠️ Emergency Rollback

If migration fails, rollback to legacy container:

```bash
# 1. Stop all applications using HPK container
# 2. Verify legacy container still has data
# 3. Switch applications back to legacy mode

# In code:
service = MetadataService(use_hpk=False)  # Use legacy container
```

### 🔄 Delete HPK Container (if needed)

```bash
# Azure Portal → Cosmos DB → documents_hpk → Delete Container
# Or via script:
python scripts/rollback_migration.py --dry-run
```

---

## Troubleshooting

### Issue: "Missing required fields"
**Cause**: Document missing `space_id`, `tenant_id`, or `user_id`

**Solution**: 
1. Identify documents: `python scripts/migrate_to_hpk.py --dry-run | grep "Would skip"`
2. Update source documents with missing fields
3. Retry migration

### Issue: "Failed to insert"
**Cause**: Cosmos DB throttling (429 errors)

**Solution**:
1. Reduce batch size: `--batch-size 50`
2. Add delays between batches
3. Increase RU/s temporarily in Azure Portal

### Issue: "Document already exists"
**Cause**: Document already migrated

**Solution**:
- Skip: This is expected behavior
- Force overwrite: `--force` (not recommended)

### Issue: Migration is slow
**Optimization**:
1. Increase batch size: `--batch-size 500`
2. Run parallel migrations (different `--skip` offsets)
3. Temporarily increase Cosmos DB RU/s

---

## Migration Timeline

### Small Dataset (<1K documents)
- **Preview**: 1 minute
- **Test batch**: 2 minutes
- **Verification**: 1 minute
- **Full migration**: 5-10 minutes
- **Total**: ~15 minutes

### Medium Dataset (1K-10K documents)
- **Preview**: 5 minutes
- **Test batch**: 5 minutes
- **Full migration**: 30-60 minutes
- **Verification**: 10 minutes
- **Total**: ~1-2 hours

### Large Dataset (>10K documents)
- **Preview**: 10 minutes
- **Test batch**: 5 minutes
- **Full migration**: 2-4 hours (batched)
- **Verification**: 30 minutes
- **Total**: ~3-5 hours

---

## Post-Migration

### 1. Update Applications
```python
# Old code:
service = MetadataService()  # Legacy by default

# New code:
service = MetadataService(use_hpk=True)  # Use HPK container
```

### 2. Monitor Performance
- Check Cosmos DB RU consumption
- Monitor query latencies
- Verify no errors in Application Insights

### 3. Deprecate Legacy Container
**Timeline**: 30-day grace period
1. Week 1-2: Both containers active (dual-write if needed)
2. Week 3: Legacy container read-only
3. Week 4: Legacy container archived/deleted

---

## Support

**Questions?** Contact:
- Backend Team: [Slack channel]
- Documentation: `docs/features/eva-data-model-faster/`
- Issues: [GitHub Issues]

**Logs**:
- Migration log: `migration.log`
- Rollback log: `rollback.log`
- Application logs: Azure Application Insights
