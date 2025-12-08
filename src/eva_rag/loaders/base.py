"""Base document loader interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class ExtractedDocument:
    """Extracted document content with metadata."""
    
    text: str
    page_count: int
    language: str | None = None
    metadata: dict[str, str | int] | None = None


class DocumentLoader(ABC):
    """Base class for document loaders."""
    
    @abstractmethod
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Load and extract text from a document file.
        
        Args:
            file: Binary file object
            filename: Original filename
            
        Returns:
            Extracted document with text and metadata
            
        Raises:
            ValueError: If file format is invalid or unsupported
        """
        pass
