"""Glue between HTTP routes, the engine, the AI provider and the database."""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .ai import get_provider
from .ai.base import AIProviderError
from .engine.analyzer import analyze
from .engine.parser import parse
from .models import Analysis, Resume, User

log = logging.getLogger(__name__)


def parsed_snapshot(text: str) -> dict:
    p = parse(text)
    d = p.to_dict()
    d["word_count"] = p.word_count
    return d


def run_analysis(db: Session, user: User, resume: Resume, *, job_title: str | None, job_description: str | None,
                 target_role: str | None, use_ai: bool) -> Analysis:
    target = target_role or user.target_role or (user.preferences or {}).get("default_target_role")
    result = analyze(resume.text, source=resume.source, job_description=job_description, job_title=job_title,
                     target_role=target)
    data = result.model_dump(mode="json")

    provider = get_provider()
    wants_ai = use_ai and (user.preferences or {}).get("ai_enhancement", True)
    if wants_ai and provider.name != "deterministic":
        try:
            enhancement = provider.enhance(resume.text, data, job_description)
            if enhancement:
                data["ai"] = enhancement.model_dump()
                data["provider"] = {"name": provider.name, "ai_enhanced": True, "note": None}
        except AIProviderError as exc:
            log.warning("AI enhancement failed: %s", exc)
            data["provider"] = {"name": "deterministic", "ai_enhanced": False,
                                "note": "AI enhancement was unavailable; showing deterministic analysis."}

    analysis = Analysis(
        user_id=user.id,
        resume_id=resume.id,
        job_title=(data["match"] or {}).get("job_title") if data.get("match") else job_title,
        job_description=job_description or None,
        target_role=data["skills"]["target_role"],
        overall_score=data["overall"]["score"],
        ats_score=data["ats"]["score"],
        match_score=data["match"]["score"] if data.get("match") else None,
        result=data,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def resume_stats(db: Session, resume_ids: list[int]) -> dict[int, tuple[int, int | None]]:
    """resume_id -> (analysis count, latest overall score)."""
    if not resume_ids:
        return {}
    counts = dict(db.execute(
        select(Analysis.resume_id, func.count(Analysis.id)).where(Analysis.resume_id.in_(resume_ids)).group_by(Analysis.resume_id)
    ).all())
    latest: dict[int, int] = {}
    rows = db.execute(
        select(Analysis.resume_id, Analysis.overall_score).where(Analysis.resume_id.in_(resume_ids))
        .order_by(Analysis.created_at.desc(), Analysis.id.desc())
    ).all()
    for rid, score in rows:
        latest.setdefault(rid, score)
    return {rid: (counts.get(rid, 0), latest.get(rid)) for rid in resume_ids}
