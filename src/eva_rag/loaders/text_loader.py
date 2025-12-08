"""Plain text document loader."""
from typing import BinaryIO

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class TextLoader(DocumentLoader):
    """Load and extract text from plain text files (TXT, MD)."""
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Extract text from plain text file.
        
        Args:
            file: Binary text file object
            filename: Original filename
            
        Returns:
            Extracted document with text and line count
            
        Raises:
            ValueError: If file is empty or cannot be decoded
        """
        try:
            # Read and decode text
            text_bytes = file.read()
            
            # Try UTF-8 first, then fallback to latin-1
            try:
                text = text_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = text_bytes.decode("latin-1")
            
            text = text.strip()
            
            if not text:
                raise ValueError(f"Text file '{filename}' is empty")
            
            # Count lines as proxy for page count
            line_count = len([line for line in text.split("\n") if line.strip()])
            
            return ExtractedDocument(
                text=text,
                page_count=max(1, line_count // 50),  # Approximate pages (50 lines/page)
                metadata={},
            )
            
        except Exception as e:
            raise ValueError(f"Failed to load text file '{filename}': {str(e)}") from e
