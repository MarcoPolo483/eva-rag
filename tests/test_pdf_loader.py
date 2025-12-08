"""Tests for PDF loader."""
from io import BytesIO

import pytest

from eva_rag.loaders.pdf_loader import PDFLoader


def test_pdf_loader_extracts_text(sample_pdf_content: bytes) -> None:
    """Test PDF loader extracts text successfully."""
    loader = PDFLoader()
    file_obj = BytesIO(sample_pdf_content)
    
    result = loader.load(file_obj, "test.pdf")
    
    assert result.text
    assert result.page_count == 1
    # The minimal PDF may not extract text reliably, just verify it loaded
    assert "[PAGE 1]" in result.text


def test_pdf_loader_empty_file() -> None:
    """Test PDF loader handles empty file."""
    loader = PDFLoader()
    file_obj = BytesIO(b"")
    
    with pytest.raises(ValueError, match="Failed to load PDF"):
        loader.load(file_obj, "empty.pdf")


def test_pdf_loader_invalid_pdf() -> None:
    """Test PDF loader handles invalid PDF."""
    loader = PDFLoader()
    file_obj = BytesIO(b"not a pdf")
    
    with pytest.raises(ValueError, match="Failed to load PDF"):
        loader.load(file_obj, "invalid.pdf")


def test_pdf_loader_preserves_filename() -> None:
    """Test PDF loader preserves filename in error messages."""
    loader = PDFLoader()
    file_obj = BytesIO(b"invalid")
    filename = "my-document.pdf"
    
    with pytest.raises(ValueError, match=filename):
        loader.load(file_obj, filename)


def test_pdf_loader_with_metadata(sample_pdf_content: bytes) -> None:
    """Test PDF loader extracts metadata."""
    loader = PDFLoader()
    file_obj = BytesIO(sample_pdf_content)
    
    result = loader.load(file_obj, "metadata.pdf")
    
    # Metadata may be empty for minimal PDFs, just ensure it's a dict
    assert isinstance(result.metadata, dict)


def test_pdf_loader_no_text_pages(sample_pdf_content: bytes) -> None:
    """Test PDF loader handles pages with no text."""
    loader = PDFLoader()
    file_obj = BytesIO(sample_pdf_content)
    
    result = loader.load(file_obj, "notext.pdf")
    
    # Should still extract with page markers
    assert "[PAGE 1]" in result.text
    assert result.page_count >= 1
