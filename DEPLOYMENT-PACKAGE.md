# EVA RAG - Complete Deployment Package

## 🎉 Overview

This package contains everything needed to deploy EVA RAG to any environment (staging/production).

**Version:** 1.0.0  
**Coverage:** 97.88%  
**Tests:** 129 passing  
**Status:** ✅ Production Ready

---

## 📦 Package Contents

### 1. Application Code
- **Location:** `src/eva_rag/`
- **Components:**
  - FastAPI application (`main.py`)
  - Document loaders (PDF, DOCX, TXT)
  - Chunking service
  - Embedding service
  - Azure integrations (Blob, Cosmos, Search, OpenAI)
  - Configuration management

### 2. Tests
- **Location:** `tests/`
- **Coverage:** 97.88%
- **Test Files:** 18
- **Total Tests:** 129 unit tests + 3 integration tests
- **Command:** `poetry run pytest --cov=src/eva_rag`

### 3. Docker Deployment
- **Dockerfile** - Multi-stage production build
- **docker-compose.yml** - Local/staging deployment
- **.dockerignore** - Build optimization
- **Command:** `docker-compose up -d`

### 4. Kubernetes Deployment
- **Location:** `deploy/kubernetes.yaml`
- **Includes:**
  - Deployment (3 replicas)
  - Service (ClusterIP)
  - ConfigMap (configuration)
  - Ingress (HTTPS)
  - HPA (auto-scaling 3-10 pods)
- **Command:** `kubectl apply -f deploy/kubernetes.yaml`

### 5. Azure Deployment
- **Script:** `deploy/deploy-azure.ps1`
- **Features:**
  - App Service creation
  - Key Vault integration
  - Application Insights
  - Managed identity
- **Command:** `.\deploy\deploy-azure.ps1 -Environment staging`

### 6. Terraform IaC
- **Location:** `terraform/`
- **Resources:**
  - Resource Group
  - App Service Plan & App Service
  - Storage Account & Container
  - Cosmos DB Account & Container
  - Key Vault & Secrets
  - Application Insights
  - Alert Rules
- **Command:** `terraform apply -var-file="staging.tfvars"`

### 7. CI/CD Pipeline
- **Location:** `.github/workflows/ci-cd.yml`
- **Stages:**
  - Test (coverage, quality)
  - Lint (black, isort, flake8)
  - Security (bandit, safety)
  - Build (Docker image)
  - Deploy (staging auto, production manual)

### 8. Documentation
- `README.md` - Project overview
- `docs/SPECIFICATION.md` - Technical specification
- `docs/API-USAGE-GUIDE.md` - API usage examples
- `docs/DEVELOPMENT-GUIDE.md` - Developer onboarding
- `docs/MONITORING.md` - Operations guide
- `deploy/DEPLOYMENT-GUIDE.md` - Deployment instructions
- `deploy/DEPLOYMENT-CHECKLIST.md` - Deployment checklist
- `terraform/README.md` - Terraform guide

---

## 🚀 Quick Start Deployment

### Option 1: Docker (Fastest for testing)

```powershell
# 1. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# 2. Start services
docker-compose up -d

# 3. Verify
curl http://localhost:8000/health
```

### Option 2: Azure App Service (Recommended for staging/prod)

```powershell
# 1. Run unified deployment script
.\deploy\deploy.ps1 -Environment staging

# 2. Access application
# URL will be displayed at end of deployment
```

### Option 3: Terraform (Infrastructure as Code)

```powershell
# 1. Navigate to terraform directory
cd terraform

# 2. Initialize and deploy
terraform init
terraform plan -var-file="staging.tfvars"
terraform apply -var-file="staging.tfvars"

# 3. Deploy application code
cd ..
.\deploy\deploy-azure.ps1 -Environment staging
```

### Option 4: Kubernetes (Scalable production)

```powershell
# 1. Create secrets
kubectl create secret generic eva-rag-secrets \
  --from-literal=storage-account-name=$AZURE_STORAGE_ACCOUNT_NAME \
  --from-literal=storage-account-key=$AZURE_STORAGE_ACCOUNT_KEY \
  # ... (see deploy/DEPLOYMENT-GUIDE.md for full list)

# 2. Deploy
kubectl apply -f deploy/kubernetes.yaml

# 3. Verify
kubectl get pods -n eva-suite
```

---

## ⚙️ Configuration

### Required Environment Variables

```bash
# Azure Storage
AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account>
AZURE_STORAGE_ACCOUNT_KEY=<your-storage-key>
AZURE_STORAGE_CONTAINER_NAME=eva-rag-documents

# Azure Cosmos DB
AZURE_COSMOS_ENDPOINT=<your-cosmos-endpoint>
AZURE_COSMOS_KEY=<your-cosmos-key>
AZURE_COSMOS_DATABASE_NAME=eva-rag
AZURE_COSMOS_CONTAINER_NAME=document-metadata

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>
AZURE_OPENAI_API_KEY=<your-openai-key>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search
AZURE_SEARCH_ENDPOINT=<your-search-endpoint>
AZURE_SEARCH_ADMIN_KEY=<your-search-key>
AZURE_SEARCH_INDEX_NAME=eva-rag-index

# Application Config
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
```

### Optional Configuration

```bash
SUPPORTED_LANGUAGES=en,fr
DEFAULT_CHUNK_SIZE=512
DEFAULT_CHUNK_OVERLAP=50
EMBEDDING_BATCH_SIZE=16
```

---

## 🧪 Testing

### Run All Tests

```powershell
poetry run pytest --cov=src/eva_rag --cov-report=html --cov-report=term -v
```

### Run Unit Tests Only

```powershell
poetry run pytest -m "not integration" -v
```

### Run Integration Tests

```powershell
# Configure Azure credentials first
poetry run pytest -m integration -v
```

### View Coverage Report

```powershell
# Generate HTML report
poetry run pytest --cov=src/eva_rag --cov-report=html

# Open in browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

---

## 📊 Monitoring & Health Checks

### Health Endpoint

```bash
curl https://your-app.azurewebsites.net/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-08T12:00:00Z",
  "checks": {
    "database": "healthy",
    "storage": "healthy",
    "search": "healthy"
  }
}
```

### Key Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Availability | 99.9% | < 99.5% |
| Response Time (P95) | < 2s | > 3s |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 80% |
| Memory Usage | < 80% | > 85% |

### View Logs

```powershell
# Azure App Service
az webapp log tail --name eva-rag-staging --resource-group eva-rag-staging

# Docker
docker logs -f eva-rag

# Kubernetes
kubectl logs -f deployment/eva-rag -n eva-suite
```

---

## 🔐 Security

### Secrets Management

✅ **DO:**
- Store secrets in Azure Key Vault
- Use managed identities
- Rotate keys regularly
- Use HTTPS everywhere

❌ **DON'T:**
- Commit secrets to Git
- Hardcode credentials
- Share secrets via email/chat
- Use same credentials across environments

### Security Checklist

- [ ] All secrets in Key Vault
- [ ] Managed identity configured
- [ ] HTTPS enforced
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation in place
- [ ] SQL injection prevented
- [ ] XSS protection enabled

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Application won't start
```powershell
# Check logs
az webapp log tail --name <app-name> --resource-group <rg-name>

# Common causes:
# - Missing environment variables
# - Invalid Azure credentials
# - Port conflict (Docker)
```

#### 2. Health check failing
```powershell
# Test directly
curl https://your-app.azurewebsites.net/health -v

# Common causes:
# - Application not fully started (wait 30s)
# - Azure services not accessible
# - Network/firewall issues
```

#### 3. High memory usage
```powershell
# Check container stats
docker stats eva-rag

# Solutions:
# - Reduce EMBEDDING_BATCH_SIZE
# - Increase memory limits
# - Scale horizontally
```

#### 4. Slow document processing
```powershell
# Check Azure service health
az monitor metrics list --resource <resource-id> --metric ResponseTime

# Solutions:
# - Optimize chunk size
# - Increase batch size
# - Scale out instances
```

---

## 📞 Support & Resources

### Documentation
- **Main README:** `README.md`
- **API Docs:** `/api/v1/docs` (when deployed)
- **Deployment Guide:** `deploy/DEPLOYMENT-GUIDE.md`
- **Monitoring Guide:** `docs/MONITORING.md`

### Commands Reference

```powershell
# Deployment
.\deploy\deploy.ps1 -Environment staging

# Health check
curl https://eva-rag-staging.azurewebsites.net/health

# View logs
az webapp log tail --name eva-rag-staging --resource-group eva-rag-staging

# Restart app
az webapp restart --name eva-rag-staging --resource-group eva-rag-staging

# Run tests
poetry run pytest --cov=src/eva_rag -v

# Build Docker image
docker build -t eva-rag:latest .

# Deploy with Terraform
cd terraform && terraform apply -var-file="staging.tfvars"
```

### Getting Help

1. Check documentation first
2. Review logs for errors
3. Verify environment variables
4. Test Azure connectivity
5. Open GitHub issue with details

---

## ✅ Deployment Checklist

Use `deploy/DEPLOYMENT-CHECKLIST.md` for complete deployment workflow.

**Quick checklist:**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Azure services provisioned
- [ ] Secrets in Key Vault
- [ ] Monitoring configured
- [ ] Backup plan ready
- [ ] Rollback plan tested
- [ ] Team notified

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ Health checks passing
- ✅ All tests passing (129/129)
- ✅ Error rate < 0.1%
- ✅ Response time p95 < 2s
- ✅ CPU < 70%, Memory < 80%
- ✅ Stable for 24 hours

---

## 📈 Performance Benchmarks

### Test Environment Specs
- **SKU:** P1v2 (Azure App Service)
- **vCPU:** 1
- **RAM:** 3.5 GB
- **Storage:** Azure Blob Storage (Standard)

### Performance Metrics

| Operation | Avg Time | P95 Time | Throughput |
|-----------|----------|----------|------------|
| Document Upload | 800ms | 1.5s | 60/min |
| Chunk Processing | 1.2s | 2.3s | 40/min |
| Embedding Generation | 3.5s | 5.2s | 15/min |
| Search Query | 450ms | 850ms | 120/min |
| Metadata CRUD | 200ms | 400ms | 300/min |

---

## 🏆 Quality Metrics

- **Test Coverage:** 97.88%
- **Lines of Code:** ~13,600
- **Files:** 65
- **Functions/Methods:** 200+
- **Test Files:** 18
- **Total Tests:** 132
- **Code Quality:** A (Black, Bandit clean)

---

**Package Version:** 1.0.0  
**Last Updated:** December 8, 2025  
**Status:** ✅ Production Ready  
**Repository:** https://github.com/MarcoPolo483/eva-rag
