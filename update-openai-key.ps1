#!/usr/bin/env pwsh
# Update Azure OpenAI API Key from GitHub Secret
# Usage: .\update-openai-key.ps1 <new-api-key>

param(
    [Parameter(Mandatory=$true)]
    [string]$NewApiKey
)

$envFile = ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: .env file not found" -ForegroundColor Red
    exit 1
}

# Validate key format (Azure OpenAI keys are typically 32 characters)
if ($NewApiKey.Length -lt 20) {
    Write-Host "⚠️  Warning: API key seems too short (expected 32+ chars)" -ForegroundColor Yellow
    $confirm = Read-Host "Continue anyway? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "❌ Aborted" -ForegroundColor Red
        exit 1
    }
}

# Read current .env
$content = Get-Content $envFile -Raw

# Replace Azure OpenAI API key
$pattern = '(?m)^AZURE_OPENAI_API_KEY=.*$'
$replacement = "AZURE_OPENAI_API_KEY=$NewApiKey"

if ($content -match $pattern) {
    $newContent = $content -replace $pattern, $replacement
    
    # Backup old .env
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = ".env.backup-$timestamp"
    Copy-Item $envFile $backupFile
    Write-Host "✅ Backed up old .env to $backupFile" -ForegroundColor Green
    
    # Write new .env
    Set-Content -Path $envFile -Value $newContent -NoNewline
    Write-Host "✅ Updated AZURE_OPENAI_API_KEY in .env" -ForegroundColor Green
    
    # Test the new key
    Write-Host "`n🧪 Testing new API key..." -ForegroundColor Cyan
    python test_search_integration.py
    
} else {
    Write-Host "❌ Error: AZURE_OPENAI_API_KEY not found in .env" -ForegroundColor Red
    exit 1
}
