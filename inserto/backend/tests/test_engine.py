from datetime import date

from app.engine.analyzer import analyze, grade
from app.engine.checks import is_quantified
from app.engine.extract import ExtractionError, clean_text, extract
from app.engine.matching import requirement_lines
from app.engine.parser import parse
from app.engine.skills import extract_skills
from app.engine.studio import rewrite

TODAY = date(2026, 10, 1)


def test_parser_recovers_contact_roles_and_education(strong_text):
    p = parse(strong_text, TODAY)
    assert p.contact.name == "Jordan Lee"
    assert p.contact.email == "jordan.lee@example.com"
    assert p.contact.location == "San Francisco, CA"
    assert any("linkedin" in link for link in p.contact.links)
    assert [r.company for r in p.roles] == ["Stripe", "Dropbox", "Microsoft"]
    assert p.roles[0].is_current and p.roles[0].duration_months == 58
    assert p.education[0].degree_level == "Bachelor's"
    assert p.education[0].gpa == "3.8/4.0"
    assert "Kubernetes" in p.skills_listed


def test_skill_extraction_handles_symbols_and_ambiguous_words():
    names = {h.name for h in extract_skills("Wrote C++ and C# services; used Node.js. Go is great. We go home.")}
    assert {"C++", "C#", "Node.js", "Go"} <= names
    assert "C" not in names
    names = {h.name for h in extract_skills("I like to go running and rest.")}
    assert "Go" not in names and "REST APIs" not in names


def test_quantification_ignores_bare_years():
    assert is_quantified("Cut costs by 30%")
    assert is_quantified("Served 2M users")
    assert is_quantified("Doubled throughput")
    assert not is_quantified("Joined the team in 2021")


def test_strong_resume_scores_higher_than_weak(strong_text, weak_text):
    strong = analyze(strong_text, today=TODAY)
    weak = analyze(weak_text, today=TODAY)
    assert strong.overall.score >= 80
    assert weak.overall.score < 45
    assert weak.recommendations[0].priority == "critical"
    assert strong.experience.total_years > 6


def test_job_match_reports_gaps(strong_text):
    jd = """Senior Backend Engineer
Requirements:
- 5+ years of experience with Python or Go
- Experience with Kubernetes and AWS
- Knowledge of GraphQL and Elasticsearch is required"""
    r = analyze(strong_text, job_description=jd, today=TODAY)
    assert r.match is not None
    assert "GraphQL" in r.match.missing_skills
    assert "Kubernetes" in r.match.matched_skills
    assert r.match.years_required == 5
    assert any(s.key == "match" for s in r.subscores)
    assert len(requirement_lines(jd)) == 3


def test_rewrite_never_invents_numbers():
    r = rewrite("I was responsible for the company website")
    assert r is not None
    assert r.improved.startswith("Owned")
    assert r.needs_input and "[" in r.improved
    assert rewrite("Built REST APIs serving 30M requests/day") is None


def test_grade_bands():
    assert grade(95)[0] == "A+"
    assert grade(10)[0] == "D"


def test_extract_rejects_unknown_types_and_short_text():
    try:
        extract("resume.exe", b"MZ....")
    except ExtractionError as e:
        assert e.code == "unsupported"
    else:
        raise AssertionError
    try:
        extract("resume.txt", b"too short")
    except ExtractionError as e:
        assert e.code == "no_text"
    else:
        raise AssertionError


def test_clean_text_normalizes_bullets():
    assert clean_text(" Item\r\n\n\n\nNext") == "• Item\n\nNext"


def test_docx_extraction(strong_text):
    import io

    import docx

    d = docx.Document()
    for line in strong_text.splitlines():
        d.add_paragraph(line)
    buf = io.BytesIO()
    d.save(buf)
    ex = extract("cv.docx", buf.getvalue())
    assert ex.source == "docx"
    assert "Stripe" in ex.text


def test_ai_enhancement_is_merged_without_changing_scores(client, auth, strong_text, monkeypatch):
    from app import services
    from app.ai.base import AIEnhancement, AIProvider

    class FakeProvider(AIProvider):
        name = "fake"

        @property
        def available(self) -> bool:
            return True

        def enhance(self, resume_text, analysis, job_description):
            return AIEnhancement(first_impression="Reads well.", strengths=["Clear impact"])

        def rewrite_bullet(self, bullet, context):
            return [bullet]

    monkeypatch.setattr(services, "get_provider", lambda: FakeProvider())
    rid = client.post("/api/resumes/paste", json={"title": "r", "text": strong_text}, headers=auth).json()["id"]
    body = client.post("/api/analyses", json={"resume_id": rid}, headers=auth).json()
    baseline = analyze(strong_text)
    assert body["result"]["ai"]["first_impression"] == "Reads well."
    assert body["result"]["provider"] == {"name": "fake", "ai_enhanced": True, "note": None}
    assert body["overall_score"] == baseline.overall.score
