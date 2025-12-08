"""Azure Blob Storage service for document persistence."""
import hashlib
from typing import BinaryIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

from eva_rag.config import settings


class StorageService:
    """Manage document uploads to Azure Blob Storage with tenant isolation."""
    
    def __init__(self) -> None:
        """Initialize Azure Blob Storage client."""
        # Use connection string if provided, otherwise use DefaultAzureCredential
        if settings.azure_storage_connection_string:
            self.client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
        else:
            credential = DefaultAzureCredential()
            self.client = BlobServiceClient(
                account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
                credential=credential,
            )
        
        self.container_name = settings.azure_storage_container
        self._ensure_container_exists()
    
    def _ensure_container_exists(self) -> None:
        """Create container if it doesn't exist."""
        try:
            self.client.create_container(self.container_name)
        except Exception:
            # Container already exists or no permission to create
            pass
    
    def _generate_blob_path(
        self,
        tenant_id: str,
        space_id: str,
        document_id: str,
        filename: str,
    ) -> str:
        """
        Generate blob path with tenant isolation.
        
        Format: {tenant_id}/{space_id}/{document_id}/{filename}
        
        Args:
            tenant_id: Tenant UUID
            space_id: Space UUID
            document_id: Document UUID
            filename: Original filename
            
        Returns:
            Blob path string
        """
        return f"{tenant_id}/{space_id}/{document_id}/{filename}"
    
    def upload_document(
        self,
        file: BinaryIO,
        filename: str,
        tenant_id: str,
        space_id: str,
        document_id: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload document to Azure Blob Storage.
        
        Args:
            file: Binary file content
            filename: Original filename
            tenant_id: Tenant UUID
            space_id: Space UUID
            document_id: Document UUID
            content_type: MIME type
            
        Returns:
            Blob URL
            
        Raises:
            Exception: If upload fails
        """
        blob_path = self._generate_blob_path(tenant_id, space_id, document_id, filename)
        
        # Get blob client
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=blob_path,
        )
        
        # Upload file
        file.seek(0)  # Reset file pointer
        content_settings = ContentSettings(content_type=content_type)
        
        blob_client.upload_blob(
            file,
            overwrite=True,
            content_settings=content_settings,
            metadata={
                "tenant_id": tenant_id,
                "space_id": space_id,
                "document_id": document_id,
                "filename": filename,
            },
        )
        
        return blob_client.url
    
    def download_document(
        self,
        tenant_id: str,
        space_id: str,
        document_id: str,
        filename: str,
    ) -> bytes:
        """
        Download document from Azure Blob Storage.
        
        Args:
            tenant_id: Tenant UUID
            space_id: Space UUID
            document_id: Document UUID
            filename: Original filename
            
        Returns:
            File content as bytes
            
        Raises:
            Exception: If download fails or file doesn't exist
        """
        blob_path = self._generate_blob_path(tenant_id, space_id, document_id, filename)
        
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=blob_path,
        )
        
        return blob_client.download_blob().readall()
    
    def delete_document(
        self,
        tenant_id: str,
        space_id: str,
        document_id: str,
        filename: str,
    ) -> None:
        """
        Delete document from Azure Blob Storage.
        
        Args:
            tenant_id: Tenant UUID
            space_id: Space UUID
            document_id: Document UUID
            filename: Original filename
            
        Raises:
            Exception: If deletion fails
        """
        blob_path = self._generate_blob_path(tenant_id, space_id, document_id, filename)
        
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=blob_path,
        )
        
        blob_client.delete_blob()
    
    def compute_content_hash(self, content: bytes) -> str:
        """
        Compute SHA-256 hash of content for deduplication.
        
        Args:
            content: File content
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content).hexdigest()
