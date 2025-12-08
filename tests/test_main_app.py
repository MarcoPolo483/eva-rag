"""Tests for main FastAPI application."""
import pytest
from fastapi.testclient import TestClient

from eva_rag.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint returns correct structure."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "eva-rag"
    assert body["version"] == "0.1.0"
    assert len(body) == 3


def test_openapi_schema(client: TestClient) -> None:
    """Test OpenAPI schema is generated."""
    response = client.get("/api/v1/openapi.json")
    
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "EVA RAG Engine"
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/rag/ingest" in schema["paths"]


def test_docs_ui_accessible(client: TestClient) -> None:
    """Test Swagger UI is accessible."""
    response = client.get("/api/v1/docs")
    
    assert response.status_code == 200
    assert b"swagger" in response.content.lower()


def test_cors_enabled(client: TestClient) -> None:
    """Test CORS middleware is configured."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    assert response.status_code == 200


def test_404_not_found(client: TestClient) -> None:
    """Test 404 for non-existent endpoint."""
    response = client.get("/api/v1/nonexistent")
    
    assert response.status_code == 404
