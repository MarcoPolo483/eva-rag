"""
Final coverage tests to reach 100%.

Targets remaining uncovered lines:
- ingestion_service.py: lines 29-30 (embedding service failure), 98-148 (full workflow)
- ingest.py: lines 146, 169-171 (filename validation, error handling)
- pdf_loader.py: lines 34, 42, 51-54 (metadata extraction)
- language_service.py: lines 48-50 (LangDetectException)
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader, PdfWriter
from langdetect.lang_detect_exception import LangDetectException
from uuid import uuid4

from eva_rag.services.ingestion_service import IngestionService
from eva_rag.services.language_service import LanguageDetectionService
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.api.ingest import ingest_document
from eva_rag.models.document import DocumentStatus


class TestIngestionServiceEmbeddingFailure:
    """Test ingestion service when embedding service fails to initialize."""
    
    @patch("eva_rag.services.ingestion_service.EmbeddingService")
    def test_embedding_service_init_failure(self, mock_embedding_class):
        """Test that ingestion service handles embedding service initialization failure."""
        # Make EmbeddingService constructor raise an exception
        mock_embedding_class.side_effect = Exception("Azure OpenAI not configured")
        
        # Should not raise, but set embedding_service to None
        service = IngestionService()
        
        assert service.embedding_service is None
        assert service.storage_service is not None
        assert service.metadata_service is not None
        assert service.language_service is not None
        assert service.chunking_service is not None


class TestIngestionServiceFullWorkflow:
    """Test complete ingestion workflow with real service calls."""
    
    @pytest.mark.asyncio
    @patch("eva_rag.services.ingestion_service.StorageService")
    @patch("eva_rag.services.ingestion_service.MetadataService")
    @patch("eva_rag.services.ingestion_service.EmbeddingService")
    async def test_full_ingestion_workflow_with_embeddings(
        self, mock_embedding_class, mock_metadata_class, mock_storage_class
    ):
        """Test complete ingestion workflow including embeddings."""
        # Setup mocks
        mock_storage = Mock()
        mock_storage.upload_document.return_value = "https://blob.url/doc.pdf"
        mock_storage.compute_content_hash.return_value = "abc123hash"
        mock_storage_class.return_value = mock_storage
        
        mock_metadata = Mock()
        mock_metadata_class.return_value = mock_metadata
        
        mock_embedding = Mock()
        mock_embedding.generate_embeddings_batch.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_embedding_class.return_value = mock_embedding
        
        # Create service
        service = IngestionService()
        
        # Create test PDF with metadata
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        
        # Add metadata to PDF
        pdf_writer.add_metadata({
            "/Title": "Test Document",
            "/Author": "Test Author"
        })
        
        pdf_buffer = BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()
        
        # Create file object
        file = BytesIO(pdf_bytes)
        
        # Ingest document
        result = await service.ingest_document(
            file=file,
            filename="test.pdf",
            file_size=len(pdf_bytes),
            content_type="application/pdf",
            tenant_id=uuid4(),
            space_id=uuid4(),
            user_id=uuid4(),
            additional_metadata={"source": "test"},
        )
        
        # Verify the full workflow executed
        assert result.status == DocumentStatus.INDEXING
        assert result.filename == "test.pdf"
        assert result.chunk_count > 0
        assert result.blob_url == "https://blob.url/doc.pdf"
        assert result.metadata["source"] == "test"
        
        # Verify services were called
        mock_storage.upload_document.assert_called_once()
        mock_metadata.create_document.assert_called_once()
        mock_embedding.generate_embeddings_batch.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("eva_rag.services.ingestion_service.StorageService")
    @patch("eva_rag.services.ingestion_service.MetadataService")
    @patch("eva_rag.services.ingestion_service.EmbeddingService")
    async def test_full_ingestion_workflow_without_embeddings(
        self, mock_embedding_class, mock_metadata_class, mock_storage_class
    ):
        """Test complete ingestion workflow when embedding service unavailable."""
        # Setup mocks - embedding service fails
        mock_embedding_class.side_effect = Exception("Azure OpenAI not configured")
        
        mock_storage = Mock()
        mock_storage.upload_document.return_value = "https://blob.url/doc.txt"
        mock_storage.compute_content_hash.return_value = "def456hash"
        mock_storage_class.return_value = mock_storage
        
        mock_metadata = Mock()
        mock_metadata_class.return_value = mock_metadata
        
        # Create service (embedding will be None)
        service = IngestionService()
        assert service.embedding_service is None
        
        # Create test text file
        file = BytesIO(b"This is test content for ingestion.\n\nSecond paragraph.")
        
        # Ingest document
        result = await service.ingest_document(
            file=file,
            filename="test.txt",
            file_size=57,
            content_type="text/plain",
            tenant_id=uuid4(),
            space_id=uuid4(),
            user_id=uuid4(),
            additional_metadata=None,
        )
        
        # Verify workflow completed without embeddings
        assert result.status == DocumentStatus.INDEXING
        assert result.filename == "test.txt"
        assert result.chunk_count > 0
        
        # Verify storage and metadata were still called
        mock_storage.upload_document.assert_called_once()
        mock_metadata.create_document.assert_called_once()


class TestAPIIngestEdgeCases:
    """Test API endpoint edge cases."""
    
    @pytest.mark.asyncio
    async def test_ingest_missing_filename(self):
        """Test ingestion fails when filename is missing."""
        # Create upload file with no filename and non-zero size
        file = UploadFile(
            filename=None,  # Missing filename
            file=BytesIO(b"content"),
            size=7  # Add size so it passes empty check
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await ingest_document(
                file=file,
                tenant_id="550e8400-e29b-41d4-a716-446655440000",
                space_id="660e8400-e29b-41d4-a716-446655440000",
                user_id="770e8400-e29b-41d4-a716-446655440000"
            )
        
        assert exc_info.value.status_code == 400
        assert "Filename is required" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_ingest_empty_filename(self):
        """Test ingestion fails when filename is empty string."""
        # Create upload file with empty filename and non-zero size
        file = UploadFile(
            filename="",  # Empty filename
            file=BytesIO(b"content"),
            size=7  # Add size so it passes empty check
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await ingest_document(
                file=file,
                tenant_id="550e8400-e29b-41d4-a716-446655440000",
                space_id="660e8400-e29b-41d4-a716-446655440000",
                user_id="770e8400-e29b-41d4-a716-446655440000"
            )
        
        assert exc_info.value.status_code == 400
        assert "Filename is required" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    @patch("eva_rag.api.ingest.IngestionService")
    async def test_ingest_service_exception_handling(self, mock_service_class):
        """Test API handles exceptions from ingestion service."""
        # Make ingestion service raise an exception
        mock_service = Mock()
        mock_service.ingest_document.side_effect = ValueError("Invalid file format")
        mock_service_class.return_value = mock_service
        
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(b"not a real pdf"),
            size=14
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await ingest_document(
                file=file,
                tenant_id="550e8400-e29b-41d4-a716-446655440000",
                space_id="660e8400-e29b-41d4-a716-446655440000",
                user_id="770e8400-e29b-41d4-a716-446655440000"
            )
        
        assert exc_info.value.status_code == 500
        assert "Failed to ingest document" in str(exc_info.value.detail)


class TestPDFLoaderMetadata:
    """Test PDF loader metadata extraction."""
    
    def test_pdf_with_title_only(self):
        """Test PDF with only title metadata."""
        # Create PDF with only title
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        pdf_writer.add_metadata({"/Title": "My Title"})
        
        pdf_buffer = BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)  # Seek to start for reading
        
        loader = PDFLoader()
        result = loader.load(pdf_buffer, "test.pdf")
        
        assert result.metadata.get("title") == "My Title"
        assert "author" not in result.metadata
    
    def test_pdf_with_author_only(self):
        """Test PDF with only author metadata."""
        # Create PDF with only author
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        pdf_writer.add_metadata({"/Author": "John Doe"})
        
        pdf_buffer = BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)  # Seek to start for reading
        
        loader = PDFLoader()
        result = loader.load(pdf_buffer, "test.pdf")
        
        assert result.metadata.get("author") == "John Doe"
        assert "title" not in result.metadata
    
    def test_pdf_with_both_title_and_author(self):
        """Test PDF with both title and author metadata."""
        # Create PDF with both metadata fields
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        pdf_writer.add_metadata({
            "/Title": "Complete Document",
            "/Author": "Jane Smith"
        })
        
        pdf_buffer = BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)  # Seek to start for reading
        
        loader = PDFLoader()
        result = loader.load(pdf_buffer, "test.pdf")
        
        assert result.metadata.get("title") == "Complete Document"
        assert result.metadata.get("author") == "Jane Smith"
    
    def test_pdf_with_no_metadata(self):
        """Test PDF with no metadata returns empty dict."""
        # Create PDF with no metadata
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        # Don't add any metadata
        
        pdf_buffer = BytesIO()
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)  # Seek to start for reading
        
        loader = PDFLoader()
        result = loader.load(pdf_buffer, "test.pdf")
        
        assert result.metadata == {}


class TestLanguageDetectionException:
    """Test language detection exception handling."""
    
    @patch("eva_rag.services.language_service.detect")
    def test_langdetect_exception_returns_default(self, mock_detect):
        """Test that LangDetectException returns default English."""
        # Make detect() raise LangDetectException
        mock_detect.side_effect = LangDetectException("no features in text", "")
        
        service = LanguageDetectionService()
        result = service.detect_language("!!!")  # Text that might cause detection to fail
        
        assert result == "en"
    
    @patch("eva_rag.services.language_service.detect")
    def test_langdetect_exception_with_empty_text(self, mock_detect):
        """Test LangDetectException handling with empty text."""
        mock_detect.side_effect = LangDetectException("text is empty", "")
        
        service = LanguageDetectionService()
        result = service.detect_language("")
        
        assert result == "en"
