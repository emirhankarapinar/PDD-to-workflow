"""
Tests for health check endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "PDD Forge"


def test_upload_invalid_file():
    """Test upload with non-PDF file."""
    # Create a fake text file
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]
