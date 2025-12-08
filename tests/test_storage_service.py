"""Tests for storage service."""
from io import BytesIO
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from eva_rag.services.storage_service import StorageService


@pytest.fixture
def mock_blob_service_client():
    """Mock Azure Blob Service Client."""
    with patch("eva_rag.services.storage_service.BlobServiceClient") as mock:
        # Setup return value chain
        mock_client_instance = MagicMock()
        mock.from_connection_string.return_value = mock_client_instance
        mock.return_value = mock_client_instance
        yield mock


def test_storage_service_upload_document(
    mock_blob_service_client,
    tenant_id: str,
    space_id: str,
    document_id: str,
) -> None:
    """Test storage service uploads document to Azure Blob."""
    # Get the mock client from fixture
    mock_client = mock_blob_service_client.from_connection_string.return_value
    
    # Setup blob client with PropertyMock for url
    mock_blob_client = MagicMock()
    expected_url = "https://storage.blob.core.windows.net/documents/test.pdf"
    type(mock_blob_client).url = PropertyMock(return_value=expected_url)
    
    mock_client.get_blob_client.return_value = mock_blob_client
    mock_client.create_container = MagicMock(side_effect=Exception("Container exists"))
    
    # Create service (will use patched BlobServiceClient)
    service = StorageService()
    
    # Upload document
    file_obj = BytesIO(b"test content")
    filename = "test.pdf"
    
    url = service.upload_document(
        file=file_obj,
        filename=filename,
        tenant_id=tenant_id,
        space_id=space_id,
        document_id=document_id,
        content_type="application/pdf",
    )
    
    # Assertions
    assert url == expected_url
    mock_blob_client.upload_blob.assert_called_once()


def test_storage_service_generates_correct_path(
    mock_blob_service_client,
    tenant_id: str,
    space_id: str,
    document_id: str,
) -> None:
    """Test storage service generates correct blob path with tenant isolation."""
    service = StorageService()
    
    path = service._generate_blob_path(
        tenant_id=tenant_id,
        space_id=space_id,
        document_id=document_id,
        filename="test.pdf",
    )
    
    assert path == f"{tenant_id}/{space_id}/{document_id}/test.pdf"


def test_storage_service_compute_content_hash(mock_blob_service_client) -> None:
    """Test storage service computes correct SHA-256 hash."""
    service = StorageService()
    
    content = b"test content"
    content_hash = service.compute_content_hash(content)
    
    # SHA-256 hash of "test content"
    expected_hash = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
    assert content_hash == expected_hash


def test_storage_service_ensures_container_exists(mock_blob_service_client) -> None:
    """Test storage service ensures container exists on init."""
    mock_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value = mock_client
    mock_client.create_container = MagicMock(side_effect=Exception("Container exists"))
    
    # Should not raise exception even if container creation fails
    service = StorageService()
    
    assert service is not None


def test_storage_service_download_document(
    mock_blob_service_client,
    tenant_id: str,
    space_id: str,
    document_id: str,
) -> None:
    """Test storage service downloads document from Azure Blob."""
    mock_client = mock_blob_service_client.from_connection_string.return_value
    
    # Setup download mock
    mock_blob_client = MagicMock()
    mock_download = MagicMock()
    mock_download.readall.return_value = b"downloaded content"
    mock_blob_client.download_blob.return_value = mock_download
    mock_client.get_blob_client.return_value = mock_blob_client
    
    service = StorageService()
    
    content = service.download_document(
        tenant_id=tenant_id,
        space_id=space_id,
        document_id=document_id,
        filename="test.pdf",
    )
    
    assert content == b"downloaded content"
    mock_blob_client.download_blob.assert_called_once()


def test_storage_service_delete_document(
    mock_blob_service_client,
    tenant_id: str,
    space_id: str,
    document_id: str,
) -> None:
    """Test storage service deletes document from Azure Blob."""
    mock_client = mock_blob_service_client.from_connection_string.return_value
    
    mock_blob_client = MagicMock()
    mock_client.get_blob_client.return_value = mock_blob_client
    
    service = StorageService()
    
    service.delete_document(
        tenant_id=tenant_id,
        space_id=space_id,
        document_id=document_id,
        filename="test.pdf",
    )
    
    mock_blob_client.delete_blob.assert_called_once()
