from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_api_test():
    response = client.get("/test")
    assert response.status_code == 200
    assert "message" in response.json()
