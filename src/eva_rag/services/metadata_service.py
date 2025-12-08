"""Azure Cosmos DB service for document metadata storage."""
from typing import Any
from uuid import UUID

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential

from eva_rag.config import settings
from eva_rag.models.document import DocumentMetadata


class MetadataService:
    """Manage document metadata in Azure Cosmos DB (eva-core Document entity)."""
    
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
        self.container_name = settings.azure_cosmos_container
        
        self._ensure_database_and_container()
    
    def _ensure_database_and_container(self) -> None:
        """Create database and container if they don't exist."""
        try:
            # Create database
            database = self.client.create_database_if_not_exists(self.database_name)
            
            # Create container with tenant_id as partition key for tenant isolation
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
    
    def get_document(self, document_id: UUID, tenant_id: UUID) -> DocumentMetadata | None:
        """
        Get document metadata by ID.
        
        Args:
            document_id: Document UUID
            tenant_id: Tenant UUID (partition key)
            
        Returns:
            Document metadata or None if not found
        """
        container = self._get_container()
        
        try:
            item = container.read_item(
                item=str(document_id),
                partition_key=str(tenant_id),
            )
            return DocumentMetadata(**item)
        except Exception:
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
    
    def delete_document(self, document_id: UUID, tenant_id: UUID) -> None:
        """
        Delete document metadata.
        
        Args:
            document_id: Document UUID
            tenant_id: Tenant UUID (partition key)
            
        Raises:
            Exception: If deletion fails
        """
        container = self._get_container()
        
        container.delete_item(
            item=str(document_id),
            partition_key=str(tenant_id),
        )
    
    def list_documents_by_space(
        self,
        space_id: UUID,
        tenant_id: UUID,
    ) -> list[DocumentMetadata]:
        """
        List all documents in a space.
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID
            
        Returns:
            List of document metadata
        """
        container = self._get_container()
        
        query = "SELECT * FROM c WHERE c.space_id = @space_id AND c.tenant_id = @tenant_id"
        parameters = [
            {"name": "@space_id", "value": str(space_id)},
            {"name": "@tenant_id", "value": str(tenant_id)},
        ]
        
        items = container.query_items(
            query=query,
            parameters=parameters,
            partition_key=str(tenant_id),
        )
        
        return [DocumentMetadata(**item) for item in items]
