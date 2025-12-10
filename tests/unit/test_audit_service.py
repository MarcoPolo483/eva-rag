"""
Unit tests for AuditService with mocked Cosmos DB.

Tests cover:
- Audit log creation with sequential numbering
- System-level hash chain
- Atomic counter for sequence numbers
- Chain verification
- Event filtering
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock, patch

from eva_rag.models.audit_log import AuditLog
from eva_rag.services.audit_service import AuditService


@pytest.fixture
def mock_cosmos_client():
    """Mock Cosmos DB client."""
    client = Mock()
    database = Mock()
    audit_container = Mock()
    counter_container = Mock()
    
    client.get_database_client.return_value = database
    
    def get_container(container_id):
        if container_id == "audit_counters":
            return counter_container
        return audit_container
    
    database.create_container_if_not_exists.side_effect = lambda **kwargs: (
        counter_container if kwargs["id"] == "audit_counters" else audit_container
    )
    database.get_container_client.side_effect = get_container
    
    return client, database, audit_container, counter_container


@pytest.fixture
def audit_service(mock_cosmos_client):
    """Create AuditService with mocked Cosmos DB."""
    client, database, audit_container, counter_container = mock_cosmos_client
    
    with patch('eva_rag.services.audit_service.CosmosClient') as mock_client_class:
        mock_client_class.return_value = client
        service = AuditService(cosmos_client=client, database_name="eva-rag")
        service.container = audit_container
        service.counter_container = counter_container
        return service, audit_container, counter_container


@pytest.fixture
def sample_audit_log():
    """Create sample AuditLog for testing."""
    return AuditLog(
        id=uuid4(),
        sequence_number=1,
        space_id=uuid4(),
        tenant_id=uuid4(),
        user_id=uuid4(),
        event_type="document.uploaded",
        event_category="data",
        event_data={"document_id": str(uuid4()), "filename": "test.pdf"},
        content_hash="hash_001",
        previous_hash="genesis",
    )


class TestSequentialNumbering:
    """Test atomic sequential numbering."""
    
    def test_get_next_sequence_first_time(self, audit_service):
        """Test getting sequence number when counter doesn't exist."""
        service, audit_container, counter_container = audit_service
        
        # Mock counter doesn't exist
        counter_container.read_item.side_effect = Exception("Not found")
        counter_container.create_item.return_value = {"id": "audit_sequence", "value": 1}
        
        seq = service._get_next_sequence_number()
        
        assert seq == 1
        counter_container.create_item.assert_called_once()
    
    def test_get_next_sequence_increments(self, audit_service):
        """Test sequence number increments."""
        service, audit_container, counter_container = audit_service
        
        # Mock existing counter
        counter_container.read_item.return_value = {
            "id": "audit_sequence",
            "value": 42,
            "_etag": "etag123",
        }
        counter_container.replace_item.return_value = {"value": 43}
        
        seq = service._get_next_sequence_number()
        
        assert seq == 43
        counter_container.replace_item.assert_called_once()


class TestAuditLogCreation:
    """Test audit log creation with hash chains."""
    
    def test_create_first_audit_log(self, audit_service, sample_audit_log):
        """Test creating first audit log (genesis)."""
        service, audit_container, counter_container = audit_service
        
        # Mock sequence number
        counter_container.read_item.side_effect = Exception("Not found")
        counter_container.create_item.return_value = {"value": 1}
        
        # Mock no previous logs
        audit_container.query_items.return_value = []
        audit_container.create_item.return_value = sample_audit_log.model_dump()
        
        result = service.create_audit_log(sample_audit_log)
        
        assert result.sequence_number == 1
        assert result.previous_hash == "genesis"
        assert result.content_hash is not None
        audit_container.create_item.assert_called_once()
    
    def test_create_chained_audit_log(self, audit_service, sample_audit_log):
        """Test creating audit log that chains to previous."""
        service, audit_container, counter_container = audit_service
        
        # Mock sequence number
        counter_container.read_item.return_value = {"id": "audit_sequence", "value": 5, "_etag": "etag"}
        counter_container.replace_item.return_value = {"value": 6}
        
        # Mock previous log
        previous_log = {
            **sample_audit_log.model_dump(),
            "sequence_number": 5,
            "content_hash": "previous_hash_xyz",
        }
        audit_container.query_items.return_value = [previous_log]
        audit_container.create_item.return_value = sample_audit_log.model_dump()
        
        result = service.create_audit_log(sample_audit_log)
        
        assert result.sequence_number == 6
        assert result.previous_hash == "previous_hash_xyz"
        audit_container.create_item.assert_called_once()
    
    def test_hash_computation(self, audit_service, sample_audit_log):
        """Test content hash computation."""
        service, audit_container, counter_container = audit_service
        
        hash1 = service._compute_content_hash(sample_audit_log)
        
        # Same log should produce same hash
        hash2 = service._compute_content_hash(sample_audit_log)
        assert hash1 == hash2
        
        # Modified log should produce different hash
        sample_audit_log.event_type = "document.deleted"
        hash3 = service._compute_content_hash(sample_audit_log)
        assert hash1 != hash3


class TestAuditLogRetrieval:
    """Test audit log retrieval operations."""
    
    def test_get_audit_log(self, audit_service, sample_audit_log):
        """Test retrieving audit log by sequence number."""
        service, audit_container, counter_container = audit_service
        audit_container.read_item.return_value = sample_audit_log.model_dump()
        
        result = service.get_audit_log(sequence_number=1)
        
        assert result.sequence_number == 1
        audit_container.read_item.assert_called_once_with(
            item="1",
            partition_key=1,
        )
    
    def test_list_audit_logs_filtered(self, audit_service, sample_audit_log):
        """Test listing audit logs with filters."""
        service, audit_container, counter_container = audit_service
        
        logs_data = [sample_audit_log.model_dump() for _ in range(5)]
        audit_container.query_items.return_value = logs_data
        
        result = service.list_audit_logs(
            event_type="document.uploaded",
            event_category="data",
        )
        
        assert len(result) == 5
        audit_container.query_items.assert_called_once()


class TestChainVerification:
    """Test system-level hash chain verification."""
    
    def test_verify_valid_chain(self, audit_service, sample_audit_log):
        """Test verification of valid audit chain."""
        service, audit_container, counter_container = audit_service
        
        # Create chain: log1 -> log2 -> log3
        log1 = sample_audit_log.model_dump()
        log1["sequence_number"] = 1
        log1["content_hash"] = "hash_001"
        log1["previous_hash"] = "genesis"
        
        log2 = sample_audit_log.model_dump()
        log2["sequence_number"] = 2
        log2["content_hash"] = "hash_002"
        log2["previous_hash"] = "hash_001"
        
        log3 = sample_audit_log.model_dump()
        log3["sequence_number"] = 3
        log3["content_hash"] = "hash_003"
        log3["previous_hash"] = "hash_002"
        
        audit_container.query_items.return_value = [log1, log2, log3]
        
        # Mock hash computation to return stored hashes
        def mock_hash(log):
            return log.content_hash
        
        with patch.object(service, '_compute_content_hash', side_effect=mock_hash):
            is_valid, error = service.verify_audit_chain(count=3)
        
        assert is_valid is True
        assert error == ""
    
    def test_verify_broken_chain(self, audit_service, sample_audit_log):
        """Test detection of broken audit chain."""
        service, audit_container, counter_container = audit_service
        
        # Create chain with broken link
        log1 = sample_audit_log.model_dump()
        log1["sequence_number"] = 1
        log1["content_hash"] = "hash_001"
        log1["previous_hash"] = "genesis"
        
        log2 = sample_audit_log.model_dump()
        log2["sequence_number"] = 2
        log2["content_hash"] = "hash_002"
        log2["previous_hash"] = "WRONG_HASH"  # Broken!
        
        audit_container.query_items.return_value = [log1, log2]
        
        is_valid, error = service.verify_audit_chain(count=2)
        
        assert is_valid is False
        assert "Hash chain broken" in error


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/eva_rag/services/audit_service", "--cov-report=term"])
