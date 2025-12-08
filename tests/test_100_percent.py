"""Additional tests to reach 100% coverage - FIXED VERSION."""
import pytest
from io import BytesIO
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from eva_rag.main import app
from eva_rag.services.language_service import LanguageDetectionService
from eva_rag.models.document import DocumentMetadata, DocumentStatus


# ===== Test api/ingest.py Exception handling (lines 102-104, 124-126) =====
def test_ingest_general_exception_handling():
    """Test ingestion handles unexpected errors with 500 status."""
    client = TestClient(app)
    
    with patch('eva_rag.api.ingest.IngestionService') as MockService:
        mock_service = Mock()
        mock_service.ingest_document = AsyncMock(side_effect=Exception("Unexpected error"))
        MockService.return_value = mock_service
        
        response = client.post(
            "/api/v1/rag/ingest",
            data={
                "space_id": str(uuid4()),
                "tenant_id": str(uuid4()),
                "user_id": str(uuid4()),
            },
            files={"file": ("test.txt", b"content", "text/plain")}
        )
        
        assert response.status_code == 500
        assert "Failed to ingest document" in response.json()["detail"]


def test_ingest_file_size_None():
    """Test ingestion when file.size is None (line 79)."""
    client = TestClient(app)
    
    # Test with empty file
    response = client.post(
        "/api/v1/rag/ingest",
        data={
            "space_id": str(uuid4()),
            "tenant_id": str(uuid4()),
            "user_id": str(uuid4()),
        },
        files={"file": ("", b"", "text/plain")}  # Empty filename and content
    )
    
    # Should get 400 for empty file
    assert response.status_code in [400, 422]  # 422 for validation error


# ===== Test ingestion_service.py error paths (lines 29-30, 98-148) =====
@pytest.mark.asyncio
async def test_ingestion_service_loader_error():
    """Test ingestion service handles document loader errors."""
    from eva_rag.services.ingestion_service import IngestionService
    
    service = IngestionService()
    
    # Test with unsupported file type
    file = BytesIO(b"fake content")
    
    with pytest.raises(ValueError, match="Unsupported"):
        await service.ingest_document(
            file=file,
            filename="test.xyz",  # Unsupported extension
            file_size=100,
            content_type="application/octet-stream",
            tenant_id=uuid4(),
            space_id=uuid4(),
            user_id=uuid4(),
            additional_metadata={}
        )


# ===== Test metadata_service.py CRUD operations =====
@pytest.fixture
def metadata_service_with_mock():
    """Create metadata service with mocked Cosmos client."""
    from eva_rag.services.metadata_service import MetadataService
    
    with patch('eva_rag.services.metadata_service.CosmosClient') as MockClient:
        mock_client = Mock()
        mock_database = Mock()
        mock_container = Mock()
        
        mock_client.get_database_client.return_value = mock_database
        mock_database.get_container_client.return_value = mock_container
        MockClient.return_value = mock_client
        
        service = MetadataService()
        return service


def test_metadata_create_document(metadata_service_with_mock):
    """Test creating metadata in Cosmos DB."""
    service = metadata_service_with_mock
    
    metadata = DocumentMetadata(
        id=uuid4(),
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
        filename="test.pdf",
        file_size_bytes=1024,
        content_hash="abc123",
        content_type="application/pdf",
        text_length=500,
        page_count=1,
        language="en",
        status=DocumentStatus.INDEXED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        blob_url="https://test.blob/test.pdf"
    )
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.create_item = Mock(return_value=metadata.model_dump(mode="json"))
        mock_get.return_value = mock_container
        
        result = service.create_document(metadata)
        
        assert result.id == metadata.id
        mock_container.create_item.assert_called_once()


def test_metadata_get_document_found(metadata_service_with_mock):
    """Test retrieving existing metadata."""
    service = metadata_service_with_mock
    
    doc_id = uuid4()
    tenant_id = uuid4()
    space_id = uuid4()
    user_id = uuid4()
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.read_item = Mock(return_value={
            "id": str(doc_id),
            "tenant_id": str(tenant_id),
            "space_id": str(space_id),
            "user_id": str(user_id),
            "filename": "test.pdf",
            "file_size_bytes": 1024,
            "content_hash": "abc123",
            "content_type": "application/pdf",
            "text_length": 500,
            "page_count": 1,
            "language": "en",
            "status": "indexed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "blob_url": "https://test.blob/test.pdf",
            "chunk_count": 0
        })
        mock_get.return_value = mock_container
        
        result = service.get_document(doc_id, tenant_id)
        
        assert result is not None
        assert result.id == doc_id


def test_metadata_get_document_not_found(metadata_service_with_mock):
    """Test retrieving non-existent metadata."""
    service = metadata_service_with_mock
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.read_item = Mock(side_effect=Exception("Not found"))
        mock_get.return_value = mock_container
        
        result = service.get_document(uuid4(), uuid4())
        
        assert result is None


def test_metadata_update_document(metadata_service_with_mock):
    """Test updating metadata."""
    service = metadata_service_with_mock
    
    metadata = DocumentMetadata(
        id=uuid4(),
        tenant_id=uuid4(),
        space_id=uuid4(),
        user_id=uuid4(),
        filename="test.pdf",
        file_size_bytes=1024,
        content_hash="abc123",
        content_type="application/pdf",
        text_length=500,
        page_count=1,
        language="en",
        status=DocumentStatus.INDEXED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        blob_url="https://test.blob/test.pdf"
    )
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.upsert_item = Mock(return_value=metadata.model_dump(mode="json"))
        mock_get.return_value = mock_container
        
        result = service.update_document(metadata)
        
        assert result.status == DocumentStatus.INDEXED
        mock_container.upsert_item.assert_called_once()


def test_metadata_delete_document(metadata_service_with_mock):
    """Test deleting metadata."""
    service = metadata_service_with_mock
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.delete_item = Mock()
        mock_get.return_value = mock_container
        
        service.delete_document(uuid4(), uuid4())
        
        mock_container.delete_item.assert_called_once()


def test_metadata_list_documents_by_space(metadata_service_with_mock):
    """Test listing documents by space."""
    service = metadata_service_with_mock
    
    tenant_id = uuid4()
    space_id = uuid4()
    user_id = uuid4()
    doc_id = uuid4()
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.query_items = Mock(return_value=[
            {
                "id": str(doc_id),
                "tenant_id": str(tenant_id),
                "space_id": str(space_id),
                "user_id": str(user_id),
                "filename": "doc1.pdf",
                "file_size_bytes": 1024,
                "content_hash": "abc123",
                "content_type": "application/pdf",
                "text_length": 500,
                "page_count": 1,
                "language": "en",
                "status": "indexed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "blob_url": "https://test.blob/doc1.pdf",
                "chunk_count": 0
            }
        ])
        mock_get.return_value = mock_container
        
        results = service.list_documents_by_space(space_id, tenant_id)
        
        assert len(results) == 1
        assert results[0].id == doc_id


def test_metadata_list_documents_empty(metadata_service_with_mock):
    """Test listing documents returns empty list when none found."""
    service = metadata_service_with_mock
    
    tenant_id = uuid4()
    space_id = uuid4()
    
    with patch.object(service, '_get_container') as mock_get:
        mock_container = Mock()
        mock_container.query_items = Mock(return_value=[])
        mock_get.return_value = mock_container
        
        results = service.list_documents_by_space(space_id, tenant_id)
        
        assert len(results) == 0
        mock_container.query_items.assert_called_once()
