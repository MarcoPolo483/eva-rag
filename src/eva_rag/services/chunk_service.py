"""Azure Cosmos DB service for chunk storage with HPK."""
from uuid import UUID

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

from eva_rag.config import settings
from eva_rag.models.chunk import DocumentChunk


class ChunkService:
    """
    Manage document chunks in Azure Cosmos DB with Hierarchical Partition Key.
    
    Uses HPK: /spaceId/tenantId/userId for complete multi-tenant isolation.
    """
    
    def __init__(self) -> None:
        """Initialize Azure Cosmos DB client."""
        # Use connection string or credential
        if settings.azure_cosmos_key:
            self.client = CosmosClient(
                settings.azure_cosmos_endpoint,
                settings.azure_cosmos_key,
            )
        else:
            credential = DefaultAzureCredential()
            self.client = CosmosClient(
                settings.azure_cosmos_endpoint,
                credential,
            )
        
        self.database_name = settings.azure_cosmos_database
        self.container_name = "chunks"
        
        self._ensure_database_and_container()
    
    def _ensure_database_and_container(self) -> None:
        """Create database and container if they don't exist."""
        try:
            # Create database
            database = self.client.create_database_if_not_exists(self.database_name)
            
            # Create container with HPK: /space_id/tenant_id/user_id
            database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(
                    path=["/space_id", "/tenant_id", "/user_id"],
                    kind="MultiHash",
                ),
            )
        except Exception:
            # Already exists or no permission
            pass
    
    def _get_container(self) -> ContainerProxy:
        """Get container client."""
        database = self.client.get_database_client(self.database_name)
        return database.get_container_client(self.container_name)
    
    def create_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """
        Create a chunk in Cosmos DB.
        
        Args:
            chunk: Document chunk
            
        Returns:
            Created chunk
            
        Raises:
            Exception: If creation fails
        """
        container = self._get_container()
        
        # Convert to dict for Cosmos DB
        chunk_dict = chunk.model_dump(mode="json")
        chunk_dict["id"] = chunk.chunk_id
        chunk_dict["document_id"] = str(chunk.document_id)
        chunk_dict["tenant_id"] = str(chunk.tenant_id)
        chunk_dict["space_id"] = str(chunk.space_id)
        
        # Create document
        container.create_item(body=chunk_dict)
        
        return chunk
    
    def create_chunks_batch(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        """
        Create multiple chunks in a batch.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            List of created chunks
            
        Note:
            All chunks must belong to the same partition (same space_id, tenant_id, user_id)
        """
        if not chunks:
            return []
        
        container = self._get_container()
        
        # Verify all chunks share the same partition key
        first_chunk = chunks[0]
        for chunk in chunks[1:]:
            if (chunk.space_id != first_chunk.space_id or
                chunk.tenant_id != first_chunk.tenant_id or
                chunk.user_id != first_chunk.user_id):
                raise ValueError("All chunks in batch must belong to the same partition")
        
        # Create chunks
        created_chunks = []
        for chunk in chunks:
            chunk_dict = chunk.model_dump(mode="json")
            chunk_dict["id"] = chunk.chunk_id
            chunk_dict["document_id"] = str(chunk.document_id)
            chunk_dict["tenant_id"] = str(chunk.tenant_id)
            chunk_dict["space_id"] = str(chunk.space_id)
            
            container.create_item(body=chunk_dict)
            created_chunks.append(chunk)
        
        return created_chunks
    
    def get_chunk(
        self,
        chunk_id: str,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> DocumentChunk | None:
        """
        Get a chunk by ID.
        
        Args:
            chunk_id: Chunk ID (format: document_id:chunk_index)
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            
        Returns:
            Document chunk or None if not found
        """
        container = self._get_container()
        
        try:
            partition_key = [str(space_id), str(tenant_id), str(user_id)]
            item = container.read_item(
                item=chunk_id,
                partition_key=partition_key,
            )
            return DocumentChunk(**item)
        except CosmosResourceNotFoundError:
            return None
    
    def list_chunks_by_document(
        self,
        document_id: UUID,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> list[DocumentChunk]:
        """
        List all chunks for a document.
        
        Args:
            document_id: Document UUID
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            
        Returns:
            List of document chunks, ordered by chunk_index
        """
        container = self._get_container()
        
        query = """
            SELECT * FROM c 
            WHERE c.document_id = @document_id 
            ORDER BY c.chunk_index ASC
        """
        parameters = [{"name": "@document_id", "value": str(document_id)}]
        
        # Use partition key for efficient query
        partition_key = [str(space_id), str(tenant_id), str(user_id)]
        items = container.query_items(
            query=query,
            parameters=parameters,
            partition_key=partition_key,
        )
        
        return [DocumentChunk(**item) for item in items]
    
    def delete_chunks_by_document(
        self,
        document_id: UUID,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            document_id: Document UUID
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            
        Returns:
            Number of chunks deleted
        """
        # First, get all chunks
        chunks = self.list_chunks_by_document(document_id, space_id, tenant_id, user_id)
        
        container = self._get_container()
        partition_key = [str(space_id), str(tenant_id), str(user_id)]
        
        # Delete each chunk
        for chunk in chunks:
            container.delete_item(
                item=chunk.chunk_id,
                partition_key=partition_key,
            )
        
        return len(chunks)
    
    def list_chunks_by_space(
        self,
        space_id: UUID,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentChunk]:
        """
        List chunks in a space (with optional tenant/user filtering).
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID (optional for cross-partition query)
            user_id: User UUID (optional)
            skip: Number of chunks to skip (pagination)
            limit: Maximum number of chunks to return
            
        Returns:
            List of document chunks
        """
        container = self._get_container()
        
        # Build query
        query_parts = ["SELECT * FROM c WHERE c.space_id = @space_id"]
        parameters = [{"name": "@space_id", "value": str(space_id)}]
        
        if tenant_id:
            query_parts.append("AND c.tenant_id = @tenant_id")
            parameters.append({"name": "@tenant_id", "value": str(tenant_id)})
        
        if user_id:
            query_parts.append("AND c.user_id = @user_id")
            parameters.append({"name": "@user_id", "value": str(user_id)})
        
        query_parts.append(f"ORDER BY c.created_at DESC OFFSET {skip} LIMIT {limit}")
        query = " ".join(query_parts)
        
        # Execute query
        if tenant_id and user_id:
            # Can use partition key for better performance
            partition_key = [str(space_id), str(tenant_id), str(user_id)]
            items = container.query_items(
                query=query,
                parameters=parameters,
                partition_key=partition_key,
            )
        else:
            # Cross-partition query
            items = container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )
        
        return [DocumentChunk(**item) for item in items]
