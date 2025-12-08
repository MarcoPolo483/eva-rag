# EVA RAG Monitoring & Operations

## 📊 Monitoring Dashboards

### Application Insights

View real-time metrics and logs:

```powershell
# Get Application Insights connection
az monitor app-insights component show \
  --app eva-rag-staging-insights \
  --resource-group eva-rag-staging
```

**Key Metrics:**
- Request rate and response times
- Failure rate and exceptions
- Dependency calls (Azure services)
- Custom events and traces

### Azure Monitor Metrics

```powershell
# CPU Usage
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.Web/serverfarms/eva-rag-staging-plan \
  --metric CpuPercentage \
  --start-time 2025-12-08T00:00:00Z

# Memory Usage
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.Web/serverfarms/eva-rag-staging-plan \
  --metric MemoryPercentage \
  --start-time 2025-12-08T00:00:00Z

# HTTP Requests
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.Web/sites/eva-rag-staging \
  --metric Requests \
  --start-time 2025-12-08T00:00:00Z
```

## 🔔 Alert Configuration

### Configured Alerts

1. **CPU Alert** - Triggers when CPU > 80% for 15 minutes
2. **Memory Alert** - Triggers when memory > 85% for 15 minutes
3. **HTTP Errors** - Triggers when 5xx errors > 10 in 15 minutes

### Add Custom Alerts

```powershell
# Response time alert
az monitor metrics alert create \
  --name eva-rag-response-time \
  --resource-group eva-rag-staging \
  --scopes /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.Web/sites/eva-rag-staging \
  --condition "avg HttpResponseTime > 5000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2
```

## 📈 Key Performance Indicators (KPIs)

### Service Level Objectives (SLOs)

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Availability | 99.9% | < 99.5% |
| Response Time (P95) | < 2s | > 3s |
| Error Rate | < 0.1% | > 1% |
| Document Processing Time | < 30s | > 60s |
| Embedding Generation | < 5s/doc | > 10s/doc |

### Custom Metrics to Track

```python
# In your application
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics

# Configure OpenTelemetry
configure_azure_monitor()
meter = metrics.get_meter(__name__)

# Create counters
documents_processed = meter.create_counter(
    "documents.processed",
    description="Number of documents processed"
)

# Track in your code
documents_processed.add(1, {"status": "success", "type": "pdf"})
```

## 🔍 Log Analysis

### View Application Logs

```powershell
# Stream live logs
az webapp log tail \
  --name eva-rag-staging \
  --resource-group eva-rag-staging

# Download logs
az webapp log download \
  --name eva-rag-staging \
  --resource-group eva-rag-staging \
  --log-file eva-rag-logs.zip
```

### Query Logs with KQL

```kql
-- Error rate over time
requests
| where timestamp > ago(1h)
| summarize 
    total = count(),
    errors = countif(success == false)
    by bin(timestamp, 5m)
| extend error_rate = (errors * 100.0) / total
| render timechart

-- Slowest endpoints
requests
| where timestamp > ago(24h)
| summarize 
    count = count(),
    avg_duration = avg(duration),
    p95_duration = percentile(duration, 95)
    by name
| order by p95_duration desc
| take 10

-- Exception analysis
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc

-- Dependency failures
dependencies
| where timestamp > ago(1h)
| where success == false
| summarize count() by target, name, resultCode
| order by count_ desc
```

## 🚨 Incident Response

### Health Check

```powershell
# Automated health check
$response = Invoke-RestMethod -Uri "https://eva-rag-staging.azurewebsites.net/health"
if ($response.status -ne "healthy") {
    Write-Host "⚠️ UNHEALTHY: $($response | ConvertTo-Json)" -ForegroundColor Red
    # Trigger incident response
} else {
    Write-Host "✅ HEALTHY" -ForegroundColor Green
}
```

### Restart Application

```powershell
# Restart app service
az webapp restart \
  --name eva-rag-staging \
  --resource-group eva-rag-staging
```

### Scale Out

```powershell
# Scale to 5 instances
az appservice plan update \
  --name eva-rag-staging-plan \
  --resource-group eva-rag-staging \
  --number-of-workers 5
```

### Rollback Deployment

```powershell
# List deployment slots
az webapp deployment list-publishing-profiles \
  --name eva-rag-staging \
  --resource-group eva-rag-staging

# Swap slots (if using staging slot)
az webapp deployment slot swap \
  --name eva-rag-staging \
  --resource-group eva-rag-staging \
  --slot staging
```

## 📊 Performance Monitoring

### Load Testing

```powershell
# Install Azure Load Testing CLI extension
az extension add --name load

# Create load test
az load test create \
  --name eva-rag-load-test \
  --resource-group eva-rag-staging \
  --load-test-config-file load-test-config.yaml
```

**load-test-config.yaml:**
```yaml
version: v0.1
testName: EVA RAG Load Test
testPlan: load-test.jmx
engineInstances: 1
configurationFiles:
  - test-data.csv
properties:
  duration: 300
  threads: 50
  rampup: 60
failureCriteria:
  - avg(response_time_ms) > 2000
  - percentage(error) > 5
```

### Application Performance Monitoring

```powershell
# Install OpenTelemetry
poetry add opentelemetry-api opentelemetry-sdk
poetry add opentelemetry-instrumentation-fastapi
poetry add azure-monitor-opentelemetry

# Configure in main.py
from azure.monitor.opentelemetry import configure_azure_monitor
configure_azure_monitor()
```

## 🔐 Security Monitoring

### Key Vault Access Logs

```powershell
# Enable diagnostics
az monitor diagnostic-settings create \
  --name eva-rag-kv-diagnostics \
  --resource /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.KeyVault/vaults/eva-rag-staging-kv \
  --logs '[{"category":"AuditEvent","enabled":true}]' \
  --workspace /subscriptions/{sub}/resourceGroups/eva-rag-staging/providers/Microsoft.OperationalInsights/workspaces/eva-rag-staging-logs
```

### Failed Authentication Attempts

```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where ResultSignature == "Unauthorized"
| summarize count() by CallerIPAddress, OperationName
| order by count_ desc
```

## 💰 Cost Management

### View Current Costs

```powershell
# Get cost for resource group
az consumption usage list \
  --start-date 2025-12-01 \
  --end-date 2025-12-08 \
  --query "[?resourceGroup=='eva-rag-staging'].{Service:consumedService, Cost:pretaxCost}" \
  --output table
```

### Set Budget Alerts

```powershell
# Create budget
az consumption budget create \
  --resource-group eva-rag-staging \
  --budget-name eva-rag-monthly-budget \
  --amount 200 \
  --time-grain Monthly \
  --start-date 2025-12-01 \
  --end-date 2026-12-01 \
  --notifications '[{"enabled":true,"operator":"GreaterThan","threshold":80,"contactEmails":["alerts@yourcompany.com"]}]'
```

## 📋 Operational Runbooks

### Daily Operations Checklist

- [ ] Check health endpoint status
- [ ] Review error rate in Application Insights
- [ ] Check CPU/Memory usage trends
- [ ] Review failed requests
- [ ] Verify Azure service dependencies
- [ ] Check storage account capacity

### Weekly Operations Checklist

- [ ] Review performance trends
- [ ] Analyze cost trends
- [ ] Update documentation
- [ ] Review and address alerts
- [ ] Security audit logs review
- [ ] Backup verification

### Monthly Operations Checklist

- [ ] Capacity planning review
- [ ] SLO/SLA compliance report
- [ ] Security patching
- [ ] Dependency updates
- [ ] Disaster recovery drill
- [ ] Cost optimization review

## 📞 Escalation Matrix

| Issue Level | Response Time | Escalation Contact |
|------------|---------------|-------------------|
| P0 (Critical) | 15 minutes | On-call engineer |
| P1 (High) | 1 hour | Team lead |
| P2 (Medium) | 4 hours | Product owner |
| P3 (Low) | 1 business day | Support team |

## 🔗 Useful Links

- [Azure Portal](https://portal.azure.com)
- [Application Insights Dashboard](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents)
- [Azure Monitor Workbooks](https://portal.azure.com/#blade/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/workbooks)
- [Cost Management](https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/overview)

---

**Last Updated:** December 8, 2025  
**Owner:** EVA Suite Operations Team
