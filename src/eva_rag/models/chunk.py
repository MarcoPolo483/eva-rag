"""Document chunk model for Azure AI Search."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A chunk of text from a document with embedding."""
    
    # Identity
    chunk_id: str = Field(..., description="Unique chunk ID (document_id:chunk_index)")
    document_id: UUID = Field(..., description="Parent document UUID")
    tenant_id: UUID = Field(..., description="Tenant UUID (for isolation)")
    space_id: UUID = Field(..., description="Space UUID (for filtering)")
    
    # Content
    text: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Chunk position in document (0-based)")
    token_count: int = Field(..., description="Number of tokens in chunk")
    
    # Document context
    filename: str = Field(..., description="Original document filename")
    page_number: int | None = Field(None, description="Page number (for PDFs)")
    language: str = Field(..., description="Detected language (en/fr)")
    
    # Vector search
    embedding: list[float] = Field(..., description="Embedding vector (1536 dimensions)")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Additional metadata
    metadata: dict[str, str | int] = Field(
        default_factory=dict,
        description="Additional metadata from parent document",
    )
