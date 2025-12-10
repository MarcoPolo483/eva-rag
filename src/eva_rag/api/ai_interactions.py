"""API endpoints for AI Interaction provenance tracking."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Query

from eva_rag.models.ai_interaction import AIInteraction
from eva_rag.services.ai_interaction_service import AIInteractionService

router = APIRouter(prefix="/spaces/{space_id}/interactions", tags=["ai-interactions"])


def _get_interaction_service() -> AIInteractionService:
    """Get AIInteractionService instance."""
    return AIInteractionService()


@router.post("", response_model=AIInteraction, status_code=201)
async def create_interaction(
    space_id: UUID,
    interaction: Annotated[AIInteraction, Body()],
) -> AIInteraction:
    """
    Record a new AI interaction for provenance tracking.
    
    This creates an **immutable** record with:
    - Query and response text
    - Chunks used (with relevance scores)
    - Citations extracted
    - Model details (name, version, temperature)
    - Hash chain linkage (tamper-evidence)
    
    **FASTER Principles**:
    - **Auditable**: Hash chain for tamper detection
    - **Transparent**: Full context of AI response
    - **Explainable**: Citations link response to source chunks
    
    **Example**: Record query interaction
    ```json
    {
        "space_id": "550e8400-e29b-41d4-a716-446655440000",
        "tenant_id": "770e8400-e29b-41d4-a716-446655440000",
        "user_id": "880e8400-e29b-41d4-a716-446655440000",
        "query": "What are the privacy provisions?",
        "response": "The privacy provisions include...",
        "chunks_used": [
            {
                "chunk_id": "doc123_chunk5",
                "document_id": "660e8400-e29b-41d4-a716-446655440001",
                "filename": "privacy-act.pdf",
                "page_number": 12,
                "text_snippet": "Section 5.1 states...",
                "relevance_score": 0.95
            }
        ],
        "citations": [
            {
                "chunk_id": "doc123_chunk5",
                "document_id": "660e8400-e29b-41d4-a716-446655440001",
                "filename": "privacy-act.pdf",
                "page_number": 12,
                "quote": "Section 5.1 states that personal information...",
                "position_in_response": 0
            }
        ],
        "model_name": "gpt-4",
        "model_version": "0613",
        "temperature": 0.7
    }
    ```
    """
    service = _get_interaction_service()
    
    try:
        # Ensure space_id matches
        if interaction.space_id != space_id:
            raise HTTPException(
                status_code=400,
                detail=f"Space ID mismatch: path={space_id}, body={interaction.space_id}",
            )
        
        return service.create_interaction(interaction)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create interaction: {str(e)}",
        )


@router.get("/{interaction_id}", response_model=AIInteraction)
async def get_interaction(
    space_id: UUID,
    interaction_id: UUID,
    tenant_id: Annotated[UUID, Query()],
    user_id: Annotated[UUID, Query()],
) -> AIInteraction:
    """
    Get a specific AI interaction by ID.
    
    **Required Query Parameters**:
    - `tenant_id`: Tenant ID (HPK level 2)
    - `user_id`: User ID (HPK level 3)
    """
    service = _get_interaction_service()
    
    try:
        interaction = service.get_interaction(
            interaction_id=interaction_id,
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )
        
        if not interaction:
            raise HTTPException(
                status_code=404,
                detail=f"Interaction {interaction_id} not found in Space {space_id}",
            )
        
        return interaction
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve interaction: {str(e)}",
        )


@router.get("", response_model=list[AIInteraction])
async def list_interactions(
    space_id: UUID,
    tenant_id: Annotated[UUID, Query()],
    user_id: Annotated[UUID, Query()],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AIInteraction]:
    """
    List AI interactions for a specific user.
    
    Returns interactions in reverse chronological order (newest first).
    
    **Required Query Parameters**:
    - `tenant_id`: Tenant ID (HPK level 2)
    - `user_id`: User ID (HPK level 3)
    
    **Optional Query Parameters**:
    - `skip`: Pagination offset (default: 0)
    - `limit`: Max results (default: 100, max: 100)
    """
    service = _get_interaction_service()
    
    try:
        return service.list_interactions_by_user(
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list interactions: {str(e)}",
        )


@router.post("/verify-chain", response_model=dict)
async def verify_hash_chain(
    space_id: UUID,
    tenant_id: Annotated[UUID, Query()],
    user_id: Annotated[UUID, Query()],
    count: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> dict:
    """
    Verify the hash chain integrity for a user's interactions.
    
    This checks:
    1. Each interaction's `previous_hash` matches the previous interaction's `content_hash`
    2. Each interaction's `content_hash` is correctly computed
    
    **Required Query Parameters**:
    - `tenant_id`: Tenant ID (HPK level 2)
    - `user_id`: User ID (HPK level 3)
    
    **Optional Query Parameters**:
    - `count`: Number of recent interactions to verify (default: 100, max: 1000)
    
    **Returns**:
    ```json
    {
        "is_valid": true,
        "message": "Hash chain verified successfully",
        "interactions_checked": 42
    }
    ```
    
    Or if chain is broken:
    ```json
    {
        "is_valid": false,
        "message": "Hash chain broken at interaction ...",
        "interactions_checked": 15
    }
    ```
    """
    service = _get_interaction_service()
    
    try:
        is_valid, error_message = service.verify_hash_chain(
            space_id=space_id,
            tenant_id=tenant_id,
            user_id=user_id,
            count=count,
        )
        
        if is_valid:
            return {
                "is_valid": True,
                "message": "Hash chain verified successfully",
                "interactions_checked": count,
            }
        else:
            return {
                "is_valid": False,
                "message": error_message,
                "interactions_checked": count,
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify hash chain: {str(e)}",
        )
