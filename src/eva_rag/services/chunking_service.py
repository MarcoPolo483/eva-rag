"""Text chunking service for splitting documents into semantic chunks."""
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken


@dataclass
class Chunk:
    """A text chunk with metadata."""
    
    text: str
    start_char: int
    end_char: int
    token_count: int
    chunk_index: int


class ChunkingService:
    """Service for chunking text into overlapping segments."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base",  # GPT-4, text-embedding-3-small
    ):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of tokens to overlap between chunks
            encoding_name: Tokenizer encoding (cl100k_base for OpenAI models)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        
        # LangChain text splitter with token-based splitting
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=encoding_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",  # Double newline (paragraphs)
                "\n",    # Single newline
                ". ",    # Sentence boundary
                "! ",    # Exclamation
                "? ",    # Question
                "; ",    # Semicolon
                ", ",    # Comma
                " ",     # Space
                "",      # Character-level fallback
            ],
            keep_separator=True,
        )
    
    def chunk_text(self, text: str) -> list[Chunk]:
        """
        Split text into semantic chunks with metadata.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of Chunk objects with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Split text using LangChain
        chunks = self.text_splitter.split_text(text)
        
        # Build Chunk objects with metadata
        result: list[Chunk] = []
        current_pos = 0
        
        for idx, chunk_text in enumerate(chunks):
            # Find chunk position in original text
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                # Fallback if exact match not found (shouldn't happen)
                start_pos = current_pos
            
            end_pos = start_pos + len(chunk_text)
            
            # Count tokens in this chunk
            token_count = len(self.encoding.encode(chunk_text))
            
            result.append(
                Chunk(
                    text=chunk_text.strip(),
                    start_char=start_pos,
                    end_char=end_pos,
                    token_count=token_count,
                    chunk_index=idx,
                )
            )
            
            current_pos = end_pos
        
        return result
    
    def estimate_chunk_count(self, text: str) -> int:
        """
        Estimate number of chunks for a given text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated chunk count
        """
        if not text:
            return 0
        
        token_count = len(self.encoding.encode(text))
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        
        # Calculate with overlap consideration
        return max(1, (token_count + effective_chunk_size - 1) // effective_chunk_size)
