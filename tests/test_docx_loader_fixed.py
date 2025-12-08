"""Tests for DOCX document loader."""
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from eva_rag.loaders.docx_loader import DOCXLoader


@pytest.fixture
def mock_docx_document():
    """Mock python-docx Document."""
    with patch("eva_rag.loaders.docx_loader.Document") as mock:
        yield mock


def test_docx_loader_basic(mock_docx_document: MagicMock) -> None:
    """Test basic DOCX text extraction."""
    # Setup mock document with paragraphs
    mock_doc = MagicMock()
    mock_p1 = MagicMock()
    mock_p1.text = "First paragraph."
    mock_p2 = MagicMock()
    mock_p2.text = "Second paragraph."
    mock_doc.paragraphs = [mock_p1, mock_p2]
    
    # Mock core properties
    mock_doc.core_properties.title = "Test Doc"
    mock_doc.core_properties.author = "Test Author"
    mock_doc.core_properties.subject = None
    
    mock_docx_document.return_value = mock_doc
    
    # Load document
    loader = DOCXLoader()
    result = loader.load(BytesIO(b"fake docx"), "test.docx")
    
    # Assertions
    assert "First paragraph" in result.text
    assert "Second paragraph" in result.text
    assert result.metadata["title"] == "Test Doc"
    assert result.metadata["author"] == "Test Author"
    assert result.page_count == 2


def test_docx_loader_empty_paragraphs(mock_docx_document: MagicMock) -> None:
    """Test DOCX with no paragraphs raises error."""
    mock_doc = MagicMock()
    mock_doc.paragraphs = []
    mock_docx_document.return_value = mock_doc
    
    loader = DOCXLoader()
    
    with pytest.raises(ValueError, match="contains no paragraphs"):
        loader.load(BytesIO(b"empty docx"), "empty.docx")


def test_docx_loader_unicode(mock_docx_document: MagicMock) -> None:
    """Test DOCX with Unicode characters."""
    mock_doc = MagicMock()
    mock_p = MagicMock()
    mock_p.text = "Français: café, naïve"
    mock_doc.paragraphs = [mock_p]
    mock_doc.core_properties.title = None
    mock_doc.core_properties.author = None
    mock_doc.core_properties.subject = None
    
    mock_docx_document.return_value = mock_doc
    
    loader = DOCXLoader()
    result = loader.load(BytesIO(b"unicode docx"), "unicode.docx")
    
    assert "café" in result.text
    assert "naïve" in result.text


def test_docx_loader_many_paragraphs(mock_docx_document: MagicMock) -> None:
    """Test DOCX with many paragraphs."""
    mock_doc = MagicMock()
    paragraphs = []
    for i in range(50):
        mock_p = MagicMock()
        mock_p.text = f"Paragraph {i}"
        paragraphs.append(mock_p)
    
    mock_doc.paragraphs = paragraphs
    mock_doc.core_properties.title = "Long Doc"
    mock_doc.core_properties.author = None
    mock_doc.core_properties.subject = None
    
    mock_docx_document.return_value = mock_doc
    
    loader = DOCXLoader()
    result = loader.load(BytesIO(b"long docx"), "long.docx")
    
    assert "Paragraph 0" in result.text
    assert "Paragraph 49" in result.text
    assert result.page_count == 50


def test_docx_loader_invalid_file(mock_docx_document: MagicMock) -> None:
    """Test DOCX loader with invalid file."""
    mock_docx_document.side_effect = Exception("Invalid DOCX format")
    
    loader = DOCXLoader()
    
    with pytest.raises(Exception, match="Invalid DOCX format"):
        loader.load(BytesIO(b"not a docx"), "bad.docx")


def test_docx_loader_whitespace_only_paragraphs(mock_docx_document: MagicMock) -> None:
    """Test DOCX with only whitespace paragraphs."""
    mock_doc = MagicMock()
    mock_p1 = MagicMock()
    mock_p1.text = "   "
    mock_p2 = MagicMock()
    mock_p2.text = "\n\t\n"
    mock_doc.paragraphs = [mock_p1, mock_p2]
    
    mock_docx_document.return_value = mock_doc
    
    loader = DOCXLoader()
    
    with pytest.raises(ValueError, match="contains no extractable text"):
        loader.load(BytesIO(b"whitespace docx"), "whitespace.docx")
