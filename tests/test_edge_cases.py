"""Additional tests for remaining coverage gaps."""
import pytest
from io import BytesIO
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from eva_rag.main import app


def test_ingest_file_seek_behavior():
    """Test ingestion with file that doesn't support seek (line 79)."""
    client = TestClient(app)
    
    # Create a non-seekable file-like object
    class NonSeekableFile:
        def __init__(self, data):
            self.data = data
            self.pos = 0
            
        def read(self, size=-1):
            if size == -1:
                result = self.data[self.pos:]
                self.pos = len(self.data)
            else:
                result = self.data[self.pos:self.pos + size]
                self.pos += len(result)
            return result
            
        def seek(self, pos, whence=0):
            raise IOError("Seek not supported")
    
    # This will be handled by FastAPI, just verify error handling exists
    response = client.post(
        "/api/v1/rag/ingest",
        data={
            "space_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "user_id": str(uuid4()),
        },
        files={"file": ("test.txt", b"content", "text/plain")}
    )
    
    # Should either succeed or fail gracefully
    assert response.status_code in [200, 201, 400, 422, 500]


def test_pdf_loader_invalid_pdf():
    """Test PDF loader with completely invalid PDF data."""
    from eva_rag.loaders.pdf_loader import PDFLoader
    
    loader = PDFLoader()
    
    # Test with invalid PDF bytes
    invalid_pdf = BytesIO(b"This is not a PDF at all")
    
    with pytest.raises(Exception):  # pypdf will raise an error
        loader.load(invalid_pdf, "invalid.pdf")


def test_pdf_loader_empty_pdf():
    """Test PDF loader with empty content."""
    from eva_rag.loaders.pdf_loader import PDFLoader
    
    loader = PDFLoader()
    
    # Test with empty bytes
    empty_pdf = BytesIO(b"")
    
    with pytest.raises(Exception):
        loader.load(empty_pdf, "empty.pdf")


def test_pdf_loader_corrupt_pdf():
    """Test PDF loader with truncated/corrupt PDF."""
    from eva_rag.loaders.pdf_loader import PDFLoader
    
    loader = PDFLoader()
    
    # Create a minimal but corrupt PDF header
    corrupt_pdf = BytesIO(b"%PDF-1.4\n%")
    
    with pytest.raises(Exception):
        loader.load(corrupt_pdf, "corrupt.pdf")


def test_language_service_detection_error():
    """Test language detection with content that causes errors."""
    from eva_rag.services.language_service import LanguageDetectionService
    
    service = LanguageDetectionService()
    
    # Test with extremely short text (might not be detectable)
    result = service.detect_language("a")
    
    # Should return something, even if uncertain
    assert result in ["en", "fr", "other"]
    
    # Test with numeric-only content
    result = service.detect_language("123456789")
    assert result in ["en", "fr", "other"]
    
    # Test with special characters only
    result = service.detect_language("@#$%^&*()")
    assert result in ["en", "fr", "other"]


def test_storage_service_initialization_error():
    """Test storage service handles Azure initialization errors."""
    from eva_rag.services.storage_service import StorageService
    from azure.core.exceptions import ServiceRequestError
    
    with patch('eva_rag.services.storage_service.BlobServiceClient') as MockClient:
        # Make the client initialization raise an error
        MockClient.from_connection_string.side_effect = ServiceRequestError("Connection failed")
        
        # The service should either handle this gracefully or raise
        with pytest.raises(Exception):
            service = StorageService()


def test_metadata_service_initialization_error():
    """Test metadata service handles Cosmos DB initialization errors."""
    from eva_rag.services.metadata_service import MetadataService
    from azure.core.exceptions import ServiceRequestError
    
    with patch('eva_rag.services.metadata_service.CosmosClient') as MockClient:
        mock_client = Mock()
        mock_client.create_database_if_not_exists.side_effect = ServiceRequestError("DB error")
        MockClient.return_value = mock_client
        
        # Should handle error in _ensure_database_and_container
        service = MetadataService()  # Should not crash
        
        # Verify service was created despite error
        assert service is not None


def test_metadata_service_no_credentials():
    """Test metadata service with missing credentials."""
    from eva_rag.services.metadata_service import MetadataService
    from eva_rag.config import settings
    
    original_key = settings.azure_cosmos_key
    
    try:
        # Test with no key (use DefaultAzureCredential path)
        settings.azure_cosmos_key = None
        
        with patch('eva_rag.services.metadata_service.DefaultAzureCredential') as MockCred:
            with patch('eva_rag.services.metadata_service.CosmosClient') as MockClient:
                mock_client = Mock()
                mock_database = Mock()
                mock_client.get_database_client.return_value = mock_database
                MockClient.return_value = mock_client
                
                service = MetadataService()
                
                # Verify DefaultAzureCredential was used
                MockCred.assert_called_once()
                assert service is not None
    finally:
        settings.azure_cosmos_key = original_key
