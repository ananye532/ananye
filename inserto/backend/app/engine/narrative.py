"""Recruiter-style feedback, recommendations and career insights, assembled from the check results."""

from __future__ import annotations

import zlib

from . import result as R
from .parser import ParsedResume


def recruiter(parsed: ParsedResume, overall: int, subs: list[R.Subscore], exp: R.Experience,
              skills: R.Skills, quant: R.Quantification, edu: R.Education, match: R.Match | None,
              top_role: str | None) -> R.Recruiter:
    latest = parsed.roles[0] if parsed.roles else None
    hard = [s.name for s in skills.found if not s.soft][:5]
    skim: list[str] = []
    if parsed.contact.name:
        skim.append(parsed.contact.name)
    if latest:
        skim.append(f"{latest.title}" + (f" at {latest.company}" if latest.company else "") +
                    (" (current)" if latest.is_current else ""))
    if exp.total_years:
        skim.append(f"{exp.total_years:g} years across {exp.role_count} role(s)")
    if hard:
        skim.append("Top skills: " + ", ".join(hard))
    if edu.highest:
        skim.append(f"{edu.highest} degree")

    strengths: list[str] = []
    concerns: list[str] = []
    if quant.ratio >= 0.5:
        strengths.append(f"Impact is evidenced: {quant.quantified} of {quant.total} bullets carry numbers.")
    elif quant.total:
        concerns.append(f"Only {quant.quantified} of {quant.total} bullets show measurable results; impact is hard to judge.")
    if exp.total_years and exp.score >= 70:
        strengths.append(f"{exp.seniority} trajectory with {exp.total_years:g} years of experience.")
    if exp.gaps:
        concerns.append(f"{len(exp.gaps)} employment gap(s) of 6+ months without explanation.")
    if len(hard) >= 5:
        strengths.append(f"Clear technical profile ({', '.join(hard[:3])}).")
    elif len(hard) < 3:
        concerns.append("Hard skills are thin or not machine-recognizable.")
    if skills.unsupported:
        concerns.append(f"{len(skills.unsupported)} listed skill(s) never appear in experience, e.g. {', '.join(skills.unsupported[:3])}.")
    for s in sorted(subs, key=lambda x: -x.score)[:2]:
        if s.score >= 80:
            strengths.append(f"Strong {s.label.lower()} ({s.score}/100).")
    for s in sorted(subs, key=lambda x: x.score)[:2]:
        if s.score < 55:
            concerns.append(f"Weak {s.label.lower()} ({s.score}/100).")
    if match:
        if match.score >= 70:
            strengths.append(f"Aligned with {match.job_title or 'the target role'}: {len(match.matched_skills)} required skills shown.")
        elif match.missing_skills:
            concerns.append(f"Missing for this job: {', '.join(match.missing_skills[:4])}.")

    who = (latest.title if latest else top_role) or "candidate"
    if overall >= 80:
        first = f"A polished {who.lower() if who == 'candidate' else who} resume that reads quickly and shows results."
        verdict = "Would likely advance to a phone screen if the role aligns."
    elif overall >= 65:
        first = f"A credible {who} profile; the signal is there but takes effort to find."
        verdict = "Competitive, but a sharper top third and more metrics would raise response rates."
    elif overall >= 45:
        first = f"Relevant background for a {who}, but impact and structure are unclear on a quick skim."
        verdict = "At risk of being passed over in a high-volume pipeline."
    else:
        first = "Hard to assess in a six-second skim: key sections, dates or outcomes are missing."
        verdict = "Needs structural fixes before it can compete."
    return R.Recruiter(first_impression=first, strengths=strengths[:5],
                       concerns=concerns[:5], skim=skim, verdict=verdict)


def recommendations(parsed: ParsedResume, ats: R.ATS, structure: R.Structure, skills: R.Skills,
                    kw: R.Keywords, exp: R.Experience, quant: R.Quantification, verbs: R.ActionVerbs,
                    read: R.Readability, edu: R.Education, match: R.Match | None,
                    rewrites: list[R.Rewrite]) -> list[R.Recommendation]:
    recs: list[R.Recommendation] = []

    def add(id_: str, priority: R.Priority, cat: str, title: str, detail: str,
            before: str | None = None, after: str | None = None) -> None:
        recs.append(R.Recommendation(id=id_, priority=priority, category=cat, title=title, detail=detail,
                                     before=before, after=after))

    for ch in ats.checks:
        if ch.status == "fail" and ch.impact == "high":
            add(f"ats-{ch.id}", "critical", "ATS", f"Fix: {ch.label.lower()}", ch.detail)
        elif ch.status == "fail" and ch.impact == "medium":
            add(f"ats-{ch.id}", "high", "ATS", f"Fix: {ch.label.lower()}", ch.detail)
        elif ch.status == "warn" and ch.impact == "high":
            add(f"ats-{ch.id}", "high", "ATS", f"Review: {ch.label.lower()}", ch.detail)

    if match and match.missing_skills:
        add("match-skills", "critical" if match.skill_score < 50 else "high", "Job match",
            f"Address {len(match.missing_skills)} skill(s) the job asks for",
            "Where you genuinely have the experience, name these skills in a bullet that shows how you used them: "
            + ", ".join(match.missing_skills[:8]) + ". Don’t add skills you can’t discuss in an interview.")
    if match and match.missing_keywords:
        add("match-keywords", "medium", "Job match", "Mirror the job’s language",
            "Terms from the posting that don’t appear in your resume: " + ", ".join(match.missing_keywords[:10]) + ".")

    if quant.total and quant.ratio < 0.5:
        ex = next((r for r in rewrites if r.needs_input), None)
        add("quantify", "critical" if quant.ratio < 0.25 else "high", "Impact",
            "Quantify your results",
            f"{quant.total - quant.quantified} of {quant.total} bullets have no numbers. Add scale (users, revenue, team size), "
            "speed (time saved) or quality (error rate) to each.",
            ex.original if ex else None, ex.improved if ex else None)
    if verbs.weak:
        w = verbs.weak[0]
        ex = next((r for r in rewrites if any("opener" in x for x in r.reasons)), None)
        add("weak-verbs", "high", "Language", "Replace passive, duty-based phrasing",
            f"“{w.phrase}” appears {w.count}×. Lead with what you did: {w.suggestion}.",
            ex.original if ex else None, ex.improved if ex else None)
    if verbs.repeated:
        add("repeated-verbs", "low", "Language", "Vary your action verbs",
            "Used 3+ times as an opener: " + ", ".join(f"{v.verb} ({v.count}×)" for v in verbs.repeated) + ".")
    if verbs.starts_with_verb_ratio < 0.6 and parsed.bullets:
        add("verb-openers", "medium", "Language", "Start every bullet with an action verb",
            f"Only {int(verbs.starts_with_verb_ratio * 100)}% of bullets open with an action verb.")

    if not parsed.summary:
        add("summary", "medium", "Structure", "Add a 2–3 line summary",
            "Lead with your role, years of experience, core stack and one headline result. It frames everything below it.")
    elif len(parsed.summary.split()) > 70:
        add("summary-long", "low", "Structure", "Shorten the summary", "Keep it under 60 words; move detail into bullets.")
    for n in structure.notes:
        if "Missing standard sections" in n:
            continue
        if n.startswith(("Too short", "Concise", "Long", "Too long")):
            title = "Expand your resume" if n.startswith(("Too short", "Concise")) else "Trim your resume"
        elif "before Experience" in n:
            title = "Lead with experience"
        elif "summary" in n.lower():
            title = "Move the summary to the top"
        else:
            title = "Improve section structure"
        add(f"structure-{zlib.crc32(n.encode()) % 10_000}", "medium", "Structure", title, n)

    if skills.unsupported:
        add("skills-evidence", "medium", "Skills", "Back listed skills with evidence",
            "These appear only in your skills list: " + ", ".join(skills.unsupported[:8]) +
            ". Mention them in an experience or project bullet so they carry weight.")
    if skills.missing and not match:
        core = [g.name for g in skills.missing if g.importance == "core"]
        if core:
            add("role-gaps", "medium", "Skills", f"Core {skills.target_role} skills not shown",
                "Commonly expected and not found: " + ", ".join(core) + ".")
    if read.first_person:
        add("pronouns", "medium", "Readability", "Drop first-person pronouns",
            f"Found {read.first_person}. Write “Led X”, not “I led X”.")
    if read.long_bullets:
        add("long-bullets", "medium", "Readability", "Shorten long bullets",
            "Keep bullets to one or two lines (under ~30 words).", read.long_bullets[0])
    if read.buzzwords:
        add("buzzwords", "low", "Readability", "Replace buzzwords with evidence",
            "Show, don’t claim: " + ", ".join(b.term for b in read.buzzwords[:5]) + ".")
    for n in exp.notes:
        if "gap" in n:
            add("gap", "low", "Experience", "Explain employment gaps", n)
            break
    if exp.role_count and exp.bullets_per_role < 2.5:
        add("thin-roles", "medium", "Experience", "Add depth to each role",
            "Aim for 3–5 outcome-focused bullets for recent roles.")
    for n in edu.notes:
        if "No education" in n:
            add("edu-missing", "medium", "Education", "Add an education section", n)
        elif "GPA" in n:
            add("edu-gpa", "low", "Education", "Consider removing your GPA", n)

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    seen: set[str] = set()
    unique = []
    for r in sorted(recs, key=lambda r: order[r.priority]):
        if r.id not in seen:
            seen.add(r.id)
            unique.append(r)
    return unique[:16]


def insights(exp: R.Experience, skills: R.Skills, fits: list[R.RoleFit], recs: list[R.Recommendation]) -> R.Insights:
    cats = sorted(skills.by_category, key=lambda c: -c.count)
    strengths = [f"{c.category} ({c.count} skills)" for c in cats if c.category != "Soft Skills"][:3]
    next_steps = [r.title for r in recs[:4]]
    top = fits[0] if fits else None
    if top and top.missing:
        next_steps.append(f"Build evidence in {', '.join(top.missing[:2])} to strengthen your {top.role} profile.")
    return R.Insights(career_level=exp.seniority, role_fits=fits[:4], strengths=strengths,
                      growth_skills=skills.missing[:6], next_steps=next_steps[:5])
