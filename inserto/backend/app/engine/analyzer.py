"""Orchestrates the deterministic pipeline: parse -> checks -> scores -> narrative."""

from __future__ import annotations

from collections import Counter
from datetime import date

from . import ENGINE_VERSION
from . import result as R
from .checks import (achievements, action_verbs, ats, clamp, education, experience, keywords, quantification,
                     readability, structure)
from .matching import match as match_jd
from .matching import role_fits
from .narrative import insights, recommendations, recruiter
from .parser import ParsedResume, parse
from .skills import SkillHit, extract_skills
from .studio import rewrites as make_rewrites
from .taxonomy import RoleProfile, SKILL_BY_NAME, find_role

DISCLAIMER = (
    "Scores are heuristic estimates from text analysis. They reflect common recruiter and ATS conventions, "
    "not any specific employer’s system, and do not predict hiring outcomes."
)

WEIGHTS_BASE = {"ats": 0.20, "structure": 0.12, "impact": 0.28, "skills": 0.15, "readability": 0.12, "experience": 0.13}
WEIGHTS_JD = {"ats": 0.15, "structure": 0.08, "impact": 0.22, "skills": 0.10, "readability": 0.08, "experience": 0.10, "match": 0.27}
LABELS = {
    "ats": ("ATS compatibility", "How reliably applicant tracking systems can parse your resume."),
    "structure": ("Structure", "Standard sections, order and length."),
    "impact": ("Impact", "Quantified results, achievements and action-oriented language."),
    "skills": ("Skills & keywords", "Breadth and evidence of recognizable skills."),
    "readability": ("Readability", "Concise, scannable, jargon-free writing."),
    "experience": ("Experience", "Clarity of roles, dates and progression."),
    "match": ("Job match", "Alignment with the job description you provided."),
}


def grade(score: int) -> tuple[str, str]:
    for cut, g, label in ((90, "A+", "Exceptional"), (82, "A", "Excellent"), (74, "B+", "Strong"), (66, "B", "Good"),
                          (58, "C+", "Fair"), (50, "C", "Needs work"), (0, "D", "Needs major work")):
        if score >= cut:
            return g, label
    return "D", "Needs major work"


def _skills_block(parsed: ParsedResume, text: str, found: list[SkillHit], role: RoleProfile | None) -> R.Skills:
    skills_sec = parsed.section("skills")
    skills_text = "\n".join(skills_sec.lines) if skills_sec else ""
    evidence_text = "\n".join(parsed.bullets + ([parsed.summary] if parsed.summary else []))
    in_sec = {h.name for h in extract_skills(skills_text)} if skills_text else set()
    in_evidence = {h.name for h in extract_skills(evidence_text)} if evidence_text else set()
    out = [R.SkillFound(name=h.name, category=h.category, count=h.count, soft=h.soft,
                        in_skills_section=h.name in in_sec, evidence=h.evidence) for h in found]
    cats = Counter(h.category for h in found)
    by_cat = [R.CategoryCount(category=c, count=n) for c, n in cats.most_common()]
    unsupported = sorted(n for n in in_sec - in_evidence if not SKILL_BY_NAME[n].soft)
    have = {h.name for h in found}
    missing: list[R.SkillGap] = []
    if role:
        for n in role.core:
            if n not in have:
                missing.append(R.SkillGap(name=n, category=SKILL_BY_NAME[n].category, importance="core",
                                          reason=f"Core skill for {role.name} roles."))
        for n in role.nice:
            if n not in have:
                missing.append(R.SkillGap(name=n, category=SKILL_BY_NAME[n].category, importance="nice",
                                          reason=f"Frequently requested for {role.name} roles."))
    hard = [h for h in found if not h.soft]
    soft = [h for h in found if h.soft]
    score = min(55, len(hard) * 4.5) + (15 if skills_sec else 0)
    if in_sec:
        score += 20 * (1 - len(unsupported) / max(1, len(in_sec)))
    else:
        score += 8
    score += min(10, len(soft) * 3)
    if role:
        core_hit = sum(1 for n in role.core if n in have) / len(role.core)
        score = score * 0.7 + core_hit * 30
    return R.Skills(score=clamp(score), found=out, by_category=by_cat, hard_count=len(hard), soft_count=len(soft),
                    missing=missing[:10], unsupported=unsupported[:10], target_role=role.name if role else None)


def analyze(text: str, *, source: str = "paste", job_description: str | None = None, job_title: str | None = None,
            target_role: str | None = None, today: date | None = None) -> R.AnalysisResult:
    parsed = parse(text, today)
    found = extract_skills(text)
    have = {h.name for h in found}
    fits = role_fits(have)
    role = find_role(target_role) or find_role(fits[0].role if fits and fits[0].fit > 0 else None)

    bullets = parsed.bullets
    quant = quantification(bullets)
    verbs = action_verbs(bullets, text)
    ach = achievements(bullets, parsed)
    read = readability(bullets, parsed, text)
    exp = experience(parsed)
    edu = education(parsed, exp.total_years)
    struct = structure(parsed, exp.total_years)
    ats_block = ats(parsed, text, source, found)
    skills = _skills_block(parsed, text, found, role)

    jd = (job_description or "").strip()
    match = match_jd(text, bullets, found, jd, job_title, exp.total_years) if len(jd) >= 80 else None
    if match:
        expected = match.matched_keywords + match.missing_keywords
    elif role:
        expected = list(role.keywords) + [n.lower() for n in role.core]
    else:
        expected = []
    kw = keywords(text, bullets, found, expected)

    impact = clamp(0.45 * quant.score + 0.30 * verbs.score + 0.25 * ach.score)
    raw = {
        "ats": ats_block.score,
        "structure": struct.score,
        "impact": impact,
        "skills": clamp(0.6 * skills.score + 0.4 * kw.score),
        "readability": read.score,
        "experience": clamp(0.8 * exp.score + 0.2 * edu.score),
    }
    weights = WEIGHTS_BASE
    if match:
        raw["match"] = match.score
        weights = WEIGHTS_JD
    subscores = [R.Subscore(key=k, label=LABELS[k][0], score=raw[k], weight=w, description=LABELS[k][1])
                 for k, w in weights.items()]
    overall_score = clamp(sum(raw[k] * w for k, w in weights.items()))
    g, label = grade(overall_score)
    best = max(subscores, key=lambda s: s.score)
    worst = min(subscores, key=lambda s: s.score)
    summary = f"{label} resume. Strongest area: {best.label.lower()} ({best.score}). Biggest opportunity: {worst.label.lower()} ({worst.score})."

    rw = make_rewrites(bullets)
    recs = recommendations(parsed, ats_block, struct, skills, kw, exp, quant, verbs, read, edu, match, rw)
    rec_block = recruiter(parsed, overall_score, subscores, exp, skills, quant, edu, match, role.name if role else None)
    ins = insights(exp, skills, fits, recs)

    pd = parsed.to_dict()
    parsed_out = R.Parsed(
        contact=R.ContactOut(**pd["contact"]),
        summary=pd["summary"],
        sections=[R.SectionOut(key=s["key"], label=s["label"], title=s["title"], line_count=s["line_count"])
                  for s in pd["sections"] if s["key"] != "header"],
        roles=[R.RoleOut(**r) for r in pd["roles"]],
        education=[R.EducationOut(institution=e["institution"], degree=e["degree"], degree_level=e["degree_level"],
                                  year=e["year"], gpa=e["gpa"]) for e in pd["education"]],
        skills_listed=pd["skills_listed"],
        certifications=pd["certifications"],
        bullet_count=len(bullets),
        word_count=parsed.word_count,
        page_estimate=round(max(1.0, parsed.word_count / 500), 1),
    )
    return R.AnalysisResult(
        engine_version=ENGINE_VERSION,
        overall=R.Overall(score=overall_score, grade=g, label=label, summary=summary),
        subscores=subscores,
        parsed=parsed_out,
        ats=ats_block,
        structure=struct,
        skills=skills,
        keywords=kw,
        experience=exp,
        education=edu,
        achievements=ach,
        quantification=quant,
        action_verbs=verbs,
        readability=read,
        match=match,
        recruiter=rec_block,
        recommendations=recs,
        rewrites=rw,
        insights=ins,
        provider=R.Provider(name="deterministic", ai_enhanced=False),
        disclaimer=DISCLAIMER,
    )
