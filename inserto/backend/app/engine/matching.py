"""Job-description matching and role-profile fit."""

from __future__ import annotations

import re

from . import result as R
from .checks import clamp
from .parser import BULLET_LINE, strip_bullet
from .skills import SkillHit, extract_skills, keyword_terms, tokens
from .taxonomy import ROLES, RoleProfile, SKILL_BY_NAME

_YEARS_REQ = re.compile(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?(?:years|yrs)", re.I)
_REQ_CUE = re.compile(r"\b(experience|proficien|knowledge|familiar|expert|must|required|require|ability|understanding|degree|background|skilled|hands-on|strong)\b", re.I)
_TITLE_LINE = re.compile(r"^(?:job title|title|position|role)\s*[:\-]\s*(.+)$", re.I)


def _stem(t: str) -> str:
    for suf in ("ing", "ers", "er", "es", "s", "ed"):
        if len(t) > 5 and t.endswith(suf):
            return t[: -len(suf)]
    return t


def guess_job_title(jd: str) -> str | None:
    for line in jd.splitlines()[:6]:
        line = line.strip()
        if m := _TITLE_LINE.match(line):
            return m.group(1).strip()[:120]
    first = next((ln.strip() for ln in jd.splitlines() if ln.strip()), "")
    if 0 < len(first.split()) <= 8 and not first.endswith("."):
        return first[:120]
    return None


def requirement_lines(jd: str) -> list[str]:
    out: list[str] = []
    for raw in jd.splitlines():
        line = raw.strip()
        if not line:
            continue
        pieces = [strip_bullet(line)] if BULLET_LINE.match(line) else [s.strip() for s in re.split(r"(?<=[.;])\s+", line)]
        for p in pieces:
            if 4 <= len(p.split()) <= 45 and _REQ_CUE.search(p):
                out.append(p.rstrip("."))
    return list(dict.fromkeys(out))[:12]


def _best_evidence(req: str, bullets: list[str]) -> tuple[str | None, float]:
    req_t = {_stem(t) for t in tokens(req) if len(t) > 3}
    best, best_s = None, 0.0
    for b in bullets:
        bt = {_stem(t) for t in tokens(b) if len(t) > 3}
        if not req_t:
            break
        s = len(req_t & bt) / len(req_t)
        if s > best_s:
            best, best_s = b, s
    return best, best_s


def match(resume_text: str, bullets: list[str], resume_skills: list[SkillHit], jd: str,
          job_title: str | None, years_found: float) -> R.Match:
    jd_skills = extract_skills(jd)
    have = {s.name for s in resume_skills}
    jd_names = [s.name for s in jd_skills]
    matched = [n for n in jd_names if n in have]
    missing = [n for n in jd_names if n not in have]
    extra = sorted(have - set(jd_names), key=lambda n: SKILL_BY_NAME[n].soft)[:12]
    hard_jd = [s for s in jd_skills if not s.soft]
    hard_matched = [s for s in hard_jd if s.name in have]
    if hard_jd:
        skill_score = clamp(len(hard_matched) / len(hard_jd) * 100)
    else:
        skill_score = clamp(len(matched) / len(jd_names) * 100) if jd_names else 50

    jd_terms = [t for t, _ in keyword_terms(jd, top=30)]
    resume_stems = {_stem(t) for t in tokens(resume_text)}
    resume_low = resume_text.lower()

    def present(term: str) -> bool:
        if " " in term:
            return term in resume_low
        return _stem(term) in resume_stems

    mk = [t for t in jd_terms if present(t)]
    mmiss = [t for t in jd_terms if not present(t)]
    keyword_score = clamp(len(mk) / len(jd_terms) * 100) if jd_terms else 50

    reqs: list[R.Requirement] = []
    for line in requirement_lines(jd):
        line_skills = {s.name for s in extract_skills(line)}
        evidence, overlap = _best_evidence(line, bullets)
        if line_skills:
            hit = line_skills & have
            met = "met" if hit == line_skills else "partial" if hit else "missing"
        else:
            met = "met" if overlap >= 0.5 else "partial" if overlap >= 0.25 else "missing"
        reqs.append(R.Requirement(text=line, met=met, evidence=evidence if overlap >= 0.2 else None))

    yrs_req = None
    if found := [int(m.group(1)) for m in _YEARS_REQ.finditer(jd)]:
        yrs_req = max(y for y in found if y <= 20) if any(y <= 20 for y in found) else None
    if yrs_req is None:
        years_fit = 80
    elif years_found >= yrs_req:
        years_fit = 100
    else:
        years_fit = clamp(years_found / yrs_req * 100)

    req_score = (sum({"met": 1, "partial": 0.5, "missing": 0}[r.met] for r in reqs) / len(reqs) * 100) if reqs else skill_score
    score = clamp(0.45 * skill_score + 0.25 * keyword_score + 0.15 * req_score + 0.15 * years_fit)
    if score >= 80:
        verdict = "Strong match. Tailor the summary to the role and apply."
    elif score >= 65:
        verdict = "Good match with a few gaps worth addressing before applying."
    elif score >= 45:
        verdict = "Partial match. Close the missing core skills or show adjacent evidence."
    else:
        verdict = "Weak match. This role asks for skills the resume does not show."
    return R.Match(score=score, job_title=job_title or guess_job_title(jd), skill_score=skill_score,
                   keyword_score=keyword_score, matched_skills=matched, missing_skills=missing[:15],
                   extra_skills=extra, matched_keywords=mk[:20], missing_keywords=mmiss[:15],
                   requirements=reqs, years_required=yrs_req, years_found=years_found, verdict=verdict)


def role_fit(role: RoleProfile, have: set[str]) -> R.RoleFit:
    core_hit = [s for s in role.core if s in have]
    nice_hit = [s for s in role.nice if s in have]
    denom = len(role.core) * 2 + len(role.nice)
    fit = clamp((len(core_hit) * 2 + len(nice_hit)) / denom * 100)
    missing = [s for s in role.core if s not in have] + [s for s in role.nice if s not in have]
    return R.RoleFit(role=role.name, fit=fit, matched=core_hit + nice_hit, missing=missing[:6])


def role_fits(have: set[str]) -> list[R.RoleFit]:
    fits = [role_fit(r, have) for r in ROLES]
    fits.sort(key=lambda f: -f.fit)
    return fits
