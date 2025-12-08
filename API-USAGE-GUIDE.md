# EVA RAG API Usage Guide

## 🚀 Quick Start

### 1. Start the Server

```powershell
poetry run uvicorn eva_rag.main:app --reload --host 127.0.0.1 --port 8000
```

Server will be available at: `http://127.0.0.1:8000`

### 2. Access API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/v1/docs
- **ReDoc**: http://127.0.0.1:8000/api/v1/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/api/v1/openapi.json

### 3. Health Check

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "service": "eva-rag",
  "version": "0.1.0"
}
```

## 📄 Document Ingestion

### Upload PDF Document

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rag/ingest" \
  -F "file=@/path/to/document.pdf" \
  -F "space_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "tenant_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "user_id=987fcdeb-51a2-43f1-8901-fedcba098765"
```

### Upload DOCX Document

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rag/ingest" \
  -F "file=@/path/to/document.docx" \
  -F "space_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "tenant_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "user_id=987fcdeb-51a2-43f1-8901-fedcba098765"
```

### Upload Text Document

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/rag/ingest" \
  -F "file=@/path/to/document.txt" \
  -F "space_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "tenant_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "user_id=987fcdeb-51a2-43f1-8901-fedcba098765"
```

### Response Example

```json
{
  "document_id": "a7b3c8d9-1234-5678-9abc-def012345678",
  "status": "indexing",
  "filename": "contract.pdf",
  "file_size_bytes": 1048576,
  "page_count": 12,
  "text_length": 8450,
  "language_detected": "en",
  "processing_time_ms": 1350,
  "created_at": "2025-12-08T10:30:00.123456Z",
  "blob_url": "https://evastorage.blob.core.windows.net/documents/a7b3c8d9-1234-5678-9abc-def012345678.pdf"
}
```

## 🐍 Python Client Examples

### Basic Upload

```python
import requests
from uuid import uuid4

# API configuration
API_URL = "http://127.0.0.1:8000/api/v1"

# Generate UUIDs (or use existing ones from your system)
space_id = "550e8400-e29b-41d4-a716-446655440000"
tenant_id = "123e4567-e89b-12d3-a456-426614174000"
user_id = "987fcdeb-51a2-43f1-8901-fedcba098765"

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{API_URL}/rag/ingest",
        files={"file": ("document.pdf", f, "application/pdf")},
        data={
            "space_id": space_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
        }
    )

# Check response
if response.status_code == 201:
    data = response.json()
    print(f"✅ Document uploaded: {data['document_id']}")
    print(f"   Language: {data['language_detected']}")
    print(f"   Pages: {data['page_count']}")
    print(f"   Processing time: {data['processing_time_ms']}ms")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
```

### Batch Upload

```python
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://127.0.0.1:8000/api/v1"
space_id = "550e8400-e29b-41d4-a716-446655440000"
tenant_id = "123e4567-e89b-12d3-a456-426614174000"
user_id = "987fcdeb-51a2-43f1-8901-fedcba098765"

def upload_document(file_path: Path):
    """Upload a single document."""
    with open(file_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/rag/ingest",
            files={"file": (file_path.name, f)},
            data={
                "space_id": space_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
            }
        )
    return file_path.name, response.status_code, response.json()

# Find all documents
documents_dir = Path("./documents")
files = list(documents_dir.glob("*.pdf")) + \
        list(documents_dir.glob("*.docx")) + \
        list(documents_dir.glob("*.txt"))

# Upload in parallel (max 5 concurrent)
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(upload_document, f) for f in files]
    
    for future in as_completed(futures):
        filename, status, data = future.result()
        if status == 201:
            print(f"✅ {filename}: {data['document_id']}")
        else:
            print(f"❌ {filename}: {data.get('detail', 'Unknown error')}")
```

### Error Handling

```python
import requests

def ingest_document_safe(file_path: str, space_id: str, tenant_id: str, user_id: str):
    """Upload document with comprehensive error handling."""
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/rag/ingest",
                files={"file": (Path(file_path).name, f)},
                data={
                    "space_id": space_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                },
                timeout=60  # 60 second timeout
            )
        
        if response.status_code == 201:
            return True, response.json()
        elif response.status_code == 400:
            return False, f"Invalid input: {response.json()['detail']}"
        elif response.status_code == 413:
            return False, "File too large (max 50MB)"
        elif response.status_code == 500:
            return False, f"Server error: {response.json()['detail']}"
        else:
            return False, f"Unexpected error: {response.status_code}"
            
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
    except requests.exceptions.Timeout:
        return False, "Request timeout (>60s)"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

# Usage
success, result = ingest_document_safe(
    "document.pdf",
    "550e8400-e29b-41d4-a716-446655440000",
    "123e4567-e89b-12d3-a456-426614174000",
    "987fcdeb-51a2-43f1-8901-fedcba098765"
)

if success:
    print(f"✅ Success: Document ID = {result['document_id']}")
else:
    print(f"❌ Error: {result}")
```

## 🔧 PowerShell Examples

### Simple Upload

```powershell
$apiUrl = "http://127.0.0.1:8000/api/v1"
$filePath = "C:\Documents\contract.pdf"
$spaceId = "550e8400-e29b-41d4-a716-446655440000"
$tenantId = "123e4567-e89b-12d3-a456-426614174000"
$userId = "987fcdeb-51a2-43f1-8901-fedcba098765"

$form = @{
    file = Get-Item -Path $filePath
    space_id = $spaceId
    tenant_id = $tenantId
    user_id = $userId
}

$response = Invoke-RestMethod -Uri "$apiUrl/rag/ingest" `
    -Method Post `
    -Form $form `
    -ContentType "multipart/form-data"

Write-Host "✅ Document uploaded: $($response.document_id)"
Write-Host "   Language: $($response.language_detected)"
Write-Host "   Processing time: $($response.processing_time_ms)ms"
```

### Batch Upload with Progress

```powershell
$apiUrl = "http://127.0.0.1:8000/api/v1"
$documentsPath = "C:\Documents"
$spaceId = "550e8400-e29b-41d4-a716-446655440000"
$tenantId = "123e4567-e89b-12d3-a456-426614174000"
$userId = "987fcdeb-51a2-43f1-8901-fedcba098765"

# Get all supported files
$files = Get-ChildItem -Path $documentsPath -Include "*.pdf","*.docx","*.txt" -Recurse

$results = @()
$i = 0

foreach ($file in $files) {
    $i++
    Write-Progress -Activity "Uploading Documents" `
        -Status "$i of $($files.Count): $($file.Name)" `
        -PercentComplete (($i / $files.Count) * 100)
    
    try {
        $form = @{
            file = $file
            space_id = $spaceId
            tenant_id = $tenantId
            user_id = $userId
        }
        
        $response = Invoke-RestMethod -Uri "$apiUrl/rag/ingest" `
            -Method Post `
            -Form $form `
            -ContentType "multipart/form-data"
        
        $results += [PSCustomObject]@{
            Filename = $file.Name
            Status = "Success"
            DocumentId = $response.document_id
            Language = $response.language_detected
            ProcessingTimeMs = $response.processing_time_ms
        }
        
        Write-Host "✅ $($file.Name)" -ForegroundColor Green
    }
    catch {
        $results += [PSCustomObject]@{
            Filename = $file.Name
            Status = "Failed"
            Error = $_.Exception.Message
        }
        
        Write-Host "❌ $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Progress -Activity "Uploading Documents" -Completed

# Display summary
Write-Host "`n📊 Summary:" -ForegroundColor Cyan
$results | Format-Table -AutoSize
```

## 📋 Supported Formats

| Format | Extension | Max Size | Notes |
|--------|-----------|----------|-------|
| PDF | `.pdf` | 50MB | Multi-page support, metadata extraction |
| Word | `.docx` | 50MB | Full document structure parsing |
| Text | `.txt` | 50MB | UTF-8, Latin-1 encoding support |
| Markdown | `.md` | 50MB | Treated as plain text |

## 🌐 Language Detection

The system automatically detects document language:

- **English (en)**: English text
- **French (fr)**: French text
- **Other**: Falls back to English processing

Language is used for:
- Optimal chunking strategies
- Language-specific tokenization
- Search optimization

## ⚡ Performance Tips

1. **File Size**: Keep files under 10MB for best performance
2. **Batch Uploads**: Use parallel uploads (max 5 concurrent)
3. **Network**: Use local server for testing, production with load balancer
4. **Monitoring**: Check processing_time_ms in response
5. **Retry**: Implement exponential backoff for 500 errors

## 🔒 Security Notes

- Always use HTTPS in production
- Validate UUIDs before sending
- Don't expose tenant/space IDs in client code
- Implement authentication/authorization at gateway level
- Rate limit at reverse proxy

## 🐛 Troubleshooting

### Error 400: Invalid UUID format
```
✗ Check UUID format: 8-4-4-4-12 hex digits
✓ Use uuid.uuid4() in Python or [guid]::NewGuid() in PowerShell
```

### Error 413: File too large
```
✗ File exceeds 50MB
✓ Compress PDF or split into smaller documents
```

### Error 500: Server error
```
✗ Azure service issue
✓ Check server logs
✓ Verify Azure credentials in .env
✓ Ensure services are running
```

### Timeout
```
✗ Large file or slow processing
✓ Increase timeout to 120s for large PDFs
✓ Check Azure service health
```

## 📞 Support

- **Issues**: https://github.com/MarcoPolo483/eva-rag/issues
- **Documentation**: `docs/SPECIFICATION.md`
- **API Docs**: http://127.0.0.1:8000/api/v1/docs
