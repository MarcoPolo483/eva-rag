"""API endpoints for Document Chunk management."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from eva_rag.models.chunk import DocumentChunk
from eva_rag.services.chunk_service import ChunkService

router = APIRouter(prefix="/spaces/{space_id}", tags=["chunks"])


def _get_chunk_service() -> ChunkService:
    """Get ChunkService instance."""
    return ChunkService()


@router.get("/documents/{document_id}/chunks", response_model=list[DocumentChunk])
async def list_document_chunks(
    space_id: UUID,
    document_id: UUID,
    tenant_id: Annotated[UUID, Query()],
    user_id: Annotated[UUID, Query()],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[DocumentChunk]:
    """
    List all chunks for a specific document.
    
    Chunks are returned in order by `chunk_index`.
    
    **Required Query Parameters**:
    - `tenant_id`: Tenant ID (HPK level 2)
    - `user_id`: User ID (HPK level 3)
    
    **Optional Query Parameters**:
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 500)
    
    **Example**: Get chunks for document
    ```
    GET /api/v1/spaces/{space_id}/documents/{document_id}/chunks?tenant_id=...&user_id=...
    ```
    """
    service = _get_chunk_service()
    
    try:
        return service.list_chunks_by_document(
            document_id=document_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chunks: {str(e)}",
        )


@router.get("/chunks/{chunk_id}", response_model=DocumentChunk)
async def get_chunk(
    space_id: UUID,
    chunk_id: str,
    tenant_id: Annotated[UUID, Query()],
    user_id: Annotated[UUID, Query()],
) -> DocumentChunk:
    """
    Get a specific chunk by ID.
    
    **Required Query Parameters**:
    - `tenant_id`: Tenant ID (HPK level 2)
    - `user_id`: User ID (HPK level 3)
    
    **Example**: Get chunk
    ```
    GET /api/v1/spaces/{space_id}/chunks/{chunk_id}?tenant_id=...&user_id=...
    ```
    """
    service = _get_chunk_service()
    
    try:
        chunk = service.get_chunk(
            chunk_id=chunk_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        if not chunk:
            raise HTTPException(
                status_code=404,
                detail=f"Chunk {chunk_id} not found in Space {space_id}",
            )
        
        return chunk
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chunk: {str(e)}",
        )


@router.get("/chunks", response_model=list[DocumentChunk])
async def list_space_chunks(
    space_id: UUID,
    tenant_id: Annotated[UUID | None, Query()] = None,
    user_id: Annotated[UUID | None, Query()] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[DocumentChunk]:
    """
    List all chunks in a Space (admin/cross-partition query).
    
    **Query Parameters**:
    - `tenant_id`: Filter by tenant (optional)
    - `user_id`: Filter by user (optional)
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 100)
    
    **Note**: Cross-partition query - may consume more RUs.
    
    **Example**: Get all chunks in Space
    ```
    GET /api/v1/spaces/{space_id}/chunks
    ```
    """
    service = _get_chunk_service()
    
    try:
        return service.list_chunks_by_space(
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chunks: {str(e)}",
        )
