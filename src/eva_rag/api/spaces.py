"""API endpoints for Space management."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from eva_rag.models.space import Space, SpaceCreate, SpaceUpdate
from eva_rag.services.space_service import SpaceService

router = APIRouter(prefix="/spaces", tags=["spaces"])

# Initialize service
space_service = SpaceService()


@router.post("", response_model=Space, status_code=201)
async def create_space(space_create: SpaceCreate) -> Space:
    """
    Create a new Space for multi-tenant isolation.
    
    A Space represents a complete data isolation boundary:
    - Each Space has its own documents, chunks, AI interactions
    - Users from Space A cannot access Space B data
    - Supports sandbox/production/archived lifecycle
    
    **Example**: Create a sandbox Space for CPPD department
    ```json
    {
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
            "max_users": 25
        }
    }
    ```
    """
    try:
        return space_service.create_space(space_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Space: {str(e)}")


@router.get("/{space_id}", response_model=Space)
async def get_space(space_id: UUID) -> Space:
    """
    Get Space by ID.
    
    Returns complete Space configuration including:
    - Current usage (documents, storage, AI calls)
    - Resource quotas
    - Operational status
    """
    space = space_service.get_space(space_id)
    if not space:
        raise HTTPException(status_code=404, detail=f"Space {space_id} not found")
    return space


@router.get("", response_model=list[Space])
async def list_spaces(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    status: Annotated[str | None, Query()] = None,
    space_type: Annotated[str | None, Query(alias="type")] = None,
) -> list[Space]:
    """
    List Spaces with optional filtering.
    
    **Query Parameters**:
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 100)
    - `status`: Filter by status (active/suspended/archived)
    - `type`: Filter by type (sandbox/production/archived)
    
    **Example**: Get all active production Spaces
    ```
    GET /api/v1/spaces?status=active&type=production
    ```
    """
    try:
        return space_service.list_spaces(
            skip=skip,
            limit=limit,
            status=status,
            space_type=space_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Spaces: {str(e)}")


@router.patch("/{space_id}", response_model=Space)
async def update_space(space_id: UUID, space_update: SpaceUpdate) -> Space:
    """
    Update Space configuration.
    
    Supports partial updates:
    - Change status (active/suspended/archived)
    - Update quotas (compute, storage, AI calls)
    - Modify metadata
    
    **Example**: Suspend a Space
    ```json
    {
        "status": "suspended"
    }
    ```
    
    **Example**: Increase quotas
    ```json
    {
        "quotas": {
            "compute_units": 5000,
            "storage_gb": 500,
            "ai_calls_per_month": 50000,
            "max_documents": 50000,
            "max_users": 500
        }
    }
    ```
    """
    try:
        return space_service.update_space(space_id, space_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update Space: {str(e)}")


@router.delete("/{space_id}", status_code=204)
async def delete_space(space_id: UUID) -> None:
    """
    Delete Space (soft delete - archives the Space).
    
    **Note**: This is a soft delete. The Space is archived but not permanently deleted.
    Documents remain accessible for compliance/audit purposes.
    """
    try:
        space_service.delete_space(space_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete Space: {str(e)}")


@router.get("/name/{name}", response_model=Space)
async def get_space_by_name(name: str) -> Space:
    """
    Get Space by name.
    
    **Example**: 
    ```
    GET /api/v1/spaces/name/Space-CPPD
    ```
    """
    space = space_service.get_space_by_name(name)
    if not space:
        raise HTTPException(status_code=404, detail=f"Space '{name}' not found")
    return space
