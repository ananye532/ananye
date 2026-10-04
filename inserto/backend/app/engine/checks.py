"""Individual resume checks. Each returns a typed block of the AnalysisResult."""

from __future__ import annotations

import re
from collections import Counter

from . import result as R
from .lexicon import ACHIEVEMENT_CUES, BUZZWORDS, FIRST_PERSON, STRONG_VERBS, WEAK_PHRASES
from .parser import DATE_RANGE, ParsedResume, Role
from .skills import SkillHit, keyword_terms, tokens

_YEAR_ONLY = re.compile(r"^(19|20)\d{2}$")
_NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?\s?(?:%|x\b|k\b|m\b|mm\b|b\b|\+)?", re.IGNORECASE)
_MAGNITUDE = re.compile(r"\b(million|billion|thousand|hundreds?|dozens?|doubled|tripled|halved|twice)\b", re.I)
_PASSIVE = re.compile(r"\b(?:was|were|been|being|is|are)\s+(?:\w+ly\s+)?\w+(?:ed|en)\b", re.I)


def clamp(v: float, lo: int = 0, hi: int = 100) -> int:
    return int(max(lo, min(hi, round(v))))


# ---------- quantification ----------

def is_quantified(text: str) -> bool:
    if _MAGNITUDE.search(text):
        return True
    for m in _NUM.finditer(text):
        tok = m.group(0).strip()
        digits = re.sub(r"[^\d]", "", tok)
        if not digits:
            continue
        if _YEAR_ONLY.match(tok):
            continue
        return True
    return False


def quantification(bullets: list[str]) -> R.Quantification:
    total = len(bullets)
    q = [b for b in bullets if is_quantified(b)]
    unq = [b for b in bullets if not is_quantified(b)]
    ratio = len(q) / total if total else 0.0
    # 60%+ quantified bullets is excellent for most roles.
    score = clamp(ratio / 0.6 * 100) if total else 10
    return R.Quantification(score=score, quantified=len(q), total=total, ratio=round(ratio, 3),
                            examples=q[:4], unquantified=unq[:8])


# ---------- action verbs ----------

def first_word(bullet: str) -> str:
    m = re.match(r"[A-Za-z][A-Za-z-]*", bullet)
    return m.group(0).lower() if m else ""


def is_action_opener(word: str) -> bool:
    return word in STRONG_VERBS or (len(word) > 4 and word.endswith("ed") and word not in {"need", "speed", "seed"})


def action_verbs(bullets: list[str], text: str) -> R.ActionVerbs:
    openers = [first_word(b) for b in bullets]
    strong = Counter(w for w in openers if w in STRONG_VERBS)
    low = text.lower()
    weak: list[R.WeakPhrase] = []
    for phrase, alt in WEAK_PHRASES.items():
        n = len(re.findall(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", low))
        # "used"/"made"/"did" are only weak as openers
        if phrase in {"used", "made", "did", "handled"}:
            n = sum(1 for w in openers if w == phrase)
        if n:
            weak.append(R.WeakPhrase(phrase=phrase, count=n, suggestion=alt))
    repeated = [R.VerbCount(verb=v, count=c) for v, c in strong.most_common() if c >= 3]
    ratio = sum(1 for w in openers if is_action_opener(w)) / len(openers) if openers else 0.0
    weak_total = sum(w.count for w in weak)
    score = clamp(ratio * 85 + min(15, len(strong) * 2) - weak_total * 6 - len(repeated) * 4) if bullets else 15
    return R.ActionVerbs(
        score=score,
        strong=[R.VerbCount(verb=v, count=c) for v, c in strong.most_common(12)],
        weak=sorted(weak, key=lambda w: -w.count),
        repeated=repeated,
        starts_with_verb_ratio=round(ratio, 3),
    )


# ---------- achievements ----------

def achievements(bullets: list[str], parsed: ParsedResume) -> R.Achievements:
    found = []
    for b in bullets:
        low = b.lower()
        cue = any(re.search(rf"\b{c}\b", low) for c in ACHIEVEMENT_CUES)
        if cue and is_quantified(b):
            found.append(b)
    awards = parsed.section("awards")
    award_lines = len(awards.lines) if awards else 0
    notes: list[str] = []
    if not found:
        notes.append("No bullet pairs a result verb with a measurable outcome.")
    if award_lines:
        notes.append(f"{award_lines} line(s) in an awards/achievements section.")
    target = max(3, len(bullets) // 3)
    score = clamp((len(found) + min(award_lines, 2)) / target * 100) if bullets else 10
    return R.Achievements(score=score, count=len(found), examples=found[:5], notes=notes)


# ---------- readability ----------

def _syllables(word: str) -> int:
    w = word.lower().strip(".,;:!?()")
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:es|ed|e)$", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    return max(1, len(groups))


def flesch(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?\n]+", text) if len(s.split()) >= 3]
    words = re.findall(r"[A-Za-z]+", text)
    if not sentences or not words:
        return 0.0
    syl = sum(_syllables(w) for w in words)
    return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syl / len(words)), 1)


def readability(bullets: list[str], parsed: ParsedResume, text: str) -> R.Readability:
    body = "\n".join(bullets + ([parsed.summary] if parsed.summary else []))
    words_per = [len(b.split()) for b in bullets]
    avg = sum(words_per) / len(words_per) if words_per else 0.0
    long_b = [b for b in bullets if len(b.split()) > 32]
    short_b = [b for b in bullets if len(b.split()) < 6]
    toks = tokens(body)
    fp = sum(1 for t in toks if t in FIRST_PERSON)
    passive = len(_PASSIVE.findall(body))
    low = text.lower()
    buzz = [R.Term(term=b, count=low.count(b)) for b in sorted(BUZZWORDS) if re.search(rf"(?<![\w-]){re.escape(b)}(?![\w-])", low)]
    fk = flesch(body) if body else 0.0
    notes: list[str] = []
    if fp:
        notes.append(f"{fp} first-person pronoun(s). Resumes conventionally drop “I” and “my”.")
    if passive:
        notes.append(f"{passive} passive construction(s) weaken ownership.")
    if long_b:
        notes.append(f"{len(long_b)} bullet(s) exceed 32 words; recruiters skim.")
    if buzz:
        notes.append("Generic buzzwords add length without evidence.")
    score = 100.0
    if bullets:
        if avg > 28:
            score -= min(25, (avg - 28) * 2.5)
        elif avg < 9:
            score -= min(20, (9 - avg) * 4)
    else:
        score -= 30
    score -= min(20, fp * 4)
    score -= min(15, passive * 4)
    score -= min(15, len(long_b) * 4)
    score -= min(15, len(buzz) * 4)
    if body and fk < 10:
        score -= 10
    return R.Readability(score=clamp(score), flesch=fk, avg_bullet_words=round(avg, 1), long_bullets=long_b[:5],
                         short_bullets=short_b[:5], first_person=fp, passive=passive, buzzwords=buzz, notes=notes)


# ---------- experience ----------

def _merged_intervals(roles: list[Role]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    spans = sorted((r.start_ym, r.end_ym) for r in roles if r.start_ym and r.end_ym and r.end_ym >= r.start_ym)
    merged: list[list[tuple[int, int]]] = []
    for s, e in spans:
        if merged and (s[0] * 12 + s[1]) <= (merged[-1][1][0] * 12 + merged[-1][1][1]) + 1:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(a, b) for a, b in merged]


def _ym(v: tuple[int, int]) -> int:
    return v[0] * 12 + v[1]


_MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _fmt(v: tuple[int, int]) -> str:
    return f"{_MONTH_NAMES[v[1] - 1]} {v[0]}"


SENIOR_TITLE = re.compile(r"\b(senior|sr\.?|lead|principal|staff|head|director|manager|vp|chief)\b", re.I)
INTERN_TITLE = re.compile(r"\b(intern|internship|trainee|apprentice)\b", re.I)


def total_years(roles: list[Role]) -> float:
    """Years of professional experience: overlapping roles are merged and internships excluded."""
    merged = _merged_intervals([r for r in roles if not INTERN_TITLE.search(r.title or "")])
    months = sum(_ym(b) - _ym(a) + 1 for a, b in merged)
    return round(months / 12, 1)


def seniority(years: float, roles: list[Role]) -> str:
    latest = roles[0].title if roles else ""
    if years < 1:
        level = "Entry level"
    elif years < 3:
        level = "Early career"
    elif years < 6:
        level = "Mid level"
    elif years < 10:
        level = "Senior"
    else:
        level = "Staff / Leadership"
    if latest and SENIOR_TITLE.search(latest) and level in {"Early career", "Mid level"}:
        level = "Senior"
    return level


def experience(parsed: ParsedResume) -> R.Experience:
    roles = parsed.roles
    notes: list[str] = []
    if not roles:
        return R.Experience(score=15, total_years=0, role_count=0, avg_tenure_months=None, seniority="Unknown",
                            gaps=[], bullets_per_role=0, notes=["No work experience entries could be parsed. Use a clear “Experience” heading with title, company and dates per role."])
    yrs = total_years(roles)
    merged = _merged_intervals([r for r in roles if not INTERN_TITLE.search(r.title or "")])
    gaps: list[R.Gap] = []
    for (a1, b1), (a2, _b2) in zip(merged, merged[1:]):
        months = _ym(a2) - _ym(b1) - 1
        if months >= 6:
            gaps.append(R.Gap(start=_fmt(b1), end=_fmt(a2), months=months))
    tenures = [r.duration_months for r in roles if r.duration_months]
    avg_tenure = int(sum(tenures) / len(tenures)) if tenures else None
    dated = sum(1 for r in roles if r.start)
    bpr = sum(len(r.bullets) for r in roles) / len(roles)
    score = 40.0
    score += 20 * dated / len(roles)
    score += 20 if 2.5 <= bpr <= 6.5 else 10 if bpr >= 1.5 else 0
    score += 10 if not gaps else 3
    score += 10 if any(r.is_current for r in roles) or (merged and merged[-1][1][0] >= 2024) else 5
    if dated < len(roles):
        notes.append(f"{len(roles) - dated} role(s) have no parsable dates.")
    if bpr < 2.5:
        notes.append("Most roles have fewer than 3 bullets; add outcomes to show scope.")
    if bpr > 6.5:
        notes.append("Some roles carry many bullets; keep the 3–5 strongest per role.")
    for g in gaps:
        notes.append(f"{g.months}-month gap between {g.start} and {g.end}. Consider a one-line explanation.")
    if avg_tenure is not None and avg_tenure < 12 and len(roles) >= 3:
        notes.append("Average tenure under a year may raise questions; group contract work under one heading.")
    return R.Experience(score=clamp(score), total_years=yrs, role_count=len(roles), avg_tenure_months=avg_tenure,
                        seniority=seniority(yrs, roles), gaps=gaps, bullets_per_role=round(bpr, 1), notes=notes)


# ---------- education ----------

def education(parsed: ParsedResume, years: float) -> R.Education:
    entries = parsed.education
    notes: list[str] = []
    if not entries:
        if parsed.section("education"):
            notes.append("An education section exists but no institution or degree was recognized.")
            return R.Education(score=45, highest=None, entries=0, notes=notes)
        notes.append("No education section. Add one even if brief; many ATS filters require it.")
        return R.Education(score=25 if years < 5 else 50, highest=None, entries=0, notes=notes)
    best = max(entries, key=lambda e: e.degree_rank)
    score = 40.0
    score += 25 if best.degree_level else 0
    score += 20 if any(e.institution for e in entries) else 0
    score += 15 if any(e.year for e in entries) else 0
    if not any(e.year for e in entries):
        notes.append("Add graduation years so dates can be parsed (or omit consistently if intentional).")
    for e in entries:
        if e.gpa:
            try:
                val = float(e.gpa.split("/")[0])
                if val < 3.0 and "/4" in (e.gpa or "/4"):
                    notes.append("GPA below 3.0 is usually better omitted.")
                elif years >= 5:
                    notes.append("With 5+ years of experience, GPA can usually be removed.")
            except ValueError:
                pass
    if parsed.certifications:
        notes.append(f"{len(parsed.certifications)} certification(s) listed.")
        score += 5
    return R.Education(score=clamp(score), highest=best.degree_level, entries=len(entries), notes=notes)


# ---------- structure ----------

REQUIRED = ("experience", "education", "skills")
RECOMMENDED = ("summary",)
OPTIONAL = ("projects", "certifications", "awards")
LABELS = {"experience": "Experience", "education": "Education", "skills": "Skills", "summary": "Summary",
          "projects": "Projects", "certifications": "Certifications", "awards": "Awards"}


def length_verdict(words: int) -> tuple[str, float]:
    if words < 200:
        return "Too short", 0.3
    if words < 400:
        return "Concise", 0.8
    if words <= 900:
        return "Ideal length", 1.0
    if words <= 1300:
        return "Long", 0.75
    return "Too long", 0.4


def structure(parsed: ParsedResume, years: float) -> R.Structure:
    keys = [s.key for s in parsed.sections]
    sections = [R.SectionPresence(key=k, label=LABELS[k], present=k in keys, required=k in REQUIRED)
                for k in (*REQUIRED, *RECOMMENDED, *OPTIONAL)]
    notes: list[str] = []
    order_ok = True
    if "experience" in keys and "education" in keys:
        exp_first = keys.index("experience") < keys.index("education")
        if not exp_first and years >= 2:
            order_ok = False
            notes.append("Education appears before Experience. With 2+ years of work history, lead with Experience.")
    if "summary" in keys and keys.index("summary") > 2:
        notes.append("Move the summary to the top, directly under your contact details.")
    verdict, length_factor = length_verdict(parsed.word_count)
    if verdict != "Ideal length":
        notes.append(f"{verdict} at {parsed.word_count} words (450–900 suits most 1–2 page resumes).")
    missing_req = [LABELS[k] for k in REQUIRED if k not in keys]
    if missing_req:
        notes.append("Missing standard sections: " + ", ".join(missing_req) + ".")
    score = sum(20 for k in REQUIRED if k in keys)
    score += 10 if "summary" in keys else 0
    score += 20 * length_factor
    score += 10 if order_ok else 0
    return R.Structure(score=clamp(score), sections=sections, order_ok=order_ok, notes=notes, length_verdict=verdict)


# ---------- ATS ----------

_ODD_GLYPH = re.compile(r"[-\U0001F300-\U0001FAFF☀-➿]")


def ats(parsed: ParsedResume, text: str, source: str, skills_found: list[SkillHit]) -> R.ATS:
    c = parsed.contact
    keys = {s.key for s in parsed.sections}
    checks: list[R.Check] = []

    def add(id_: str, label: str, ok: bool | None, detail: str, impact: R.Impact, warn: bool = False) -> None:
        status: R.Status = "pass" if ok else ("warn" if warn else "fail")
        checks.append(R.Check(id=id_, label=label, status=status, detail=detail, impact=impact))

    add("email", "Email address", bool(c.email), c.email or "No email address found.", "high")
    add("phone", "Phone number", bool(c.phone), c.phone or "No phone number found in the header.", "medium", warn=True)
    add("name", "Candidate name", bool(c.name), c.name or "The first lines don’t look like a name. Put your name alone on line one.", "medium", warn=True)
    std = [k for k in ("experience", "education", "skills") if k in keys]
    add("headings", "Standard section headings", len(std) == 3,
        f"Recognized {len(std)}/3 standard headings" + ("." if len(std) == 3 else f"; missing {', '.join(k.title() for k in ('experience', 'education', 'skills') if k not in keys)}."),
        "high", warn=len(std) == 2)
    if parsed.roles:
        dated = sum(1 for r in parsed.roles if r.start)
        add("dates", "Parsable employment dates", dated == len(parsed.roles),
            f"{dated}/{len(parsed.roles)} roles have dates in a recognizable format (e.g. “Jan 2022 – Present”).",
            "medium", warn=dated > 0)
    else:
        add("dates", "Parsable employment dates", False, "No roles with dates were found.", "medium")
    lines = [ln for ln in parsed.lines if ln.strip()]
    short = sum(1 for ln in lines if len(ln.split()) <= 2)
    ratio = short / len(lines) if lines else 0
    add("layout", "Single-column, linear layout", ratio < 0.4,
        "Text reads in a linear order." if ratio < 0.4 else
        f"{int(ratio * 100)}% of lines are 1–2 words, a sign of columns, tables or text boxes that ATS may scramble.",
        "high", warn=ratio < 0.55)
    odd = len(_ODD_GLYPH.findall(text))
    add("glyphs", "No icons or special glyphs", odd == 0,
        "No icon fonts or emoji detected." if odd == 0 else f"{odd} icon/emoji character(s) may render as garbage in ATS.",
        "low", warn=odd < 5)
    add("bullets", "Bulleted achievements", len(parsed.bullets) >= 5,
        f"{len(parsed.bullets)} bullet point(s) detected.", "medium", warn=len(parsed.bullets) >= 2)
    hard = [s for s in skills_found if not s.soft]
    add("keywords", "Machine-readable skills", len(hard) >= 8,
        f"{len(hard)} recognized hard skills.", "high", warn=len(hard) >= 4)
    add("length", "Appropriate length", 350 <= parsed.word_count <= 1100,
        f"{parsed.word_count} words (~{max(1, round(parsed.word_count / 500, 1))} page(s)).", "medium",
        warn=200 <= parsed.word_count <= 1400)
    add("filetype", "ATS-friendly file type", source in {"pdf", "docx", "txt", "paste"},
        {"pdf": "Text-based PDF.", "docx": "Word document (most ATS parse DOCX best).", "txt": "Plain text.",
         "paste": "Pasted text; export as PDF or DOCX when applying."}.get(source, source), "low")
    has_li = any("linkedin" in ln.lower() for ln in c.links)
    add("linkedin", "LinkedIn profile", has_li, "LinkedIn URL found." if has_li else "Add a LinkedIn URL to the header.", "low", warn=True)
    if parsed.contact.email and re.search(r"\d{4,}|hotmail|aol\.", parsed.contact.email or ""):
        add("email_style", "Professional email", False, "Consider an address based on your name on a current provider.", "low", warn=True)

    weight = {"high": 3, "medium": 2, "low": 1}
    val = {"pass": 1.0, "warn": 0.5, "fail": 0.0}
    total = sum(weight[ch.impact] for ch in checks)
    score = clamp(sum(weight[ch.impact] * val[ch.status] for ch in checks) / total * 100)

    fields = [bool(c.name), bool(c.email), bool(c.phone), bool(parsed.roles and parsed.roles[0].start),
              bool(parsed.education), bool(parsed.skills_listed)]
    confidence = clamp(sum(fields) / len(fields) * 100)
    fails = [ch for ch in checks if ch.status == "fail"]
    if score >= 85:
        summary = "Likely to parse cleanly in mainstream ATS."
    elif score >= 65:
        summary = f"Mostly parseable; {len(fails) or 'a few'} issue(s) could drop fields."
    else:
        summary = "High risk of fields being lost or misfiled by ATS parsers."
    return R.ATS(score=score, checks=checks, parse_confidence=confidence, summary=summary)


# ---------- keywords ----------

def keywords(text: str, bullets: list[str], skills_found: list[SkillHit], expected: list[str]) -> R.Keywords:
    top = [R.Term(term=t, count=c) for t, c in keyword_terms(text, top=24)]
    body_tokens = Counter(t for t in tokens(" ".join(bullets)) if len(t) > 3)
    skill_words = {w.lower() for s in skills_found for w in s.name.split()}
    overused = [R.Term(term=t, count=c) for t, c in body_tokens.most_common(40)
                if c >= 4 and t not in skill_words and t not in {"with", "that", "from", "team", "teams", "using"}][:6]
    resume_low = text.lower()
    missing = [k for k in expected if k.lower() not in resume_low][:15]
    words = max(1, len(tokens(text)))
    distinct_hard = len([s for s in skills_found if not s.soft])
    density = round(distinct_hard / words * 100, 2)
    if expected:
        coverage = 1 - len(missing) / len(expected)
        score = clamp(coverage * 85 + min(15, distinct_hard))
    else:
        score = clamp(min(70, distinct_hard * 5) + min(30, density * 8))
    score = clamp(score - len(overused) * 3)
    return R.Keywords(score=score, top=top, overused=overused, missing=missing, density=density)
