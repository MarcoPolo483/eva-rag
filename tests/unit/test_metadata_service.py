"""
Unit tests for MetadataService with mocked Cosmos DB.

Tests cover:
- Dual-mode operation (legacy + HPK)
- Backward compatibility
- Conditional partition key building
- Metadata CRUD operations
- Cross-partition queries
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock, patch

from eva_rag.models.document_metadata import DocumentMetadata
from eva_rag.services.metadata_service import MetadataService


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client with both legacy and HPK containers."""
    client = Mock()
    database = Mock()
    legacy_container = Mock()
    hpk_container = Mock()
    
    client.get_database_client.return_value = database
    
    def get_container(container_id):
        if container_id == "documents_hpk":
            return hpk_container
        return legacy_container
    
    database.create_container_if_not_exists.side_effect = lambda **kwargs: (
        hpk_container if kwargs["id"] == "documents_hpk" else legacy_container
    )
    database.get_container_client.side_effect = get_container
    
    return client, database, legacy_container, hpk_container


@pytest.fixture
def metadata_service(mock_cosmos_client):
    """Create MetadataService with mocked Cosmos DB."""
    client, database, legacy_container, hpk_container = mock_cosmos_client
    
    with patch('eva_rag.services.metadata_service.CosmosClient') as mock_client_class:
        mock_client_class.return_value = client
        service = MetadataService(cosmos_client=client, database_name="eva-rag")
        service.legacy_container = legacy_container
        service.hpk_container = hpk_container
        return service, legacy_container, hpk_container


@pytest.fixture
def sample_metadata():
    """Create sample DocumentMetadata for testing."""
    return DocumentMetadata(
        id=uuid4(),
        space_id=uuid4(),
        tenant_id=uuid4(),
        user_id=uuid4(),
        filename="test_document.pdf",
        content_type="application/pdf",
        size_bytes=1024000,
        source_url="https://example.com/docs/test.pdf",
        tags=["legal", "contract"],
        custom_metadata={"department": "legal", "year": 2025},
    )


class TestDualModeOperation:
    """Test dual-mode (legacy + HPK) operation."""
    
    def test_create_metadata_with_hpk(self, metadata_service, sample_metadata):
        """Test creating metadata in HPK container."""
        service, legacy_container, hpk_container = metadata_service
        
        hpk_container.create_item.return_value = sample_metadata.model_dump()
        
        result = service.create_metadata(sample_metadata, use_hpk=True)
        
        assert result.id == sample_metadata.id
        hpk_container.create_item.assert_called_once()
        legacy_container.create_item.assert_not_called()
    
    def test_create_metadata_legacy(self, metadata_service, sample_metadata):
        """Test creating metadata in legacy container."""
        service, legacy_container, hpk_container = metadata_service
        
        legacy_container.create_item.return_value = sample_metadata.model_dump()
        
        result = service.create_metadata(sample_metadata, use_hpk=False)
        
        assert result.id == sample_metadata.id
        legacy_container.create_item.assert_called_once()
        hpk_container.create_item.assert_not_called()
    
    def test_backward_compatibility_mode(self, metadata_service, sample_metadata):
        """Test backward compatibility (default to legacy)."""
        service, legacy_container, hpk_container = metadata_service
        
        legacy_container.create_item.return_value = sample_metadata.model_dump()
        
        # Default should use legacy for backward compatibility
        result = service.create_metadata(sample_metadata)
        
        legacy_container.create_item.assert_called_once()
        hpk_container.create_item.assert_not_called()


class TestPartitionKeyBuilding:
    """Test conditional partition key building."""
    
    def test_build_hpk_partition_key(self, metadata_service, sample_metadata):
        """Test building HPK partition key."""
        service, legacy_container, hpk_container = metadata_service
        
        partition_key = service._build_partition_key(sample_metadata, use_hpk=True)
        
        assert len(partition_key) == 3
        assert partition_key[0] == str(sample_metadata.space_id)
        assert partition_key[1] == str(sample_metadata.tenant_id)
        assert partition_key[2] == str(sample_metadata.user_id)
    
    def test_build_legacy_partition_key(self, metadata_service, sample_metadata):
        """Test building legacy partition key (single tenant_id)."""
        service, legacy_container, hpk_container = metadata_service
        
        partition_key = service._build_partition_key(sample_metadata, use_hpk=False)
        
        assert partition_key == str(sample_metadata.tenant_id)
    
    def test_hpk_requires_all_fields(self, metadata_service):
        """Test HPK validation requires all three IDs."""
        service, legacy_container, hpk_container = metadata_service
        
        # Missing user_id
        incomplete_metadata = DocumentMetadata(
            id=uuid4(),
            space_id=uuid4(),
            tenant_id=uuid4(),
            user_id=None,  # Missing!
            filename="test.pdf",
        )
        
        with pytest.raises(ValueError, match="space_id, tenant_id, and user_id"):
            service._build_partition_key(incomplete_metadata, use_hpk=True)


class TestMetadataRetrieval:
    """Test metadata retrieval operations."""
    
    def test_get_metadata_hpk(self, metadata_service, sample_metadata):
        """Test retrieving metadata from HPK container."""
        service, legacy_container, hpk_container = metadata_service
        
        hpk_container.read_item.return_value = sample_metadata.model_dump()
        
        result = service.get_metadata(
            document_id=sample_metadata.id,
            space_id=sample_metadata.space_id,
            tenant_id=sample_metadata.tenant_id,
            user_id=sample_metadata.user_id,
            use_hpk=True,
        )
        
        assert result.id == sample_metadata.id
        hpk_container.read_item.assert_called_once()
    
    def test_get_metadata_legacy(self, metadata_service, sample_metadata):
        """Test retrieving metadata from legacy container."""
        service, legacy_container, hpk_container = metadata_service
        
        legacy_container.read_item.return_value = sample_metadata.model_dump()
        
        result = service.get_metadata(
            document_id=sample_metadata.id,
            tenant_id=sample_metadata.tenant_id,
            use_hpk=False,
        )
        
        assert result.id == sample_metadata.id
        legacy_container.read_item.assert_called_once()
    
    def test_list_metadata_by_space(self, metadata_service, sample_metadata):
        """Test listing metadata by space (cross-partition in HPK)."""
        service, legacy_container, hpk_container = metadata_service
        
        docs_data = [sample_metadata.model_dump() for _ in range(5)]
        hpk_container.query_items.return_value = docs_data
        
        result = service.list_metadata_by_space(
            space_id=sample_metadata.space_id,
            limit=10,
        )
        
        assert len(result) == 5
        hpk_container.query_items.assert_called_once()
        # Verify cross-partition query enabled
        call_kwargs = hpk_container.query_items.call_args[1]
        assert call_kwargs.get("enable_cross_partition_query") is True


class TestMetadataUpdate:
    """Test metadata update operations."""
    
    def test_update_metadata_hpk(self, metadata_service, sample_metadata):
        """Test updating metadata in HPK container."""
        service, legacy_container, hpk_container = metadata_service
        
        # Mock read existing
        hpk_container.read_item.return_value = sample_metadata.model_dump()
        
        # Mock update
        updated_data = sample_metadata.model_dump()
        updated_data["tags"] = ["legal", "contract", "reviewed"]
        hpk_container.replace_item.return_value = updated_data
        
        result = service.update_metadata(
            document_id=sample_metadata.id,
            space_id=sample_metadata.space_id,
            tenant_id=sample_metadata.tenant_id,
            user_id=sample_metadata.user_id,
            updates={"tags": ["legal", "contract", "reviewed"]},
            use_hpk=True,
        )
        
        assert "reviewed" in result.tags
        hpk_container.replace_item.assert_called_once()
    
    def test_update_metadata_legacy(self, metadata_service, sample_metadata):
        """Test updating metadata in legacy container."""
        service, legacy_container, hpk_container = metadata_service
        
        legacy_container.read_item.return_value = sample_metadata.model_dump()
        
        updated_data = sample_metadata.model_dump()
        updated_data["tags"] = ["updated"]
        legacy_container.replace_item.return_value = updated_data
        
        result = service.update_metadata(
            document_id=sample_metadata.id,
            tenant_id=sample_metadata.tenant_id,
            updates={"tags": ["updated"]},
            use_hpk=False,
        )
        
        assert result.tags == ["updated"]
        legacy_container.replace_item.assert_called_once()


class TestMetadataDeletion:
    """Test metadata deletion operations."""
    
    def test_delete_metadata_hpk(self, metadata_service, sample_metadata):
        """Test deleting metadata from HPK container."""
        service, legacy_container, hpk_container = metadata_service
        
        hpk_container.delete_item.return_value = None
        
        service.delete_metadata(
            document_id=sample_metadata.id,
            space_id=sample_metadata.space_id,
            tenant_id=sample_metadata.tenant_id,
            user_id=sample_metadata.user_id,
            use_hpk=True,
        )
        
        hpk_container.delete_item.assert_called_once()
        legacy_container.delete_item.assert_not_called()
    
    def test_delete_metadata_legacy(self, metadata_service, sample_metadata):
        """Test deleting metadata from legacy container."""
        service, legacy_container, hpk_container = metadata_service
        
        legacy_container.delete_item.return_value = None
        
        service.delete_metadata(
            document_id=sample_metadata.id,
            tenant_id=sample_metadata.tenant_id,
            use_hpk=False,
        )
        
        legacy_container.delete_item.assert_called_once()
        hpk_container.delete_item.assert_not_called()


class TestSearchOperations:
    """Test metadata search operations."""
    
    def test_search_by_tags(self, metadata_service, sample_metadata):
        """Test searching metadata by tags."""
        service, legacy_container, hpk_container = metadata_service
        
        docs_data = [sample_metadata.model_dump() for _ in range(3)]
        hpk_container.query_items.return_value = docs_data
        
        result = service.search_by_tags(
            tags=["legal", "contract"],
            space_id=sample_metadata.space_id,
            use_hpk=True,
        )
        
        assert len(result) == 3
        hpk_container.query_items.assert_called_once()
    
    def test_search_by_filename(self, metadata_service, sample_metadata):
        """Test searching metadata by filename pattern."""
        service, legacy_container, hpk_container = metadata_service
        
        docs_data = [sample_metadata.model_dump()]
        legacy_container.query_items.return_value = docs_data
        
        result = service.search_by_filename(
            filename_pattern="test_*.pdf",
            tenant_id=sample_metadata.tenant_id,
            use_hpk=False,
        )
        
        assert len(result) == 1
        assert result[0].filename == "test_document.pdf"
        legacy_container.query_items.assert_called_once()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/eva_rag/services/metadata_service", "--cov-report=term"])
