"""Deterministic bullet rewriting for the Improvement Studio.

Rewrites never invent facts. Where a metric is missing, the rewrite inserts a
bracketed placeholder and flags `needs_input` so the user supplies the real number.
"""

from __future__ import annotations

import re

from . import result as R
from .checks import first_word, is_action_opener, is_quantified
from .lexicon import WEAK_PHRASES

_REPLACE_OPENERS: dict[str, str] = {
    "responsible for": "Owned",
    "worked on": "Built",
    "helped": "Contributed to",
    "helped to": "Contributed to",
    "assisted with": "Supported",
    "assisted in": "Supported",
    "assisted": "Supported",
    "involved in": "Contributed to",
    "participated in": "Contributed to",
    "tasked with": "Delivered",
    "duties included": "Delivered",
    "handled": "Managed",
    "was in charge of": "Led",
    "worked with": "Partnered with",
    "used": "Applied",
    "made": "Created",
    "did": "Executed",
}
_FILLER = re.compile(r"\b(successfully|various|several|numerous|a lot of|lots of|really|very|basically|actually|effectively)\s+", re.I)
_PRONOUN_START = re.compile(r"^(?:i|we)\s+(?:have\s+|had\s+|was\s+|am\s+|were\s+)?", re.I)
_PRONOUNS = re.compile(r"\b(?:my|our)\s+", re.I)
_GERUND_TO_PAST = {
    "managing": "Managed", "leading": "Led", "building": "Built", "developing": "Developed",
    "designing": "Designed", "creating": "Created", "implementing": "Implemented", "maintaining": "Maintained",
    "supporting": "Supported", "coordinating": "Coordinated", "writing": "Wrote", "running": "Ran",
    "analyzing": "Analyzed", "improving": "Improved", "testing": "Tested", "training": "Trained",
}
_PRESENT_TO_PAST = {
    "manage": "Managed", "lead": "Led", "build": "Built", "develop": "Developed", "design": "Designed",
    "create": "Created", "implement": "Implemented", "maintain": "Maintained", "support": "Supported",
    "write": "Wrote", "run": "Ran", "analyze": "Analyzed", "improve": "Improved", "test": "Tested",
    "manages": "Managed", "leads": "Led", "builds": "Built", "develops": "Developed", "designs": "Designed",
}


def _metric_placeholder(bullet: str) -> str:
    low = bullet.lower()
    if re.search(r"\b(cost|budget|spend|revenue|sales|saving)", low):
        return "saving [$X] per [period]"
    if re.search(r"\b(customer|client|user|ticket|support)", low):
        return "serving [N] users and lifting satisfaction to [X%]"
    if re.search(r"\b(process|workflow|pipeline|deploy|release|build|automat)", low):
        return "cutting turnaround time by [X%]"
    if re.search(r"\b(team|engineer|mentor|hire|train)", low):
        return "resulting in [outcome, e.g. X% faster delivery]"
    if re.search(r"\b(website|app|feature|product|page|service|api)", low):
        return "used by [N] users, improving [metric] by [X%]"
    return "improving [metric] by [X%]"


def rewrite(bullet: str) -> R.Rewrite | None:
    text = bullet.strip().rstrip(".")
    reasons: list[str] = []
    needs_input = False

    if _PRONOUN_START.match(text):
        text = _PRONOUN_START.sub("", text)
        reasons.append("Removed first-person pronoun")
    if _PRONOUNS.search(text):
        text = _PRONOUNS.sub("", text)
        if "Removed first-person pronoun" not in reasons:
            reasons.append("Removed first-person pronoun")

    low = text.lower()
    for phrase in sorted(_REPLACE_OPENERS, key=len, reverse=True):
        if low.startswith(phrase + " ") or low == phrase:
            rest = text[len(phrase):].lstrip()
            rest = re.sub(r"^(?:the\s+)?(?:helping|assisting)\s+(?:with\s+)?", "", rest, flags=re.I)
            text = f"{_REPLACE_OPENERS[phrase]} {rest}".strip()
            reasons.append(f"Replaced weak opener “{phrase}” with an action verb")
            break
    else:
        fw = first_word(text)
        if fw in _GERUND_TO_PAST:
            text = _GERUND_TO_PAST[fw] + text[len(fw):]
            reasons.append("Converted to past-tense action verb")
        elif fw in _PRESENT_TO_PAST:
            text = _PRESENT_TO_PAST[fw] + text[len(fw):]
            reasons.append("Converted to past-tense action verb")

    cleaned = _FILLER.sub("", text)
    if cleaned != text:
        text = cleaned
        reasons.append("Cut filler words")

    words = text.split()
    if len(words) > 32:
        # Keep the leading clause; long bullets bury the result.
        cut = re.split(r",\s+(?:and\s+|which\s+|while\s+)|;\s+", text, maxsplit=1)[0]
        if 8 <= len(cut.split()) < len(words):
            text = cut
            reasons.append("Tightened to one idea")

    if not is_quantified(text):
        text = f"{text}, {_metric_placeholder(text)}"
        reasons.append("Added a measurable outcome (fill in your real numbers)")
        needs_input = True

    text = text[:1].upper() + text[1:]
    text = re.sub(r"\s{2,}", " ", text).strip()
    if not reasons or text.rstrip(".") == bullet.strip().rstrip("."):
        return None
    return R.Rewrite(original=bullet.strip(), improved=text, reasons=reasons, needs_input=needs_input)


def weakness(bullet: str) -> int:
    w = 0
    low = bullet.lower()
    if not is_quantified(bullet):
        w += 3
    if any(low.startswith(p) for p in WEAK_PHRASES):
        w += 3
    if not is_action_opener(first_word(bullet)):
        w += 1
    if re.search(r"\b(i|my|we|our)\b", low):
        w += 2
    if len(bullet.split()) > 32:
        w += 1
    return w


def rewrites(bullets: list[str], limit: int = 8) -> list[R.Rewrite]:
    ranked = sorted(bullets, key=weakness, reverse=True)
    out: list[R.Rewrite] = []
    for b in ranked:
        if weakness(b) == 0:
            break
        if r := rewrite(b):
            out.append(r)
        if len(out) >= limit:
            break
    return out
