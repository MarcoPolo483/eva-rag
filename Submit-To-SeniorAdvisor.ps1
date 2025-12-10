# Submit Request to Senior Advisor (SP01) via ChatGPT API
# Usage: .\Submit-To-SeniorAdvisor.ps1 [-ApiKey "sk-..."]

param(
    [string]$RequestFile = "SENIOR-ADVISOR-REQUEST.md",
    [string]$OutputFile = "SENIOR-ADVISOR-RESPONSE.md",
    [string]$ApiKey = ""
)

Write-Host "📋 Submitting request to Senior Advisor (SP01)..." -ForegroundColor Cyan

# Check if request file exists
if (-not (Test-Path $RequestFile)) {
    Write-Host "❌ Request file not found: $RequestFile" -ForegroundColor Red
    exit 1
}

# Read the request
$requestContent = Get-Content $RequestFile -Raw

# Prepare the prompt with SP01 preamble
$prompt = @"
You are SP01 (Senior Advisor), an external-facing EVA Service Persona.

Your role: High-level framing, patterns, and critique for complex problems.

Classification: This content is UNCLASSIFIED and sanitized.

Context: You received the eva-orchestrator repository tree earlier today.
This request comes from a GitHub Copilot L2 agent working with Marco Presta.

Please provide advisory guidance on the architectural integration question below.
All outputs are advisory and will be validated against internal EVA specs.

---

$requestContent
"@

# Check for OpenAI API key
if (-not $ApiKey) {
    $ApiKey = $env:EVA_OPENAI_API_KEY
}
if (-not $ApiKey) {
    $ApiKey = $env:OPENAI_API_KEY
}
if (-not $ApiKey) {
    Write-Host "⚠️  EVA_OPENAI_API_KEY or OPENAI_API_KEY not found in environment" -ForegroundColor Yellow
    Write-Host "Please set it with: `$env:EVA_OPENAI_API_KEY = 'your-key'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Copy the request to ChatGPT web interface" -ForegroundColor Cyan
    Write-Host "1. Open: https://chatgpt.com" -ForegroundColor Gray
    Write-Host "2. Start new conversation" -ForegroundColor Gray
    Write-Host "3. Paste content from: $RequestFile" -ForegroundColor Gray
    Write-Host "4. Save response to: $OutputFile" -ForegroundColor Gray
    exit 1
}

# Prepare API request
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $ApiKey"
}

$body = @{
    model = "gpt-4"
    messages = @(
        @{
            role = "user"
            content = $prompt
        }
    )
    temperature = 0.7
    max_tokens = 4000
} | ConvertTo-Json -Depth 10

Write-Host "🔄 Calling OpenAI API..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "https://api.openai.com/v1/chat/completions" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 60

    $advisorResponse = $response.choices[0].message.content

    # Save response
    $output = @"
# Senior Advisor (SP01) Response
**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Model:** $($response.model)
**Request File:** $RequestFile

---

$advisorResponse

---

**Metadata:**
- Tokens Used: $($response.usage.total_tokens)
- Prompt Tokens: $($response.usage.prompt_tokens)
- Completion Tokens: $($response.usage.completion_tokens)
- Finish Reason: $($response.choices[0].finish_reason)
"@

    $output | Out-File $OutputFile -Encoding UTF8
    
    Write-Host "✅ Response saved to: $OutputFile" -ForegroundColor Green
    Write-Host "📊 Tokens used: $($response.usage.total_tokens)" -ForegroundColor Gray
    
    # Display first 500 chars of response
    Write-Host "`n📄 Response preview:" -ForegroundColor Cyan
    Write-Host "---"
    Write-Host $advisorResponse.Substring(0, [Math]::Min(500, $advisorResponse.Length))
    if ($advisorResponse.Length -gt 500) {
        Write-Host "... (see $OutputFile for full response)"
    }
    
} catch {
    Write-Host "❌ API call failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fallback: Use ChatGPT web interface" -ForegroundColor Cyan
    Write-Host "1. Open: https://chatgpt.com" -ForegroundColor Gray
    Write-Host "2. Paste content from: $RequestFile" -ForegroundColor Gray
    exit 1
}

Write-Host "`n✅ Request complete. Review response and bring back to GitHub Copilot for validation." -ForegroundColor Green
