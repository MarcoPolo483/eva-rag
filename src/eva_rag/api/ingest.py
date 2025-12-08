"""Document ingestion API endpoint."""
import time
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from eva_rag.config import settings
from eva_rag.models.ingest import IngestResponse
from eva_rag.services.ingestion_service import IngestionService

router = APIRouter(prefix="/rag", tags=["RAG"])


def get_ingestion_service() -> IngestionService:
    """Dependency injection for IngestionService."""
    return IngestionService()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Document",
    description="Upload and process document through RAG pipeline",
    responses={
        201: {
            "description": "Document successfully ingested",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "indexing",
                        "filename": "sample.pdf",
                        "file_size_bytes": 1048576,
                        "page_count": 5,
                        "text_length": 2500,
                        "language_detected": "en",
                        "processing_time_ms": 1250,
                        "created_at": "2025-12-08T10:30:00Z",
                        "blob_url": "https://storage.blob.core.windows.net/docs/sample.pdf"
                    }
                }
            }
        },
        400: {"description": "Invalid input (bad UUID, empty file, unsupported format)"},
        413: {"description": "File too large (max 50MB)"},
        500: {"description": "Server error during processing"},
    },
)
async def ingest_document(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, TXT, MD)"),
    space_id: str = Form(..., description="Space UUID", example="550e8400-e29b-41d4-a716-446655440000"),
    tenant_id: str = Form(..., description="Tenant UUID", example="123e4567-e89b-12d3-a456-426614174000"),
    user_id: str = Form(..., description="User UUID", example="987fcdeb-51a2-43f1-8901-fedcba098765"),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    """
    Ingest document through the RAG pipeline.
    
    ## Pipeline Steps
    
    1. **Validate Input**
       - Check file size (max 50MB)
       - Verify file format (PDF, DOCX, TXT, MD)
       - Validate UUIDs
    
    2. **Extract Content**
       - PDF: Extract text from all pages using pypdf
       - DOCX: Parse document structure with python-docx
       - TXT/MD: Read as plain text with encoding detection
    
    3. **Detect Language**
       - Automatic detection for English/French
       - Sets document language for downstream processing
    
    4. **Chunk Text**
       - Semantic chunking with 500-token chunks
       - 100-token overlap for context preservation
       - Maintains document structure
    
    5. **Generate Embeddings**
       - Azure OpenAI text-embedding-ada-002
       - Vector embeddings for semantic search
       - Batch processing for efficiency
    
    6. **Store**
       - Upload original file to Azure Blob Storage
       - Save metadata to Cosmos DB
       - Return document ID for tracking
    
    ## Example Usage
    
    ```bash
    curl -X POST "http://localhost:8000/api/v1/rag/ingest" \\
      -F "file=@document.pdf" \\
      -F "space_id=550e8400-e29b-41d4-a716-446655440000" \\
      -F "tenant_id=123e4567-e89b-12d3-a456-426614174000" \\
      -F "user_id=987fcdeb-51a2-43f1-8901-fedcba098765"
    ```
    
    ## Response
    
    Returns document metadata including:
    - `document_id`: Unique identifier for tracking
    - `status`: Current processing status
    - `language_detected`: Detected language code
    - `processing_time_ms`: Total processing time
    - `blob_url`: Azure storage URL
    
    ## Error Handling
    
    - **400**: Invalid UUID format, empty file, unsupported format
    - **413**: File exceeds 50MB limit
    - **500**: Azure service errors, processing failures
    """
    start_time = time.time()
    
    # Validate UUIDs
    try:
        space_uuid = UUID(space_id)
        tenant_uuid = UUID(tenant_id)
        user_uuid = UUID(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}",
        ) from e
    
    # Validate file size
    if not file.size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )
    
    max_size = settings.max_file_size_mb * 1024 * 1024
    if file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file.size} bytes) exceeds maximum ({max_size} bytes)",
        )
    
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )
    
    try:
        # Read file content
        content = await file.read()
        file_obj = BytesIO(content)
        
        # Ingest document
        metadata = await ingestion_service.ingest_document(
            file=file_obj,
            filename=file.filename,
            file_size=file.size,
            content_type=file.content_type or "application/octet-stream",
            tenant_id=tenant_uuid,
            space_id=space_uuid,
            user_id=user_uuid,
            additional_metadata={},
        )
        
        # Build response
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return IngestResponse(
            document_id=metadata.id,
            status=metadata.status.value,
            filename=metadata.filename,
            file_size_bytes=metadata.file_size_bytes,
            page_count=metadata.page_count,
            text_length=metadata.text_length,
            language_detected=metadata.language,
            processing_time_ms=processing_time_ms,
            created_at=metadata.created_at,
            blob_url=metadata.blob_url,
        )
        
    except ValueError as e:
        # Document loading error (invalid format, unsupported extension)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    
    except Exception as e:
        # Storage or database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}",
        ) from e
