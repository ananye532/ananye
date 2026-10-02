"""Transparent resume <-> job-description comparison metrics.

Three metrics are reported separately, each with its definition. They are
deliberately never combined into one "match score": see docs/LIMITATIONS.md.
"""

from __future__ import annotations

from .keywords import Keyword
from .skills import SkillHit, group_by_category


def compare_skills(resume: dict[str, SkillHit], job: dict[str, SkillHit]) -> dict:
    r, j = set(resume), set(job)
    matched, missing, extra = r & j, j - r, r - j
    coverage = round(len(matched) / len(j), 4) if j else None
    return {
        "value": coverage,
        "matched": sorted(matched, key=str.lower),
        "missing": sorted(missing, key=str.lower),
        "missing_by_category": group_by_category(missing),
        "resume_only": sorted(extra, key=str.lower),
        "matched_count": len(matched),
        "required_count": len(j),
        "definition": "matched JD skills / all skills found in the JD (taxonomy-based). "
        "Null when the JD mentions no taxonomy skills.",
    }


def keyword_coverage(job_keywords: list[Keyword], resume_terms: set[str]) -> dict:
    rows = [{"term": k.term, "weight": k.weight, "in_resume": k.term in resume_terms} for k in job_keywords]
    present = sum(r["in_resume"] for r in rows)
    return {
        "value": round(present / len(rows), 4) if rows else None,
        "present_count": present,
        "total": len(rows),
        "keywords": rows,
        "missing": [r["term"] for r in rows if not r["in_resume"]],
        "definition": "share of the JD's top TF-IDF terms (lemmatized unigrams/bigrams) that also appear in the resume.",
    }


def cosine_metric(value: float) -> dict:
    return {
        "value": value,
        "definition": "cosine of the angle between the TF-IDF vectors of the resume and the JD "
        "(0 = no shared weighted terms, 1 = identical term distribution). "
        "Measures vocabulary overlap, not suitability.",
    }
