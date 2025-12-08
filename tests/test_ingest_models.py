"""Tests for ingestion request/response models."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from eva_rag.models.ingest import IngestRequest, IngestResponse


def test_ingest_request_valid() -> None:
    """Test IngestRequest with valid data."""
    tenant_id = uuid4()
    space_id = uuid4()
    user_id = uuid4()
    
    request = IngestRequest(
        tenant_id=tenant_id,
        space_id=space_id,
        user_id=user_id,
        metadata={"document_type": "policy", "version": 1},
    )
    
    assert request.tenant_id == tenant_id
    assert request.space_id == space_id
    assert request.user_id == user_id
    assert request.metadata["document_type"] == "policy"


def test_ingest_request_empty_metadata() -> None:
    """Test IngestRequest with empty metadata."""
    request = IngestRequest(
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
    )
    
    assert request.metadata == {}


def test_ingest_request_invalid_uuid() -> None:
    """Test IngestRequest with invalid UUID."""
    with pytest.raises(ValidationError):
        IngestRequest(
            tenant_id="not-a-uuid",
            space_id=uuid4(),
            user_id=uuid4(),
        )


def test_ingest_response_valid() -> None:
    """Test IngestResponse with all fields."""
    doc_id = uuid4()
    now = datetime.now(timezone.utc)
    
    response = IngestResponse(
        document_id=doc_id,
        status="indexed",
        filename="test.pdf",
        file_size_bytes=1024,
        page_count=5,
        text_length=5000,
        language_detected="en",
        processing_time_ms=1500,
        created_at=now,
        blob_url="https://storage.blob.core.windows.net/docs/test.pdf",
    )
    
    assert response.document_id == doc_id
    assert response.status == "indexed"
    assert response.filename == "test.pdf"
    assert response.file_size_bytes == 1024
    assert response.page_count == 5
    assert response.text_length == 5000
    assert response.language_detected == "en"
    assert response.processing_time_ms == 1500
    assert response.blob_url == "https://storage.blob.core.windows.net/docs/test.pdf"


def test_ingest_response_serialization() -> None:
    """Test IngestResponse JSON serialization."""
    response = IngestResponse(
        document_id=uuid4(),
        status="indexed",
        filename="doc.pdf",
        file_size_bytes=2048,
        page_count=10,
        text_length=10000,
        language_detected="fr",
        processing_time_ms=2000,
        created_at=datetime.now(timezone.utc),
        blob_url="https://example.com/doc.pdf",
    )
    
    json_data = response.model_dump_json()
    assert "doc.pdf" in json_data
    assert "indexed" in json_data
    assert "fr" in json_data
