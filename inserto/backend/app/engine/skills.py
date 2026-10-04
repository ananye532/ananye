"""Skill extraction against the taxonomy, with evidence snippets."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .taxonomy import SKILL_BY_NAME, compiled_patterns
from .lexicon import STOPWORDS


@dataclass
class SkillHit:
    name: str
    category: str
    count: int
    soft: bool
    evidence: str


def _snippet(text: str, start: int, end: int, width: int = 60) -> str:
    a = max(0, start - width)
    b = min(len(text), end + width)
    s = text[a:b].replace("\n", " ").strip()
    return ("…" if a > 0 else "") + s + ("…" if b < len(text) else "")


def extract_skills(text: str) -> list[SkillHit]:
    hits: list[SkillHit] = []
    for skill, ipat, cpat in compiled_patterns():
        matches = list(ipat.finditer(text))
        if cpat is not None:
            matches += list(cpat.finditer(text))
        if not matches:
            continue
        first = min(matches, key=lambda m: m.start())
        hits.append(SkillHit(skill.name, skill.category, len(matches), skill.soft, _snippet(text, first.start(), first.end())))
    hits.sort(key=lambda h: (-h.count, h.name))
    return hits


def skill_names(text: str) -> set[str]:
    return {h.name for h in extract_skills(text)}


_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9+#./-]*[A-Za-z0-9+#]|[A-Za-z]")


def tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


def keyword_terms(text: str, *, top: int = 40) -> list[tuple[str, int]]:
    """Unigrams and bigrams without stopwords, ranked by frequency (bigrams weighted up)."""
    toks = [t for t in tokens(text) if len(t) > 2 and not t.isdigit()]
    uni = Counter(t for t in toks if t not in STOPWORDS)
    bi: Counter[str] = Counter()
    for a, b in zip(toks, toks[1:]):
        if a not in STOPWORDS and b not in STOPWORDS:
            bi[f"{a} {b}"] += 1
    scored: dict[str, float] = {}
    for term, c in uni.items():
        scored[term] = c
    for term, c in bi.items():
        if c >= 2:
            scored[term] = c * 1.5
    ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
    out: list[tuple[str, int]] = []
    for term, _ in ranked:
        count = bi[term] if " " in term else uni[term]
        out.append((term, count))
        if len(out) >= top:
            break
    return out


def category_of(name: str) -> str:
    s = SKILL_BY_NAME.get(name)
    return s.category if s else "Other"
