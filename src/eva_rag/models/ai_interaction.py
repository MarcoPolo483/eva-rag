"""Pydantic models for AI Interaction provenance tracking."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ChunkReference(BaseModel):
    """Reference to a chunk used in AI response."""
    
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: UUID = Field(..., description="Source document UUID")
    filename: str = Field(..., description="Source document filename")
    page_number: int | None = Field(None, description="Page number (if applicable)")
    text_snippet: str = Field(..., description="Relevant text snippet (max 500 chars)")
    relevance_score: float = Field(..., description="Relevance score (0-1)")


class Citation(BaseModel):
    """Citation linking AI output to source material."""
    
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: UUID = Field(..., description="Source document UUID")
    filename: str = Field(..., description="Source document filename")
    page_number: int | None = Field(None, description="Page number (if applicable)")
    quote: str = Field(..., description="Exact quote from source (max 200 chars)")
    position_in_response: int = Field(..., description="Character position in AI response where citation applies")


class AIInteraction(BaseModel):
    """
    Immutable record of AI interaction for provenance tracking.
    
    This is a write-once record that captures the complete context of an AI response:
    - Input (user query)
    - Output (AI response)
    - Chunks used (which documents informed the response)
    - Citations (how to verify the response)
    - Model details (which AI model generated the response)
    - Hash chain (tamper-evidence)
    
    **IMPORTANT**: Once created, this record CANNOT be modified or deleted.
    """
    
    # Identity (HPK: /space_id/tenant_id/user_id)
    id: UUID = Field(default_factory=uuid4, description="Interaction UUID")
    space_id: UUID = Field(..., description="Space UUID (partition key level 1)")
    tenant_id: UUID = Field(..., description="Tenant UUID (partition key level 2)")
    user_id: UUID = Field(..., description="User UUID who made the query (partition key level 3)")
    
    # Input
    query: str = Field(..., description="User query text")
    query_language: str = Field(..., description="Detected language of query (en/fr)")
    query_intent: str | None = Field(None, description="Classified intent (optional)")
    
    # Output
    response: str = Field(..., description="AI-generated response text")
    response_language: str = Field(..., description="Language of response (en/fr)")
    
    # Provenance
    chunks_used: list[ChunkReference] = Field(
        default_factory=list,
        description="Chunks that informed the response",
    )
    citations: list[Citation] = Field(
        default_factory=list,
        description="Citations linking response to source material",
    )
    
    # Model Details
    model_name: str = Field(..., description="AI model used (e.g., 'gpt-4o-mini')")
    model_version: str = Field(..., description="Model version (e.g., '2024-07-18')")
    temperature: float = Field(default=0.7, description="Model temperature setting")
    max_tokens: int = Field(default=1000, description="Maximum tokens in response")
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Interaction timestamp (ISO 8601)",
    )
    latency_ms: int = Field(..., description="Response latency in milliseconds")
    token_count_input: int = Field(..., description="Number of tokens in input")
    token_count_output: int = Field(..., description="Number of tokens in output")
    
    # Hash Chain (Tamper-Evidence)
    content_hash: str = Field(..., description="SHA-256 hash of interaction content")
    previous_hash: str = Field(..., description="Hash of previous interaction (for chain)")
    
    # Quality & Safety
    safety_flags: list[str] = Field(
        default_factory=list,
        description="Safety flags (e.g., 'bias_detected', 'pii_removed')",
    )
    quality_score: float | None = Field(
        None,
        description="Quality score (0-1) if available",
    )
    
    # Additional metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (context, tags, etc.)",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "space_id": "123e4567-e89b-12d3-a456-426614174001",
                "tenant_id": "123e4567-e89b-12d3-a456-426614174002",
                "user_id": "123e4567-e89b-12d3-a456-426614174003",
                "query": "What are the eligibility requirements for CPP disability benefits?",
                "query_language": "en",
                "query_intent": "eligibility_question",
                "response": "To be eligible for CPP disability benefits, you must: 1) Have made sufficient contributions...",
                "response_language": "en",
                "chunks_used": [
                    {
                        "chunk_id": "doc-123:0",
                        "document_id": "123e4567-e89b-12d3-a456-426614174004",
                        "filename": "cpp-disability-policy.pdf",
                        "page_number": 5,
                        "text_snippet": "Eligibility for CPP disability benefits requires...",
                        "relevance_score": 0.95,
                    }
                ],
                "citations": [
                    {
                        "chunk_id": "doc-123:0",
                        "document_id": "123e4567-e89b-12d3-a456-426614174004",
                        "filename": "cpp-disability-policy.pdf",
                        "page_number": 5,
                        "quote": "Eligibility for CPP disability benefits requires sufficient contributions",
                        "position_in_response": 47,
                    }
                ],
                "model_name": "gpt-4o-mini",
                "model_version": "2024-07-18",
                "temperature": 0.7,
                "max_tokens": 1000,
                "created_at": "2025-12-08T14:30:00+00:00",
                "latency_ms": 1250,
                "token_count_input": 150,
                "token_count_output": 300,
                "content_hash": "abc123...",
                "previous_hash": "def456...",
                "safety_flags": [],
                "quality_score": 0.92,
                "metadata": {
                    "session_id": "session-789",
                    "channel": "web",
                },
            }
        }
    )
