"""Embedding service using Azure OpenAI."""
from typing import Sequence

from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from eva_rag.config import settings


class EmbeddingService:
    """Service for generating text embeddings via Azure OpenAI."""
    
    def __init__(self):
        """Initialize embedding service with Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version="2024-02-01",
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.openai_embedding_model
        self.dimensions = settings.openai_embedding_dimensions
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector (1536 dimensions for text-embedding-3-small)
            
        Raises:
            Exception: If Azure OpenAI API fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        response = self.client.embeddings.create(
            model=self.model,
            input=text.strip(),
            dimensions=self.dimensions,
        )
        
        return response.data[0].embedding
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_embeddings_batch(
        self,
        texts: Sequence[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts to embed
            batch_size: Number of texts to process per API call (max 2048 for Azure)
            
        Returns:
            List of embedding vectors in same order as input texts
            
        Raises:
            Exception: If Azure OpenAI API fails after retries
        """
        if not texts:
            return []
        
        # Filter out empty texts and track their positions
        valid_texts = [(i, text.strip()) for i, text in enumerate(texts) if text and text.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        all_embeddings: list[list[float] | None] = [None] * len(texts)
        
        # Process in batches
        for batch_start in range(0, len(valid_texts), batch_size):
            batch_end = min(batch_start + batch_size, len(valid_texts))
            batch = valid_texts[batch_start:batch_end]
            
            # Extract texts and indices
            indices, batch_texts = zip(*batch)
            
            # Call Azure OpenAI
            response = self.client.embeddings.create(
                model=self.model,
                input=list(batch_texts),
                dimensions=self.dimensions,
            )
            
            # Map embeddings back to original positions
            for idx, embedding_data in zip(indices, response.data):
                all_embeddings[idx] = embedding_data.embedding
        
        # Return only valid embeddings (filter out None placeholders)
        return [emb for emb in all_embeddings if emb is not None]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters for English
        return len(text) // 4
