from app.nlp.keywords import rank_keywords, term_set, tfidf_cosine
from app.nlp.matching import compare_skills, keyword_coverage
from app.nlp.sections import detect_sections
from app.nlp.skills import extract_skills
from app.services.analyzer import DISCLAIMER, analyze

from .conftest import JOB_TEXT, RESUME_TEXT


def test_compare_skills_sets_and_coverage():
    cmp = compare_skills(extract_skills("Python, Docker, Go"), extract_skills("Python, Kafka, Docker, Terraform"))
    assert cmp["matched"] == ["Docker", "Python"]
    assert cmp["missing"] == ["Apache Kafka", "Terraform"]
    assert cmp["resume_only"] == ["Go"]
    assert cmp["value"] == 0.5


def test_skill_coverage_is_null_when_job_has_no_skills():
    assert compare_skills(extract_skills("Python"), {})["value"] is None


def test_cosine_bounds():
    assert tfidf_cosine(RESUME_TEXT, RESUME_TEXT) == 1.0
    assert tfidf_cosine("Python developer building APIs", "Pastry chef baking croissants") == 0.0
    assert tfidf_cosine("", JOB_TEXT) == 0.0
    assert 0.0 < tfidf_cosine(RESUME_TEXT, JOB_TEXT) < 1.0


def test_related_resume_scores_higher_than_unrelated():
    unrelated = "Pastry chef. Baked croissants and managed a bakery kitchen for ten years."
    assert tfidf_cosine(RESUME_TEXT, JOB_TEXT) > tfidf_cosine(unrelated, JOB_TEXT)


def test_keywords_are_ranked_and_normalized():
    kws = rank_keywords(JOB_TEXT)
    assert kws[0].weight == 1.0
    assert all(0 < k.weight <= 1.0 for k in kws)
    terms = [k.term for k in kws]
    assert "kafka" in terms and "machine learning" in terms
    assert "experience" not in terms  # domain stop word
    assert "machine" not in terms  # redundant with the bigram


def test_bigrams_do_not_cross_removed_words():
    assert "care rest" not in term_set("We care about the rest of it.")


def test_keyword_coverage():
    kws = rank_keywords("Kafka streaming. Kafka consumers. Terraform modules.")
    cov = keyword_coverage(kws, term_set("I built kafka consumers."))
    present = {r["term"] for r in cov["keywords"] if r["in_resume"]}
    assert "kafka" in present and "terraform module" in cov["missing"]
    assert 0 < cov["value"] < 1


def test_sections_and_contact_flags():
    sec = detect_sections(RESUME_TEXT)
    assert [s["name"] for s in sec["detected"]] == ["Summary", "Experience", "Education", "Skills"]
    assert sec["missing_recommended"] == []
    assert sec["contact"] == {"email": True, "phone": True, "linkedin": True, "github": False}


def test_heading_variants_and_missing_sections():
    sec = detect_sections("Name\nPROFESSIONAL EXPERIENCE:\nstuff\nTechnical Skills\nPython\nDates 2019-2023")
    assert [s["name"] for s in sec["detected"]] == ["Experience", "Skills"]
    assert sec["missing_recommended"] == ["Education"]
    assert sec["contact"]["phone"] is False  # a year range is not a phone number


def test_full_analysis_is_explainable_and_has_no_composite_score():
    a = analyze(RESUME_TEXT, JOB_TEXT)
    assert a["disclaimer"] == DISCLAIMER
    assert set(a["metrics"]) == {"skill_coverage", "keyword_coverage", "cosine_similarity"}
    assert all("definition" in m for m in a["metrics"].values())
    assert "Apache Kafka" in a["skills"]["missing"] and "Python" in a["skills"]["matched"]
    assert {s["rule"] for s in a["suggestions"]} >= {"missing_skills"}
    assert a["limitations"]


def test_suggestions_flag_missing_sections_and_contact():
    a = analyze("Python developer. Built things with Docker. " * 5, JOB_TEXT)
    rules = {s["rule"] for s in a["suggestions"]}
    assert {"missing_section", "missing_email", "quantify_impact", "too_short"} <= rules


def test_keywords_still_work_with_blank_fallback_pipeline():
    import spacy

    terms = [k.term for k in rank_keywords(JOB_TEXT, nlp=spacy.blank("en"))]
    assert "kafka" in terms and "terraform" in terms
