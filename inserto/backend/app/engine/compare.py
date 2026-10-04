"""Side-by-side comparison of two stored analysis results."""

from __future__ import annotations

from typing import Any


def compare(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    def subs(r: dict[str, Any]) -> dict[str, dict[str, Any]]:
        return {s["key"]: s for s in r["subscores"]}

    sa, sb = subs(a), subs(b)
    keys = [k for k in sa if k in sb] + [k for k in sb if k not in sa]
    rows = []
    for k in keys:
        va = sa.get(k, {}).get("score")
        vb = sb.get(k, {}).get("score")
        rows.append({"key": k, "label": (sa.get(k) or sb.get(k))["label"], "a": va, "b": vb,
                     "delta": (vb - va) if va is not None and vb is not None else None})
    skills_a = {s["name"] for s in a["skills"]["found"]}
    skills_b = {s["name"] for s in b["skills"]["found"]}
    metrics = [
        ("Overall", a["overall"]["score"], b["overall"]["score"]),
        ("Quantified bullets", a["quantification"]["quantified"], b["quantification"]["quantified"]),
        ("Bullets", a["quantification"]["total"], b["quantification"]["total"]),
        ("Hard skills", a["skills"]["hard_count"], b["skills"]["hard_count"]),
        ("Words", a["parsed"]["word_count"], b["parsed"]["word_count"]),
        ("Recommendations", len(a["recommendations"]), len(b["recommendations"])),
    ]
    winner = "a" if a["overall"]["score"] > b["overall"]["score"] else "b" if b["overall"]["score"] > a["overall"]["score"] else "tie"
    return {
        "subscores": rows,
        "metrics": [{"label": l, "a": x, "b": y, "delta": y - x} for l, x, y in metrics],
        "skills_only_a": sorted(skills_a - skills_b),
        "skills_only_b": sorted(skills_b - skills_a),
        "skills_shared": sorted(skills_a & skills_b),
        "winner": winner,
    }
