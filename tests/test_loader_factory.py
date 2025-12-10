"""Tests for loader factory."""
from io import BytesIO

import pytest

from eva_rag.loaders.factory import LoaderFactory
from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.text_loader import TextLoader


def test_factory_returns_pdf_loader() -> None:
    """Test factory returns PDF loader for .pdf extension."""
    loader = LoaderFactory.get_loader("document.pdf")
    assert isinstance(loader, PDFLoader)


def test_factory_returns_text_loader_for_txt() -> None:
    """Test factory returns text loader for .txt extension."""
    loader = LoaderFactory.get_loader("document.txt")
    assert isinstance(loader, TextLoader)


def test_factory_returns_text_loader_for_md() -> None:
    """Test factory returns text loader for .md extension."""
    loader = LoaderFactory.get_loader("readme.md")
    assert isinstance(loader, TextLoader)


def test_factory_returns_html_loader_for_html() -> None:
    """Test factory returns HTML loader for .html extension."""
    loader = LoaderFactory.get_loader("page.html")
    assert isinstance(loader, HTMLLoader)


def test_factory_returns_html_loader_for_htm() -> None:
    """Test factory returns HTML loader for .htm extension."""
    loader = LoaderFactory.get_loader("page.htm")
    assert isinstance(loader, HTMLLoader)


def test_factory_case_insensitive() -> None:
    """Test factory handles uppercase extensions."""
    loader = LoaderFactory.get_loader("DOCUMENT.PDF")
    assert isinstance(loader, PDFLoader)


def test_factory_unsupported_extension() -> None:
    """Test factory raises error for unsupported extension."""
    with pytest.raises(ValueError, match="Unsupported file extension"):
        LoaderFactory.get_loader("file.xlsx")


def test_factory_no_extension() -> None:
    """Test factory raises error for file without extension."""
    with pytest.raises(ValueError, match="Unsupported file extension"):
        LoaderFactory.get_loader("noextension")


def test_factory_load_document(sample_text_content: str) -> None:
    """Test factory load_document method."""
    file_obj = BytesIO(sample_text_content.encode("utf-8"))
    
    result = LoaderFactory.load_document(file_obj, "test.txt")
    
    assert result.text
    assert result.page_count > 0


def test_factory_supported_extensions() -> None:
    """Test factory returns supported extensions list."""
    extensions = LoaderFactory.supported_extensions()
    
    assert ".pdf" in extensions
    assert ".docx" in extensions
    assert ".txt" in extensions
    assert ".md" in extensions
    assert ".html" in extensions
    assert ".htm" in extensions
