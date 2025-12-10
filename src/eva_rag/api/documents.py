"""API endpoints for Document management with HPK support."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from eva_rag.models.document import DocumentMetadata
from eva_rag.services.metadata_service import MetadataService

router = APIRouter(prefix="/spaces/{space_id}/documents", tags=["documents"])


def _get_metadata_service(use_hpk: bool = True) -> MetadataService:
    """Get MetadataService instance (HPK mode by default)."""
    return MetadataService(use_hpk=use_hpk)


@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(
    space_id: UUID,
    document_id: UUID,
    tenant_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
) -> DocumentMetadata:
    """
    Get document metadata by ID.
    
    Uses Hierarchical Partition Keys (HPK) for efficient retrieval:
    - space_id: Required (from path)
    - tenant_id: Optional (query param for tenant-level access)
    - user_id: Optional (query param for user-level access)
    
    **Example**: Get document from Space A, Tenant B, User C
    ```
    GET /api/v1/spaces/550e8400-e29b-41d4-a716-446655440000/documents/660e8400-e29b-41d4-a716-446655440001?tenant_id=770e8400-e29b-41d4-a716-446655440000&user_id=880e8400-e29b-41d4-a716-446655440000
    ```
    """
    service = _get_metadata_service(use_hpk=True)
    
    try:
        document = service.get_document(
            document_id=document_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found in Space {space_id}",
            )
        
        return document
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}",
        )


@router.get("", response_model=list[DocumentMetadata])
async def list_documents(
    space_id: UUID,
    tenant_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[DocumentMetadata]:
    """
    List documents in a Space with optional tenant/user filtering.
    
    **Query Parameters**:
    - `tenant_id`: Filter by tenant (optional)
    - `user_id`: Filter by user (optional)
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 100)
    
    **Examples**:
    - All documents in Space: `GET /api/v1/spaces/{space_id}/documents`
    - Tenant documents: `GET /api/v1/spaces/{space_id}/documents?tenant_id=...`
    - User documents: `GET /api/v1/spaces/{space_id}/documents?tenant_id=...&user_id=...`
    """
    service = _get_metadata_service(use_hpk=True)
    
    try:
        return service.list_documents_by_space(
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.patch("/{document_id}", response_model=DocumentMetadata)
async def update_document(
    space_id: UUID,
    document_id: UUID,
    update_data: dict,
    tenant_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
) -> DocumentMetadata:
    """
    Update document metadata (status, progress, error).
    
    **Allowed fields**:
    - `status`: processing_status update
    - `progress_percent`: processing progress
    - `error_message`: error details
    
    **Example**: Update processing status
    ```json
    {
        "status": "completed",
        "progress_percent": 100
    }
    ```
    """
    service = _get_metadata_service(use_hpk=True)
    
    try:
        # Get existing document
        document = service.get_document(
            document_id=document_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found in Space {space_id}",
            )
        
        # Update document
        updated = service.update_document(
            document_id=document_id,
            update_data=update_data,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        return updated
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update document: {str(e)}",
        )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    space_id: UUID,
    document_id: UUID,
    tenant_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
) -> None:
    """
    Delete a document (soft delete - marks as deleted).
    
    Also deletes associated chunks via cascade.
    """
    service = _get_metadata_service(use_hpk=True)
    
    try:
        service.delete_document(
            document_id=document_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}",
        )
