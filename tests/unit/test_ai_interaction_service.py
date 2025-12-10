"""
Unit tests for AIInteractionService with mocked Cosmos DB.

Tests cover:
- Interaction creation with hash chain
- Hash computation
- Chain verification
- Listing interactions by user
- Genesis hash handling
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import Mock, patch

from eva_rag.models.ai_interaction import AIInteraction, ChunkReference, Citation
from eva_rag.services.ai_interaction_service import AIInteractionService


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
def interaction_service(mock_cosmos_client):
    """Create AIInteractionService with mocked Cosmos DB."""
    client, database, container = mock_cosmos_client
    
    with patch('eva_rag.services.ai_interaction_service.CosmosClient') as mock_client_class:
        mock_client_class.return_value = client
        service = AIInteractionService()
        service.container = container
        return service, container


@pytest.fixture
def sample_interaction():
    """Create sample AIInteraction for testing."""
    space_id = uuid4()
    tenant_id = uuid4()
    user_id = uuid4()
    
    return AIInteraction(
        id=uuid4(),
        space_id=space_id,
        tenant_id=tenant_id,
        user_id=user_id,
        query="What is the privacy policy?",
        query_language="en",
        response="The privacy policy states...",
        response_language="en",
        chunks_used=[
            ChunkReference(
                chunk_id="doc123_chunk5",
                document_id=uuid4(),
                filename="privacy.pdf",
                text_snippet="Section 5...",
                relevance_score=0.95,
            )
        ],
        citations=[
            Citation(
                chunk_id="doc123_chunk5",
                document_id=uuid4(),
                filename="privacy.pdf",
                quote="Section 5 states...",
                position_in_response=0,
            )
        ],
        model_name="gpt-4",
        model_version="0613",
        latency_ms=250,
        token_count_input=15,
        token_count_output=25,
        content_hash="placeholder",
        previous_hash="genesis",
    )


class TestInteractionCreation:
    """Test AI interaction creation with hash chains."""
    
    def test_create_first_interaction(self, interaction_service, sample_interaction):
        """Test creating first interaction (genesis)."""
        service, container = interaction_service
        
        # Mock empty list (no previous interactions)
        container.query_items.return_value = []
        container.create_item.return_value = sample_interaction.model_dump()
        
        result = service.create_interaction(sample_interaction)
        
        assert result.previous_hash == "genesis"
        assert result.content_hash is not None
        container.create_item.assert_called_once()
    
    def test_create_chained_interaction(self, interaction_service, sample_interaction):
        """Test creating interaction that chains to previous."""
        service, container = interaction_service
        
        # Mock previous interaction
        previous_interaction = {
            **sample_interaction.model_dump(),
            "content_hash": "previous_hash_abc123",
        }
        container.query_items.return_value = [previous_interaction]
        container.create_item.return_value = sample_interaction.model_dump()
        
        result = service.create_interaction(sample_interaction)
        
        # Should chain to previous interaction's content_hash
        assert result.previous_hash == "previous_hash_abc123"
        container.create_item.assert_called_once()
    
    def test_hash_computation(self, interaction_service, sample_interaction):
        """Test content hash is computed correctly."""
        service, container = interaction_service
        
        hash1 = service._compute_content_hash(sample_interaction)
        
        # Same interaction should produce same hash
        hash2 = service._compute_content_hash(sample_interaction)
        assert hash1 == hash2
        
        # Modified interaction should produce different hash
        sample_interaction.query = "Different query"
        hash3 = service._compute_content_hash(sample_interaction)
        assert hash1 != hash3


class TestInteractionRetrieval:
    """Test interaction retrieval operations."""
    
    def test_get_interaction(self, interaction_service, sample_interaction):
        """Test retrieving interaction by ID."""
        service, container = interaction_service
        container.read_item.return_value = sample_interaction.model_dump()
        
        result = service.get_interaction(
            interaction_id=sample_interaction.id,
            space_id=sample_interaction.space_id,
            tenant_id=sample_interaction.tenant_id,
            user_id=sample_interaction.user_id,
        )
        
        assert result.id == sample_interaction.id
        container.read_item.assert_called_once()
    
    def test_list_interactions_by_user(self, interaction_service, sample_interaction):
        """Test listing interactions for a user."""
        service, container = interaction_service
        
        interactions_data = [sample_interaction.model_dump() for _ in range(3)]
        container.query_items.return_value = interactions_data
        
        result = service.list_interactions_by_user(
            space_id=sample_interaction.space_id,
            tenant_id=sample_interaction.tenant_id,
            user_id=sample_interaction.user_id,
        )
        
        assert len(result) == 3
        container.query_items.assert_called_once()


class TestHashChainVerification:
    """Test hash chain integrity verification."""
    
    def test_verify_valid_chain(self, interaction_service, sample_interaction):
        """Test verification of valid hash chain."""
        service, container = interaction_service
        
        # Create chain: interaction1 -> interaction2 -> interaction3
        interaction1 = sample_interaction.model_dump()
        interaction1["content_hash"] = "hash_001"
        interaction1["previous_hash"] = "genesis"
        
        interaction2 = sample_interaction.model_dump()
        interaction2["id"] = str(uuid4())
        interaction2["content_hash"] = "hash_002"
        interaction2["previous_hash"] = "hash_001"
        
        interaction3 = sample_interaction.model_dump()
        interaction3["id"] = str(uuid4())
        interaction3["content_hash"] = "hash_003"
        interaction3["previous_hash"] = "hash_002"
        
        # Mock query returning chain in order
        container.query_items.return_value = [interaction1, interaction2, interaction3]
        
        # Mock hash computation to return stored hashes
        def mock_hash(interaction):
            return interaction.content_hash
        
        with patch.object(service, '_compute_content_hash', side_effect=mock_hash):
            is_valid, error = service.verify_hash_chain(
                space_id=sample_interaction.space_id,
                tenant_id=sample_interaction.tenant_id,
                user_id=sample_interaction.user_id,
            )
        
        assert is_valid is True
        assert error == ""
    
    def test_verify_broken_chain(self, interaction_service, sample_interaction):
        """Test detection of broken hash chain."""
        service, container = interaction_service
        
        # Create chain with broken link
        interaction1 = sample_interaction.model_dump()
        interaction1["content_hash"] = "hash_001"
        interaction1["previous_hash"] = "genesis"
        
        interaction2 = sample_interaction.model_dump()
        interaction2["id"] = str(uuid4())
        interaction2["content_hash"] = "hash_002"
        interaction2["previous_hash"] = "WRONG_HASH"  # Broken link!
        
        container.query_items.return_value = [interaction1, interaction2]
        
        is_valid, error = service.verify_hash_chain(
            space_id=sample_interaction.space_id,
            tenant_id=sample_interaction.tenant_id,
            user_id=sample_interaction.user_id,
        )
        
        assert is_valid is False
        assert "Hash chain broken" in error


class TestProvenance:
    """Test AI provenance tracking."""
    
    def test_interaction_has_chunks_used(self, sample_interaction):
        """Test interaction records chunks used."""
        assert len(sample_interaction.chunks_used) == 1
        assert sample_interaction.chunks_used[0].filename == "privacy.pdf"
    
    def test_interaction_has_citations(self, sample_interaction):
        """Test interaction records citations."""
        assert len(sample_interaction.citations) == 1
        assert sample_interaction.citations[0].quote == "Section 5 states..."


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/eva_rag/services/ai_interaction_service", "--cov-report=term"])
