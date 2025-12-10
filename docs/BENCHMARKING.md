# Performance Benchmarking Guide

## Overview

This guide covers performance benchmarking for the HPK-enabled Cosmos DB deployment.

## Prerequisites

- Deployed Cosmos DB with HPK containers (see [AZURE-DEPLOYMENT.md](AZURE-DEPLOYMENT.md))
- Connection string configured in `.env`
- Python dependencies: `azure-cosmos`, `rich`

## Quick Start

### Run All Benchmarks

```bash
python scripts/benchmark_hpk.py
```

This runs:
- Single-partition queries (100 iterations)
- Cross-partition queries (100 iterations)
- Batch operations (50 iterations)

### Run Specific Scenarios

```bash
# Single-partition only
python scripts/benchmark_hpk.py --scenarios single

# Cross-partition only
python scripts/benchmark_hpk.py --scenarios cross

# Batch operations only
python scripts/benchmark_hpk.py --scenarios batch

# Multiple scenarios
python scripts/benchmark_hpk.py --scenarios single,cross
```

### Custom Iterations

```bash
# More iterations for statistical significance
python scripts/benchmark_hpk.py --iterations 500

# Quick test
python scripts/benchmark_hpk.py --iterations 10
```

### Custom Output

```bash
python scripts/benchmark_hpk.py --output my_results.json
```

## Benchmark Scenarios

### 1. Single-Partition Query

**What it tests**: Query performance within a single HPK partition.

**Query**:
```sql
SELECT * FROM c WHERE c.space_id = @space_id
```

**Expected Performance**:
- Latency: 5-20ms (p50)
- RU consumption: 1-5 RU per query
- Throughput: 50-200 ops/sec

**Optimization Tips**:
- Always include full partition key in WHERE clause
- Use indexed fields
- Limit result set with TOP N

### 2. Cross-Partition Query

**What it tests**: Query performance across all partitions.

**Query**:
```sql
SELECT * FROM c WHERE ARRAY_CONTAINS(c.tags, 'benchmark')
```

**Expected Performance**:
- Latency: 50-200ms (p50)
- RU consumption: 10-50 RU per query
- Throughput: 5-20 ops/sec

**Optimization Tips**:
- Avoid cross-partition queries when possible
- Use composite indexes for multi-field filters
- Consider pagination with continuation tokens

### 3. Batch Operations

**What it tests**: Bulk insert performance.

**Operation**: Insert 10 documents per batch, same partition key.

**Expected Performance**:
- Latency: 20-100ms per batch
- RU consumption: 50-100 RU per batch
- Throughput: 10-50 batches/sec

**Optimization Tips**:
- Keep batch size within same partition (HPK requirement)
- Use async operations for parallel inserts
- Consider stored procedures for server-side batching

## Interpreting Results

### Sample Output

```
╔════════════════════════════════════════════════════════════════╗
║            Performance Benchmark Results                       ║
╚════════════════════════════════════════════════════════════════╝

┌─────────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬─────────┐
│ Scenario                │ Avg (ms) │ p50 (ms) │ p95 (ms) │ p99 (ms) │ Ops/sec  │ Avg RU  │
├─────────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼─────────┤
│ Single Partition Query  │   12.34  │   11.50  │   18.20  │   25.30  │   81.03  │   2.50  │
│ Cross-Partition Query   │   85.67  │   82.10  │  125.40  │  158.90  │   11.67  │  25.00  │
│ Batch Operations        │   45.23  │   43.80  │   68.50  │   89.20  │   22.11  │  50.00  │
└─────────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴─────────┘
```

### Key Metrics Explained

**Latency Percentiles**:
- **p50 (median)**: Typical user experience
- **p95**: 95% of requests faster than this
- **p99**: 99% of requests faster than this (long-tail)

**Operations per Second (Ops/sec)**:
- Throughput under current load
- Higher is better
- Limited by RU/s provisioned

**Average RU (Request Units)**:
- Cost per operation
- Lower is better for cost optimization
- Single-partition queries most efficient

### Performance Targets

| Metric               | Target (Good)  | Warning (Review) | Critical (Fix)   |
|---------------------|---------------|------------------|------------------|
| Single-partition p50 | <20ms         | 20-50ms          | >50ms            |
| Cross-partition p50  | <100ms        | 100-200ms        | >200ms           |
| Batch p50           | <50ms         | 50-150ms         | >150ms           |
| Single-partition RU  | <5 RU         | 5-10 RU          | >10 RU           |
| Cross-partition RU   | <50 RU        | 50-100 RU        | >100 RU          |

## Performance Optimization

### 1. Query Optimization

**Always use partition keys**:
```python
# ❌ Bad: Cross-partition scan
container.query_items(
    query="SELECT * FROM c WHERE c.filename = 'test.pdf'",
    enable_cross_partition_query=True
)

# ✅ Good: Single-partition query
container.query_items(
    query="SELECT * FROM c WHERE c.space_id = @space_id AND c.filename = 'test.pdf'",
    partition_key=[space_id, tenant_id, user_id]
)
```

**Use composite indexes**:
```json
{
  "compositeIndexes": [
    [
      {"path": "/space_id", "order": "ascending"},
      {"path": "/created_at", "order": "descending"}
    ]
  ]
}
```

### 2. Indexing Strategy

**Exclude large fields**:
```json
{
  "excludedPaths": [
    {"path": "/content/?"},     // Don't index document content
    {"path": "/embedding/?"}    // Don't index vectors
  ]
}
```

### 3. Throughput Optimization

**Autoscale vs Manual**:
```bash
# Autoscale (recommended for variable load)
az cosmosdb sql container throughput update \
  --account-name eva-rag-cosmos \
  --database-name eva-rag \
  --name documents_hpk \
  --max-throughput 10000

# Manual (predictable load)
az cosmosdb sql container throughput update \
  --account-name eva-rag-cosmos \
  --database-name eva-rag \
  --name documents_hpk \
  --throughput 4000
```

### 4. Batch Operations

**Use transactional batch** (same partition):
```python
# Within same partition
batch = [
    ("create", ({"id": "1", "space_id": space_id, ...},)),
    ("create", ({"id": "2", "space_id": space_id, ...},)),
]
container.execute_item_batch(batch, partition_key=[space_id, tenant_id, user_id])
```

## Monitoring in Production

### Azure Portal Metrics

1. Navigate to Cosmos DB account
2. Go to **Metrics** blade
3. Monitor:
   - **Total Request Units**: RU consumption over time
   - **Total Requests**: Request volume
   - **Throttled Requests (429)**: Rate limiting events
   - **Server-side Latency**: Query execution time

### Application Insights

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string='...'))

# Log query metrics
logger.info('cosmos_query', extra={
    'custom_dimensions': {
        'latency_ms': latency,
        'ru_consumed': ru,
        'query_type': 'single_partition'
    }
})
```

### Query Profiling

```python
from azure.cosmos.diagnostics import RecordDiagnostics

# Enable diagnostics
diagnostics = RecordDiagnostics()
container.query_items(
    query="SELECT * FROM c",
    response_hook=diagnostics
)

# Analyze
print(f"Request charge: {diagnostics.headers['x-ms-request-charge']}")
print(f"Activity ID: {diagnostics.headers['x-ms-activity-id']}")
```

## Continuous Benchmarking

### Automated Testing

```bash
# Run benchmarks in CI/CD
python scripts/benchmark_hpk.py --iterations 50 --output results/benchmark_$(date +%Y%m%d).json

# Compare with baseline
python scripts/compare_benchmarks.py --baseline baseline.json --current results/benchmark_*.json
```

### Regression Detection

Set thresholds in CI:
```yaml
# .github/workflows/benchmark.yml
- name: Run benchmarks
  run: python scripts/benchmark_hpk.py

- name: Check thresholds
  run: |
    python scripts/check_thresholds.py \
      --max-p50-latency 20 \
      --max-p95-latency 50 \
      --max-ru-single 5
```

## Troubleshooting

### High Latency

**Symptoms**: p95/p99 latency spikes

**Causes**:
- Throttling (429 errors)
- Cross-partition queries
- Large result sets
- Network issues

**Solutions**:
1. Increase RU/s provisioning
2. Add partition keys to queries
3. Use pagination (TOP/OFFSET)
4. Check network connectivity

### High RU Consumption

**Symptoms**: Unexpectedly high RU charges

**Causes**:
- Missing indexes
- Cross-partition queries
- Large documents
- Unnecessary property indexing

**Solutions**:
1. Review indexing policy
2. Optimize queries (use partition keys)
3. Exclude large fields from indexing
4. Use SELECT with specific fields

### Throttling (429 Errors)

**Symptoms**: `TooManyRequests` exceptions

**Causes**:
- Exceeded provisioned RU/s
- Burst traffic
- Hot partition

**Solutions**:
1. Enable autoscale
2. Increase max RU/s
3. Implement retry logic
4. Redistribute load across partitions

## Best Practices

1. **Always benchmark with production-like data** - Volume and distribution matter
2. **Run multiple iterations** - Statistical significance requires 100+ samples
3. **Test under load** - Concurrent requests reveal bottlenecks
4. **Monitor p95/p99** - Tail latency affects user experience
5. **Track RU consumption** - Cost directly tied to RU usage
6. **Baseline before/after changes** - Measure optimization impact
7. **Test different partition key distributions** - Hotspots degrade performance

## Next Steps

1. ✅ Run initial benchmarks
2. ✅ Establish baseline metrics
3. ⏭️ Optimize based on results
4. ⏭️ Set up continuous monitoring
5. ⏭️ Integrate with CI/CD

## References

- [Cosmos DB Performance Tips](https://docs.microsoft.com/azure/cosmos-db/performance-tips)
- [Request Units](https://docs.microsoft.com/azure/cosmos-db/request-units)
- [Partitioning Best Practices](https://docs.microsoft.com/azure/cosmos-db/partitioning-overview)
- [HPK Documentation](https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys)
