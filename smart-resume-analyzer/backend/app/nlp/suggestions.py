"""Deterministic, rule-based improvement suggestions. Each suggestion names its rule."""

from __future__ import annotations

import re

from .sections import section_text
from .skills import SKILLS

_NUMBER = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|percent|x\b|k\b|m\b|ms\b)|\$\s?\d|\b\d{2,}\b", re.IGNORECASE)

MIN_WORDS, MAX_WORDS = 250, 1000


def _s(rule: str, severity: str, message: str) -> dict:
    return {"rule": rule, "severity": severity, "message": message}


def generate_suggestions(resume_text: str, sections: dict, skills_cmp: dict, keyword_cmp: dict) -> list[dict]:
    out: list[dict] = []

    missing_hard = [s for s in skills_cmp["missing"] if SKILLS[s].category != "Soft Skills"]
    missing_soft = [s for s in skills_cmp["missing"] if SKILLS[s].category == "Soft Skills"]
    if missing_hard:
        out.append(
            _s(
                "missing_skills",
                "important",
                "The job description mentions skills not found in your resume: "
                + ", ".join(missing_hard[:12])
                + ". Where you genuinely have one of these, name it explicitly and show where you used it. "
                "Don't add skills you don't have.",
            )
        )
    if missing_soft:
        out.append(
            _s(
                "missing_soft_skills",
                "consider",
                "The job description emphasises: " + ", ".join(missing_soft)
                + ". Show them through concrete examples (e.g. 'mentored 3 engineers') rather than listing the words.",
            )
        )

    for name in sections["missing_recommended"]:
        out.append(
            _s(
                "missing_section",
                "important" if name == "Experience" else "consider",
                f"No '{name}' heading was detected. Use a clear, conventional heading so both people and parsers can find it.",
            )
        )

    contact = sections["contact"]
    if not contact["email"]:
        out.append(_s("missing_email", "important", "No email address was detected."))
    if not contact["phone"]:
        out.append(_s("missing_phone", "info", "No phone number was detected. Optional, but many employers expect one."))

    experience = section_text(resume_text, sections, "Experience") or resume_text
    if len(_NUMBER.findall(experience)) < 3:
        out.append(
            _s(
                "quantify_impact",
                "consider",
                "Few numbers were found in your experience. Where accurate, quantify impact "
                "(e.g. latency reduced 40%, served 2M users, team of 5).",
            )
        )

    words = len(resume_text.split())
    if words < MIN_WORDS:
        out.append(
            _s(
                "too_short",
                "consider",
                f"Only {words} words were extracted. Either the resume is very brief, or the layout "
                "(columns, tables, text in images) prevented extraction. Check the extracted text.",
            )
        )
    elif words > MAX_WORDS:
        out.append(
            _s(
                "too_long",
                "info",
                f"{words} words extracted. Consider trimming content not relevant to this role. "
                "Length conventions vary by country and seniority.",
            )
        )

    kw_missing = [k for k in keyword_cmp["missing"] if k.lower() not in {s.lower() for s in skills_cmp["missing"]}][:8]
    if kw_missing:
        out.append(
            _s(
                "missing_keywords",
                "info",
                "Prominent JD terms absent from your resume: " + ", ".join(kw_missing)
                + ". Use the employer's wording where it accurately describes your experience.",
            )
        )
    return out
