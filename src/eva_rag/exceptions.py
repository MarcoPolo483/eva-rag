"""
Custom exceptions for EVA RAG application.

Provides structured error handling with proper HTTP status codes.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class EVAException(Exception):
    """Base exception for EVA RAG application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "message": self.message,
                "error_type": self.__class__.__name__,
                **self.details
            }
        )


# Cosmos DB Errors
class CosmosDBError(EVAException):
    """Base class for Cosmos DB errors."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class DocumentNotFoundError(EVAException):
    """Document not found in Cosmos DB."""
    
    def __init__(self, document_id: str, container: str):
        super().__init__(
            message=f"Document not found: {document_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"document_id": document_id, "container": container}
        )


class DocumentExistsError(EVAException):
    """Document already exists."""
    
    def __init__(self, document_id: str, container: str):
        super().__init__(
            message=f"Document already exists: {document_id}",
            status_code=status.HTTP_409_CONFLICT,
            details={"document_id": document_id, "container": container}
        )


class ThrottlingError(CosmosDBError):
    """Cosmos DB request throttled (429)."""
    
    def __init__(self, retry_after_ms: Optional[int] = None):
        details = {}
        if retry_after_ms:
            details["retry_after_ms"] = retry_after_ms
        
        super().__init__(
            message="Request throttled. Please retry after specified time.",
            details=details
        )


# Validation Errors
class ValidationError(EVAException):
    """Data validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class HPKValidationError(ValidationError):
    """Hierarchical partition key validation error."""
    
    def __init__(self, message: str, missing_fields: Optional[List[str]] = None):
        details = {}
        if missing_fields:
            details["missing_fields"] = missing_fields
        
        super().__init__(message=message)
        self.details.update(details)


# Authentication/Authorization Errors
class AuthenticationError(EVAException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(EVAException):
    """Authorization failed (insufficient permissions)."""
    
    def __init__(self, message: str = "Insufficient permissions", required_role: Optional[str] = None):
        details = {}
        if required_role:
            details["required_role"] = required_role
        
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class TokenExpiredError(AuthenticationError):
    """JWT token expired."""
    
    def __init__(self):
        super().__init__(message="Token expired")


# Storage Errors
class StorageError(EVAException):
    """Base class for storage errors."""
    
    def __init__(self, message: str, storage_type: str = "unknown"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"storage_type": storage_type}
        )


class BlobStorageError(StorageError):
    """Azure Blob Storage error."""
    
    def __init__(self, message: str, blob_name: Optional[str] = None):
        details = {"storage_type": "blob"}
        if blob_name:
            details["blob_name"] = blob_name
        
        super().__init__(message=message, storage_type="blob")
        self.details.update(details)


# Processing Errors
class ProcessingError(EVAException):
    """Document processing error."""
    
    def __init__(self, message: str, document_id: Optional[str] = None):
        details = {}
        if document_id:
            details["document_id"] = document_id
        
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ChunkingError(ProcessingError):
    """Document chunking error."""
    
    def __init__(self, message: str, document_id: Optional[str] = None):
        super().__init__(message=f"Chunking failed: {message}", document_id=document_id)


class EmbeddingError(ProcessingError):
    """Embedding generation error."""
    
    def __init__(self, message: str, document_id: Optional[str] = None):
        super().__init__(message=f"Embedding generation failed: {message}", document_id=document_id)


# Search/Retrieval Errors
class SearchError(EVAException):
    """Search operation error."""
    
    def __init__(self, message: str, query: Optional[str] = None):
        details = {}
        if query:
            details["query"] = query
        
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


# Configuration Errors
class ConfigurationError(EVAException):
    """Configuration error."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class MissingEnvironmentVariableError(ConfigurationError):
    """Required environment variable missing."""
    
    def __init__(self, var_name: str):
        super().__init__(
            message=f"Required environment variable missing: {var_name}",
            config_key=var_name
        )


# Rate Limiting
class RateLimitError(EVAException):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after_seconds: Optional[int] = None):
        details = {}
        if retry_after_seconds:
            details["retry_after_seconds"] = retry_after_seconds
        
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


# Business Logic Errors
class BusinessLogicError(EVAException):
    """Business logic error."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class SpaceNotFoundError(BusinessLogicError):
    """Space not found."""
    
    def __init__(self, space_id: str):
        super().__init__(message=f"Space not found: {space_id}")
        self.details["space_id"] = space_id


class InvalidOperationError(BusinessLogicError):
    """Invalid operation for current state."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message=message)
        if operation:
            self.details["operation"] = operation


# Audit/Integrity Errors
class IntegrityError(EVAException):
    """Data integrity error."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class HashChainBrokenError(IntegrityError):
    """Hash chain integrity compromised."""
    
    def __init__(self, sequence_number: Optional[int] = None):
        message = "Hash chain integrity compromised"
        if sequence_number:
            message += f" at sequence number {sequence_number}"
        
        super().__init__(message=message)
        if sequence_number:
            self.details["sequence_number"] = sequence_number
