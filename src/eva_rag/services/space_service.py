"""Azure Cosmos DB service for Space management."""
from datetime import datetime
from typing import Any
from uuid import UUID

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

from eva_rag.config import settings
from eva_rag.models.space import Space, SpaceCreate, SpaceUpdate


class SpaceService:
    """Manage Spaces in Azure Cosmos DB for multi-tenant isolation."""
    
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
        self.container_name = "spaces"  # Dedicated container for Spaces
        
        self._ensure_database_and_container()
    
    def _ensure_database_and_container(self) -> None:
        """Create database and container if they don't exist."""
        try:
            # Create database
            database = self.client.create_database_if_not_exists(self.database_name)
            
            # Create Spaces container with /spaceId as partition key
            database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/space_id"),
            )
        except Exception:
            # Already exists or no permission
            pass
    
    def _get_container(self) -> ContainerProxy:
        """Get container client."""
        database = self.client.get_database_client(self.database_name)
        return database.get_container_client(self.container_name)
    
    def create_space(self, space_create: SpaceCreate) -> Space:
        """
        Create a new Space.
        
        Args:
            space_create: Space creation request
            
        Returns:
            Created Space
            
        Raises:
            ValueError: If Space name already exists
            Exception: If creation fails
        """
        container = self._get_container()
        
        # Check if Space name already exists
        query = "SELECT * FROM c WHERE c.name = @name"
        parameters = [{"name": "@name", "value": space_create.name}]
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        ))
        
        if items:
            raise ValueError(f"Space with name '{space_create.name}' already exists")
        
        # Create Space instance
        space = Space(
            name=space_create.name,
            description=space_create.description,
            type=space_create.type,
            owner_id=space_create.owner_id,
            owner_email=space_create.owner_email,
            quotas=space_create.quotas or Space.model_fields["quotas"].default_factory(),
            metadata=space_create.metadata,
        )
        
        # Ensure space_id matches id for partition key
        space.space_id = space.id
        
        # Convert to dict for Cosmos DB
        space_dict = space.model_dump(mode="json")
        space_dict["id"] = str(space.id)
        space_dict["space_id"] = str(space.space_id)
        space_dict["owner_id"] = str(space.owner_id)
        
        # Create document
        try:
            container.create_item(body=space_dict)
        except CosmosResourceExistsError:
            raise ValueError(f"Space with ID '{space.id}' already exists")
        
        return space
    
    def get_space(self, space_id: UUID) -> Space | None:
        """
        Get Space by ID.
        
        Args:
            space_id: Space UUID
            
        Returns:
            Space or None if not found
        """
        container = self._get_container()
        
        try:
            item = container.read_item(
                item=str(space_id),
                partition_key=str(space_id),
            )
            return Space(**item)
        except CosmosResourceNotFoundError:
            return None
    
    def get_space_by_name(self, name: str) -> Space | None:
        """
        Get Space by name.
        
        Args:
            name: Space name
            
        Returns:
            Space or None if not found
        """
        container = self._get_container()
        
        query = "SELECT * FROM c WHERE c.name = @name"
        parameters = [{"name": "@name", "value": name}]
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
            max_item_count=1,
        ))
        
        if not items:
            return None
        
        return Space(**items[0])
    
    def update_space(self, space_id: UUID, space_update: SpaceUpdate) -> Space:
        """
        Update Space.
        
        Args:
            space_id: Space UUID
            space_update: Space update request
            
        Returns:
            Updated Space
            
        Raises:
            ValueError: If Space not found or name already exists
            Exception: If update fails
        """
        container = self._get_container()
        
        # Get existing Space
        space = self.get_space(space_id)
        if not space:
            raise ValueError(f"Space with ID '{space_id}' not found")
        
        # Check if new name already exists (if name is being updated)
        if space_update.name and space_update.name != space.name:
            existing = self.get_space_by_name(space_update.name)
            if existing:
                raise ValueError(f"Space with name '{space_update.name}' already exists")
        
        # Update fields
        update_data = space_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(space, key, value)
        
        # Update timestamp
        space.updated_at = datetime.utcnow()
        
        # If status changed to ARCHIVED, set archived_at
        if space_update.status == "archived" and not space.archived_at:
            space.archived_at = datetime.utcnow()
        
        # Convert to dict
        space_dict = space.model_dump(mode="json")
        space_dict["id"] = str(space.id)
        space_dict["space_id"] = str(space.space_id)
        space_dict["owner_id"] = str(space.owner_id)
        
        # Upsert document
        container.upsert_item(body=space_dict)
        
        return space
    
    def delete_space(self, space_id: UUID) -> None:
        """
        Delete Space (soft delete - archive).
        
        Args:
            space_id: Space UUID
            
        Raises:
            ValueError: If Space not found
            Exception: If deletion fails
        """
        # Use update to archive instead of delete
        space_update = SpaceUpdate(status="archived")
        self.update_space(space_id, space_update)
    
    def list_spaces(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        space_type: str | None = None,
    ) -> list[Space]:
        """
        List Spaces with optional filtering.
        
        Args:
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return
            status: Filter by status (active/suspended/archived)
            space_type: Filter by type (sandbox/production/archived)
            
        Returns:
            List of Spaces
        """
        container = self._get_container()
        
        # Build query
        query_parts = ["SELECT * FROM c"]
        parameters: list[dict[str, Any]] = []
        
        where_clauses = []
        if status:
            where_clauses.append("c.status = @status")
            parameters.append({"name": "@status", "value": status})
        
        if space_type:
            where_clauses.append("c.type = @type")
            parameters.append({"name": "@type", "value": space_type})
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        query_parts.append("ORDER BY c.created_at DESC")
        query_parts.append(f"OFFSET {skip} LIMIT {limit}")
        
        query = " ".join(query_parts)
        
        # Execute query
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        ))
        
        return [Space(**item) for item in items]
    
    def increment_usage(
        self,
        space_id: UUID,
        documents: int = 0,
        storage_bytes: int = 0,
        ai_calls: int = 0,
    ) -> Space:
        """
        Increment usage counters for a Space.
        
        Args:
            space_id: Space UUID
            documents: Number of documents to add
            storage_bytes: Storage bytes to add
            ai_calls: AI calls to add
            
        Returns:
            Updated Space
            
        Raises:
            ValueError: If Space not found or quota exceeded
        """
        space = self.get_space(space_id)
        if not space:
            raise ValueError(f"Space with ID '{space_id}' not found")
        
        # Check quotas before incrementing
        new_document_count = space.current_document_count + documents
        new_storage_bytes = space.current_storage_bytes + storage_bytes
        new_ai_calls = space.current_ai_calls_this_month + ai_calls
        
        if new_document_count > space.quotas.max_documents:
            raise ValueError(
                f"Document quota exceeded: {new_document_count} > {space.quotas.max_documents}"
            )
        
        if new_storage_bytes > (space.quotas.storage_gb * 1024 * 1024 * 1024):
            raise ValueError(
                f"Storage quota exceeded: {new_storage_bytes} bytes > {space.quotas.storage_gb} GB"
            )
        
        if new_ai_calls > space.quotas.ai_calls_per_month:
            raise ValueError(
                f"AI calls quota exceeded: {new_ai_calls} > {space.quotas.ai_calls_per_month}"
            )
        
        # Increment counters
        space.current_document_count = new_document_count
        space.current_storage_bytes = new_storage_bytes
        space.current_ai_calls_this_month = new_ai_calls
        space.updated_at = datetime.utcnow()
        
        # Save
        container = self._get_container()
        space_dict = space.model_dump(mode="json")
        space_dict["id"] = str(space.id)
        space_dict["space_id"] = str(space.space_id)
        space_dict["owner_id"] = str(space.owner_id)
        
        container.upsert_item(body=space_dict)
        
        return space
