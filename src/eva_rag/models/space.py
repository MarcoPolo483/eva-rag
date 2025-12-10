"""Pydantic models for Space (multi-tenant isolation)."""
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class SpaceType(str, Enum):
    """Space type for lifecycle management."""
    
    SANDBOX = "sandbox"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class SpaceStatus(str, Enum):
    """Space operational status."""
    
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class SpaceQuotas(BaseModel):
    """Resource quotas for a Space."""
    
    compute_units: int = Field(
        default=1000,
        description="Compute units allocation (RU/s for Cosmos DB)",
    )
    storage_gb: int = Field(
        default=100,
        description="Storage allocation in GB",
    )
    ai_calls_per_month: int = Field(
        default=10000,
        description="AI API calls per month (OpenAI, embeddings)",
    )
    max_documents: int = Field(
        default=10000,
        description="Maximum documents allowed",
    )
    max_users: int = Field(
        default=100,
        description="Maximum users in this Space",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "compute_units": 1000,
                "storage_gb": 100,
                "ai_calls_per_month": 10000,
                "max_documents": 10000,
                "max_users": 100,
            }
        }
    )


class Space(BaseModel):
    """
    Space model for multi-tenant isolation.
    
    A Space represents a complete data isolation boundary:
    - Each Space has its own documents, chunks, interactions
    - Users from Space A cannot access Space B data
    - Supports sandbox/production/archived lifecycle
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Space UUID")
    space_id: UUID = Field(default_factory=uuid4, description="Space ID (partition key)")
    
    # Configuration
    name: str = Field(..., description="Space name (must be unique)")
    description: str = Field(default="", description="Space description")
    type: SpaceType = Field(default=SpaceType.SANDBOX, description="Space type")
    status: SpaceStatus = Field(default=SpaceStatus.ACTIVE, description="Operational status")
    
    # Ownership
    owner_id: UUID = Field(..., description="User UUID who owns this Space")
    owner_email: str = Field(..., description="Owner email for notifications")
    
    # Resource Management
    quotas: SpaceQuotas = Field(
        default_factory=SpaceQuotas,
        description="Resource quotas",
    )
    
    # Usage Tracking
    current_document_count: int = Field(default=0, description="Current document count")
    current_storage_bytes: int = Field(default=0, description="Current storage usage in bytes")
    current_ai_calls_this_month: int = Field(default=0, description="AI calls this month")
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (ISO 8601)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (ISO 8601)",
    )
    archived_at: datetime | None = Field(
        None,
        description="Archive timestamp (ISO 8601)",
    )
    
    # Additional metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (department, cost center, tags, etc.)",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "space_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Space-CPPD",
                "description": "Canada Pension Plan Disability - Production Space",
                "type": "production",
                "status": "active",
                "owner_id": "123e4567-e89b-12d3-a456-426614174001",
                "owner_email": "admin@cppd.gc.ca",
                "quotas": {
                    "compute_units": 5000,
                    "storage_gb": 500,
                    "ai_calls_per_month": 50000,
                    "max_documents": 50000,
                    "max_users": 500,
                },
                "current_document_count": 1234,
                "current_storage_bytes": 5368709120,
                "current_ai_calls_this_month": 12500,
                "created_at": "2025-12-01T00:00:00+00:00",
                "updated_at": "2025-12-08T14:30:00+00:00",
                "archived_at": None,
                "metadata": {
                    "department": "ESDC",
                    "cost_center": "CPPD-IT",
                    "tags": ["production", "disability", "benefits"],
                },
            }
        }
    )


class SpaceCreate(BaseModel):
    """Request model for creating a Space."""
    
    name: str = Field(..., description="Space name (must be unique)", min_length=3, max_length=100)
    description: str = Field(default="", description="Space description", max_length=500)
    type: SpaceType = Field(default=SpaceType.SANDBOX, description="Space type")
    owner_id: UUID = Field(..., description="User UUID who owns this Space")
    owner_email: str = Field(..., description="Owner email for notifications")
    quotas: SpaceQuotas | None = Field(None, description="Custom quotas (optional)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Space-CPPD-Sandbox",
                "description": "Sandbox environment for CPPD testing",
                "type": "sandbox",
                "owner_id": "123e4567-e89b-12d3-a456-426614174001",
                "owner_email": "admin@cppd.gc.ca",
                "quotas": {
                    "compute_units": 1000,
                    "storage_gb": 100,
                    "ai_calls_per_month": 10000,
                    "max_documents": 10000,
                    "max_users": 25,
                },
                "metadata": {
                    "department": "ESDC",
                    "cost_center": "CPPD-IT",
                    "environment": "sandbox",
                },
            }
        }
    )


class SpaceUpdate(BaseModel):
    """Request model for updating a Space."""
    
    name: str | None = Field(None, description="Space name", min_length=3, max_length=100)
    description: str | None = Field(None, description="Space description", max_length=500)
    status: SpaceStatus | None = Field(None, description="Operational status")
    quotas: SpaceQuotas | None = Field(None, description="Updated quotas")
    metadata: dict[str, Any] | None = Field(None, description="Updated metadata")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "suspended",
                "quotas": {
                    "compute_units": 5000,
                    "storage_gb": 500,
                    "ai_calls_per_month": 50000,
                    "max_documents": 50000,
                    "max_users": 500,
                },
            }
        }
    )
