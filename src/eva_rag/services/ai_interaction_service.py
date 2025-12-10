"""Azure Cosmos DB service for AI Interaction provenance tracking."""
import hashlib
from uuid import UUID

from azure.cosmos import ContainerProxy, CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.identity import DefaultAzureCredential

from eva_rag.config import settings
from eva_rag.models.ai_interaction import AIInteraction


class AIInteractionService:
    """
    Manage AI Interactions in Azure Cosmos DB with Hierarchical Partition Key.
    
    **Provenance Tracking**: Every AI response is recorded with:
    - Input (user query)
    - Output (AI response)
    - Chunks used (which documents informed the response)
    - Citations (how to verify the response)
    - Hash chain (tamper-evidence)
    
    **Immutability**: AI interactions are WRITE-ONCE. No updates or deletes allowed.
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
        self.container_name = "ai_interactions"
        
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
    
    def _compute_content_hash(self, interaction: AIInteraction) -> str:
        """
        Compute SHA-256 hash of interaction content.
        
        Args:
            interaction: AI interaction
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        # Concatenate key fields
        content = (
            f"{interaction.id}|"
            f"{interaction.query}|"
            f"{interaction.response}|"
            f"{interaction.model_name}|"
            f"{interaction.created_at.isoformat()}|"
            f"{len(interaction.chunks_used)}|"
            f"{interaction.previous_hash}"
        )
        
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def get_latest_interaction_hash(
        self,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> str:
        """
        Get the hash of the most recent interaction for hash chaining.
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            
        Returns:
            Content hash of latest interaction, or "genesis" if none exist
        """
        container = self._get_container()
        
        query = """
            SELECT TOP 1 c.content_hash 
            FROM c 
            ORDER BY c.created_at DESC
        """
        
        partition_key = [str(space_id), str(tenant_id), str(user_id)]
        items = list(container.query_items(
            query=query,
            partition_key=partition_key,
        ))
        
        if items:
            return items[0]["content_hash"]
        else:
            return "genesis"  # First interaction in the chain
    
    def create_interaction(self, interaction: AIInteraction) -> AIInteraction:
        """
        Create an AI interaction record (write-once, immutable).
        
        Args:
            interaction: AI interaction
            
        Returns:
            Created interaction with computed hash
            
        Raises:
            Exception: If creation fails
        """
        container = self._get_container()
        
        # Get previous hash for chain
        if interaction.previous_hash == "":
            interaction.previous_hash = self.get_latest_interaction_hash(
                interaction.space_id,
                interaction.tenant_id,
                interaction.user_id,
            )
        
        # Compute content hash
        interaction.content_hash = self._compute_content_hash(interaction)
        
        # Convert to dict for Cosmos DB
        interaction_dict = interaction.model_dump(mode="json")
        interaction_dict["id"] = str(interaction.id)
        interaction_dict["space_id"] = str(interaction.space_id)
        interaction_dict["tenant_id"] = str(interaction.tenant_id)
        interaction_dict["user_id"] = str(interaction.user_id)
        
        # Create document (write-once)
        container.create_item(body=interaction_dict)
        
        return interaction
    
    def get_interaction(
        self,
        interaction_id: UUID,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
    ) -> AIInteraction | None:
        """
        Get an AI interaction by ID.
        
        Args:
            interaction_id: Interaction UUID
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            
        Returns:
            AI interaction or None if not found
        """
        container = self._get_container()
        
        try:
            partition_key = [str(space_id), str(tenant_id), str(user_id)]
            item = container.read_item(
                item=str(interaction_id),
                partition_key=partition_key,
            )
            return AIInteraction(**item)
        except CosmosResourceNotFoundError:
            return None
    
    def list_interactions_by_user(
        self,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AIInteraction]:
        """
        List AI interactions for a user.
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            skip: Number of interactions to skip (pagination)
            limit: Maximum number of interactions to return
            
        Returns:
            List of AI interactions, ordered by created_at DESC
        """
        container = self._get_container()
        
        query = f"""
            SELECT * FROM c 
            ORDER BY c.created_at DESC 
            OFFSET {skip} LIMIT {limit}
        """
        
        partition_key = [str(space_id), str(tenant_id), str(user_id)]
        items = container.query_items(
            query=query,
            partition_key=partition_key,
        )
        
        return [AIInteraction(**item) for item in items]
    
    def verify_hash_chain(
        self,
        space_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        count: int = 100,
    ) -> tuple[bool, str]:
        """
        Verify the integrity of the hash chain for a user.
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID
            user_id: User UUID
            count: Number of recent interactions to verify
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if chain is valid
            - (False, "error details") if chain is broken
        """
        # Get interactions in chronological order
        container = self._get_container()
        
        query = f"""
            SELECT * FROM c 
            ORDER BY c.created_at ASC 
            OFFSET 0 LIMIT {count}
        """
        
        partition_key = [str(space_id), str(tenant_id), str(user_id)]
        items = list(container.query_items(
            query=query,
            partition_key=partition_key,
        ))
        
        if not items:
            return (True, "")  # Empty chain is valid
        
        # Verify each interaction
        expected_previous_hash = "genesis"
        for item in items:
            interaction = AIInteraction(**item)
            
            # Check previous hash
            if interaction.previous_hash != expected_previous_hash:
                return (
                    False,
                    f"Hash chain broken at interaction {interaction.id}: "
                    f"expected previous_hash={expected_previous_hash}, "
                    f"got {interaction.previous_hash}",
                )
            
            # Recompute content hash
            computed_hash = self._compute_content_hash(interaction)
            if computed_hash != interaction.content_hash:
                return (
                    False,
                    f"Content hash mismatch at interaction {interaction.id}: "
                    f"expected {interaction.content_hash}, got {computed_hash}",
                )
            
            # Update expected previous hash for next iteration
            expected_previous_hash = interaction.content_hash
        
        return (True, "")
    
    def list_interactions_by_space(
        self,
        space_id: UUID,
        tenant_id: UUID | None = None,
        user_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AIInteraction]:
        """
        List AI interactions in a space (with optional tenant/user filtering).
        
        Args:
            space_id: Space UUID
            tenant_id: Tenant UUID (optional for cross-partition query)
            user_id: User UUID (optional)
            skip: Number of interactions to skip (pagination)
            limit: Maximum number of interactions to return
            
        Returns:
            List of AI interactions
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
        
        return [AIInteraction(**item) for item in items]
