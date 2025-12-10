"""
Audit Log model for EVA RAG - System-level tamper-evident audit trail.

This model implements FASTER principles:
- **Auditable**: Hash chain for tamper-evidence
- **Transparent**: All system events logged with immutable references
- **Secure**: Dual-write to Cosmos DB + Azure Immutable Blob Storage

Partition key: /sequence_number (sequential, not HPK)
Hash chain: System-level (not per-user, global sequence)
"""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """
    Audit log entry for system events with tamper-evidence via hash chains.

    Each audit log entry is:
    1. Assigned a sequential sequence_number (partition key)
    2. Hashed using previous entry's hash (forming a chain)
    3. Written to Cosmos DB + Azure Immutable Blob Storage (dual-write)
    4. Immutable (no updates/deletes allowed)

    This creates a tamper-evident audit trail where any modification breaks the chain.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique audit log ID")
    sequence_number: int = Field(..., description="Sequential number (partition key)")

    # Context (which Space/Tenant/User triggered this event)
    space_id: Optional[UUID] = Field(None, description="Space ID (if applicable)")
    tenant_id: Optional[UUID] = Field(None, description="Tenant ID (if applicable)")
    user_id: Optional[UUID] = Field(None, description="User ID (if applicable)")

    # Event details
    event_type: str = Field(..., description="Event type (e.g., 'document.uploaded', 'query.executed')")
    event_category: str = Field(..., description="Category (e.g., 'data', 'security', 'compliance')")
    event_data: dict[str, Any] = Field(default_factory=dict, description="Event payload (JSON)")

    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When event occurred")
    source_ip: Optional[str] = Field(None, description="Client IP address (if available)")
    user_agent: Optional[str] = Field(None, description="Client user agent (if available)")

    # Hash chain fields (tamper-evidence)
    content_hash: str = Field(..., description="SHA-256 hash of this log entry")
    previous_hash: str = Field(..., description="Hash of previous log (or 'genesis' for first)")

    # Immutable storage reference
    immutable_blob_url: Optional[str] = Field(None, description="Azure Immutable Blob URL (backup)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "sequence_number": 12345,
                "space_id": "660e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "770e8400-e29b-41d4-a716-446655440000",
                "user_id": "880e8400-e29b-41d4-a716-446655440000",
                "event_type": "document.uploaded",
                "event_category": "data",
                "event_data": {
                    "document_id": "990e8400-e29b-41d4-a716-446655440000",
                    "filename": "contract.pdf",
                    "size_bytes": 1048576,
                },
                "timestamp": "2025-12-10T14:30:00Z",
                "source_ip": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "content_hash": "abc123...",
                "previous_hash": "def456...",
                "immutable_blob_url": "https://storage.azure.net/audit/12345.json",
            }
        }


class AuditLogSummary(BaseModel):
    """
    Lightweight summary of an audit log entry (for list operations).
    """

    id: UUID
    sequence_number: int
    event_type: str
    event_category: str
    timestamp: datetime
    space_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
