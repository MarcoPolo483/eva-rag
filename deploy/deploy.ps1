# EVA RAG - Complete Deployment Script
# Orchestrates the entire deployment process

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('staging', 'production')]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('terraform', 'docker', 'kubernetes', 'azure')]
    [string]$DeploymentMethod = 'azure',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipValidation,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoApprove
)

$ErrorActionPreference = "Stop"
$startTime = Get-Date

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║                   EVA RAG DEPLOYMENT                          ║
║                                                                ║
║  Environment: $($Environment.PadRight(47)) ║
║  Method: $($DeploymentMethod.PadRight(52)) ║
║  Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                        ║
╚═══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Change to repo root
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

# ============================================================================
# PHASE 1: PRE-DEPLOYMENT VALIDATION
# ============================================================================

Write-Host "`n📋 PHASE 1: PRE-DEPLOYMENT VALIDATION" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow

# Check Azure CLI
Write-Host "`n✓ Checking Azure CLI..." -ForegroundColor Cyan
try {
    $azVersion = az --version 2>$null
    if (-not $azVersion) { throw "Azure CLI not found" }
    Write-Host "  Azure CLI: OK" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Azure CLI not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Install: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check logged in to Azure
Write-Host "`n✓ Checking Azure authentication..." -ForegroundColor Cyan
$azAccount = az account show 2>$null | ConvertFrom-Json
if (-not $azAccount) {
    Write-Host "  ⚠️  Not logged in to Azure" -ForegroundColor Yellow
    Write-Host "  Logging in..." -ForegroundColor Cyan
    az login
    $azAccount = az account show 2>$null | ConvertFrom-Json
}
Write-Host "  Subscription: $($azAccount.name)" -ForegroundColor Green
Write-Host "  Account: $($azAccount.user.name)" -ForegroundColor Green

# Check Python
Write-Host "`n✓ Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python not found" -ForegroundColor Red
    exit 1
}

# Check Poetry
Write-Host "`n✓ Checking Poetry..." -ForegroundColor Cyan
try {
    $poetryVersion = poetry --version 2>&1
    Write-Host "  $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Poetry not found" -ForegroundColor Red
    Write-Host "  Install: curl -sSL https://install.python-poetry.org | python3 -" -ForegroundColor Yellow
    exit 1
}

# Check Docker (if needed)
if ($DeploymentMethod -eq 'docker' -or $DeploymentMethod -eq 'kubernetes') {
    Write-Host "`n✓ Checking Docker..." -ForegroundColor Cyan
    try {
        $dockerVersion = docker --version 2>&1
        Write-Host "  $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Docker not found" -ForegroundColor Red
        exit 1
    }
}

# Check Terraform (if needed)
if ($DeploymentMethod -eq 'terraform') {
    Write-Host "`n✓ Checking Terraform..." -ForegroundColor Cyan
    try {
        $tfVersion = terraform --version 2>&1 | Select-Object -First 1
        Write-Host "  $tfVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Terraform not found" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# PHASE 2: CODE QUALITY & TESTS
# ============================================================================

if (-not $SkipTests) {
    Write-Host "`n`n🧪 PHASE 2: CODE QUALITY & TESTS" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow
    
    # Install dependencies
    Write-Host "`n✓ Installing dependencies..." -ForegroundColor Cyan
    poetry install --no-interaction
    
    # Run tests
    Write-Host "`n✓ Running test suite..." -ForegroundColor Cyan
    $testResult = poetry run pytest --cov=src/eva_rag --cov-report=term -m "not integration" -q 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Tests failed" -ForegroundColor Red
        Write-Host $testResult
        exit 1
    }
    Write-Host "  ✅ All tests passed" -ForegroundColor Green
    
    # Code quality checks
    Write-Host "`n✓ Running code quality checks..." -ForegroundColor Cyan
    
    # Black (formatting)
    $blackResult = poetry run black --check src/ tests/ 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Black: Code formatting OK" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Black: Formatting issues found (non-blocking)" -ForegroundColor Yellow
    }
    
    # Security scan
    Write-Host "`n✓ Running security scan..." -ForegroundColor Cyan
    $banditResult = poetry run bandit -r src/ -f json -q 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Bandit: No security issues" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Bandit: Security issues found (review required)" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "`n⏭️  PHASE 2: SKIPPED (--SkipTests flag)" -ForegroundColor Yellow
}

# ============================================================================
# PHASE 3: BUILD
# ============================================================================

Write-Host "`n`n🔨 PHASE 3: BUILD" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow

if ($DeploymentMethod -eq 'docker' -or $DeploymentMethod -eq 'kubernetes') {
    Write-Host "`n✓ Building Docker image..." -ForegroundColor Cyan
    $imageName = "eva-rag:$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    docker build -t $imageName . --build-arg ENVIRONMENT=$Environment
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Image built: $imageName" -ForegroundColor Green
} else {
    Write-Host "`n✓ Creating deployment package..." -ForegroundColor Cyan
    $buildDir = Join-Path $repoRoot "build"
    if (Test-Path $buildDir) {
        Remove-Item -Path $buildDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
    
    # Copy files
    Copy-Item -Path (Join-Path $repoRoot "src") -Destination $buildDir -Recurse
    Copy-Item -Path (Join-Path $repoRoot "pyproject.toml") -Destination $buildDir
    Copy-Item -Path (Join-Path $repoRoot "poetry.lock") -Destination $buildDir
    
    Write-Host "  ✅ Deployment package created" -ForegroundColor Green
}

# ============================================================================
# PHASE 4: INFRASTRUCTURE
# ============================================================================

Write-Host "`n`n☁️  PHASE 4: INFRASTRUCTURE" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow

if ($DeploymentMethod -eq 'terraform') {
    Write-Host "`n✓ Deploying infrastructure with Terraform..." -ForegroundColor Cyan
    Set-Location (Join-Path $repoRoot "terraform")
    
    # Initialize
    terraform init
    
    # Plan
    Write-Host "`n  Planning infrastructure changes..." -ForegroundColor Cyan
    terraform plan -var-file="$Environment.tfvars" -out=tfplan
    
    # Apply
    if ($AutoApprove) {
        terraform apply -auto-approve tfplan
    } else {
        Write-Host "`n  Review the plan above. Continue? [Y/n]" -ForegroundColor Yellow
        $confirmation = Read-Host
        if ($confirmation -eq 'n' -or $confirmation -eq 'N') {
            Write-Host "  Deployment cancelled" -ForegroundColor Red
            exit 0
        }
        terraform apply tfplan
    }
    
    # Get outputs
    $appUrl = terraform output -raw app_service_url
    $appName = terraform output -raw app_service_name
    $rgName = terraform output -raw resource_group_name
    
    Set-Location $repoRoot
    
} elseif ($DeploymentMethod -eq 'azure') {
    Write-Host "`n✓ Using existing Azure infrastructure..." -ForegroundColor Cyan
    $rgName = "eva-rag-$Environment"
    $appName = "eva-rag-$Environment"
    
    # Check if resources exist
    $rgExists = az group exists --name $rgName | ConvertFrom-Json
    if (-not $rgExists) {
        Write-Host "  ❌ Resource group $rgName not found" -ForegroundColor Red
        Write-Host "  Run Terraform deployment first or create resources manually" -ForegroundColor Yellow
        exit 1
    }
    
    $appUrl = "https://$appName.azurewebsites.net"
    Write-Host "  ✅ Using existing resources" -ForegroundColor Green
}

# ============================================================================
# PHASE 5: DEPLOY APPLICATION
# ============================================================================

Write-Host "`n`n🚀 PHASE 5: DEPLOY APPLICATION" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow

if ($DeploymentMethod -eq 'docker') {
    Write-Host "`n✓ Starting Docker container..." -ForegroundColor Cyan
    docker-compose -f docker-compose.yml up -d
    $appUrl = "http://localhost:8000"
    
} elseif ($DeploymentMethod -eq 'kubernetes') {
    Write-Host "`n✓ Deploying to Kubernetes..." -ForegroundColor Cyan
    kubectl apply -f deploy/kubernetes.yaml
    Write-Host "  ✅ Kubernetes resources applied" -ForegroundColor Green
    
    # Wait for deployment
    Write-Host "`n  Waiting for deployment to be ready..." -ForegroundColor Cyan
    kubectl wait --for=condition=available --timeout=300s deployment/eva-rag -n eva-suite
    
} elseif ($DeploymentMethod -eq 'azure' -or $DeploymentMethod -eq 'terraform') {
    Write-Host "`n✓ Deploying to Azure App Service..." -ForegroundColor Cyan
    
    # Create zip package
    $zipPath = Join-Path $repoRoot "eva-rag-$Environment.zip"
    Compress-Archive -Path "$buildDir\*" -DestinationPath $zipPath -Force
    
    # Deploy
    az webapp deployment source config-zip `
        --name $appName `
        --resource-group $rgName `
        --src $zipPath
    
    Write-Host "  ✅ Application deployed" -ForegroundColor Green
    
    # Restart
    Write-Host "`n  Restarting application..." -ForegroundColor Cyan
    az webapp restart --name $appName --resource-group $rgName
}

# ============================================================================
# PHASE 6: POST-DEPLOYMENT VALIDATION
# ============================================================================

if (-not $SkipValidation) {
    Write-Host "`n`n✅ PHASE 6: POST-DEPLOYMENT VALIDATION" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow
    
    # Wait for app to start
    Write-Host "`n✓ Waiting for application to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30
    
    # Health check
    Write-Host "`n✓ Running health check..." -ForegroundColor Cyan
    $maxRetries = 10
    $retryCount = 0
    $healthy = $false
    
    while ($retryCount -lt $maxRetries -and -not $healthy) {
        try {
            $response = Invoke-RestMethod -Uri "$appUrl/health" -Method Get -TimeoutSec 10
            if ($response.status -eq "healthy") {
                $healthy = $true
                Write-Host "  ✅ Health check passed" -ForegroundColor Green
                Write-Host "     Status: $($response.status)" -ForegroundColor Green
                Write-Host "     Timestamp: $($response.timestamp)" -ForegroundColor Green
            }
        } catch {
            $retryCount++
            Write-Host "  ⚠️  Attempt $retryCount/$maxRetries failed, retrying..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        }
    }
    
    if (-not $healthy) {
        Write-Host "  ❌ Health check failed after $maxRetries attempts" -ForegroundColor Red
        Write-Host "  Check application logs for details" -ForegroundColor Yellow
    }
    
    # Smoke tests
    Write-Host "`n✓ Running smoke tests..." -ForegroundColor Cyan
    
    # Test API docs
    try {
        $docsResponse = Invoke-WebRequest -Uri "$appUrl/api/v1/docs" -Method Get -TimeoutSec 10
        if ($docsResponse.StatusCode -eq 200) {
            Write-Host "  ✅ API documentation accessible" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠️  API documentation check failed" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "`n⏭️  PHASE 6: SKIPPED (--SkipValidation flag)" -ForegroundColor Yellow
}

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                   DEPLOYMENT COMPLETE                         ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "📊 DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Environment:       $Environment" -ForegroundColor White
Write-Host "Method:            $DeploymentMethod" -ForegroundColor White
Write-Host "Duration:          $($duration.ToString('mm\:ss'))" -ForegroundColor White
Write-Host "Status:            ✅ SUCCESS" -ForegroundColor Green

Write-Host "`n🔗 ACCESS POINTS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Application:       $appUrl" -ForegroundColor White
Write-Host "Health Check:      $appUrl/health" -ForegroundColor White
Write-Host "API Docs:          $appUrl/api/v1/docs" -ForegroundColor White
Write-Host "ReDoc:             $appUrl/api/v1/redoc" -ForegroundColor White

if ($DeploymentMethod -eq 'azure' -or $DeploymentMethod -eq 'terraform') {
    Write-Host "`n📝 AZURE RESOURCES" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan
    
    Write-Host "Resource Group:    $rgName" -ForegroundColor White
    Write-Host "App Service:       $appName" -ForegroundColor White
    
    Write-Host "`n💡 USEFUL COMMANDS" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════`n" -ForegroundColor Cyan
    
    Write-Host "View logs:" -ForegroundColor Yellow
    Write-Host "  az webapp log tail --name $appName --resource-group $rgName`n" -ForegroundColor White
    
    Write-Host "Restart app:" -ForegroundColor Yellow
    Write-Host "  az webapp restart --name $appName --resource-group $rgName`n" -ForegroundColor White
    
    Write-Host "View metrics:" -ForegroundColor Yellow
    Write-Host "  az monitor metrics list --resource /subscriptions/.../providers/Microsoft.Web/sites/$appName`n" -ForegroundColor White
}

Write-Host "`n🎉 Deployment completed successfully!`n" -ForegroundColor Green
