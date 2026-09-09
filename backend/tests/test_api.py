import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8999

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Devil's Advocate" in response.json()["message"]
