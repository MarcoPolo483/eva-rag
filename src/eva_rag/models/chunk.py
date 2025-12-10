"""Document chunk model for Azure AI Search and Cosmos DB."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A chunk of text from a document with embedding."""
    
    # Identity (HPK: /space_id/tenant_id/user_id)
    chunk_id: str = Field(..., description="Unique chunk ID (document_id:chunk_index)")
    document_id: UUID = Field(..., description="Parent document UUID")
    space_id: UUID = Field(..., description="Space UUID (partition key level 1)")
    tenant_id: UUID = Field(..., description="Tenant UUID (partition key level 2)")
    user_id: UUID = Field(..., description="User UUID who owns the document (partition key level 3)")
    
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
