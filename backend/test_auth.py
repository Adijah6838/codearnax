from fastapi.testclient import TestClient
from app.main import app
import random

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_user():
    email = f"test{random.randint(1000,9999)}@example.com"
    payload = {
        "email": email,
        "password": "Password123",
        "full_name": "Test User",
        "role": "Candidate"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == email

def test_login_and_protected_route():
    email = f"test{random.randint(1000,9999)}@example.com"
    client.post("/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Test User",
        "role": "Candidate"
    })
    
    login_response = client.post("/auth/login", json={
        "email": email,
        "password": "Password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email
