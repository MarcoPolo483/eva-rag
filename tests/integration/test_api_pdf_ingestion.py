"""
Integration test for PDF document ingestion.

Validates the complete pipeline with a real PDF file:
1. Upload PDF via POST /api/v1/rag/ingest
2. Extract text from PDF pages
3. Detect language
4. Upload to Azure Blob Storage
5. Save metadata to Cosmos DB
"""

import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from eva_rag.main import app

client = TestClient(app)


def create_test_pdf(output_path: Path, content: str) -> Path:
    """Create a simple PDF with text content for testing."""
    pdf_canvas = canvas.Canvas(str(output_path), pagesize=letter)
    
    # Add title
    pdf_canvas.setFont("Helvetica-Bold", 16)
    pdf_canvas.drawString(100, 750, "EVA RAG Test Document")
    
    # Add content
    pdf_canvas.setFont("Helvetica", 12)
    y_position = 700
    for line in content.split('\n'):
        if line.strip():
            pdf_canvas.drawString(100, y_position, line.strip())
            y_position -= 20
            if y_position < 50:  # Start new page if needed
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
    
    pdf_canvas.save()
    return output_path


@pytest.mark.integration
def test_pdf_document_ingestion():
    """
    Test PDF document ingestion with live Azure services.
    
    Expected outcome:
    - 201 Created status
    - PDF text extracted successfully
    - Language detected as 'en'
    - Blob uploaded to Azure Storage
    - Metadata saved in Cosmos DB
    """
    # Create unique IDs
    space_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create test PDF content
    pdf_content = """
This is a comprehensive test of the EVA RAG PDF ingestion pipeline.

Key Features:
- Multi-page document support
- Text extraction from PDF format
- Language detection capabilities
- Azure Blob Storage integration
- Cosmos DB metadata persistence

Test Validation:
The system should successfully extract this text from the PDF,
detect the language as English, upload the document to Azure Storage,
and save all metadata to Cosmos DB with proper indexing.
"""
    
    # Create temporary PDF file
    test_pdf = Path("test_document.pdf")
    create_test_pdf(test_pdf, pdf_content)
    
    try:
        # Upload PDF document
        with open(test_pdf, "rb") as f:
            response = client.post(
                "/api/v1/rag/ingest",
                files={"file": ("test_document.pdf", f, "application/pdf")},
                data={
                    "space_id": space_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id
                }
            )
        
        # Validate response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check required fields
        assert "document_id" in data
        assert "status" in data
        assert "filename" in data
        assert "language_detected" in data
        assert "blob_url" in data
        assert "file_size_bytes" in data
        assert "page_count" in data
        assert "text_length" in data
        
        # Validate values
        assert data["status"] in ["extracting", "chunking", "embedding", "indexing", "indexed"], \
            f"Unexpected status: {data['status']}"
        assert data["filename"] == "test_document.pdf"
        assert data["language_detected"] == "en", f"Expected 'en', got '{data['language_detected']}'"
        assert data["blob_url"].startswith("https://"), f"Invalid blob URL: {data['blob_url']}"
        assert "evasuitestoragedev" in data["blob_url"], "Should use eva storage account"
        assert data["file_size_bytes"] > 0, "PDF should have non-zero size"
        assert data["page_count"] >= 1, f"PDF should have at least 1 page, got {data['page_count']}"
        assert data["text_length"] > 0, f"PDF should have extracted text, got {data['text_length']} chars"
        
        print(f"\n✅ PDF Integration test passed!")
        print(f"   Document ID: {data['document_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Filename: {data['filename']}")
        print(f"   Language: {data['language_detected']}")
        print(f"   File Size: {data['file_size_bytes']} bytes")
        print(f"   Pages: {data['page_count']}")
        print(f"   Text Length: {data['text_length']} characters")
        print(f"   Processing Time: {data['processing_time_ms']} ms")
        print(f"   Blob URL: {data['blob_url']}")
        
    finally:
        # Cleanup
        if test_pdf.exists():
            test_pdf.unlink()


if __name__ == "__main__":
    print("🧪 Running EVA RAG PDF Integration Test\n")
    test_pdf_document_ingestion()
    print("\n🎉 PDF integration test passed!")
