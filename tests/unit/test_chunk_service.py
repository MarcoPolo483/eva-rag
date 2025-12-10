"""
Unit tests for ChunkService with mocked Cosmos DB.

Tests cover:
- Chunk creation (single + batch)
- Chunk retrieval by ID
- Listing chunks by document
- Listing chunks by space
- HPK validation
- Batch partition key validation
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock

from eva_rag.models.chunk import DocumentChunk
from eva_rag.services.chunk_service import ChunkService


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client."""
    client = Mock()
    database = Mock()
    container = Mock()
    
    client.get_database_client.return_value = database
    database.create_container_if_not_exists.return_value = container
    database.get_container_client.return_value = container
    
    return client, database, container


@pytest.fixture
def chunk_service(mock_cosmos_client):
    """Create ChunkService with mocked Cosmos DB."""
    client, database, container = mock_cosmos_client
    
    with patch('eva_rag.services.chunk_service.CosmosClient') as mock_client_class:
        mock_client_class.return_value = client
        service = ChunkService()
        service.container = container  # Inject mock container
        return service, container


@pytest.fixture
def sample_chunk():
    """Create sample DocumentChunk for testing."""
    space_id = uuid4()
    tenant_id = uuid4()
    user_id = uuid4()
    document_id = uuid4()
    
    return DocumentChunk(
        chunk_id=f"{document_id}_chunk_1",
        document_id=document_id,
        space_id=space_id,
        tenant_id=tenant_id,
        user_id=user_id,
        text="This is a test chunk of text.",
        chunk_index=1,
        token_count=8,
        filename="test.pdf",
        language="en",
        embedding=[0.1] * 1536,
        created_at=datetime.now(timezone.utc),
    )


class TestChunkCreation:
    """Test chunk creation operations."""
    
    def test_create_single_chunk(self, chunk_service, sample_chunk):
        """Test creating a single chunk."""
        service, container = chunk_service
        container.create_item.return_value = sample_chunk.model_dump()
        
        result = service.create_chunk(sample_chunk)
        
        assert result == sample_chunk
        container.create_item.assert_called_once()
        
        # Verify call arguments
        call_args = container.create_item.call_args
        assert call_args[1]["body"]["chunk_id"] == sample_chunk.chunk_id
    
    def test_create_batch_same_partition(self, chunk_service, sample_chunk):
        """Test batch creation with same partition key."""
        service, container = chunk_service
        
        # Create 3 chunks with same partition key
        chunks = [
            sample_chunk,
            DocumentChunk(
                chunk_id=f"{sample_chunk.document_id}_chunk_2",
                document_id=sample_chunk.document_id,
                space_id=sample_chunk.space_id,
                tenant_id=sample_chunk.tenant_id,
                user_id=sample_chunk.user_id,
                text="Second chunk",
                chunk_index=2,
                token_count=5,
                filename="test.pdf",
                language="en",
                embedding=[0.2] * 1536,
                created_at=datetime.now(timezone.utc),
            ),
            DocumentChunk(
                chunk_id=f"{sample_chunk.document_id}_chunk_3",
                document_id=sample_chunk.document_id,
                space_id=sample_chunk.space_id,
                tenant_id=sample_chunk.tenant_id,
                user_id=sample_chunk.user_id,
                text="Third chunk",
                chunk_index=3,
                token_count=5,
                filename="test.pdf",
                language="en",
                embedding=[0.3] * 1536,
                created_at=datetime.now(timezone.utc),
            ),
        ]
        
        container.create_item.side_effect = [c.model_dump() for c in chunks]
        
        result = service.create_chunks_batch(chunks)
        
        assert len(result) == 3
        assert container.create_item.call_count == 3
    
    def test_create_batch_different_partitions_fails(self, chunk_service, sample_chunk):
        """Test batch creation with different partition keys raises error."""
        service, container = chunk_service
        
        # Create chunks with different partition keys
        chunk1 = sample_chunk
        chunk2 = DocumentChunk(
            chunk_id="different_chunk",
            document_id=uuid4(),  # Different document
            space_id=uuid4(),  # Different space
            tenant_id=uuid4(),  # Different tenant
            user_id=uuid4(),  # Different user
            text="Different partition",
            chunk_index=1,
            token_count=5,
            filename="other.pdf",
            language="en",
            embedding=[0.4] * 1536,
            created_at=datetime.now(timezone.utc),
        )
        
        with pytest.raises(ValueError, match="same partition key"):
            service.create_chunks_batch([chunk1, chunk2])


class TestChunkRetrieval:
    """Test chunk retrieval operations."""
    
    def test_get_chunk_success(self, chunk_service, sample_chunk):
        """Test retrieving a chunk by ID."""
        service, container = chunk_service
        container.read_item.return_value = sample_chunk.model_dump()
        
        result = service.get_chunk(
            chunk_id=sample_chunk.chunk_id,
            space_id=sample_chunk.space_id,
            tenant_id=sample_chunk.tenant_id,
            user_id=sample_chunk.user_id,
        )
        
        assert result.chunk_id == sample_chunk.chunk_id
        container.read_item.assert_called_once_with(
            item=sample_chunk.chunk_id,
            partition_key=[
                str(sample_chunk.space_id),
                str(sample_chunk.tenant_id),
                str(sample_chunk.user_id),
            ],
        )
    
    def test_get_chunk_not_found(self, chunk_service, sample_chunk):
        """Test retrieving non-existent chunk returns None."""
        service, container = chunk_service
        
        from azure.cosmos import exceptions
        container.read_item.side_effect = exceptions.CosmosResourceNotFoundError()
        
        result = service.get_chunk(
            chunk_id="nonexistent",
            space_id=sample_chunk.space_id,
            tenant_id=sample_chunk.tenant_id,
            user_id=sample_chunk.user_id,
        )
        
        assert result is None
    
    def test_list_chunks_by_document(self, chunk_service, sample_chunk):
        """Test listing all chunks for a document."""
        service, container = chunk_service
        
        # Mock 3 chunks
        chunks_data = [
            {**sample_chunk.model_dump(), "chunk_id": f"{sample_chunk.document_id}_chunk_{i}", "chunk_index": i}
            for i in range(1, 4)
        ]
        container.query_items.return_value = chunks_data
        
        result = service.list_chunks_by_document(
            document_id=sample_chunk.document_id,
            space_id=sample_chunk.space_id,
            tenant_id=sample_chunk.tenant_id,
            user_id=sample_chunk.user_id,
        )
        
        assert len(result) == 3
        assert all(isinstance(c, DocumentChunk) for c in result)
        container.query_items.assert_called_once()
    
    def test_list_chunks_by_space(self, chunk_service, sample_chunk):
        """Test listing chunks at space level (cross-partition query)."""
        service, container = chunk_service
        
        chunks_data = [sample_chunk.model_dump()]
        container.query_items.return_value = chunks_data
        
        result = service.list_chunks_by_space(
            space_id=sample_chunk.space_id,
        )
        
        assert len(result) == 1
        assert result[0].chunk_id == sample_chunk.chunk_id
        
        # Verify cross-partition query enabled
        call_args = container.query_items.call_args
        assert call_args[1]["enable_cross_partition_query"] is True


class TestChunkDeletion:
    """Test chunk deletion operations."""
    
    def test_delete_chunks_by_document(self, chunk_service, sample_chunk):
        """Test deleting all chunks for a document."""
        service, container = chunk_service
        
        # Mock chunks to delete
        chunks_data = [
            {**sample_chunk.model_dump(), "chunk_id": f"{sample_chunk.document_id}_chunk_{i}"}
            for i in range(1, 3)
        ]
        container.query_items.return_value = chunks_data
        
        service.delete_chunks_by_document(
            document_id=sample_chunk.document_id,
            space_id=sample_chunk.space_id,
            tenant_id=sample_chunk.tenant_id,
            user_id=sample_chunk.user_id,
        )
        
        # Verify delete called for each chunk
        assert container.delete_item.call_count == 2


class TestHPKValidation:
    """Test Hierarchical Partition Key validation."""
    
    def test_hpk_fields_required(self, chunk_service):
        """Test that all HPK fields are required."""
        service, container = chunk_service
        
        # Missing user_id
        with pytest.raises(Exception):  # Pydantic ValidationError
            DocumentChunk(
                chunk_id="test_chunk",
                document_id=uuid4(),
                space_id=uuid4(),
                tenant_id=uuid4(),
                # user_id missing
                text="Test",
                chunk_index=1,
                token_count=5,
                filename="test.pdf",
                language="en",
                embedding=[0.1] * 1536,
                created_at=datetime.now(timezone.utc),
            )
    
    def test_hpk_uuid_validation(self, sample_chunk):
        """Test that HPK fields are valid UUIDs."""
        assert isinstance(sample_chunk.space_id, UUID)
        assert isinstance(sample_chunk.tenant_id, UUID)
        assert isinstance(sample_chunk.user_id, UUID)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/eva_rag/services/chunk_service", "--cov-report=term"])
