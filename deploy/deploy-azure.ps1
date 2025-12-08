# EVA RAG - Azure Web App Deployment Script
# This script deploys EVA RAG to Azure App Service

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('staging', 'production')]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "eva-suite-$Environment",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "eva-rag-$Environment",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$SkuName = "P1v2"
)

Write-Host "🚀 Deploying EVA RAG to Azure" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host "App Name: $AppName" -ForegroundColor Cyan

# Check if logged in to Azure
Write-Host "`n1️⃣ Checking Azure login..." -ForegroundColor Yellow
$azAccount = az account show 2>$null
if (-not $azAccount) {
    Write-Host "Not logged in. Please login to Azure..." -ForegroundColor Red
    az login
}

# Create resource group if it doesn't exist
Write-Host "`n2️⃣ Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# Create App Service Plan
Write-Host "`n3️⃣ Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name "$AppName-plan" `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku $SkuName `
    --is-linux

# Create Web App
Write-Host "`n4️⃣ Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan "$AppName-plan" `
    --runtime "PYTHON:3.11"

# Configure Web App settings
Write-Host "`n5️⃣ Configuring Web App settings..." -ForegroundColor Yellow

# Set startup command
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --startup-file "uvicorn eva_rag.main:app --host 0.0.0.0 --port 8000"

# Configure environment variables
Write-Host "`n6️⃣ Setting environment variables..." -ForegroundColor Yellow

# Get environment variables from Key Vault
$keyVaultName = "eva-suite-$Environment-kv"

Write-Host "Retrieving secrets from Key Vault: $keyVaultName" -ForegroundColor Cyan

az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        ENVIRONMENT=$Environment `
        LOG_LEVEL="INFO" `
        MAX_FILE_SIZE_MB="50" `
        SUPPORTED_LANGUAGES="en,fr" `
        DEFAULT_CHUNK_SIZE="512" `
        DEFAULT_CHUNK_OVERLAP="50" `
        EMBEDDING_BATCH_SIZE="16" `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" `
        WEBSITE_HTTPLOGGING_RETENTION_DAYS="7"

# Configure App Settings from Key Vault references
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-storage-account-name/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-storage-account-key/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-cosmos-endpoint/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-cosmos-key/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-openai-endpoint/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-openai-api-key/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-search-endpoint/)" `
        "@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/azure-search-admin-key/)"

# Enable managed identity
Write-Host "`n7️⃣ Enabling managed identity..." -ForegroundColor Yellow
az webapp identity assign `
    --name $AppName `
    --resource-group $ResourceGroup

# Deploy application
Write-Host "`n8️⃣ Deploying application code..." -ForegroundColor Yellow
$buildDir = Join-Path $PSScriptRoot ".." "build"

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Cyan
if (Test-Path $buildDir) {
    Remove-Item -Path $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null

# Copy necessary files
Copy-Item -Path (Join-Path $PSScriptRoot ".." "src") -Destination $buildDir -Recurse
Copy-Item -Path (Join-Path $PSScriptRoot ".." "pyproject.toml") -Destination $buildDir
Copy-Item -Path (Join-Path $PSScriptRoot ".." "poetry.lock") -Destination $buildDir

# Create zip package
$zipPath = Join-Path $PSScriptRoot ".." "eva-rag-$Environment.zip"
Compress-Archive -Path "$buildDir\*" -DestinationPath $zipPath -Force

# Deploy via ZIP
az webapp deployment source config-zip `
    --name $AppName `
    --resource-group $ResourceGroup `
    --src $zipPath

# Configure logging
Write-Host "`n9️⃣ Configuring logging..." -ForegroundColor Yellow
az webapp log config `
    --name $AppName `
    --resource-group $ResourceGroup `
    --application-logging filesystem `
    --detailed-error-messages true `
    --failed-request-tracing true `
    --web-server-logging filesystem

# Enable Application Insights
Write-Host "`n🔟 Enabling Application Insights..." -ForegroundColor Yellow
$appInsightsName = "$AppName-insights"

az monitor app-insights component create `
    --app $appInsightsName `
    --location $Location `
    --resource-group $ResourceGroup `
    --application-type web

$instrumentationKey = az monitor app-insights component show `
    --app $appInsightsName `
    --resource-group $ResourceGroup `
    --query instrumentationKey `
    --output tsv

az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey `
        APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$instrumentationKey"

# Restart the app
Write-Host "`n♻️  Restarting Web App..." -ForegroundColor Yellow
az webapp restart `
    --name $AppName `
    --resource-group $ResourceGroup

# Get the URL
$appUrl = az webapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query defaultHostName `
    --output tsv

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "`n📍 Application URL: https://$appUrl" -ForegroundColor Cyan
Write-Host "📍 Health Check: https://$appUrl/health" -ForegroundColor Cyan
Write-Host "📍 API Docs: https://$appUrl/api/v1/docs" -ForegroundColor Cyan
Write-Host "📍 Logs: az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Cyan

# Run health check
Write-Host "`n🏥 Running health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

try {
    $healthResponse = Invoke-RestMethod -Uri "https://$appUrl/health" -Method Get
    if ($healthResponse.status -eq "healthy") {
        Write-Host "✅ Health check passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Health check returned unexpected status" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Deployment to $Environment completed successfully!" -ForegroundColor Green
