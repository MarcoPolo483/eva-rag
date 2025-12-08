"""Pydantic models for document metadata."""
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(str, Enum):
    """Document processing status."""
    
    UPLOADING = "uploading"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Document metadata for Cosmos DB storage."""
    
    # Identity
    id: UUID = Field(..., description="Document UUID")
    tenant_id: UUID = Field(..., description="Tenant UUID")
    space_id: UUID = Field(..., description="Space UUID")
    user_id: UUID = Field(..., description="User who uploaded the document")
    
    # File information
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    content_hash: str = Field(..., description="SHA-256 hash of file content")
    content_type: str = Field(..., description="MIME type")
    
    # Extracted content
    text_length: int = Field(..., description="Length of extracted text")
    page_count: int = Field(..., description="Number of pages")
    language: str = Field(..., description="Detected language (en/fr)")
    
    # Processing status
    status: DocumentStatus = Field(..., description="Current processing status")
    chunk_count: int = Field(default=0, description="Number of chunks generated")
    
    # Timestamps
    created_at: datetime = Field(..., description="Upload timestamp (ISO 8601)")
    updated_at: datetime = Field(..., description="Last update timestamp (ISO 8601)")
    indexed_at: datetime | None = Field(None, description="Indexing completion timestamp")
    
    # Storage
    blob_url: str = Field(..., description="Azure Blob Storage URL")
    
    # Additional metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (title, author, tags, etc.)",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174001",
                "space_id": "123e4567-e89b-12d3-a456-426614174002",
                "user_id": "123e4567-e89b-12d3-a456-426614174003",
                "filename": "benefits-policy.pdf",
                "file_size_bytes": 1048576,
                "content_hash": "abc123...",
                "content_type": "application/pdf",
                "text_length": 50000,
                "page_count": 10,
                "language": "en",
                "status": "indexed",
                "chunk_count": 42,
                "created_at": "2025-12-07T14:30:00+00:00",
                "updated_at": "2025-12-07T14:35:00+00:00",
                "indexed_at": "2025-12-07T14:35:00+00:00",
                "blob_url": "https://storage.blob.core.windows.net/documents/...",
                "metadata": {
                    "title": "Benefits Policy",
                    "document_type": "policy",
                    "tags": ["benefits", "eligibility"],
                },
            }
        }
    )
