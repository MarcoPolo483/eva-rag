"""Document ingestion service orchestrating the full pipeline."""
import logging
import time
import uuid
from io import BytesIO
from typing import BinaryIO

from eva_rag.loaders.factory import LoaderFactory
from eva_rag.models.chunk import DocumentChunk
from eva_rag.models.document import DocumentMetadata, DocumentStatus
from eva_rag.services.chunking_service import ChunkingService
from eva_rag.services.embedding_service import EmbeddingService
from eva_rag.services.language_service import LanguageDetectionService
from eva_rag.services.metadata_service import MetadataService
from eva_rag.services.search_service import SearchService
from eva_rag.services.storage_service import StorageService
from eva_rag.utils.datetime_utils import now_utc

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrate document ingestion pipeline: extract → detect language → store."""
    
    def __init__(self) -> None:
        """Initialize ingestion service with dependencies."""
        self.storage_service = StorageService()
        self.metadata_service = MetadataService()
        self.language_service = LanguageDetectionService()
        self.chunking_service = ChunkingService()
        # Embedding service requires Azure OpenAI deployment
        try:
            self.embedding_service = EmbeddingService()
        except Exception:
            self.embedding_service = None  # Will skip embedding if not available
        
        # Search service requires Azure AI Search configuration
        try:
            self.search_service = SearchService()
            self.search_service.create_index_if_not_exists()
        except Exception as e:
            logger.warning(f"Search service unavailable, indexing will be skipped: {e}")
            self.search_service = None
    
    async def ingest_document(
        self,
        file: BinaryIO,
        filename: str,
        file_size: int,
        content_type: str,
        tenant_id: uuid.UUID,
        space_id: uuid.UUID,
        user_id: uuid.UUID,
        additional_metadata: dict[str, str | int] | None = None,
    ) -> DocumentMetadata:
        """
        Ingest document through full pipeline.
        
        Pipeline:
        1. Extract text from file (PDF/DOCX/TXT)
        2. Detect language (EN-CA/FR-CA)
        3. Chunk text into semantic segments
        4. Generate embeddings for chunks
        5. Upload to Azure Blob Storage
        6. Store metadata in Cosmos DB
        7. Index chunks in Azure AI Search
        
        Args:
            file: Binary file content
            filename: Original filename
            file_size: File size in bytes
            content_type: MIME type
            tenant_id: Tenant UUID
            space_id: Space UUID
            user_id: User UUID
            additional_metadata: Optional metadata (tags, document_type, etc.)
            
        Returns:
            Document metadata with extraction results
            
        Raises:
            ValueError: If file processing fails
            Exception: If storage or database operations fail
        """
        start_time = time.time()
        document_id = uuid.uuid4()
        
        # Read file content for hash
        file.seek(0)
        file_content = file.read()
        content_hash = self.storage_service.compute_content_hash(file_content)
        
        # Step 1: Extract text from document
        file.seek(0)
        extracted = LoaderFactory.load_document(file, filename)
        
        # Step 2: Detect language
        language = self.language_service.detect_language(extracted.text)
        
        # Step 3: Chunk text
        chunks = self.chunking_service.chunk_text(extracted.text)
        chunk_count = len(chunks)
        
        # Step 4: Generate embeddings for chunks (if service available)
        embeddings = []
        if self.embedding_service and chunk_count > 0:
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Step 5: Upload to Azure Blob Storage
        file.seek(0)
        blob_url = self.storage_service.upload_document(
            file=file,
            filename=filename,
            tenant_id=str(tenant_id),
            space_id=str(space_id),
            document_id=str(document_id),
            content_type=content_type,
        )
        
        # Step 6: Create metadata document
        now = now_utc()
        metadata = DocumentMetadata(
            id=document_id,
            tenant_id=tenant_id,
            space_id=space_id,
            user_id=user_id,
            filename=filename,
            file_size_bytes=file_size,
            content_hash=content_hash,
            content_type=content_type,
            text_length=len(extracted.text),
            page_count=extracted.page_count,
            language=language,
            status=DocumentStatus.INDEXING,  # Chunks embedded, ready for search indexing
            chunk_count=chunk_count,
            created_at=now,
            updated_at=now,
            indexed_at=None,  # Will be set when indexed in Azure AI Search
            blob_url=blob_url,
            metadata=additional_metadata or {},
        )
        
        # Merge extracted metadata
        if extracted.metadata:
            metadata.metadata.update(extracted.metadata)
        
        # Step 7: Store in Cosmos DB
        self.metadata_service.create_document(metadata)
        
        # Step 8: Index chunks in Azure AI Search
        if self.search_service and chunk_count > 0 and embeddings:
            try:
                # Create DocumentChunk objects for indexing
                document_chunks = []
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    doc_chunk = DocumentChunk(
                        chunk_id=f"{document_id}_{i}",  # Use underscore instead of colon (Azure AI Search key restriction)
                        document_id=document_id,
                        space_id=space_id,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        text=chunk.text,
                        chunk_index=i,
                        token_count=len(chunk.text.split()),  # Approximate token count
                        filename=filename,
                        page_number=chunk.page_number if hasattr(chunk, 'page_number') else None,
                        embedding=embedding,
                        language=language,
                        created_at=now,
                        metadata={
                            "document_name": filename,
                            "document_type": additional_metadata.get("document_type", "other") if additional_metadata else "other",
                        },
                    )
                    document_chunks.append(doc_chunk)
                
                # Index in Azure AI Search
                indexed_count = self.search_service.index_chunks(document_chunks)
                
                # Update document status to INDEXED
                if indexed_count == chunk_count:
                    metadata.status = DocumentStatus.INDEXED
                    metadata.indexed_at = now_utc()
                    self.metadata_service.update_document(metadata)
                    logger.info(f"✅ Indexed {indexed_count} chunks for document {document_id}")
                else:
                    logger.warning(
                        f"⚠️  Partial indexing: {indexed_count}/{chunk_count} chunks indexed"
                    )
            except Exception as e:
                logger.error(f"Failed to index chunks for document {document_id}: {e}")
                # Continue - document still usable even if indexing failed
        
        # Log processing time
        processing_time = int((time.time() - start_time) * 1000)
        print(
            f"✅ Ingested document {document_id} ({filename}) in {processing_time}ms: "
            f"{chunk_count} chunks, {len(embeddings)} embeddings, "
            f"status={metadata.status}"
        )
        
        return metadata
