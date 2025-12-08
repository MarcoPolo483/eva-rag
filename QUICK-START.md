# EVA RAG - Quick Start Guide

## 🚀 Choose Your Deployment Method

### 1️⃣ Local Development (Docker) - 5 minutes

```powershell
# Setup
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"
cp .env.example .env
# Edit .env with your Azure credentials

# Start
docker-compose up -d

# Verify
curl http://localhost:8000/health
start http://localhost:8000/api/v1/docs
```

### 2️⃣ Azure Staging - 10 minutes

```powershell
# One-command deployment
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"
.\deploy\deploy.ps1 -Environment staging

# Access
# URL displayed at end: https://eva-rag-staging.azurewebsites.net
```

### 3️⃣ Terraform Infrastructure - 15 minutes

```powershell
# Deploy infrastructure
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag\terraform"
terraform init
terraform plan -var-file="staging.tfvars"
terraform apply -var-file="staging.tfvars"

# Deploy application
cd ..
.\deploy\deploy-azure.ps1 -Environment staging
```

### 4️⃣ Kubernetes Production - 20 minutes

```bash
# Create secrets
kubectl create namespace eva-suite
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

# Deploy
kubectl apply -f deploy/kubernetes.yaml

# Verify
kubectl get pods -n eva-suite
kubectl port-forward service/eva-rag-service 8000:80 -n eva-suite
```

---

## 📚 Documentation Index

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [README.md](README.md) | Project overview | First time here |
| [DEPLOYMENT-COMPLETE.md](DEPLOYMENT-COMPLETE.md) | Complete summary | See what's delivered |
| [DEPLOYMENT-PACKAGE.md](DEPLOYMENT-PACKAGE.md) | Full package details | Understand everything |
| [deploy/DEPLOYMENT-GUIDE.md](deploy/DEPLOYMENT-GUIDE.md) | Step-by-step deployment | Deploy to any environment |
| [deploy/DEPLOYMENT-CHECKLIST.md](deploy/DEPLOYMENT-CHECKLIST.md) | Production checklist | Before production deploy |
| [terraform/README.md](terraform/README.md) | Terraform guide | Using Terraform |
| [docs/MONITORING.md](docs/MONITORING.md) | Operations & monitoring | After deployment |
| [docs/DEVELOPMENT-GUIDE.md](docs/DEVELOPMENT-GUIDE.md) | Developer setup | Contributing code |

---

## 🔍 Quick Commands

### Testing
```powershell
# Run all tests
poetry run pytest --cov=src/eva_rag -v

# Run with coverage report
poetry run pytest --cov=src/eva_rag --cov-report=html
start htmlcov/index.html

# Integration tests only
poetry run pytest -m integration -v
```

### Local Server
```powershell
# Start development server
poetry run uvicorn eva_rag.main:app --reload --port 8000

# Access
start http://localhost:8000/api/v1/docs
```

### Docker
```powershell
# Build
docker build -t eva-rag:latest .

# Run
docker run -d -p 8000:8000 --env-file .env eva-rag:latest

# Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Azure
```powershell
# View logs
az webapp log tail --name eva-rag-staging --resource-group eva-rag-staging

# Restart
az webapp restart --name eva-rag-staging --resource-group eva-rag-staging

# Deploy
.\deploy\deploy.ps1 -Environment staging
```

### Git
```powershell
# Status
git status
git log --oneline -5

# Push changes
git add .
git commit -m "feat: your changes"
git push origin master
```

---

## 🎯 What to Do First

### If you're Marco (owner):
1. **Test locally with Docker**
   ```powershell
   docker-compose up -d
   curl http://localhost:8000/health
   ```

2. **Deploy to staging**
   ```powershell
   .\deploy\deploy.ps1 -Environment staging
   ```

3. **Monitor deployment**
   - Check Application Insights
   - Review logs
   - Run smoke tests

### If you're a developer:
1. Read `docs/DEVELOPMENT-GUIDE.md`
2. Set up local environment
3. Run tests: `poetry run pytest`
4. Start coding!

### If you're DevOps:
1. Review `deploy/DEPLOYMENT-GUIDE.md`
2. Set up Azure resources (Terraform)
3. Configure CI/CD secrets
4. Deploy to staging first

---

## ✅ Health Checks

```powershell
# Local
curl http://localhost:8000/health

# Staging
curl https://eva-rag-staging.azurewebsites.net/health

# Production
curl https://eva-rag-prod.azurewebsites.net/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-08T12:00:00Z"
}
```

---

## 🚨 Quick Troubleshooting

### Issue: Tests failing
```powershell
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
poetry install

# Clear cache
poetry run pytest --cache-clear
```

### Issue: Docker build fails
```powershell
# Check Docker is running
docker --version

# Clean build
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Azure deployment fails
```powershell
# Check Azure login
az account show

# Re-login if needed
az login

# Check resource group exists
az group exists --name eva-rag-staging
```

---

## 📞 Get Help

- **Documentation:** See index above
- **Issues:** https://github.com/MarcoPolo483/eva-rag/issues
- **Logs:** `az webapp log tail` or `docker logs`
- **Repository:** https://github.com/MarcoPolo483/eva-rag

---

**Quick Start Version:** 1.0  
**Last Updated:** December 8, 2025  
**Status:** ✅ Production Ready
