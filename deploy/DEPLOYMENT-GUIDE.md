# EVA RAG - Deployment Guide

## 🚀 Deployment Options

EVA RAG supports multiple deployment methods:
1. **Docker** - For local/development deployment
2. **Azure App Service** - Managed PaaS deployment
3. **Kubernetes** - For scalable production workloads
4. **GitHub Actions** - Automated CI/CD

---

## 📋 Prerequisites

### All Deployments
- Python 3.11+
- Poetry 1.7+
- Azure account with active subscription
- Azure CLI installed and configured

### Docker Deployment
- Docker Desktop or Docker Engine
- Docker Compose

### Kubernetes Deployment
- kubectl configured
- Kubernetes cluster (AKS, EKS, GKE, etc.)
- Helm (optional, for easier deployment)

---

## 🐳 Docker Deployment

### Local Development

```powershell
# Build the image
docker build -t eva-rag:latest .

# Run the container
docker run -d \
  --name eva-rag \
  -p 8000:8000 \
  --env-file .env \
  eva-rag:latest

# View logs
docker logs -f eva-rag

# Stop the container
docker stop eva-rag
```

### Using Docker Compose

```powershell
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Access the Application
- **Health Check:** http://localhost:8000/health
- **API Docs:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

---

## ☁️ Azure App Service Deployment

### Prerequisites
1. Azure CLI installed
2. Logged in to Azure: `az login`
3. Environment variables configured in Azure Key Vault

### Staging Deployment

```powershell
cd deploy
.\deploy-azure.ps1 -Environment staging
```

### Production Deployment

```powershell
cd deploy
.\deploy-azure.ps1 -Environment production -SkuName P2v2
```

### Manual Deployment Steps

```powershell
# 1. Create resource group
az group create --name eva-rag-prod --location eastus

# 2. Create App Service Plan
az appservice plan create \
  --name eva-rag-plan \
  --resource-group eva-rag-prod \
  --sku P1v2 \
  --is-linux

# 3. Create Web App
az webapp create \
  --name eva-rag-prod \
  --resource-group eva-rag-prod \
  --plan eva-rag-plan \
  --runtime "PYTHON:3.11"

# 4. Configure startup command
az webapp config set \
  --name eva-rag-prod \
  --resource-group eva-rag-prod \
  --startup-file "uvicorn eva_rag.main:app --host 0.0.0.0 --port 8000"

# 5. Deploy code
az webapp up \
  --name eva-rag-prod \
  --resource-group eva-rag-prod \
  --runtime "PYTHON:3.11"
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
1. Kubernetes cluster running
2. kubectl configured
3. Secrets created for Azure credentials

### Create Namespace

```bash
kubectl create namespace eva-suite
```

### Create Secrets

```bash
# Create secrets from environment variables
kubectl create secret generic eva-rag-secrets \
  --from-literal=storage-account-name=$AZURE_STORAGE_ACCOUNT_NAME \
  --from-literal=storage-account-key=$AZURE_STORAGE_ACCOUNT_KEY \
  --from-literal=cosmos-endpoint=$AZURE_COSMOS_ENDPOINT \
  --from-literal=cosmos-key=$AZURE_COSMOS_KEY \
  --from-literal=openai-endpoint=$AZURE_OPENAI_ENDPOINT \
  --from-literal=openai-api-key=$AZURE_OPENAI_API_KEY \
  --from-literal=search-endpoint=$AZURE_SEARCH_ENDPOINT \
  --from-literal=search-admin-key=$AZURE_SEARCH_ADMIN_KEY \
  --namespace eva-suite
```

### Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f deploy/kubernetes.yaml

# Check deployment status
kubectl get deployments -n eva-suite
kubectl get pods -n eva-suite
kubectl get services -n eva-suite

# View logs
kubectl logs -f deployment/eva-rag -n eva-suite

# Port forward for testing
kubectl port-forward service/eva-rag-service 8000:80 -n eva-suite
```

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment eva-rag --replicas=5 -n eva-suite

# Auto-scaling is configured via HPA in kubernetes.yaml
kubectl get hpa -n eva-suite
```

---

## 🔄 CI/CD with GitHub Actions

### Setup

1. **Configure GitHub Secrets:**
   - `AZURE_CREDENTIALS_STAGING` - Azure service principal for staging
   - `AZURE_CREDENTIALS_PRODUCTION` - Azure service principal for production
   - `GITHUB_TOKEN` - Automatically provided

2. **Workflow Triggers:**
   - Push to `master` - Runs tests, builds, deploys to staging
   - Push to `production` tag - Deploys to production
   - Pull requests - Runs tests and code quality checks

### Manual Workflow Dispatch

```bash
# Trigger deployment via GitHub CLI
gh workflow run ci-cd.yml -f environment=staging

# Or via GitHub UI:
# Actions → CI/CD Pipeline → Run workflow
```

### Monitor Workflow

```bash
# View workflow status
gh run list --workflow=ci-cd.yml

# View logs
gh run view <run-id> --log
```

---

## 🔍 Post-Deployment Validation

### Health Checks

```powershell
# Local Docker
curl http://localhost:8000/health

# Azure App Service
curl https://eva-rag-staging.azurewebsites.net/health

# Kubernetes
kubectl exec -it deployment/eva-rag -n eva-suite -- curl http://localhost:8000/health
```

### Smoke Tests

```powershell
# Test document ingestion
$response = Invoke-RestMethod `
  -Uri "https://eva-rag-staging.azurewebsites.net/api/v1/rag/ingest" `
  -Method Post `
  -Form @{
    file = Get-Item "test-document.pdf"
    tenant_id = "test-tenant-123"
    space_id = "test-space-456"
    user_id = "test-user-789"
  }

# Verify response
$response | ConvertTo-Json
```

### Integration Tests

```powershell
# Run integration tests against deployed environment
$env:API_BASE_URL = "https://eva-rag-staging.azurewebsites.net"
poetry run pytest tests/integration/ -v
```

---

## 📊 Monitoring & Logging

### Azure Application Insights

```powershell
# View live metrics
az monitor app-insights component show \
  --app eva-rag-staging-insights \
  --resource-group eva-rag-staging

# Query logs
az monitor app-insights query \
  --app eva-rag-staging-insights \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by resultCode"
```

### View Logs

```powershell
# Azure App Service logs
az webapp log tail --name eva-rag-staging --resource-group eva-rag-staging

# Kubernetes logs
kubectl logs -f deployment/eva-rag -n eva-suite --tail=100

# Docker logs
docker logs -f eva-rag
```

---

## 🔐 Security Best Practices

### Environment Variables
- ✅ Store secrets in Azure Key Vault
- ✅ Use managed identities when possible
- ✅ Rotate keys regularly
- ✅ Never commit secrets to Git

### Network Security
- ✅ Use HTTPS for all endpoints
- ✅ Configure CORS properly
- ✅ Implement rate limiting
- ✅ Use API keys or OAuth for authentication

### Container Security
- ✅ Run as non-root user
- ✅ Scan images for vulnerabilities
- ✅ Keep base images updated
- ✅ Minimize image size

---

## 🚨 Troubleshooting

### Common Issues

#### Container Fails to Start
```powershell
# Check logs
docker logs eva-rag

# Common causes:
# - Missing environment variables
# - Port already in use
# - Insufficient memory
```

#### Health Check Failing
```powershell
# Test health endpoint directly
curl http://localhost:8000/health -v

# Common causes:
# - Application not fully started
# - Azure services not configured
# - Network connectivity issues
```

#### High Memory Usage
```powershell
# Check container stats
docker stats eva-rag

# Solutions:
# - Reduce EMBEDDING_BATCH_SIZE
# - Increase container memory limits
# - Scale horizontally
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review environment variables
3. Verify Azure services are accessible
4. Consult DELIVERY-PACKAGE.md
5. Open GitHub issue with logs

---

## 🎯 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Azure services provisioned
- [ ] Secrets stored in Key Vault
- [ ] Documentation reviewed

### Staging Deployment
- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Verify health checks
- [ ] Test key workflows
- [ ] Performance testing

### Production Deployment
- [ ] Staging validation complete
- [ ] Backup current production
- [ ] Deploy during maintenance window
- [ ] Run smoke tests
- [ ] Monitor for errors
- [ ] Rollback plan ready

### Post-Deployment
- [ ] Verify all endpoints
- [ ] Check monitoring dashboards
- [ ] Review error logs
- [ ] Update documentation
- [ ] Notify stakeholders

---

**Deployment Guide Version:** 1.0  
**Last Updated:** December 8, 2025  
**Status:** Production Ready ✅
