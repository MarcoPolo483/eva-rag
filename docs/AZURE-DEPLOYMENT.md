# Azure Cosmos DB Deployment Guide

## Overview

This guide covers deploying the EVA RAG Cosmos DB infrastructure with Hierarchical Partition Keys (HPK) to Azure.

## Prerequisites

- **Azure CLI**: [Install Azure CLI](https://aka.ms/installazurecliwindows)
- **Azure Subscription**: Active subscription with Contributor access
- **PowerShell**: Version 7+ recommended
- **Bicep**: Included with Azure CLI (2.20.0+)

## Quick Start

### 1. Login to Azure

```powershell
az login
```

### 2. Deploy to Development Environment

```powershell
cd infra
.\deploy.ps1 -Environment dev
```

This will:
- Create resource group `eva-rag-dev`
- Deploy Cosmos DB account with HPK-enabled containers
- Configure 7 containers (6 production + 1 legacy)
- Save connection information

### 3. Verify Deployment

```powershell
python scripts/verify_containers.py --detailed
```

Expected output:
```
✅ All containers verified successfully!
HPK configuration is correct.
```

## Deployment Options

### Environment-Specific Deployments

**Development:**
```powershell
.\deploy.ps1 -Environment dev -Location eastus
```

**Staging:**
```powershell
.\deploy.ps1 -Environment staging -Location eastus2
```

**Production:**
```powershell
.\deploy.ps1 -Environment prod -Location westus2
```

### Preview Changes (WhatIf Mode)

```powershell
.\deploy.ps1 -Environment dev -WhatIf
```

### Custom Resource Group

```powershell
.\deploy.ps1 -Environment dev -ResourceGroup my-custom-rg -Location centralus
```

## Container Configuration

### HPK-Enabled Containers

| Container          | Partition Key                          | Purpose                    |
|--------------------|---------------------------------------|----------------------------|
| `spaces`           | `/space_id`, `/tenant_id`, `/created_by` | Collaborative spaces       |
| `documents_hpk`    | `/space_id`, `/tenant_id`, `/user_id`    | User documents (HPK)       |
| `chunks`           | `/space_id`, `/tenant_id`, `/user_id`    | Document chunks            |
| `ai_interactions`  | `/space_id`, `/tenant_id`, `/user_id`    | AI provenance tracking     |

### Single Partition Key Containers

| Container          | Partition Key        | Purpose                    |
|--------------------|---------------------|----------------------------|
| `audit_logs`       | `/sequence_number`  | System-level audit chain   |
| `audit_counters`   | `/id`               | Atomic sequence numbers    |
| `documents` (legacy)| `/tenant_id`       | Backward compatibility     |

## Throughput Configuration

### Autoscale (Default)

- **Dev**: Max 4,000 RU/s per container
- **Staging**: Max 10,000 RU/s per container
- **Prod**: Max 20,000 RU/s per container

Autoscale scales down to 10% of max when idle, reducing costs.

### Manual Throughput

Edit `cosmos_db.parameters.json`:

```json
{
  "throughputPolicy": {
    "value": "manual"
  }
}
```

Then deploy with fixed 400 RU/s per container.

### Serverless (Cost-Effective for Dev)

Edit `cosmos_db.bicep`, uncomment:

```bicep
capabilities: [
  {
    name: 'EnableServerless'
  }
]
```

**Note**: Serverless has limitations (5,000 RU/s max, no autoscale).

## Connection Configuration

### 1. Get Connection String

After deployment:

```powershell
az cosmosdb keys list \
  --resource-group eva-rag-dev \
  --name eva-rag-cosmos-dev \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv
```

### 2. Update `.env` File

```bash
# Azure Cosmos DB
COSMOS_CONNECTION_STRING="AccountEndpoint=https://...;AccountKey=...;"
COSMOS_DATABASE_NAME="eva-rag"

# Container names (HPK)
COSMOS_CONTAINER_SPACES="spaces"
COSMOS_CONTAINER_DOCUMENTS_HPK="documents_hpk"
COSMOS_CONTAINER_CHUNKS="chunks"
COSMOS_CONTAINER_AI_INTERACTIONS="ai_interactions"
COSMOS_CONTAINER_AUDIT_LOGS="audit_logs"
COSMOS_CONTAINER_AUDIT_COUNTERS="audit_counters"

# Legacy container
COSMOS_CONTAINER_DOCUMENTS_LEGACY="documents"
```

## Data Migration

After deploying HPK containers, migrate existing data:

### 1. Dry Run (Preview)

```bash
python scripts/migrate_to_hpk.py --dry-run --batch-size 100
```

### 2. Migrate Small Batch (Test)

```bash
python scripts/migrate_to_hpk.py --batch-size 10 --skip 0
```

### 3. Full Migration

```bash
python scripts/migrate_to_hpk.py --batch-size 100
```

### 4. Verify Migration

```bash
python scripts/migrate_to_hpk.py --verify-only
```

See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for detailed migration procedures.

## Monitoring & Troubleshooting

### View Metrics in Azure Portal

1. Navigate to Cosmos DB account
2. Go to **Metrics** blade
3. Monitor:
   - Total Request Units
   - Throttled Requests
   - Storage Used
   - Latency

### Common Issues

#### Issue: "Container already exists"

**Solution**: Container names must be unique. Either:
- Delete existing containers
- Change container names in parameters

#### Issue: "Insufficient permissions"

**Solution**: Ensure Azure account has `Contributor` role:

```powershell
az role assignment create \
  --assignee user@domain.com \
  --role Contributor \
  --scope /subscriptions/{subscription-id}/resourceGroups/eva-rag-dev
```

#### Issue: "Throttling (429 errors)"

**Solution**: Increase throughput:

```powershell
az cosmosdb sql container throughput update \
  --resource-group eva-rag-dev \
  --account-name eva-rag-cosmos-dev \
  --database-name eva-rag \
  --name documents_hpk \
  --max-throughput 10000
```

### View Container Properties

```powershell
az cosmosdb sql container show \
  --resource-group eva-rag-dev \
  --account-name eva-rag-cosmos-dev \
  --database-name eva-rag \
  --name documents_hpk
```

## Cost Optimization

### Recommendations

1. **Use Autoscale**: Scales down when idle (saves ~60% vs. manual)
2. **Enable Free Tier**: First 1,000 RU/s free (dev accounts)
3. **Serverless for Dev**: No minimum RU/s (pay per operation)
4. **Archive Old Data**: Use TTL to auto-delete old records
5. **Optimize Queries**: Use partition keys in WHERE clauses

### Cost Estimates (US East)

| Configuration           | Cost/Month (Approx.) |
|-------------------------|---------------------|
| Free Tier (1,000 RU/s)  | $0                  |
| Autoscale (4,000 max)   | ~$30-50             |
| Manual (400 RU/s)       | ~$25 per container  |
| Serverless              | ~$0.25 per 1M ops   |

## Backup & Recovery

### Continuous Backup (Enabled)

- **Retention**: 7 days (Continuous7Days tier)
- **Recovery**: Point-in-time restore to any minute within 7 days

### Restore from Backup

```powershell
az cosmosdb sql database restore \
  --account-name eva-rag-cosmos-dev \
  --resource-group eva-rag-dev \
  --name eva-rag \
  --restore-timestamp "2025-12-08T10:30:00Z"
```

## Cleanup

### Delete Development Environment

```powershell
az group delete --name eva-rag-dev --yes --no-wait
```

### Delete Specific Container

```powershell
az cosmosdb sql container delete \
  --resource-group eva-rag-dev \
  --account-name eva-rag-cosmos-dev \
  --database-name eva-rag \
  --name documents_hpk
```

## Next Steps

1. ✅ Deploy Cosmos DB infrastructure
2. ✅ Verify container configuration
3. ⏭️ Run data migration (see [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md))
4. ⏭️ Run performance benchmarks (see [BENCHMARKING.md](BENCHMARKING.md))
5. ⏭️ Configure authentication (see [AUTHENTICATION.md](AUTHENTICATION.md))

## Support

- **Azure Cosmos DB Docs**: https://docs.microsoft.com/azure/cosmos-db/
- **HPK Documentation**: https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys
- **EVA RAG Issues**: https://github.com/MarcoPolo483/eva-rag/issues
