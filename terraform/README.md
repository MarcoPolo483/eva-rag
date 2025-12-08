# EVA RAG - Terraform Deployment Guide

## 📋 Prerequisites

- Terraform >= 1.5
- Azure CLI installed and authenticated
- Appropriate Azure permissions to create resources
- Backend storage account for Terraform state (optional but recommended)

## 🚀 Quick Start

### 1. Initialize Terraform

```powershell
cd terraform

# Initialize Terraform (first time only)
terraform init
```

### 2. Review the Plan

```powershell
# Staging
terraform plan -var-file="staging.tfvars"

# Production
terraform plan -var-file="production.tfvars"
```

### 3. Deploy Infrastructure

```powershell
# Staging
terraform apply -var-file="staging.tfvars"

# Production
terraform apply -var-file="production.tfvars"
```

## 📦 What Gets Created

### Core Infrastructure
- **Resource Group** - Container for all resources
- **App Service Plan** - Hosting plan (P1v2 staging, P2v2 production)
- **App Service** - Web application host
- **Application Insights** - Monitoring and telemetry
- **Log Analytics Workspace** - Centralized logging

### Storage & Data
- **Storage Account** - Document storage with versioning
- **Storage Container** - eva-rag-documents container
- **Cosmos DB Account** - NoSQL database (serverless)
- **Cosmos DB Database** - eva-rag database
- **Cosmos DB Container** - document-metadata container

### Security
- **Key Vault** - Secrets management
- **Managed Identity** - App Service identity for Key Vault access
- **Key Vault Secrets** - Secure storage for connection strings

### Monitoring
- **CPU Alert** - Triggers when CPU > 80%
- **Memory Alert** - Triggers when memory > 85%
- **HTTP Errors Alert** - Triggers on 5xx errors > 10

## 🔧 Configuration

### Environment Variables

Edit `staging.tfvars` or `production.tfvars`:

```hcl
environment         = "staging"
location           = "eastus"
app_service_sku    = "P1v2"
cosmos_db_throughput = 400

allowed_ip_addresses = [
  "1.2.3.4",  # Your office IP
  "5.6.7.8",  # CI/CD pipeline IP
]

tags = {
  Project     = "EVA Suite"
  Component   = "RAG Engine"
  Environment = "Staging"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}
```

### Backend Configuration

For team environments, configure remote state:

```hcl
# In main.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "eva-suite-terraform"
    storage_account_name = "evaterraformstate"
    container_name       = "tfstate"
    key                  = "eva-rag-staging.terraform.tfstate"
  }
}
```

Create the backend:

```powershell
# Create resource group
az group create --name eva-suite-terraform --location eastus

# Create storage account
az storage account create `
  --name evaterraformstate `
  --resource-group eva-suite-terraform `
  --location eastus `
  --sku Standard_LRS `
  --encryption-services blob

# Create container
az storage container create `
  --name tfstate `
  --account-name evaterraformstate
```

## 🎯 Deployment Workflow

### First-Time Deployment

```powershell
# 1. Initialize
terraform init

# 2. Format and validate
terraform fmt
terraform validate

# 3. Plan and review
terraform plan -var-file="staging.tfvars" -out=tfplan

# 4. Apply
terraform apply tfplan

# 5. Verify outputs
terraform output
```

### Updates

```powershell
# 1. Pull latest state (if using remote backend)
terraform refresh

# 2. Plan changes
terraform plan -var-file="staging.tfvars"

# 3. Apply changes
terraform apply -var-file="staging.tfvars"
```

### Destroy Resources

```powershell
# WARNING: This will delete all resources!
terraform destroy -var-file="staging.tfvars"
```

## 📊 Post-Deployment Setup

### 1. Configure OpenAI and Search Secrets

```powershell
# Get Key Vault name from output
$kvName = terraform output -raw key_vault_uri | Select-String -Pattern "https://(.+?)\.vault" | ForEach-Object { $_.Matches.Groups[1].Value }

# Set secrets
az keyvault secret set --vault-name $kvName --name "openai-endpoint" --value "YOUR_ENDPOINT"
az keyvault secret set --vault-name $kvName --name "openai-api-key" --value "YOUR_KEY"
az keyvault secret set --vault-name $kvName --name "search-endpoint" --value "YOUR_ENDPOINT"
az keyvault secret set --vault-name $kvName --name "search-admin-key" --value "YOUR_KEY"
```

### 2. Deploy Application Code

```powershell
# Get app name
$appName = terraform output -raw app_service_name
$rgName = terraform output -raw resource_group_name

# Deploy using Azure CLI
cd ..
az webapp up --name $appName --resource-group $rgName --runtime "PYTHON:3.11"
```

### 3. Verify Deployment

```powershell
# Get app URL
$appUrl = terraform output -raw app_service_url

# Test health endpoint
Invoke-RestMethod -Uri "$appUrl/health"

# Open in browser
Start-Process "$appUrl/api/v1/docs"
```

## 🔍 Troubleshooting

### State Lock Issues

```powershell
# If state is locked, force unlock (use carefully!)
terraform force-unlock LOCK_ID
```

### Import Existing Resources

```powershell
# Import existing resource group
terraform import azurerm_resource_group.eva_rag /subscriptions/SUBSCRIPTION_ID/resourceGroups/eva-rag-staging
```

### Refresh State

```powershell
# Sync state with actual infrastructure
terraform refresh -var-file="staging.tfvars"
```

### Debug Mode

```powershell
# Enable debug logging
$env:TF_LOG = "DEBUG"
terraform plan -var-file="staging.tfvars"
```

## 📈 Cost Estimation

### Staging Environment (~$150/month)
- App Service Plan P1v2: ~$80/month
- Cosmos DB (Serverless): ~$10-30/month
- Storage Account: ~$5/month
- Application Insights: ~$10/month
- Key Vault: ~$5/month

### Production Environment (~$350/month)
- App Service Plan P2v2: ~$160/month
- Cosmos DB (Serverless): ~$50-100/month
- Storage Account (GRS): ~$15/month
- Application Insights: ~$30/month
- Key Vault: ~$5/month

Run cost estimation:

```powershell
# Install Infracost
choco install infracost

# Generate cost estimate
infracost breakdown --path . --terraform-var-file staging.tfvars
```

## 🛡️ Security Best Practices

### 1. State File Security
- Store state remotely in Azure Storage
- Enable encryption at rest
- Restrict access with RBAC

### 2. Secrets Management
- Never store secrets in .tfvars files
- Use Azure Key Vault for all secrets
- Rotate secrets regularly

### 3. Network Security
- Configure allowed IP addresses
- Enable private endpoints (production)
- Use managed identities

### 4. Access Control
- Use service principals for CI/CD
- Apply least privilege principle
- Enable audit logging

## 📝 Terraform Commands Reference

```powershell
# Initialize workspace
terraform init

# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

# Plan changes
terraform plan -var-file="staging.tfvars"

# Apply changes
terraform apply -var-file="staging.tfvars"

# Show current state
terraform show

# List resources
terraform state list

# Show specific resource
terraform state show azurerm_linux_web_app.eva_rag

# Output values
terraform output
terraform output -json

# Refresh state
terraform refresh -var-file="staging.tfvars"

# Destroy resources
terraform destroy -var-file="staging.tfvars"

# Import resource
terraform import RESOURCE_TYPE.NAME AZURE_RESOURCE_ID

# Workspace commands
terraform workspace list
terraform workspace new staging
terraform workspace select staging
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Terraform Init
  run: terraform init

- name: Terraform Plan
  run: terraform plan -var-file="staging.tfvars" -out=tfplan

- name: Terraform Apply
  if: github.ref == 'refs/heads/master'
  run: terraform apply -auto-approve tfplan
```

## 📞 Support

For Terraform issues:
1. Check `terraform.log` for errors
2. Verify Azure permissions
3. Review state file for conflicts
4. Consult [Terraform Azure Provider docs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

---

**Terraform Version:** >= 1.5  
**Azure Provider Version:** ~> 3.80  
**Last Updated:** December 8, 2025
