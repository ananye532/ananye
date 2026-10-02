"""Render a stored analysis as a downloadable Markdown or JSON report."""

from __future__ import annotations

import json
from datetime import datetime


def _pct(v: float | None) -> str:
    return "n/a" if v is None else f"{v * 100:.0f}%"


def to_json(analysis: dict, meta: dict) -> str:
    return json.dumps({"meta": meta, **analysis}, indent=2, default=str)


def to_markdown(analysis: dict, meta: dict) -> str:
    m = analysis["metrics"]
    s = analysis["skills"]
    created = meta.get("created_at")
    created = created.isoformat(timespec="seconds") if isinstance(created, datetime) else str(created)
    lines = [
        "# Resume Analysis Report",
        "",
        f"- Resume: {meta.get('resume_filename', '')}",
        f"- Job: {meta.get('job_title', '')}",
        f"- Generated: {created}",
        f"- Skill taxonomy version: {analysis['taxonomy_version']}",
        "",
        f"> **Important:** {analysis['disclaimer']}",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Definition |",
        "|---|---|---|",
        f"| Skill coverage | {_pct(m['skill_coverage']['value'])} "
        f"({m['skill_coverage']['matched_count']}/{m['skill_coverage']['required_count']}) | {m['skill_coverage']['definition']} |",
        f"| Keyword coverage | {_pct(m['keyword_coverage']['value'])} "
        f"({m['keyword_coverage']['present_count']}/{m['keyword_coverage']['total']}) | {m['keyword_coverage']['definition']} |",
        f"| TF-IDF cosine similarity | {m['cosine_similarity']['value']:.2f} | {m['cosine_similarity']['definition']} |",
        "",
        "## Skills",
        "",
        f"**Matched ({len(s['matched'])}):** {', '.join(s['matched']) or 'none'}",
        "",
        f"**Missing from resume ({len(s['missing'])}):**",
        "",
    ]
    if s["missing_by_category"]:
        lines += [f"- {cat}: {', '.join(names)}" for cat, names in sorted(s["missing_by_category"].items())]
    else:
        lines.append("- none")
    lines += ["", f"**In resume but not in JD:** {', '.join(s['resume_only']) or 'none'}", "", "## Top job-description keywords", ""]
    lines += ["| Term | Weight | In resume |", "|---|---|---|"]
    lines += [f"| {k['term']} | {k['weight']:.2f} | {'yes' if k['in_resume'] else 'no'} |" for k in analysis["keywords"]["job_top"]]

    sec = analysis["sections"]
    lines += ["", "## Sections detected", ""]
    lines += [f"- {d['name']} (heading: \"{d['heading']}\", {d['word_count']} words)" for d in sec["detected"]] or ["- none"]
    if sec["missing_recommended"]:
        lines.append(f"- Not detected (recommended): {', '.join(sec['missing_recommended'])}")

    lines += ["", "## Suggestions", ""]
    lines += [f"- **[{x['severity']}]** {x['message']} _(rule: {x['rule']})_" for x in analysis["suggestions"]] or ["- none"]

    lines += ["", "## Limitations of automated resume matching", ""]
    lines += [f"- {x}" for x in analysis["limitations"]]
    return "\n".join(lines) + "\n"
