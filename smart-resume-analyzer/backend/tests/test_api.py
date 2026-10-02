import uuid

from .conftest import JOB_TEXT, make_pdf


def upload(client, headers, data=None, name="resume.pdf", ctype="application/pdf"):
    return client.post("/api/resumes", headers=headers, files={"file": (name, data or make_pdf(), ctype)})


def full_flow(client, headers):
    resume = upload(client, headers).json()
    job = client.post("/api/jobs", headers=headers, json={"title": "Backend Engineer", "description": JOB_TEXT}).json()
    r = client.post("/api/analyses", headers=headers, json={"resume_id": resume["id"], "job_id": job["id"]})
    assert r.status_code == 201, r.text
    return resume, job, r.json()


def test_health_and_security_headers(client):
    r = client.get("/api/health")
    assert r.json() == {"status": "ok"}
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "no-store"


def test_register_returns_key_once_and_rejects_duplicates(client):
    r = client.post("/api/users", json={"email": "A@Example.com"})
    assert r.status_code == 201 and len(r.json()["api_key"]) >= 40
    assert client.post("/api/users", json={"email": "a@example.com"}).status_code == 409
    assert client.post("/api/users", json={"email": "not-an-email"}).status_code == 422


def test_auth_required(client):
    assert client.get("/api/resumes").status_code == 401
    assert client.get("/api/resumes", headers={"X-API-Key": "wrong"}).status_code == 401


def test_upload_resume(client, auth):
    h = auth()
    r = upload(client, h, name="../../etc/My Résumé.pdf")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["filename"] == "My R_sum_.pdf"
    assert body["page_count"] == 1
    assert {"Python", "Docker"} <= {s["name"] for s in body["skills"]}
    assert "Experience" in [s["name"] for s in body["sections"]["detected"]]
    assert [x["id"] for x in client.get("/api/resumes", headers=h).json()] == [body["id"]]


def test_upload_validation(client, auth):
    h = auth()
    cases = [
        (dict(name="resume.docx"), 415, "bad_extension"),
        (dict(ctype="text/plain"), 415, "bad_content_type"),
        (dict(data=b"MZ\x90\x00 executable"), 422, "not_pdf"),
        (dict(data=b"%PDF-" + b"0" * (1024 * 1024)), 413, "too_large"),
        (dict(data=make_pdf(pages=4)), 422, "too_many_pages"),
    ]
    for kwargs, status, code in cases:
        r = upload(client, h, **kwargs)
        assert r.status_code == status, (kwargs.keys(), r.text)
        assert r.json()["detail"]["code"] == code


def test_job_validation(client, auth):
    h = auth()
    assert client.post("/api/jobs", headers=h, json={"title": "x", "description": "too short"}).status_code == 422
    r = client.post("/api/jobs", headers=h, json={"title": "Backend", "description": JOB_TEXT})
    assert r.status_code == 201
    assert "Terraform" in {s["name"] for s in r.json()["skills"]}


def test_analysis_and_reports(client, auth):
    h = auth()
    _, _, analysis = full_flow(client, h)
    metrics = analysis["result"]["metrics"]
    assert 0 < metrics["skill_coverage"]["value"] < 1
    assert "Apache Kafka" in analysis["result"]["skills"]["missing"]
    assert client.get(f"/api/analyses/{analysis['id']}", headers=h).json()["id"] == analysis["id"]

    md = client.get(f"/api/analyses/{analysis['id']}/report?format=md", headers=h)
    assert md.status_code == 200 and md.headers["content-type"].startswith("text/markdown")
    assert "attachment" in md.headers["content-disposition"]
    assert "do not predict whether you will be interviewed or hired" in md.text
    assert "Limitations of automated resume matching" in md.text

    js = client.get(f"/api/analyses/{analysis['id']}/report?format=json", headers=h)
    assert js.json()["meta"]["job_title"] == "Backend Engineer"
    assert client.get(f"/api/analyses/{analysis['id']}/report?format=exe", headers=h).status_code == 422


def test_users_cannot_access_each_others_data(client, auth):
    alice, bob = auth("alice@example.com"), auth("bob@example.com")
    resume, job, analysis = full_flow(client, alice)
    assert client.get(f"/api/resumes/{resume['id']}", headers=bob).status_code == 404
    assert client.get(f"/api/analyses/{analysis['id']}/report", headers=bob).status_code == 404
    assert client.delete(f"/api/jobs/{job['id']}", headers=bob).status_code == 404
    r = client.post("/api/analyses", headers=bob, json={"resume_id": resume["id"], "job_id": job["id"]})
    assert r.status_code == 404
    assert client.get(f"/api/resumes/{uuid.uuid4()}", headers=alice).status_code == 404


def test_delete_resume_cascades_to_analyses(client, auth):
    h = auth()
    resume, _, analysis = full_flow(client, h)
    assert client.delete(f"/api/resumes/{resume['id']}", headers=h).status_code == 204
    assert client.get(f"/api/analyses/{analysis['id']}", headers=h).status_code == 404


def test_delete_account_removes_everything(client, auth):
    h = auth()
    full_flow(client, h)
    assert client.delete("/api/users/me", headers=h).status_code == 204
    assert client.get("/api/resumes", headers=h).status_code == 401
    assert client.post("/api/users", json={"email": "jane@example.com"}).status_code == 201
