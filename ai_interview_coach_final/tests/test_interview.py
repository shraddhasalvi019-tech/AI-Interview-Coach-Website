import os

def get_auth_headers(client):
    email = f"interview_user_{os.urandom(4).hex()}@example.com"
    client.post("/api/auth/register", json={
        "name": "Interview Candidate",
        "email": email,
        "password": "password123"
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_full_interview_flow(client):
    headers = get_auth_headers(client)

    # 1. Create Interview
    create_payload = {
        "target_role": "Java Developer",
        "interview_type": "Technical",
        "difficulty": "Medium",
        "total_questions": 2
    }
    create_resp = client.post("/api/interviews", json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    interview = create_resp.json()
    interview_id = interview["id"]
    assert interview["status"] == "configured"

    # 2. Start Interview & Get Q1
    start_resp = client.post(f"/api/interviews/{interview_id}/start", headers=headers)
    assert start_resp.status_code == 200
    q1 = start_resp.json()
    assert "question_text" in q1

    # 3. Submit Answer 1
    ans1_payload = {
        "answer_text": "HashMap uses hashing and array of bucket nodes. Collisions are handled via LinkedList and Red-Black Trees in Java 8+."
    }
    ans1_resp = client.post(f"/api/interviews/{interview_id}/answer?question_id={q1['id']}", json=ans1_payload, headers=headers)
    assert ans1_resp.status_code == 200
    res1 = ans1_resp.json()
    assert "evaluation" in res1

    # 4. Answer next question if available
    if res1.get("next_question"):
        q2 = res1["next_question"]
        ans2_payload = {
            "answer_text": "Single inheritance is class A to class B. Multilevel is class A to B to C. Interfaces allow multiple inheritance."
        }
        ans2_resp = client.post(f"/api/interviews/{interview_id}/answer?question_id={q2['id']}", json=ans2_payload, headers=headers)
        assert ans2_resp.status_code == 200

    # 5. Complete Interview
    comp_resp = client.post(f"/api/interviews/{interview_id}/complete", headers=headers)
    assert comp_resp.status_code == 200
    completed_interview = comp_resp.json()
    assert completed_interview["status"] == "completed"

    # 6. Check Feedback API
    fb_resp = client.get(f"/api/interviews/{interview_id}/feedback", headers=headers)
    assert fb_resp.status_code == 200
    fb = fb_resp.json()
    assert "overall_summary" in fb

    # 7. Check Detailed Report API
    rep_resp = client.get(f"/api/reports/{interview_id}", headers=headers)
    assert rep_resp.status_code == 200
    rep = rep_resp.json()
    assert "overall_score" in rep
