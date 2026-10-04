from .conftest import register


def _paste(client, auth, text, title="Resume"):
    r = client.post("/api/resumes/paste", json={"title": title, "text": text}, headers=auth)
    assert r.status_code == 201, r.text
    return r.json()


def test_auth_flow(client):
    headers = register(client)
    assert client.get("/api/auth/me", headers=headers).json()["email"] == "ada@example.com"
    assert client.post("/api/auth/register", json={"email": "ADA@example.com", "name": "x", "password": "12345678"}).status_code == 409
    assert client.post("/api/auth/login", json={"email": "ada@example.com", "password": "wrong-pass"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "ada@example.com", "password": "correct-horse"}).status_code == 200
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_paste_analyze_history_dashboard(client, auth, strong_text):
    resume = _paste(client, auth, strong_text)
    assert resume["parsed"]["contact"]["name"] == "Jordan Lee"
    r = client.post("/api/analyses", json={"resume_id": resume["id"]}, headers=auth)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["overall_score"] == body["result"]["overall"]["score"]
    assert body["result"]["provider"]["name"] == "deterministic"
    assert body["match_score"] is None

    jd = "Backend Engineer. Requirements: 3+ years of experience with Python, Kubernetes and GraphQL. Strong communication skills."
    r2 = client.post("/api/analyses", json={"resume_id": resume["id"], "job_description": jd}, headers=auth)
    assert r2.status_code == 201
    assert r2.json()["match_score"] is not None

    hist = client.get("/api/analyses", headers=auth).json()
    assert [h["id"] for h in hist] == [r2.json()["id"], body["id"]]
    dash = client.get("/api/dashboard", headers=auth).json()
    assert dash["analysis_count"] == 2 and dash["resume_count"] == 1
    lst = client.get("/api/resumes", headers=auth).json()
    assert lst[0]["analysis_count"] == 2

    cmp = client.post("/api/compare", json={"a": body["id"], "b": r2.json()["id"]}, headers=auth).json()
    assert {row["key"] for row in cmp["subscores"]} >= {"ats", "impact"}


def test_short_jd_rejected(client, auth, strong_text):
    resume = _paste(client, auth, strong_text)
    r = client.post("/api/analyses", json={"resume_id": resume["id"], "job_description": "python"}, headers=auth)
    assert r.status_code == 422


def test_isolation_between_users(client, auth, strong_text):
    resume = _paste(client, auth, strong_text)
    a = client.post("/api/analyses", json={"resume_id": resume["id"]}, headers=auth).json()
    other = register(client, "eve@example.com")
    assert client.get(f"/api/resumes/{resume['id']}", headers=other).status_code == 404
    assert client.get(f"/api/analyses/{a['id']}", headers=other).status_code == 404
    assert client.post("/api/analyses", json={"resume_id": resume["id"]}, headers=other).status_code == 404
    assert client.delete(f"/api/resumes/{resume['id']}", headers=other).status_code == 404


def test_upload_validation(client, auth, strong_text):
    r = client.post("/api/resumes/upload", files={"file": ("cv.exe", b"MZ", "application/octet-stream")}, headers=auth)
    assert r.status_code == 415
    r = client.post("/api/resumes/upload", files={"file": ("cv.pdf", b"not a pdf at all" * 20, "application/pdf")}, headers=auth)
    assert r.status_code == 422
    r = client.post("/api/resumes/upload", files={"file": ("cv.txt", strong_text.encode(), "text/plain")},
                    data={"title": "My CV"}, headers=auth)
    assert r.status_code == 201 and r.json()["title"] == "My CV"


def test_cascade_delete_and_account_deletion(client, auth, strong_text):
    resume = _paste(client, auth, strong_text)
    client.post("/api/analyses", json={"resume_id": resume["id"]}, headers=auth)
    assert client.delete(f"/api/resumes/{resume['id']}", headers=auth).status_code == 204
    assert client.get("/api/analyses", headers=auth).json() == []
    assert client.delete("/api/me", headers=auth).status_code == 204
    assert client.get("/api/auth/me", headers=auth).status_code == 401


def test_profile_preferences_password_and_rewrite(client, auth):
    r = client.patch("/api/me", json={"headline": "Backend engineer", "target_role": "Backend Engineer"}, headers=auth)
    assert r.json()["target_role"] == "Backend Engineer"
    r = client.put("/api/me/preferences", json={"ai_enhancement": False, "theme": "dark"}, headers=auth)
    assert r.json()["preferences"]["theme"] == "dark"
    assert client.post("/api/me/password", json={"current_password": "nope", "new_password": "newpassword1"}, headers=auth).status_code == 400
    assert client.post("/api/me/password", json={"current_password": "correct-horse", "new_password": "newpassword1"}, headers=auth).status_code == 204
    r = client.post("/api/studio/rewrite", json={"bullet": "Responsible for the website"}, headers=auth)
    assert r.json()["options"][0].startswith("Owned")
    assert client.get("/api/meta").json()["ai_provider"] == "deterministic"
