"""Tests for document metadata models."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from eva_rag.models.document import DocumentMetadata, DocumentStatus


def test_document_status_enum() -> None:
    """Test DocumentStatus enum values."""
    assert DocumentStatus.UPLOADING == "uploading"
    assert DocumentStatus.EXTRACTING == "extracting"
    assert DocumentStatus.CHUNKING == "chunking"
    assert DocumentStatus.EMBEDDING == "embedding"
    assert DocumentStatus.INDEXING == "indexing"
    assert DocumentStatus.INDEXED == "indexed"
    assert DocumentStatus.FAILED == "failed"
    
    # Verify all 7 statuses exist
    assert len([s for s in DocumentStatus]) == 7


def test_document_metadata_valid() -> None:
    """Test DocumentMetadata with all required fields."""
    doc_id = uuid4()
    tenant_id = uuid4()
    space_id = uuid4()
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    
    metadata = DocumentMetadata(
        id=doc_id,
        tenant_id=tenant_id,
        space_id=space_id,
        user_id=user_id,
        filename="test.pdf",
        file_size_bytes=1024,
        content_hash="abc123",
        content_type="application/pdf",
        text_length=5000,
        page_count=10,
        language="en",
        status=DocumentStatus.INDEXED,
        chunk_count=25,
        created_at=now,
        updated_at=now,
        indexed_at=now,
        blob_url="https://storage.blob.core.windows.net/docs/test.pdf",
        metadata={"title": "Test Document"},
    )
    
    assert metadata.id == doc_id
    assert metadata.tenant_id == tenant_id
    assert metadata.status == DocumentStatus.INDEXED
    assert metadata.chunk_count == 25
    assert metadata.metadata["title"] == "Test Document"


def test_document_metadata_defaults() -> None:
    """Test DocumentMetadata with default values."""
    metadata = DocumentMetadata(
        id=uuid4(),
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
        filename="test.txt",
        file_size_bytes=100,
        content_hash="hash123",
        content_type="text/plain",
        text_length=50,
        page_count=1,
        language="en",
        status=DocumentStatus.UPLOADING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        blob_url="https://example.com/test.txt",
    )
    
    # Check defaults
    assert metadata.chunk_count == 0
    assert metadata.indexed_at is None
    assert metadata.metadata == {}


def test_document_metadata_invalid_uuid() -> None:
    """Test DocumentMetadata with invalid UUID."""
    with pytest.raises(ValidationError):
        DocumentMetadata(
            id="not-a-uuid",
            tenant_id=uuid4(),
            space_id=uuid4(),
            user_id=uuid4(),
            filename="test.pdf",
            file_size_bytes=100,
            content_hash="hash",
            content_type="application/pdf",
            text_length=50,
            page_count=1,
            language="en",
            status=DocumentStatus.UPLOADING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            blob_url="https://example.com/test.pdf",
        )


def test_document_metadata_serialization() -> None:
    """Test DocumentMetadata JSON serialization."""
    metadata = DocumentMetadata(
        id=uuid4(),
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
        filename="document.pdf",
        file_size_bytes=2048,
        content_hash="def456",
        content_type="application/pdf",
        text_length=10000,
        page_count=20,
        language="fr",
        status=DocumentStatus.INDEXED,
        chunk_count=50,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        blob_url="https://example.com/document.pdf",
        metadata={"author": "Test Author"},
    )
    
    json_data = metadata.model_dump_json()
    assert "document.pdf" in json_data
    assert "indexed" in json_data
    assert "fr" in json_data
    assert "Test Author" in json_data


def test_document_metadata_failed_status() -> None:
    """Test DocumentMetadata with failed status."""
    metadata = DocumentMetadata(
        id=uuid4(),
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
        filename="failed.pdf",
        file_size_bytes=100,
        content_hash="hash",
        content_type="application/pdf",
        text_length=0,
        page_count=0,
        language="en",
        status=DocumentStatus.FAILED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        blob_url="https://example.com/failed.pdf",
    )
    
    assert metadata.status == DocumentStatus.FAILED
    assert metadata.chunk_count == 0
