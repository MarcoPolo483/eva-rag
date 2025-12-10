"""Search API endpoints for hybrid search and retrieval."""
import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, status

from eva_rag.models.search import ChunkResult, SearchRequest, SearchResponse
from eva_rag.services.embedding_service import EmbeddingService
from eva_rag.services.search_service import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search documents with hybrid vector + keyword search",
    description="""
    Execute hybrid search (vector + BM25 keyword) across indexed documents.
    
    **Features:**
    - Vector search: Cosine similarity on embeddings
    - Keyword search: BM25 on content text
    - RRF fusion: Reciprocal Rank Fusion combines rankings
    - Reranking: Optional cross-encoder for precision
    - Filters: Language, document type, space/tenant isolation
    
    **Performance:**
    - Target latency: < 500ms (p95)
    - Top-K limit: 1-50 results
    
    **Example:**
    ```json
    {
      "query": "What are the EI voluntary leaving requirements?",
      "space_id": "...",
      "tenant_id": "...",
      "user_id": "...",
      "top_k": 5,
      "rerank": true,
      "language": "en"
    }
    ```
    """,
)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """
    Search documents using hybrid vector + keyword search.
    
    Args:
        request: Search request with query and filters
        
    Returns:
        Search results with relevance scores
        
    Raises:
        400: Missing required fields
        503: Search service unavailable
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    logger.info(
        f"Search query '{request.query[:50]}...' "
        f"(space={request.space_id}, tenant={request.tenant_id})"
    )
    
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        search_service = SearchService()
        
        # Generate query embedding
        query_vector = embedding_service.generate_embedding(request.query)
        
        # Build filters
        filters = {}
        if request.language:
            filters["language"] = request.language
        if request.document_type:
            filters["document_type"] = request.document_type
        
        # Execute hybrid search
        search_results = search_service.hybrid_search(
            query=request.query,
            query_vector=query_vector,
            space_id=str(request.space_id),
            tenant_id=str(request.tenant_id),
            top_k=request.top_k,
            filters=filters,
        )
        
        # TODO: Add cross-encoder reranking if request.rerank=True
        # This will be implemented in next task
        
        # Convert to response format
        chunk_results = [
            ChunkResult(
                chunk_id=result["chunk_id"],
                document_id=result["document_id"],
                document_name=result["document_name"],
                page_number=result.get("page_number"),
                content=result["content"],
                relevance_score=min(result["relevance_score"] / 10.0, 1.0),  # Normalize to 0-1
                language=result["language"],
                document_type=result.get("document_type", "other"),
                chunk_index=result.get("chunk_index", 0),
            )
            for result in search_results
        ]
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        response = SearchResponse(
            query_id=query_id,
            query=request.query,
            results=chunk_results,
            processing_time_ms=processing_time,
            total_results=len(chunk_results),
            reranked=False,  # Will be True after reranking implemented
        )
        
        logger.info(
            f"✅ Search completed: {len(chunk_results)} results in {processing_time}ms"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Invalid search request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service unavailable. Please try again later.",
        )
