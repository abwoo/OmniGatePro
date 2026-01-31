import pytest
from fastapi.testclient import TestClient
from api.main import app
from db.session import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_and_login():
    # Register
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    register_data = {
        "email": email,
        "password": "testpassword",
        "user_id": f"user_{uuid.uuid4().hex[:8]}"
    }
    response = client.post("/v1/auth/register", json=register_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login
    login_data = {
        "username": email,
        "password": "testpassword"
    }
    response = client.post("/v1/auth/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get Me
    response = client.get("/v1/user/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email
