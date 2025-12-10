"""Tests for Space API endpoints."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from eva_rag.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_space():
    """Test creating a new Space."""
    space_data = {
        "name": f"Test-Space-{uuid4().hex[:8]}",
        "description": "Test sandbox space",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
        "quotas": {
            "compute_units": 1000,
            "storage_gb": 100,
            "ai_calls_per_month": 10000,
            "max_documents": 10000,
            "max_users": 25,
        },
        "metadata": {
            "department": "Test",
            "environment": "test",
        },
    }
    
    response = client.post("/api/v1/spaces", json=space_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == space_data["name"]
    assert data["description"] == space_data["description"]
    assert data["type"] == "sandbox"
    assert data["status"] == "active"
    assert "id" in data
    assert "space_id" in data
    assert data["quotas"]["max_users"] == 25


def test_create_space_duplicate_name():
    """Test creating a Space with duplicate name fails."""
    space_name = f"Duplicate-Space-{uuid4().hex[:8]}"
    space_data = {
        "name": space_name,
        "description": "First space",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    # Create first space
    response1 = client.post("/api/v1/spaces", json=space_data)
    assert response1.status_code == 201
    
    # Try to create duplicate
    response2 = client.post("/api/v1/spaces", json=space_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_get_space():
    """Test getting a Space by ID."""
    # Create space first
    space_data = {
        "name": f"Get-Test-Space-{uuid4().hex[:8]}",
        "description": "Test space for GET",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    create_response = client.post("/api/v1/spaces", json=space_data)
    assert create_response.status_code == 201
    space_id = create_response.json()["id"]
    
    # Get space
    response = client.get(f"/api/v1/spaces/{space_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == space_id
    assert data["name"] == space_data["name"]


def test_get_space_not_found():
    """Test getting a non-existent Space returns 404."""
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/spaces/{fake_id}")
    assert response.status_code == 404


def test_list_spaces():
    """Test listing Spaces."""
    response = client.get("/api/v1/spaces")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_spaces_with_filters():
    """Test listing Spaces with filters."""
    # Create a sandbox space
    space_data = {
        "name": f"Filter-Test-Space-{uuid4().hex[:8]}",
        "description": "Test space for filtering",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    client.post("/api/v1/spaces", json=space_data)
    
    # Filter by type
    response = client.get("/api/v1/spaces?type=sandbox&limit=10")
    assert response.status_code == 200
    spaces = response.json()
    assert all(space["type"] == "sandbox" for space in spaces)


def test_update_space():
    """Test updating a Space."""
    # Create space
    space_data = {
        "name": f"Update-Test-Space-{uuid4().hex[:8]}",
        "description": "Original description",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    create_response = client.post("/api/v1/spaces", json=space_data)
    space_id = create_response.json()["id"]
    
    # Update space
    update_data = {
        "description": "Updated description",
        "status": "suspended",
    }
    
    response = client.patch(f"/api/v1/spaces/{space_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["status"] == "suspended"


def test_delete_space():
    """Test deleting (archiving) a Space."""
    # Create space
    space_data = {
        "name": f"Delete-Test-Space-{uuid4().hex[:8]}",
        "description": "Space to delete",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    create_response = client.post("/api/v1/spaces", json=space_data)
    space_id = create_response.json()["id"]
    
    # Delete space
    response = client.delete(f"/api/v1/spaces/{space_id}")
    assert response.status_code == 204
    
    # Verify space is archived
    get_response = client.get(f"/api/v1/spaces/{space_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "archived"


def test_get_space_by_name():
    """Test getting a Space by name."""
    # Create space
    space_name = f"ByName-Test-Space-{uuid4().hex[:8]}"
    space_data = {
        "name": space_name,
        "description": "Test space for name lookup",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
    }
    
    create_response = client.post("/api/v1/spaces", json=space_data)
    assert create_response.status_code == 201
    
    # Get by name
    response = client.get(f"/api/v1/spaces/name/{space_name}")
    assert response.status_code == 200
    assert response.json()["name"] == space_name


def test_space_quotas_defaults():
    """Test that Space quotas have sensible defaults."""
    space_data = {
        "name": f"Quota-Test-Space-{uuid4().hex[:8]}",
        "description": "Test default quotas",
        "type": "sandbox",
        "owner_id": str(uuid4()),
        "owner_email": "test@example.com",
        # No quotas specified
    }
    
    response = client.post("/api/v1/spaces", json=space_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["quotas"]["compute_units"] == 1000
    assert data["quotas"]["storage_gb"] == 100
    assert data["quotas"]["ai_calls_per_month"] == 10000
    assert data["quotas"]["max_documents"] == 10000
    assert data["quotas"]["max_users"] == 100
