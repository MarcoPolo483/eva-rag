"""Request and response models for ingestion API."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    
    space_id: UUID = Field(..., description="Space UUID")
    tenant_id: UUID = Field(..., description="Tenant UUID")
    user_id: UUID = Field(..., description="User UUID")
    metadata: dict[str, str | int] = Field(
        default_factory=dict,
        description="Additional metadata (document_type, tags, etc.)",
    )


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    
    document_id: UUID = Field(..., description="Generated document UUID")
    status: str = Field(..., description="Processing status")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    page_count: int = Field(..., description="Number of pages extracted")
    text_length: int = Field(..., description="Length of extracted text")
    language_detected: str = Field(..., description="Detected language (en/fr)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    created_at: datetime = Field(..., description="Upload timestamp")
    blob_url: str = Field(..., description="Azure Blob Storage URL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "indexed",
                "filename": "benefits-policy.pdf",
                "file_size_bytes": 1048576,
                "page_count": 10,
                "text_length": 50000,
                "language_detected": "en",
                "processing_time_ms": 3500,
                "created_at": "2025-12-07T14:30:00+00:00",
                "blob_url": "https://storage.blob.core.windows.net/documents/...",
            }
        }
    )
