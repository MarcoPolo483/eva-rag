"""Tests for DocumentChunk model."""
import pytest
from datetime import datetime
from uuid import uuid4

from eva_rag.models.chunk import DocumentChunk


# Test fixtures for UUIDs
TEST_DOC_ID = uuid4()
TEST_TENANT_ID = uuid4()
TEST_SPACE_ID = uuid4()


def test_document_chunk_creation():
    """Test creating a DocumentChunk instance."""
    now = datetime.utcnow()
    chunk = DocumentChunk(
        chunk_id=f"{TEST_DOC_ID}:0",
        document_id=TEST_DOC_ID,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="This is a test chunk",
        chunk_index=0,
        token_count=5,
        filename="test.pdf",
        page_number=1,
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    
    assert chunk.chunk_id == f"{TEST_DOC_ID}:0"
    assert chunk.document_id == TEST_DOC_ID
    assert chunk.tenant_id == TEST_TENANT_ID
    assert chunk.space_id == TEST_SPACE_ID
    assert chunk.text == "This is a test chunk"
    assert chunk.chunk_index == 0
    assert chunk.token_count == 5
    assert chunk.filename == "test.pdf"
    assert chunk.page_number == 1
    assert chunk.language == "en"
    assert len(chunk.embedding) == 1536
    assert chunk.created_at == now


def test_document_chunk_with_optional_fields():
    """Test chunk with optional metadata fields."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    chunk = DocumentChunk(
        chunk_id=f"{doc_id}:1",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Second chunk",
        chunk_index=1,
        token_count=2,
        filename="document.pdf",
        language="fr",
        embedding=[0.5] * 1536,
        created_at=now,
        metadata={"custom_field": "value", "category": "research"}
    )
    
    assert chunk.metadata == {"custom_field": "value", "category": "research"}
    assert chunk.page_number is None  # Optional field


def test_document_chunk_minimal_required_fields():
    """Test chunk with only required fields."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    chunk = DocumentChunk(
        chunk_id=f"{doc_id}:0",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Minimal chunk",
        chunk_index=0,
        token_count=2,
        filename="file.txt",
        language="en",
        embedding=[0.9] * 1536,
        created_at=now
    )
    
    assert chunk.chunk_id == f"{doc_id}:0"
    assert chunk.text == "Minimal chunk"
    assert chunk.page_number is None
    assert chunk.metadata == {}  # Defaults to empty dict


def test_document_chunk_embedding_dimensions():
    """Test various embedding dimension scenarios."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    # Standard 1536 dimensions
    chunk = DocumentChunk(
        chunk_id=f"{doc_id}:0",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Test",
        chunk_index=0,
        token_count=1,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    assert len(chunk.embedding) == 1536
    
    # Different dimensions (model flexibility)
    doc_id2 = uuid4()
    chunk_small = DocumentChunk(
        chunk_id=f"{doc_id2}:0",
        document_id=doc_id2,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Test",
        chunk_index=0,
        token_count=1,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 512,
        created_at=now
    )
    assert len(chunk_small.embedding) == 512


def test_document_chunk_chunk_id_format():
    """Test chunk_id follows document_id:index format."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    chunk = DocumentChunk(
        chunk_id=f"{doc_id}:5",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Test",
        chunk_index=5,
        token_count=1,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    
    # Validate format convention
    assert chunk.chunk_id.startswith(str(chunk.document_id))
    assert chunk.chunk_id.endswith(str(chunk.chunk_index))
    assert ":" in chunk.chunk_id


def test_document_chunk_text_variations():
    """Test different text content scenarios."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    # Long text
    long_text = "Lorem ipsum " * 100
    chunk = DocumentChunk(
        chunk_id=f"{doc_id}:0",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text=long_text,
        chunk_index=0,
        token_count=200,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    assert len(chunk.text) > 1000
    
    # Empty text (edge case)
    doc_id2 = uuid4()
    chunk_empty = DocumentChunk(
        chunk_id=f"{doc_id2}:0",
        document_id=doc_id2,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="",
        chunk_index=0,
        token_count=0,
        filename="empty.txt",
        language="en",
        embedding=[0.0] * 1536,
        created_at=now
    )
    assert chunk_empty.text == ""


def test_document_chunk_language_codes():
    """Test different language codes."""
    doc_id = uuid4()
    now = datetime.utcnow()
    languages = ["en", "fr", "es", "de", "zh", "ja"]
    
    for i, lang in enumerate(languages):
        chunk = DocumentChunk(
            chunk_id=f"{doc_id}:{i}",
            document_id=doc_id,
            tenant_id=TEST_TENANT_ID,
            space_id=TEST_SPACE_ID,
            text=f"Text in {lang}",
            chunk_index=i,
            token_count=3,
            filename="multilang.txt",
            language=lang,
            embedding=[0.1] * 1536,
            created_at=now
        )
        assert chunk.language == lang


def test_document_chunk_page_number_scenarios():
    """Test page number handling."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    # First page
    chunk1 = DocumentChunk(
        chunk_id=f"{doc_id}:0",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Page 1",
        chunk_index=0,
        token_count=2,
        filename="doc.pdf",
        language="en",
        page_number=1,
        embedding=[0.1] * 1536,
        created_at=now
    )
    assert chunk1.page_number == 1
    
    # High page number
    chunk_high = DocumentChunk(
        chunk_id=f"{doc_id}:50",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Page 100",
        chunk_index=50,
        token_count=2,
        filename="doc.pdf",
        language="en",
        page_number=100,
        embedding=[0.1] * 1536,
        created_at=now
    )
    assert chunk_high.page_number == 100
    
    # No page number (text file)
    doc_id2 = uuid4()
    chunk_no_page = DocumentChunk(
        chunk_id=f"{doc_id2}:0",
        document_id=doc_id2,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Text file",
        chunk_index=0,
        token_count=2,
        filename="text.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    assert chunk_no_page.page_number is None


def test_document_chunk_metadata_structure():
    """Test metadata dictionary variations."""
    doc_id = uuid4()
    now = datetime.utcnow()
    
    # Simple metadata
    chunk1 = DocumentChunk(
        chunk_id=f"{doc_id}:0",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Test",
        chunk_index=0,
        token_count=1,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now,
        metadata={"author": "John Doe"}
    )
    assert chunk1.metadata["author"] == "John Doe"
    
    # Complex metadata (only str | int values allowed)
    chunk2 = DocumentChunk(
        chunk_id=f"{doc_id}:1",
        document_id=doc_id,
        tenant_id=TEST_TENANT_ID,
        space_id=TEST_SPACE_ID,
        text="Test",
        chunk_index=1,
        token_count=1,
        filename="test.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now,
        metadata={
            "author": "Jane Smith",
            "date": "2024-01-15",
            "category": "research",
            "page_count": 42
        }
    )
    assert chunk2.metadata["author"] == "Jane Smith"
    assert chunk2.metadata["date"] == "2024-01-15"
    assert chunk2.metadata["category"] == "research"
    assert chunk2.metadata["page_count"] == 42


def test_document_chunk_multi_tenant_isolation():
    """Test that chunks maintain tenant and space isolation."""
    doc_id1 = uuid4()
    doc_id2 = uuid4()
    tenant_id1 = uuid4()
    tenant_id2 = uuid4()
    space_id1 = uuid4()
    space_id2 = uuid4()
    now = datetime.utcnow()
    
    # Same document in different tenants
    chunk_tenant1 = DocumentChunk(
        chunk_id=f"{doc_id1}:0",
        document_id=doc_id1,
        tenant_id=tenant_id1,
        space_id=space_id1,
        text="Tenant 1 data",
        chunk_index=0,
        token_count=3,
        filename="doc.txt",
        language="en",
        embedding=[0.1] * 1536,
        created_at=now
    )
    
    chunk_tenant2 = DocumentChunk(
        chunk_id=f"{doc_id2}:0",
        document_id=doc_id2,
        tenant_id=tenant_id2,
        space_id=space_id2,
        text="Tenant 2 data",
        chunk_index=0,
        token_count=3,
        filename="doc.txt",
        language="en",
        embedding=[0.2] * 1536,
        created_at=now
    )
    
    # Verify isolation
    assert chunk_tenant1.tenant_id != chunk_tenant2.tenant_id
    assert chunk_tenant1.space_id != chunk_tenant2.space_id
    assert chunk_tenant1.document_id != chunk_tenant2.document_id
