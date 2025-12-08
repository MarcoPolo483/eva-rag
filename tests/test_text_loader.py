"""Tests for text loader."""
from io import BytesIO

import pytest

from eva_rag.loaders.text_loader import TextLoader


def test_text_loader_extracts_text(sample_text_content: str) -> None:
    """Test text loader extracts text successfully."""
    loader = TextLoader()
    file_obj = BytesIO(sample_text_content.encode("utf-8"))
    
    result = loader.load(file_obj, "test.txt")
    
    assert result.text == sample_text_content.strip()
    assert result.page_count > 0
    assert "sample document" in result.text


def test_text_loader_empty_file() -> None:
    """Test text loader handles empty file."""
    loader = TextLoader()
    file_obj = BytesIO(b"")
    
    with pytest.raises(ValueError, match="empty"):
        loader.load(file_obj, "empty.txt")


def test_text_loader_whitespace_only() -> None:
    """Test text loader handles whitespace-only file."""
    loader = TextLoader()
    file_obj = BytesIO(b"   \n\n   \t  ")
    
    with pytest.raises(ValueError, match="empty"):
        loader.load(file_obj, "whitespace.txt")


def test_text_loader_handles_utf8() -> None:
    """Test text loader handles UTF-8 encoding."""
    loader = TextLoader()
    text = "Français: Bonjour! 你好"
    file_obj = BytesIO(text.encode("utf-8"))
    
    result = loader.load(file_obj, "utf8.txt")
    
    assert result.text == text


def test_text_loader_handles_latin1() -> None:
    """Test text loader fallback to latin-1 encoding."""
    loader = TextLoader()
    text = "Café résumé"
    file_obj = BytesIO(text.encode("latin-1"))
    
    result = loader.load(file_obj, "latin1.txt")
    
    assert "Caf" in result.text
