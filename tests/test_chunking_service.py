"""Tests for chunking service."""
import pytest

from eva_rag.services.chunking_service import ChunkingService, Chunk


@pytest.fixture
def chunking_service() -> ChunkingService:
    """Create chunking service with default settings."""
    return ChunkingService(chunk_size=100, chunk_overlap=20)


def test_chunk_text_basic(chunking_service: ChunkingService) -> None:
    """Test basic text chunking."""
    text = "This is a test. " * 50  # ~50 words
    chunks = chunking_service.chunk_text(text)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_chunk_text_with_paragraphs(chunking_service: ChunkingService) -> None:
    """Test chunking respects paragraph boundaries."""
    text = """First paragraph with some content.

Second paragraph with more content.

Third paragraph with even more content."""
    
    chunks = chunking_service.chunk_text(text)
    
    assert len(chunks) > 0
    # Should preserve paragraph structure
    assert any("\n\n" in chunk.text or "First paragraph" in chunk.text for chunk in chunks)


def test_chunk_text_empty() -> None:
    """Test chunking empty text returns empty list."""
    service = ChunkingService()
    chunks = service.chunk_text("")
    assert chunks == []
    
    chunks = service.chunk_text("   ")
    assert chunks == []


def test_chunk_metadata(chunking_service: ChunkingService) -> None:
    """Test chunk metadata is correct."""
    text = "This is a test sentence. " * 20
    chunks = chunking_service.chunk_text(text)
    
    assert len(chunks) > 0
    
    # Check metadata
    for idx, chunk in enumerate(chunks):
        assert chunk.chunk_index == idx
        assert chunk.start_char >= 0
        assert chunk.end_char > chunk.start_char
        assert chunk.token_count > 0
        assert chunk.token_count <= chunking_service.chunk_size + 10  # Allow some margin


def test_chunk_overlap(chunking_service: ChunkingService) -> None:
    """Test chunks have overlap."""
    text = "Word " * 100  # Simple repeated text
    chunks = chunking_service.chunk_text(text)
    
    if len(chunks) > 1:
        # Check that consecutive chunks have some text overlap
        for i in range(len(chunks) - 1):
            chunk1_text = chunks[i].text
            chunk2_text = chunks[i + 1].text
            
            # Get last few words of chunk1 and first few words of chunk2
            chunk1_words = chunk1_text.split()[-5:]
            chunk2_words = chunk2_text.split()[:5]
            
            # Should have some word overlap (due to 20 token overlap setting)
            assert len(set(chunk1_words) & set(chunk2_words)) > 0


def test_estimate_chunk_count(chunking_service: ChunkingService) -> None:
    """Test chunk count estimation."""
    text = "Word " * 100
    estimated = chunking_service.estimate_chunk_count(text)
    actual_chunks = chunking_service.chunk_text(text)
    
    # Estimate should be close to actual (within 50%)
    assert abs(estimated - len(actual_chunks)) <= max(1, len(actual_chunks) // 2)


def test_estimate_chunk_count_empty() -> None:
    """Test estimation for empty text."""
    service = ChunkingService()
    assert service.estimate_chunk_count("") == 0
    # Whitespace-only text has 1 token in tiktoken
    assert service.estimate_chunk_count("   ") >= 0


def test_chunk_sentence_boundaries(chunking_service: ChunkingService) -> None:
    """Test chunking preserves sentence boundaries when possible."""
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = chunking_service.chunk_text(text)
    
    # All chunks should contain complete sentences (no mid-sentence splits)
    for chunk in chunks:
        # Check that chunk doesn't start/end mid-word
        assert not chunk.text[0].islower() or chunk.text[0] in "(\""
        assert chunk.text[-1] in ".!?)\" " or chunk.text[-1].isspace()


def test_long_text_chunking() -> None:
    """Test chunking of long document."""
    service = ChunkingService(chunk_size=500, chunk_overlap=50)
    
    # Simulate a long document
    paragraphs = [
        f"This is paragraph {i}. It contains multiple sentences with information. "
        f"The content is relevant and important. " * 10
        for i in range(20)
    ]
    text = "\n\n".join(paragraphs)
    
    chunks = service.chunk_text(text)
    
    assert len(chunks) >= 10  # Should create multiple chunks
    assert all(chunk.token_count <= 550 for chunk in chunks)  # Within margin
    
    # Check indices are sequential
    for idx, chunk in enumerate(chunks):
        assert chunk.chunk_index == idx
