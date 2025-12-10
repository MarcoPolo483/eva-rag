"""Document loader factory."""
from pathlib import Path
from typing import BinaryIO

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument
from eva_rag.loaders.csv_loader import CSVLoader
from eva_rag.loaders.docx_loader import DOCXLoader
from eva_rag.loaders.excel_loader import ExcelLoader
from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.mpp_loader import MSProjectLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.pptx_loader import PowerPointLoader
from eva_rag.loaders.text_loader import TextLoader
from eva_rag.loaders.xml_loader import XMLLoader


class LoaderFactory:
    """Factory for creating document loaders based on file extension."""
    
    _loaders: dict[str, type[DocumentLoader]] = {
        ".pdf": PDFLoader,
        ".docx": DOCXLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
        ".html": HTMLLoader,
        ".htm": HTMLLoader,
        ".xml": XMLLoader,
        ".csv": CSVLoader,
        ".xlsx": ExcelLoader,
        ".xls": ExcelLoader,
        ".pptx": PowerPointLoader,
        ".ppt": PowerPointLoader,
        ".mpp": MSProjectLoader,  # MS Project XML format
    }
    
    @classmethod
    def get_loader(cls, filename: str) -> DocumentLoader:
        """
        Get appropriate loader for file extension.
        
        Args:
            filename: Name of file
            
        Returns:
            Document loader instance
            
        Raises:
            ValueError: If file extension is not supported
        """
        ext = Path(filename).suffix.lower()
        
        loader_class = cls._loaders.get(ext)
        if not loader_class:
            supported = ", ".join(cls._loaders.keys())
            raise ValueError(
                f"Unsupported file extension '{ext}'. "
                f"Supported extensions: {supported}"
            )
        
        return loader_class()
    
    @classmethod
    def load_document(cls, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Load document using appropriate loader.
        
        Args:
            file: Binary file object
            filename: Original filename
            
        Returns:
            Extracted document with text and metadata
            
        Raises:
            ValueError: If file extension is unsupported or loading fails
        """
        loader = cls.get_loader(filename)
        return loader.load(file, filename)
    
    @classmethod
    def supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions."""
        return list(cls._loaders.keys())
