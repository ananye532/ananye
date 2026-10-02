"""Orchestrates the NLP functions into one explainable analysis result."""

from __future__ import annotations

from ..nlp.entities import extract_entities
from ..nlp.keywords import rank_keywords, term_set, tfidf_cosine
from ..nlp.matching import compare_skills, cosine_metric, keyword_coverage
from ..nlp.preprocessing import clean_text
from ..nlp.sections import detect_sections
from ..nlp.skills import TAXONOMY_VERSION, extract_skills
from ..nlp.suggestions import generate_suggestions

DISCLAIMER = (
    "These numbers measure textual overlap between your resume and this job description. "
    "They do not predict whether you will be interviewed or hired, and they should not be "
    "used to rank or reject candidates."
)

LIMITATIONS = [
    "Synonyms and paraphrases are only recognised when listed in the skill taxonomy.",
    "Depth, recency and context of experience are not measured; negations ('no Java') are not understood.",
    "Skills outside the curated taxonomy are invisible to skill extraction.",
    "PDF extraction can scramble multi-column layouts and cannot read text inside images.",
    "Named entities are shown for reference only and may be mislabelled.",
    "English only.",
]


def analyze(resume_text: str, job_text: str, top_n_keywords: int = 25) -> dict:
    resume_text, job_text = clean_text(resume_text), clean_text(job_text)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    skills_cmp = compare_skills(resume_skills, job_skills)

    job_keywords = rank_keywords(job_text, top_n=top_n_keywords)
    kw_cmp = keyword_coverage(job_keywords, term_set(resume_text))
    cosine = cosine_metric(tfidf_cosine(resume_text, job_text))

    sections = detect_sections(resume_text)
    suggestions = generate_suggestions(resume_text, sections, skills_cmp, kw_cmp)

    return {
        "taxonomy_version": TAXONOMY_VERSION,
        "disclaimer": DISCLAIMER,
        "metrics": {
            "skill_coverage": {k: skills_cmp[k] for k in ("value", "matched_count", "required_count", "definition")},
            "keyword_coverage": {k: kw_cmp[k] for k in ("value", "present_count", "total", "definition")},
            "cosine_similarity": cosine,
        },
        "skills": {
            "matched": skills_cmp["matched"],
            "missing": skills_cmp["missing"],
            "missing_by_category": skills_cmp["missing_by_category"],
            "resume_only": skills_cmp["resume_only"],
            "resume_details": [h.to_dict() for h in resume_skills.values()],
            "job_details": [h.to_dict() for h in job_skills.values()],
        },
        "keywords": {"job_top": kw_cmp["keywords"], "missing": kw_cmp["missing"]},
        "sections": sections,
        "entities": extract_entities(resume_text),
        "suggestions": suggestions,
        "limitations": LIMITATIONS,
        "stats": {"resume_words": len(resume_text.split()), "job_words": len(job_text.split())},
    }
