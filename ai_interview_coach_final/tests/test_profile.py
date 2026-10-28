import os

def get_auth_headers(client):
    email = f"prof_{os.urandom(4).hex()}@example.com"
    reg = client.post("/api/auth/register", json={
        "name": "Profile Candidate",
        "email": email,
        "password": "password123"
    })
    if reg.status_code != 201:
        print("GET_AUTH_HEADERS REGISTER ERROR:", reg.status_code, reg.text)
    assert reg.status_code == 201

    resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    if resp.status_code != 200:
        print("GET_AUTH_HEADERS LOGIN ERROR:", resp.status_code, resp.text)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_and_update_profile(client):
    headers = get_auth_headers(client)
    
    get_resp = client.get("/api/profile", headers=headers)
    assert get_resp.status_code == 200
    p = get_resp.json()
    assert "target_role" in p

    update_payload = {
        "full_name": "Updated Profile Name",
        "education": "M.Tech in Software Engineering",
        "skills": ["Java", "Spring Boot", "SQL", "Docker", "AWS"],
        "programming_languages": ["Java", "Python", "SQL"],
        "experience_level": "Junior",
        "target_role": "Java Developer",
        "preferred_interview_type": "Technical",
        "preferred_difficulty": "Hard"
    }
    put_resp = client.put("/api/profile", json=update_payload, headers=headers)
    assert put_resp.status_code == 200
    updated_p = put_resp.json()
    assert updated_p["full_name"] == "Updated Profile Name"
    assert updated_p["education"] == "M.Tech in Software Engineering"

def test_skill_gap_analysis(client):
    headers = get_auth_headers(client)
    resp = client.get("/api/profile/skill-gap", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "target_role" in data
    assert "strong_skills" in data
