"""Named-entity recognition. Informational only, never used in any metric.

The small English model frequently tags technologies (e.g. "Python", "AWS") as
ORG, so entities that are known skills are filtered out.
"""

from __future__ import annotations

from spacy.language import Language

from .pipeline import get_nlp, has_ner
from .skills import SKILLS

LABELS = {"ORG": "organizations", "GPE": "locations", "DATE": "dates"}
_SKILL_NAMES = {n.lower() for n in SKILLS} | {a.lower() for e in SKILLS.values() for a in (*e.aliases, *e.cased)}


def extract_entities(text: str, nlp: Language | None = None, limit: int = 15) -> dict[str, list[str]]:
    nlp = nlp or get_nlp()
    out: dict[str, list[str]] = {v: [] for v in LABELS.values()}
    if not has_ner(nlp):
        return out
    for ent in nlp(text).ents:
        key = LABELS.get(ent.label_)
        value = " ".join(ent.text.split())
        if (
            not key
            or len(value) < 3
            or "\n" in ent.text  # entity spans a line break: almost always a parsing artefact
            or any(t.lower_ in _SKILL_NAMES for t in ent)  # e.g. "Redis, Docker" tagged ORG
            or value.lower() in _SKILL_NAMES
        ):
            continue
        if value not in out[key] and len(out[key]) < limit:
            out[key].append(value)
    return out
