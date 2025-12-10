"""Search models for RAG queries."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    
    query: str = Field(..., min_length=1, max_length=2000, description="Search query text")
    space_id: UUID = Field(..., description="Space to search within")
    tenant_id: UUID = Field(..., description="Tenant to search within")
    user_id: UUID = Field(..., description="User performing the search")
    
    # Search parameters
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    rerank: bool = Field(default=True, description="Apply cross-encoder reranking")
    
    # Filters
    language: Optional[str] = Field(None, description="Filter by language (en/fr)")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    document_ids: Optional[list[UUID]] = Field(None, description="Filter by specific documents")


class ChunkResult(BaseModel):
    """Single search result chunk."""
    
    chunk_id: str = Field(..., description="Chunk identifier")
    document_id: str = Field(..., description="Parent document UUID")
    document_name: str = Field(..., description="Source document filename")
    page_number: Optional[int] = Field(None, description="Page number for citation")
    content: str = Field(..., description="Chunk text content")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    language: str = Field(..., description="Content language (en/fr)")
    document_type: str = Field(..., description="Document type classification")
    chunk_index: int = Field(..., description="Position in document")


class SearchResponse(BaseModel):
    """Response model for semantic search."""
    
    query_id: str = Field(..., description="Unique query identifier")
    query: str = Field(..., description="Original query text")
    results: list[ChunkResult] = Field(..., description="Search results")
    processing_time_ms: int = Field(..., description="Query processing time in milliseconds")
    total_results: int = Field(..., description="Number of results returned")
    reranked: bool = Field(..., description="Whether results were reranked")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Query timestamp")
