"""Azure AI Search service for vector indexing and hybrid search."""
import logging
from typing import Any, Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from eva_rag.config import settings
from eva_rag.models.chunk import DocumentChunk

logger = logging.getLogger(__name__)


class SearchService:
    """Azure AI Search service for vector indexing and hybrid search."""
    
    def __init__(self) -> None:
        """Initialize Azure AI Search clients."""
        if not settings.azure_search_endpoint or not settings.azure_search_api_key:
            raise ValueError(
                "Azure AI Search configuration missing. Set AZURE_SEARCH_ENDPOINT "
                "and AZURE_SEARCH_API_KEY environment variables."
            )
        
        credential = AzureKeyCredential(settings.azure_search_api_key)
        
        # Index management client
        self.index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential,
        )
        
        # Search client for querying
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=credential,
        )
        
        logger.info(
            f"Initialized Azure AI Search: endpoint={settings.azure_search_endpoint}, "
            f"index={settings.azure_search_index_name}"
        )
    
    def create_index_if_not_exists(self) -> None:
        """
        Create Azure AI Search index with vector search configuration.
        
        Index schema:
        - chunk_id: Unique identifier
        - document_id: Parent document reference
        - space_id: Space isolation
        - tenant_id: Tenant isolation
        - content: Full chunk text (searchable, retrievable)
        - content_vector: Embedding vector (1536 dims for text-embedding-3-small)
        - chunk_index: Position in document
        - page_number: Page reference for citations
        - document_name: Source document filename
        - language: en or fr
        - document_type: policy, jurisprudence, guidance, faq
        - indexed_at: Indexing timestamp
        
        Vector search configuration:
        - HNSW algorithm (Hierarchical Navigable Small World)
        - m=4 (connections per layer)
        - ef_construction=400 (search depth during indexing)
        - ef_search=500 (search depth during querying)
        - Cosine similarity metric
        """
        try:
            # Check if index exists
            existing_indexes = self.index_client.list_index_names()
            if settings.azure_search_index_name in existing_indexes:
                logger.info(f"Index '{settings.azure_search_index_name}' already exists")
                return
            
            # Define fields
            fields = [
                # Identity fields
                SimpleField(
                    name="chunk_id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SimpleField(
                    name="document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="space_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="tenant_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                
                # Content fields
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    analyzer_name="standard.lucene",
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=settings.azure_openai_embedding_dimensions,
                    vector_search_profile_name="vector-profile",
                ),
                
                # Metadata fields
                SimpleField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                ),
                SimpleField(
                    name="page_number",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                ),
                SearchableField(
                    name="document_name",
                    type=SearchFieldDataType.String,
                ),
                SimpleField(
                    name="language",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="document_type",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SimpleField(
                    name="indexed_at",
                    type=SearchFieldDataType.DateTimeOffset,
                    filterable=True,
                    sortable=True,
                ),
            ]
            
            # Vector search configuration (HNSW algorithm)
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="hnsw-algorithm",
                        parameters=HnswParameters(
                            m=4,  # Connections per layer (balance: 4-8 typical)
                            ef_construction=400,  # Search depth during indexing
                            ef_search=500,  # Search depth during querying
                            metric="cosine",  # Cosine similarity for embeddings
                        ),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="vector-profile",
                        algorithm_configuration_name="hnsw-algorithm",
                    )
                ],
            )
            
            # Semantic search configuration (Azure GPT-4 reranking)
            semantic_config = SemanticConfiguration(
                name="semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[SemanticField(field_name="content")],
                    keywords_fields=[SemanticField(field_name="document_name")],
                ),
            )
            
            semantic_search = SemanticSearch(configurations=[semantic_config])
            
            # Create index
            index = SearchIndex(
                name=settings.azure_search_index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search,
            )
            
            self.index_client.create_index(index)
            logger.info(f"✅ Created index '{settings.azure_search_index_name}'")
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def index_chunks(self, chunks: list[DocumentChunk]) -> int:
        """
        Index document chunks in Azure AI Search.
        
        Args:
            chunks: List of document chunks with embeddings
            
        Returns:
            Number of chunks successfully indexed
            
        Raises:
            ValueError: If chunks missing embeddings
            Exception: If indexing fails
        """
        if not chunks:
            logger.warning("No chunks to index")
            return 0
        
        # Validate chunks have embeddings
        for chunk in chunks:
            if not chunk.embedding or len(chunk.embedding) != settings.azure_openai_embedding_dimensions:
                raise ValueError(
                    f"Chunk {chunk.chunk_id} missing or invalid embedding "
                    f"(expected {settings.azure_openai_embedding_dimensions} dimensions)"
                )
        
        # Convert to search documents
        documents = []
        for chunk in chunks:
            doc = {
                "chunk_id": str(chunk.chunk_id),
                "document_id": str(chunk.document_id),
                "space_id": str(chunk.space_id),
                "tenant_id": str(chunk.tenant_id),
                "content": chunk.text,
                "content_vector": chunk.embedding,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "document_name": chunk.metadata.get("document_name", "") if chunk.metadata else "",
                "language": chunk.language,
                "document_type": chunk.metadata.get("document_type", "other") if chunk.metadata else "other",
                "indexed_at": chunk.created_at.isoformat() if chunk.created_at else None,
            }
            documents.append(doc)
        
        try:
            # Upload documents in batches
            result = self.search_client.upload_documents(documents=documents)
            
            # Count successful uploads
            success_count = sum(1 for r in result if r.succeeded)
            
            if success_count < len(chunks):
                failed = [r for r in result if not r.succeeded]
                logger.warning(
                    f"Indexed {success_count}/{len(chunks)} chunks. "
                    f"Failed: {[r.key for r in failed]}"
                )
            else:
                logger.info(f"✅ Indexed {success_count} chunks successfully")
            
            return success_count
            
        except Exception as e:
            logger.error(f"Failed to index chunks: {e}")
            raise
    
    def hybrid_search(
        self,
        query: str,
        query_vector: list[float],
        space_id: str,
        tenant_id: str,
        top_k: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Execute hybrid search (vector + keyword) with RRF fusion.
        
        Args:
            query: Text query
            query_vector: Query embedding vector
            space_id: Space to search within
            tenant_id: Tenant to search within
            top_k: Number of results to return
            filters: Additional filters (language, document_type, etc.)
            
        Returns:
            List of search results with relevance scores
            
        Raises:
            ValueError: If query_vector dimensions invalid
            Exception: If search fails
        """
        if len(query_vector) != settings.azure_openai_embedding_dimensions:
            raise ValueError(
                f"Query vector has {len(query_vector)} dimensions, "
                f"expected {settings.azure_openai_embedding_dimensions}"
            )
        
        # Build filter expression
        filter_parts = [
            f"space_id eq '{space_id}'",
            f"tenant_id eq '{tenant_id}'",
        ]
        
        if filters:
            if "language" in filters:
                filter_parts.append(f"language eq '{filters['language']}'")
            if "document_type" in filters:
                filter_parts.append(f"document_type eq '{filters['document_type']}'")
        
        filter_expression = " and ".join(filter_parts)
        
        # Create vector query
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=settings.search_top_k_max,  # Retrieve top-20 for reranking
            fields="content_vector",
        )
        
        try:
            # Execute hybrid search (vector + BM25 keyword)
            results = self.search_client.search(
                search_text=query,  # BM25 keyword search
                vector_queries=[vector_query],  # Vector search
                filter=filter_expression,
                select=[
                    "chunk_id",
                    "document_id",
                    "document_name",
                    "page_number",
                    "content",
                    "language",
                    "document_type",
                    "chunk_index",
                ],
                top=top_k,
            )
            
            # Convert to list and extract scores
            search_results = []
            for result in results:
                search_results.append({
                    "chunk_id": result["chunk_id"],
                    "document_id": result["document_id"],
                    "document_name": result["document_name"],
                    "page_number": result.get("page_number"),
                    "content": result["content"],
                    "language": result["language"],
                    "document_type": result.get("document_type", "other"),
                    "chunk_index": result.get("chunk_index", 0),
                    "relevance_score": result["@search.score"],
                })
            
            logger.info(
                f"Hybrid search returned {len(search_results)} results for query: '{query[:50]}...'"
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise
    
    def delete_chunks_by_document(self, document_id: str, tenant_id: str) -> int:
        """
        Delete all chunks for a document from the search index.
        
        Args:
            document_id: Document UUID
            tenant_id: Tenant UUID for isolation
            
        Returns:
            Number of chunks deleted
            
        Raises:
            Exception: If deletion fails
        """
        try:
            # Search for chunks by document_id and tenant_id
            filter_expression = f"document_id eq '{document_id}' and tenant_id eq '{tenant_id}'"
            
            results = self.search_client.search(
                search_text="*",
                filter=filter_expression,
                select=["chunk_id"],
                top=1000,  # Max chunks per document
            )
            
            # Extract chunk IDs
            chunk_ids = [r["chunk_id"] for r in results]
            
            if not chunk_ids:
                logger.warning(f"No chunks found for document {document_id}")
                return 0
            
            # Delete documents by key
            documents = [{"chunk_id": cid} for cid in chunk_ids]
            result = self.search_client.delete_documents(documents=documents)
            
            # Count successful deletions
            success_count = sum(1 for r in result if r.succeeded)
            
            logger.info(
                f"✅ Deleted {success_count}/{len(chunk_ids)} chunks for document {document_id}"
            )
            
            return success_count
            
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            raise
