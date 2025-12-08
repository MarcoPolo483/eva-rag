"""Tests for embedding service."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from eva_rag.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_azure_openai():
    """Mock Azure OpenAI client."""
    with patch('eva_rag.services.embedding_service.AzureOpenAI') as mock:
        # Mock the embeddings.create response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        
        mock_client = Mock()
        mock_client.embeddings.create.return_value = mock_response
        mock.return_value = mock_client
        
        yield mock_client


def test_embedding_service_initialization(mock_azure_openai):
    """Test embedding service initializes correctly."""
    service = EmbeddingService()
    
    assert service.client is not None
    assert service.model == "text-embedding-3-small"
    assert service.dimensions == 1536


def test_generate_embedding_single_text(mock_azure_openai):
    """Test generating embedding for single text."""
    service = EmbeddingService()
    
    # Mock response
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.5] * 1536)]
    mock_azure_openai.embeddings.create.return_value = mock_response
    
    embedding = service.generate_embedding("Test text")
    
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)
    mock_azure_openai.embeddings.create.assert_called_once()


def test_generate_embedding_empty_text():
    """Test error handling for empty text."""
    service = EmbeddingService()
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.generate_embedding("")
    
    with pytest.raises(ValueError, match="Text cannot be empty"):
        service.generate_embedding("   ")


def test_generate_embeddings_batch(mock_azure_openai):
    """Test batch embedding generation."""
    service = EmbeddingService()
    
    # Mock response for batch
    mock_response = Mock()
    mock_response.data = [
        Mock(embedding=[0.1] * 1536),
        Mock(embedding=[0.2] * 1536),
        Mock(embedding=[0.3] * 1536),
    ]
    mock_azure_openai.embeddings.create.return_value = mock_response
    
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = service.generate_embeddings_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)
    mock_azure_openai.embeddings.create.assert_called_once()


def test_generate_embeddings_batch_empty_list():
    """Test batch with empty list."""
    service = EmbeddingService()
    embeddings = service.generate_embeddings_batch([])
    assert embeddings == []


def test_generate_embeddings_batch_filters_empty_texts(mock_azure_openai):
    """Test batch generation filters out empty texts."""
    service = EmbeddingService()
    
    # Mock response for valid texts only
    mock_response = Mock()
    mock_response.data = [
        Mock(embedding=[0.1] * 1536),
        Mock(embedding=[0.2] * 1536),
    ]
    mock_azure_openai.embeddings.create.return_value = mock_response
    
    texts = ["Valid text 1", "", "Valid text 2", "   "]
    embeddings = service.generate_embeddings_batch(texts)
    
    # Should return 2 embeddings (filtered out 2 empty texts)
    assert len(embeddings) == 2


def test_generate_embeddings_batch_all_empty_texts():
    """Test error when all texts are empty."""
    service = EmbeddingService()
    
    with pytest.raises(ValueError, match="All texts are empty"):
        service.generate_embeddings_batch(["", "   ", ""])


def test_generate_embeddings_batch_large_batch(mock_azure_openai):
    """Test batch processing with large number of texts."""
    service = EmbeddingService()
    
    # Mock responses for multiple batches
    def mock_create(**kwargs):
        input_texts = kwargs['input']
        num_texts = len(input_texts) if isinstance(input_texts, list) else 1
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536) for _ in range(num_texts)]
        return mock_response
    
    mock_azure_openai.embeddings.create.side_effect = mock_create
    
    # Create 250 texts (should be split into 3 batches with batch_size=100)
    texts = [f"Text {i}" for i in range(250)]
    embeddings = service.generate_embeddings_batch(texts, batch_size=100)
    
    assert len(embeddings) == 250
    # Should be called 3 times (100, 100, 50)
    assert mock_azure_openai.embeddings.create.call_count == 3


def test_generate_embeddings_batch_custom_batch_size(mock_azure_openai):
    """Test custom batch size."""
    service = EmbeddingService()
    
    def mock_create(**kwargs):
        input_texts = kwargs['input']
        num_texts = len(input_texts) if isinstance(input_texts, list) else 1
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536) for _ in range(num_texts)]
        return mock_response
    
    mock_azure_openai.embeddings.create.side_effect = mock_create
    
    texts = [f"Text {i}" for i in range(15)]
    embeddings = service.generate_embeddings_batch(texts, batch_size=5)
    
    assert len(embeddings) == 15
    # Should be called 3 times (5, 5, 5)
    assert mock_azure_openai.embeddings.create.call_count == 3


def test_generate_embedding_retry_on_failure(mock_azure_openai):
    """Test retry logic on API failure."""
    service = EmbeddingService()
    
    # Mock to fail twice, then succeed
    call_count = 0
    def mock_create_with_retries(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("API Error")
        
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        return mock_response
    
    mock_azure_openai.embeddings.create.side_effect = mock_create_with_retries
    
    # Should succeed after retries
    embedding = service.generate_embedding("Test")
    assert len(embedding) == 1536
    assert call_count == 3


def test_generate_embedding_max_retries_exceeded(mock_azure_openai):
    """Test failure after max retries."""
    service = EmbeddingService()
    
    # Mock to always fail
    mock_azure_openai.embeddings.create.side_effect = Exception("Persistent API Error")
    
    with pytest.raises(Exception, match="Persistent API Error"):
        service.generate_embedding("Test")


def test_estimate_tokens():
    """Test token estimation."""
    service = EmbeddingService()
    
    # Rough estimate: 1 token ≈ 4 characters
    assert service.estimate_tokens("") == 0
    assert service.estimate_tokens("test") == 1  # 4 chars
    assert service.estimate_tokens("this is a test") == 3  # 14 chars
    assert service.estimate_tokens("a" * 400) == 100  # 400 chars


def test_generate_embeddings_batch_maintains_order(mock_azure_openai):
    """Test that batch generation maintains input order."""
    service = EmbeddingService()
    
    # Mock with distinct embeddings
    def mock_create(**kwargs):
        input_texts = kwargs['input']
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[float(i)] * 1536) 
            for i, _ in enumerate(input_texts)
        ]
        return mock_response
    
    mock_azure_openai.embeddings.create.side_effect = mock_create
    
    texts = ["First", "Second", "Third"]
    embeddings = service.generate_embeddings_batch(texts)
    
    # Check order is maintained
    assert embeddings[0][0] == 0.0
    assert embeddings[1][0] == 1.0
    assert embeddings[2][0] == 2.0


def test_generate_embedding_strips_whitespace(mock_azure_openai):
    """Test that text is stripped before embedding."""
    service = EmbeddingService()
    
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_azure_openai.embeddings.create.return_value = mock_response
    
    service.generate_embedding("  Test with spaces  ")
    
    # Check that stripped text was passed to API
    call_args = mock_azure_openai.embeddings.create.call_args
    assert call_args[1]['input'] == "Test with spaces"
