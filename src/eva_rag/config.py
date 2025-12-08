"""Configuration settings for eva-rag."""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "eva-rag"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    
    # Azure Storage
    azure_storage_connection_string: str = ""
    azure_storage_account_name: str = ""
    azure_storage_container: str = "documents"
    
    # Azure Cosmos DB
    azure_cosmos_endpoint: str = ""
    azure_cosmos_key: str = ""
    azure_cosmos_database: str = "eva-core"
    azure_cosmos_container: str = "documents"
    
    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    openai_embedding_model: str = "text-embedding-3-small"  # Model name for API calls
    openai_embedding_dimensions: int = 1536
    azure_openai_embedding_dimensions: int = 1536
    azure_openai_api_version: str = "2024-02-01"
    
    # Azure AI Search
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index_name: str = "eva-rag-chunks"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ttl_seconds: int = 604800  # 7 days
    
    # Document Processing
    max_file_size_mb: int = 50
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 50
    batch_size_embeddings: int = 100
    
    # Search
    search_top_k_default: int = 5
    search_top_k_max: int = 20
    rerank_threshold: float = 0.5
    hybrid_search_rrf_k: int = 60
    
    # Supported Languages
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "fr"])
    
    # Rate Limiting
    openai_max_retries: int = 3
    openai_retry_delay_seconds: float = 1.0
    openai_max_requests_per_minute: int = 3000


# Global settings instance
settings = Settings()
