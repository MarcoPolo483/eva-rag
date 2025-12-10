"""PDF document loader using pypdf with advanced table extraction."""
from io import BytesIO
from typing import BinaryIO

from pypdf import PdfReader

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class PDFLoader(DocumentLoader):
    """Load and extract text from PDF files with table-aware layout preservation."""
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Extract text from PDF file with layout-preserving extraction.
        
        Args:
            file: Binary PDF file object
            filename: Original filename
            
        Returns:
            Extracted document with text and page count
            
        Raises:
            ValueError: If PDF is invalid or empty
        """
        try:
            # Read PDF
            pdf_bytes = file.read()
            pdf_file = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            if len(reader.pages) == 0:
                raise ValueError(f"PDF file '{filename}' contains no pages")
            
            # Extract text from all pages with layout mode for tables
            text_parts: list[str] = []
            for page_num, page in enumerate(reader.pages, start=1):
                # Use layout mode to preserve table structure
                # This mode maintains spacing and alignment better for tabular data
                page_text = page.extract_text(extraction_mode="layout")
                
                # Fallback to plain extraction if layout mode fails
                if not page_text.strip():
                    page_text = page.extract_text()
                
                # Add page marker even if no text (for minimal PDFs in tests)
                if page_text.strip():
                    text_parts.append(f"[PAGE {page_num}]\n{page_text}")
                else:
                    text_parts.append(f"[PAGE {page_num}]\n")
            
            full_text = "\n\n".join(text_parts)
            
            # Extract metadata
            metadata = {}
            if reader.metadata:
                if reader.metadata.title:
                    metadata["title"] = reader.metadata.title
                if reader.metadata.author:
                    metadata["author"] = reader.metadata.author
            
            return ExtractedDocument(
                text=full_text,
                page_count=len(reader.pages),
                metadata=metadata,
            )
            
        except Exception as e:
            raise ValueError(f"Failed to load PDF '{filename}': {str(e)}") from e
