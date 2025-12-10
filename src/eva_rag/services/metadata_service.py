"""Azure Cosmos DB service for document metadata storage."""
from typing import Any
from uuid import UUID

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

from eva_rag.config import settings
from eva_rag.models.document import DocumentMetadata


class MetadataService:
    """
    Manage document metadata in Azure Cosmos DB.
    
    Supports both legacy (simple partition key) and HPK (Hierarchical Partition Key) modes:
    - Legacy: /tenant_id (for backward compatibility)
    - HPK: /spaceId/tenantId/userId (new multi-tenant isolation)
    """
    
    def __init__(self, use_hpk: bool = False) -> None:
        """
        Initialize Azure Cosmos DB client.
        
        Args:
            use_hpk: If True, use Hierarchical Partition Key (HPK) for new collections.
                     If False, use legacy /tenant_id partition key.
        """
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
        self.use_hpk = use_hpk
        
        # Use different container names for legacy vs HPK
        if use_hpk:
            self.container_name = "documents_hpk"
        else:
            self.container_name = settings.azure_cosmos_container  # Legacy
        
        self._ensure_database_and_container()
    
    def _ensure_database_and_container(self) -> None:
        """Create database and container if they don't exist."""
        try:
            # Create database
            database = self.client.create_database_if_not_exists(self.database_name)
            
            if self.use_hpk:
                # Create container with HPK: /spaceId/tenantId/userId
                database.create_container_if_not_exists(
                    id=self.container_name,
                    partition_key=PartitionKey(
                        path=["/space_id", "/tenant_id", "/user_id"],
                        kind="MultiHash",
                    ),
                )
            else:
                # Create container with legacy partition key: /tenant_id
                database.create_container_if_not_exists(
                    id=self.container_name,
                    partition_key=PartitionKey(path="/tenant_id"),
                )
        except Exception:
            # Already exists or no permission
            pass
    
    def _get_container(self) -> ContainerProxy:
        """Get container client."""
        database = self.client.get_database_client(self.database_name)
        return database.get_container_client(self.container_name)
    
    def _get_partition_key(self, metadata: DocumentMetadata) -> str | list[str]:
        """
        Get partition key value(s) based on mode.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Single string for legacy mode, list of strings for HPK mode
        """
        if self.use_hpk:
            return [str(metadata.space_id), str(metadata.tenant_id), str(metadata.user_id)]
        else:
            return str(metadata.tenant_id)
    
    def create_document(self, metadata: DocumentMetadata) -> DocumentMetadata:
        """
        Create document metadata in Cosmos DB.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Created document metadata
            
        Raises:
            Exception: If creation fails
        """
        container = self._get_container()
        
        # Convert to dict for Cosmos DB
        doc_dict = metadata.model_dump(mode="json")
        doc_dict["id"] = str(metadata.id)
        doc_dict["tenant_id"] = str(metadata.tenant_id)
        doc_dict["space_id"] = str(metadata.space_id)
        doc_dict["user_id"] = str(metadata.user_id)
        
        # Create document
        container.create_item(body=doc_dict)
        
        return metadata
    
    def get_document(
        self,
        document_id: UUID,
        space_id: UUID | None = None,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> DocumentMetadata | None:
        """
        Get document metadata by ID.
        
        Args:
            document_id: Document UUID
            space_id: Space UUID (required for HPK mode)
            tenant_id: Tenant UUID (required for both modes)
            user_id: User UUID (required for HPK mode)
            
        Returns:
            Document metadata or None if not found
        """
        container = self._get_container()
        
        try:
            if self.use_hpk:
                if not (space_id and tenant_id and user_id):
                    raise ValueError("HPK mode requires space_id, tenant_id, and user_id")
                
                partition_key = [str(space_id), str(tenant_id), str(user_id)]
            else:
                if not tenant_id:
                    raise ValueError("Legacy mode requires tenant_id")
                
                partition_key = str(tenant_id)
            
            item = container.read_item(
                item=str(document_id),
                partition_key=partition_key,
            )
            return DocumentMetadata(**item)
        except CosmosResourceNotFoundError:
            return None
    
    def update_document(self, metadata: DocumentMetadata) -> DocumentMetadata:
        """
        Update document metadata.
        
        Args:
            metadata: Updated document metadata
            
        Returns:
            Updated document metadata
            
        Raises:
            Exception: If update fails
        """
        container = self._get_container()
        
        # Convert to dict
        doc_dict = metadata.model_dump(mode="json")
        doc_dict["id"] = str(metadata.id)
        doc_dict["tenant_id"] = str(metadata.tenant_id)
        doc_dict["space_id"] = str(metadata.space_id)
        doc_dict["user_id"] = str(metadata.user_id)
        
        # Upsert document
        container.upsert_item(body=doc_dict)
        
        return metadata
    
    def delete_document(
        self,
        document_id: UUID,
        space_id: UUID | None = None,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Delete document metadata.
        
        Args:
            document_id: Document UUID
            space_id: Space UUID (required for HPK mode)
            tenant_id: Tenant UUID (required for both modes)
            user_id: User UUID (required for HPK mode)
            
        Raises:
            Exception: If deletion fails
        """
        container = self._get_container()
        
        if self.use_hpk:
            if not (space_id and tenant_id and user_id):
                raise ValueError("HPK mode requires space_id, tenant_id, and user_id")
            
            partition_key = [str(space_id), str(tenant_id), str(user_id)]
        else:
            if not tenant_id:
                raise ValueError("Legacy mode requires tenant_id")
            
            partition_key = str(tenant_id)
        
        container.delete_item(
            item=str(document_id),
            partition_key=partition_key,
        )
    
    def list_documents_by_space(
        self,
        space_id: UUID,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DocumentMetadata]:
        """
        List all documents in a space.
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID (optional for cross-partition query)
            user_id: User UUID (optional)
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            
        Returns:
            List of document metadata
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
        if self.use_hpk and tenant_id and user_id:
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
        
        return [DocumentMetadata(**item) for item in items]
