"""Typed analysis result. This is the contract the frontend renders."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["pass", "warn", "fail"]
Impact = Literal["high", "medium", "low"]
Priority = Literal["critical", "high", "medium", "low"]


class Subscore(BaseModel):
    key: str
    label: str
    score: int
    weight: float
    description: str


class Overall(BaseModel):
    score: int
    grade: str
    label: str
    summary: str


class ContactOut(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = []


class SectionOut(BaseModel):
    key: str
    label: str
    title: str
    line_count: int


class RoleOut(BaseModel):
    title: str
    company: str | None
    start: str | None
    end: str | None
    is_current: bool
    duration_months: int | None
    bullets: list[str]


class EducationOut(BaseModel):
    institution: str | None
    degree: str | None
    degree_level: str | None
    year: int | None
    gpa: str | None


class Parsed(BaseModel):
    contact: ContactOut
    summary: str | None
    sections: list[SectionOut]
    roles: list[RoleOut]
    education: list[EducationOut]
    skills_listed: list[str]
    certifications: list[str]
    bullet_count: int
    word_count: int
    page_estimate: float


class Check(BaseModel):
    id: str
    label: str
    status: Status
    detail: str
    impact: Impact


class ATS(BaseModel):
    score: int
    checks: list[Check]
    parse_confidence: int = Field(description="0-100: how completely the parser recovered the standard fields")
    summary: str


class SectionPresence(BaseModel):
    key: str
    label: str
    present: bool
    required: bool


class Structure(BaseModel):
    score: int
    sections: list[SectionPresence]
    order_ok: bool
    notes: list[str]
    length_verdict: str


class SkillFound(BaseModel):
    name: str
    category: str
    count: int
    soft: bool
    in_skills_section: bool
    evidence: str


class CategoryCount(BaseModel):
    category: str
    count: int


class SkillGap(BaseModel):
    name: str
    category: str
    importance: Literal["core", "nice"]
    reason: str


class Skills(BaseModel):
    score: int
    found: list[SkillFound]
    by_category: list[CategoryCount]
    hard_count: int
    soft_count: int
    missing: list[SkillGap]
    unsupported: list[str] = Field(description="Listed in the skills section but never shown in experience")
    target_role: str | None


class Term(BaseModel):
    term: str
    count: int


class Keywords(BaseModel):
    score: int
    top: list[Term]
    overused: list[Term]
    missing: list[str]
    density: float


class Gap(BaseModel):
    start: str
    end: str
    months: int


class Experience(BaseModel):
    score: int
    total_years: float
    role_count: int
    avg_tenure_months: int | None
    seniority: str
    gaps: list[Gap]
    bullets_per_role: float
    notes: list[str]


class Education(BaseModel):
    score: int
    highest: str | None
    entries: int
    notes: list[str]


class Achievements(BaseModel):
    score: int
    count: int
    examples: list[str]
    notes: list[str]


class Quantification(BaseModel):
    score: int
    quantified: int
    total: int
    ratio: float
    examples: list[str]
    unquantified: list[str]


class VerbCount(BaseModel):
    verb: str
    count: int


class WeakPhrase(BaseModel):
    phrase: str
    count: int
    suggestion: str


class ActionVerbs(BaseModel):
    score: int
    strong: list[VerbCount]
    weak: list[WeakPhrase]
    repeated: list[VerbCount]
    starts_with_verb_ratio: float


class Readability(BaseModel):
    score: int
    flesch: float
    avg_bullet_words: float
    long_bullets: list[str]
    short_bullets: list[str]
    first_person: int
    passive: int
    buzzwords: list[Term]
    notes: list[str]


class Requirement(BaseModel):
    text: str
    met: Literal["met", "partial", "missing"]
    evidence: str | None


class Match(BaseModel):
    score: int
    job_title: str | None
    skill_score: int
    keyword_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    requirements: list[Requirement]
    years_required: int | None
    years_found: float
    verdict: str


class Recruiter(BaseModel):
    first_impression: str
    strengths: list[str]
    concerns: list[str]
    skim: list[str]
    verdict: str


class Recommendation(BaseModel):
    id: str
    priority: Priority
    category: str
    title: str
    detail: str
    before: str | None = None
    after: str | None = None


class Rewrite(BaseModel):
    original: str
    improved: str
    reasons: list[str]
    needs_input: bool = Field(description="True when the rewrite contains placeholders the user must fill in")


class RoleFit(BaseModel):
    role: str
    fit: int
    matched: list[str]
    missing: list[str]


class Insights(BaseModel):
    career_level: str
    role_fits: list[RoleFit]
    strengths: list[str]
    growth_skills: list[SkillGap]
    next_steps: list[str]


class Provider(BaseModel):
    name: str
    ai_enhanced: bool
    note: str | None = None


class AnalysisResult(BaseModel):
    engine_version: str
    overall: Overall
    subscores: list[Subscore]
    parsed: Parsed
    ats: ATS
    structure: Structure
    skills: Skills
    keywords: Keywords
    experience: Experience
    education: Education
    achievements: Achievements
    quantification: Quantification
    action_verbs: ActionVerbs
    readability: Readability
    match: Match | None
    recruiter: Recruiter
    recommendations: list[Recommendation]
    rewrites: list[Rewrite]
    insights: Insights
    provider: Provider
    disclaimer: str
