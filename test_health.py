from fastapi.testclient import TestClient
from main import app

def test_health_endpoint():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["version"] == "5.0.0"

def test_home_page_is_served():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "GHOST BOTS" in response.text
