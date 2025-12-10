"""
Authentication and authorization utilities for EVA RAG API.

Implements:
- Azure AD JWT token validation
- Role-Based Access Control (RBAC)
- Space-level access control
- User identity extraction
"""

from typing import Optional, List
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import os
from datetime import datetime, timezone
from enum import Enum


# Security scheme
security = HTTPBearer()


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    SYSTEM = "system"


class UserIdentity(BaseModel):
    """Authenticated user identity."""
    user_id: str
    email: str
    name: Optional[str] = None
    roles: List[UserRole] = []
    tenant_id: str
    spaces: List[str] = []  # Space IDs user has access to


class AuthConfig:
    """Authentication configuration."""
    
    def __init__(self):
        self.azure_ad_tenant_id = os.getenv("AZURE_AD_TENANT_ID")
        self.azure_ad_client_id = os.getenv("AZURE_AD_CLIENT_ID")
        self.jwt_secret = os.getenv("JWT_SECRET", "dev-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_audience = os.getenv("JWT_AUDIENCE", "eva-rag-api")
        self.auth_enabled = os.getenv("AUTH_ENABLED", "false").lower() == "true"
        
        # Azure AD issuer
        if self.azure_ad_tenant_id:
            self.jwt_issuer = f"https://login.microsoftonline.com/{self.azure_ad_tenant_id}/v2.0"
        else:
            self.jwt_issuer = "eva-rag-dev"


auth_config = AuthConfig()


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
            audience=auth_config.jwt_audience,
            issuer=auth_config.jwt_issuer,
        )
        
        # Validate expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )


def extract_user_identity(token_payload: dict) -> UserIdentity:
    """
    Extract user identity from token payload.
    
    Args:
        token_payload: Decoded JWT payload
        
    Returns:
        UserIdentity object
    """
    return UserIdentity(
        user_id=token_payload.get("sub") or token_payload.get("oid"),
        email=token_payload.get("email") or token_payload.get("preferred_username"),
        name=token_payload.get("name"),
        roles=[UserRole(r) for r in token_payload.get("roles", [])],
        tenant_id=token_payload.get("tenant_id") or token_payload.get("tid"),
        spaces=token_payload.get("spaces", []),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> UserIdentity:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        UserIdentity object
        
    Raises:
        HTTPException: If authentication fails
    """
    if not auth_config.auth_enabled:
        # Development mode: return mock user
        return UserIdentity(
            user_id="dev-user-123",
            email="dev@example.com",
            name="Development User",
            roles=[UserRole.ADMIN],
            tenant_id="dev-tenant-123",
            spaces=["*"],  # Access all spaces in dev mode
        )
    
    token = credentials.credentials
    payload = decode_token(token)
    return extract_user_identity(payload)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[UserIdentity]:
    """
    Get current user if authenticated, None otherwise.
    
    Useful for endpoints that support both authenticated and anonymous access.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_roles: List[UserRole]):
    """
    Dependency to require specific roles.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: UserIdentity = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    async def role_checker(user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Requires one of roles: {[r.value for r in required_roles]}"
            )
        return user
    
    return role_checker


def require_space_access(space_id: str):
    """
    Dependency to require access to a specific space.
    
    Usage:
        @app.get("/spaces/{space_id}/documents")
        async def get_documents(
            space_id: str,
            user: UserIdentity = Depends(require_space_access(space_id))
        ):
            ...
    """
    async def space_checker(user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
        # Admin has access to all spaces
        if UserRole.ADMIN in user.roles:
            return user
        
        # Wildcard access (dev mode)
        if "*" in user.spaces:
            return user
        
        # Check explicit space access
        if space_id not in user.spaces:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to space: {space_id}"
            )
        
        return user
    
    return space_checker


def require_tenant_match(tenant_id: str):
    """
    Dependency to require tenant ID match.
    
    Usage:
        @app.get("/tenants/{tenant_id}/data")
        async def get_tenant_data(
            tenant_id: str,
            user: UserIdentity = Depends(require_tenant_match(tenant_id))
        ):
            ...
    """
    async def tenant_checker(user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
        # Admin can access all tenants
        if UserRole.ADMIN in user.roles:
            return user
        
        if user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: tenant mismatch"
            )
        
        return user
    
    return tenant_checker


def require_owner_or_admin(resource_user_id: str):
    """
    Dependency to require resource ownership or admin role.
    
    Usage:
        @app.delete("/documents/{doc_id}")
        async def delete_document(
            doc_id: str,
            user: UserIdentity = Depends(require_owner_or_admin(doc.user_id))
        ):
            ...
    """
    async def owner_checker(user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
        if UserRole.ADMIN in user.roles:
            return user
        
        if user.user_id != resource_user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: not resource owner"
            )
        
        return user
    
    return owner_checker


# Convenience decorators for common combinations
async def require_admin(user: UserIdentity = Depends(require_role([UserRole.ADMIN]))) -> UserIdentity:
    """Require admin role."""
    return user


async def require_user_or_admin(
    user: UserIdentity = Depends(require_role([UserRole.USER, UserRole.ADMIN]))
) -> UserIdentity:
    """Require user or admin role."""
    return user


async def require_authenticated(user: UserIdentity = Depends(get_current_user)) -> UserIdentity:
    """Require any authenticated user."""
    return user
