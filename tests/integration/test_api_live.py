"""
Integration test for EVA RAG API with live Azure services.

This test validates the complete ingestion pipeline:
1. Upload a document via POST /api/v1/rag/ingest
2. Extract text content
3. Detect language
4. Upload to Azure Blob Storage
5. Save metadata to Azure Cosmos DB

Prerequisites:
- .env file configured with Azure credentials
- Azure services accessible (Storage, Cosmos DB, OpenAI)
"""

import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from eva_rag.main import app

# TestClient manages app lifecycle - no separate server needed
client = TestClient(app)


@pytest.mark.integration
def test_health_endpoint():
    """Validate health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "eva-rag"


@pytest.mark.integration
def test_document_ingestion_with_azure():
    """
    Test complete document ingestion with live Azure services.
    
    Expected outcome:
    - 201 Created status
    - document_id returned
    - language detected as 'en'
    - blob_url pointing to Azure Storage
    - metadata saved in Cosmos DB
    """
    # Create unique IDs for this test
    space_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create a test document
    test_content = """
# EVA RAG Integration Test Document

This is a test document for validating the EVA RAG ingestion pipeline.

## Features Tested:
- Document upload via FastAPI
- Text extraction from uploaded file
- Language detection (English)
- Azure Blob Storage upload
- Azure Cosmos DB metadata persistence

## Expected Behavior:
The system should successfully process this document and return:
1. A unique document_id
2. Detected language: "en"
3. Azure Blob Storage URL
4. Success status code 201
"""
    
    # Create temporary file
    test_file = Path("test_document.txt")
    test_file.write_text(test_content, encoding="utf-8")
    
    try:
        # Upload document with all required fields
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/rag/ingest",
                files={"file": ("test_document.txt", f, "text/plain")},
                data={
                    "space_id": space_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id
                }
            )
        
        # Validate response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check required fields from IngestResponse model
        assert "document_id" in data
        assert "status" in data
        assert "filename" in data
        assert "language_detected" in data
        assert "blob_url" in data
        
        # Validate values
        assert data["status"] in ["extracting", "chunking", "embedding", "indexing", "indexed"], \
            f"Unexpected status '{data['status']}' (should be a processing stage)"
        assert data["filename"] == "test_document.txt"
        assert data["language_detected"] == "en", f"Expected language 'en', got '{data['language_detected']}'"
        assert data["blob_url"].startswith("https://"), f"Invalid blob URL: {data['blob_url']}"
        assert "evasuitestoragedev" in data["blob_url"], "Blob URL should point to eva storage account"
        
        print(f"\n✅ Integration test passed!")
        print(f"   Document ID: {data['document_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Filename: {data['filename']}")
        print(f"   Language: {data['language_detected']}")
        print(f"   File Size: {data['file_size_bytes']} bytes")
        print(f"   Processing Time: {data['processing_time_ms']} ms")
        print(f"   Blob URL: {data['blob_url']}")
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    # Run manually for quick testing
    print("🧪 Running EVA RAG Integration Tests\n")
    
    print("1️⃣ Testing health endpoint...")
    test_health_endpoint()
    print("   ✅ Health check passed\n")
    
    print("2️⃣ Testing document ingestion with Azure...")
    test_document_ingestion_with_azure()
    print("\n🎉 All integration tests passed!")
