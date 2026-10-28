import os

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"

def test_register_user(client):
    email = f"test_user_{os.urandom(4).hex()}@example.com"
    payload = {
        "name": "Test Candidate",
        "email": email,
        "password": "password123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email

def test_login_user(client):
    email = f"login_user_{os.urandom(4).hex()}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "name": "Login User",
        "email": email,
        "password": "password123"
    })
    assert reg_resp.status_code == 201

    response = client.post("/api/auth/login", json={
        "email": email,
        "password": "password123"
    })
    if response.status_code != 200:
        print("LOGIN ERROR RESPONSE:", response.status_code, response.text)
    assert response.status_code == 200
