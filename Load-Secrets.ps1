# Load OpenAI API Key from GitHub Secret
# Usage: . .\Load-Secrets.ps1

Write-Host "🔐 Loading secrets from GitHub..." -ForegroundColor Cyan

# Try to get from GitHub CLI
try {
    $result = gh secret list --repo MarcoPolo483/eva-orchestrator 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub CLI authenticated" -ForegroundColor Green
        
        # Check if OPENAI_API_KEY secret exists
        if ($result -match "OPENAI_API_KEY") {
            Write-Host "✅ OPENAI_API_KEY secret found in GitHub" -ForegroundColor Green
            Write-Host "⚠️  Note: GitHub Codespaces/Actions can access it directly" -ForegroundColor Yellow
            Write-Host "   For local use, you need to set it manually:" -ForegroundColor Yellow
            Write-Host "   `$env:OPENAI_API_KEY = 'your-key'" -ForegroundColor Gray
        } else {
            Write-Host "❌ OPENAI_API_KEY secret not found in GitHub repo" -ForegroundColor Red
            Write-Host "   Add it with: gh secret set OPENAI_API_KEY" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "⚠️  GitHub CLI not available or not authenticated" -ForegroundColor Yellow
    Write-Host "   Install: winget install GitHub.cli" -ForegroundColor Gray
    Write-Host "   Authenticate: gh auth login" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Alternative: Set manually for this session" -ForegroundColor Cyan
Write-Host "   `$env:OPENAI_API_KEY = 'sk-...'" -ForegroundColor Gray
Write-Host ""
Write-Host "Then run: .\Submit-To-SeniorAdvisor.ps1" -ForegroundColor Green
