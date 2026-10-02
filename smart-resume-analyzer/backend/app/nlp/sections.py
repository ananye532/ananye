"""Resume section detection from heading lines."""

from __future__ import annotations

import re

SECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    name: re.compile(rf"^(?:{pattern})$", re.IGNORECASE)
    for name, pattern in {
        "Summary": r"(?:professional |career )?(?:summary|profile|objective)|about me",
        "Experience": r"(?:professional |work |relevant |employment )?(?:experience|history)|employment|work",
        "Education": r"education(?:al background)?|academic (?:background|qualifications)",
        "Skills": r"(?:technical |core |key )?(?:skills|competencies|technologies)(?: & tools| and tools)?|tech stack",
        "Projects": r"(?:personal |selected |academic |key )?projects",
        "Certifications": r"certifications?|licen[cs]es(?: (?:&|and) certifications)?|certifications? (?:&|and) licen[cs]es",
        "Awards": r"awards?|honou?rs(?: (?:&|and) awards)?|achievements",
        "Publications": r"publications|papers",
        "Volunteer": r"volunteer(?:ing| experience| work)?",
        "Languages": r"languages",
        "Interests": r"interests|hobbies",
    }.items()
}

RECOMMENDED = ("Experience", "Education", "Skills")

_HEADING_STRIP = re.compile(r"^[\s#*\-•\d.)]+|[\s:|\-_=]+$")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+?\d[\s().-]?){9,14}\d")  # 10+ digits, so year ranges are not phones
_LINKEDIN = re.compile(r"linkedin\.com/in/", re.IGNORECASE)
_GITHUB = re.compile(r"github\.com/[\w-]+", re.IGNORECASE)


def _match_heading(line: str) -> str | None:
    candidate = _HEADING_STRIP.sub("", line).strip()
    if not candidate or len(candidate) > 40 or len(candidate.split()) > 5:
        return None
    for name, pattern in SECTION_PATTERNS.items():
        if pattern.match(candidate):
            return name
    return None


def detect_sections(text: str) -> dict:
    """Return detected sections, missing recommended ones, and which contact fields are present.

    Contact values are never returned, only booleans, so personal data isn't
    duplicated into analysis results.
    """
    lines = text.split("\n")
    found: list[dict] = []
    for i, line in enumerate(lines):
        name = _match_heading(line)
        if name and name not in {s["name"] for s in found}:
            found.append({"name": name, "heading": line.strip(), "line": i})

    # Word count of each section's body, up to the next detected heading.
    for idx, sec in enumerate(found):
        end = found[idx + 1]["line"] if idx + 1 < len(found) else len(lines)
        sec["word_count"] = sum(len(l.split()) for l in lines[sec["line"] + 1 : end])

    names = {s["name"] for s in found}
    return {
        "detected": found,
        "missing_recommended": [r for r in RECOMMENDED if r not in names],
        "contact": {
            "email": bool(_EMAIL.search(text)),
            "phone": bool(_PHONE.search(text)),
            "linkedin": bool(_LINKEDIN.search(text)),
            "github": bool(_GITHUB.search(text)),
        },
    }


def section_text(text: str, sections: dict, name: str) -> str:
    """Return the body text of one detected section, or '' if it wasn't detected."""
    lines = text.split("\n")
    detected = sections["detected"]
    for idx, sec in enumerate(detected):
        if sec["name"] == name:
            end = detected[idx + 1]["line"] if idx + 1 < len(detected) else len(lines)
            return "\n".join(lines[sec["line"] + 1 : end])
    return ""
