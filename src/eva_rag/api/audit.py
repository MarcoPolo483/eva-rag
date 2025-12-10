"""API endpoints for system-level Audit Logs."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from eva_rag.models.audit_log import AuditLog, AuditLogSummary
from eva_rag.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


def _get_audit_service() -> AuditService:
    """Get AuditService instance."""
    return AuditService()


@router.get("/{sequence_number}", response_model=AuditLog)
async def get_audit_log(sequence_number: int) -> AuditLog:
    """
    Get a specific audit log by sequence number.
    
    **Example**: Get audit log #12345
    ```
    GET /api/v1/audit/12345
    ```
    """
    service = _get_audit_service()
    
    try:
        log = service.get_audit_log(sequence_number)
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail=f"Audit log {sequence_number} not found",
            )
        
        return log
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit log: {str(e)}",
        )


@router.get("", response_model=list[AuditLogSummary])
async def list_audit_logs(
    space_id: Annotated[UUID | None, Query()] = None,
    event_type: Annotated[str | None, Query()] = None,
    event_category: Annotated[str | None, Query()] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AuditLogSummary]:
    """
    List audit logs with optional filtering.
    
    **Query Parameters**:
    - `space_id`: Filter by Space (optional)
    - `event_type`: Filter by event type (optional, e.g., "document.uploaded")
    - `event_category`: Filter by category (optional, e.g., "data", "security", "compliance")
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 100)
    
    **Examples**:
    - All logs: `GET /api/v1/audit`
    - Document events: `GET /api/v1/audit?event_type=document.uploaded`
    - Security events: `GET /api/v1/audit?event_category=security`
    - Space logs: `GET /api/v1/audit?space_id=550e8400-e29b-41d4-a716-446655440000`
    
    **Note**: Admin-only endpoint (implement RBAC in future).
    """
    service = _get_audit_service()
    
    try:
        return service.list_audit_logs(
            space_id=str(space_id) if space_id else None,
            event_type=event_type,
            event_category=event_category,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list audit logs: {str(e)}",
        )


@router.post("/verify", response_model=dict)
async def verify_audit_chain(
    count: Annotated[int, Query(ge=1, le=10000)] = 1000,
) -> dict:
    """
    Verify the system-level audit log hash chain.
    
    This checks:
    1. Each log's `previous_hash` matches the previous log's `content_hash`
    2. Each log's `content_hash` is correctly computed
    
    **Query Parameters**:
    - `count`: Number of recent logs to verify (default: 1000, max: 10000)
    
    **Returns**:
    ```json
    {
        "is_valid": true,
        "message": "Audit chain verified successfully",
        "logs_checked": 1000
    }
    ```
    
    Or if chain is broken:
    ```json
    {
        "is_valid": false,
        "message": "Hash chain broken at sequence ...",
        "logs_checked": 523
    }
    ```
    
    **Note**: Admin-only endpoint (implement RBAC in future).
    """
    service = _get_audit_service()
    
    try:
        is_valid, error_message = service.verify_audit_chain(count=count)
        
        if is_valid:
            return {
                "is_valid": True,
                "message": "Audit chain verified successfully",
                "logs_checked": count,
            }
        else:
            return {
                "is_valid": False,
                "message": error_message,
                "logs_checked": count,
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify audit chain: {str(e)}",
        )
