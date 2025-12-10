#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy EVA RAG Cosmos DB infrastructure to Azure
.DESCRIPTION
    Deploys HPK-enabled Cosmos DB using Bicep templates
.PARAMETER Environment
    Target environment (dev, staging, prod)
.PARAMETER ResourceGroup
    Azure resource group name
.PARAMETER Location
    Azure region
.PARAMETER WhatIf
    Preview deployment without making changes
.EXAMPLE
    .\deploy.ps1 -Environment dev -ResourceGroup eva-rag-dev -Location eastus
.EXAMPLE
    .\deploy.ps1 -Environment dev -WhatIf
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'dev',
    
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup = "eva-rag-$Environment",
    
    [Parameter(Mandatory = $false)]
    [string]$Location = 'eastus',
    
    [Parameter(Mandatory = $false)]
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       EVA RAG - Azure Cosmos DB Deployment                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📋 Deployment Configuration:" -ForegroundColor Yellow
Write-Host "   Environment:     $Environment" -ForegroundColor White
Write-Host "   Resource Group:  $ResourceGroup" -ForegroundColor White
Write-Host "   Location:        $Location" -ForegroundColor White
Write-Host "   WhatIf Mode:     $($WhatIf.IsPresent)" -ForegroundColor White
Write-Host ""

# Check Azure CLI
Write-Host "🔍 Checking Azure CLI..." -ForegroundColor Cyan
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "   ✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Azure CLI not found. Please install: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

# Check login status
Write-Host "`n🔐 Checking Azure login status..." -ForegroundColor Cyan
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "   ✅ Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "   ✅ Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Not logged in. Running az login..." -ForegroundColor Yellow
    az login
}

# Create resource group if needed
Write-Host "`n📦 Checking resource group..." -ForegroundColor Cyan
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq 'false') {
    Write-Host "   Creating resource group '$ResourceGroup'..." -ForegroundColor Yellow
    if (-not $WhatIf) {
        az group create --name $ResourceGroup --location $Location
        Write-Host "   ✅ Resource group created" -ForegroundColor Green
    } else {
        Write-Host "   [WhatIf] Would create resource group '$ResourceGroup'" -ForegroundColor Magenta
    }
} else {
    Write-Host "   ✅ Resource group exists" -ForegroundColor Green
}

# Validate Bicep template
Write-Host "`n🔍 Validating Bicep template..." -ForegroundColor Cyan
$bicepFile = Join-Path $PSScriptRoot "cosmos_db.bicep"
$parametersFile = Join-Path $PSScriptRoot "cosmos_db.parameters.json"

if (-not (Test-Path $bicepFile)) {
    Write-Host "   ❌ Bicep file not found: $bicepFile" -ForegroundColor Red
    exit 1
}

try {
    az bicep build --file $bicepFile --stdout | Out-Null
    Write-Host "   ✅ Bicep template is valid" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Bicep validation failed" -ForegroundColor Red
    exit 1
}

# Deploy
Write-Host "`n🚀 Deploying Cosmos DB..." -ForegroundColor Cyan
$deploymentName = "eva-rag-cosmos-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

if ($WhatIf) {
    Write-Host "   [WhatIf] Would deploy with name: $deploymentName" -ForegroundColor Magenta
    az deployment group what-if `
        --resource-group $ResourceGroup `
        --template-file $bicepFile `
        --parameters $parametersFile `
        --parameters environment=$Environment
} else {
    Write-Host "   Deployment name: $deploymentName" -ForegroundColor White
    az deployment group create `
        --resource-group $ResourceGroup `
        --name $deploymentName `
        --template-file $bicepFile `
        --parameters $parametersFile `
        --parameters environment=$Environment `
        --output table
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n   ✅ Deployment successful!" -ForegroundColor Green
        
        # Get outputs
        Write-Host "`n📊 Deployment Outputs:" -ForegroundColor Cyan
        $outputs = az deployment group show `
            --resource-group $ResourceGroup `
            --name $deploymentName `
            --query properties.outputs `
            --output json | ConvertFrom-Json
        
        Write-Host "   Cosmos Account: $($outputs.cosmosAccountName.value)" -ForegroundColor White
        Write-Host "   Endpoint:       $($outputs.cosmosEndpoint.value)" -ForegroundColor White
        Write-Host "   Database:       $($outputs.databaseName.value)" -ForegroundColor White
        Write-Host "`n   Containers:" -ForegroundColor White
        foreach ($container in $outputs.containerNames.value) {
            Write-Host "      • $container" -ForegroundColor Cyan
        }
        
        # Save connection info
        Write-Host "`n💾 Saving connection information..." -ForegroundColor Cyan
        $connectionInfo = @{
            cosmos_account = $outputs.cosmosAccountName.value
            cosmos_endpoint = $outputs.cosmosEndpoint.value
            database_name = $outputs.databaseName.value
            containers = $outputs.containerNames.value
            deployed_at = (Get-Date).ToString('o')
            environment = $Environment
        }
        
        $outputFile = Join-Path $PSScriptRoot "deployment-output-$Environment.json"
        $connectionInfo | ConvertTo-Json -Depth 10 | Set-Content $outputFile
        Write-Host "   ✅ Saved to: $outputFile" -ForegroundColor Green
        
        # Get connection string
        Write-Host "`n🔑 Retrieving connection string..." -ForegroundColor Cyan
        $connectionString = az cosmosdb keys list `
            --resource-group $ResourceGroup `
            --name $outputs.cosmosAccountName.value `
            --type connection-strings `
            --query "connectionStrings[0].connectionString" `
            --output tsv
        
        Write-Host "   ✅ Connection string retrieved (save to .env)" -ForegroundColor Green
        Write-Host "`n   COSMOS_CONNECTION_STRING=$connectionString`n" -ForegroundColor Yellow
        
    } else {
        Write-Host "`n   ❌ Deployment failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                   Deployment Complete!                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Add connection string to .env file" -ForegroundColor White
Write-Host "   2. Run migration: python scripts/migrate_to_hpk.py --dry-run" -ForegroundColor White
Write-Host "   3. Verify deployment: python scripts/verify_containers.py" -ForegroundColor White
Write-Host ""
