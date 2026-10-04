from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..ai import get_provider
from ..ai.base import AIProviderError
from ..ai.deterministic import DeterministicProvider
from ..db import get_db
from ..deps import current_user
from ..engine import ENGINE_VERSION
from ..engine.compare import compare
from ..engine.taxonomy import ROLES
from ..models import Analysis, Resume, User
from ..schemas import (AnalysisOut, AnalysisSummary, AnalyzeIn, CompareIn, DashboardOut, MetaOut, RewriteIn,
                       RewriteOut)
from ..services import run_analysis

router = APIRouter(tags=["analysis"])


def _summary(a: Analysis) -> AnalysisSummary:
    return AnalysisSummary(id=a.id, resume_id=a.resume_id, resume_title=a.resume.title, job_title=a.job_title,
                           target_role=a.target_role, overall_score=a.overall_score, ats_score=a.ats_score,
                           match_score=a.match_score, created_at=a.created_at)


def _full(a: Analysis) -> AnalysisOut:
    return AnalysisOut(**_summary(a).model_dump(), result=a.result, job_description=a.job_description)


def _owned(db: Session, user: User, analysis_id: int) -> Analysis:
    a = db.get(Analysis, analysis_id, options=[joinedload(Analysis.resume)])
    if not a or a.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found")
    return a


@router.get("/meta", response_model=MetaOut)
def meta() -> MetaOut:
    p = get_provider()
    return MetaOut(roles=[r.name for r in ROLES], ai_provider=p.name, ai_available=p.name != "deterministic",
                   engine_version=ENGINE_VERSION)


@router.post("/analyses", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def create_analysis(body: AnalyzeIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> AnalysisOut:
    resume = db.get(Resume, body.resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    jd = (body.job_description or "").strip() or None
    if jd and len(jd) < 80:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Paste the full job description (at least 80 characters)")
    a = run_analysis(db, user, resume, job_title=(body.job_title or "").strip() or None, job_description=jd,
                     target_role=body.target_role, use_ai=body.use_ai)
    a.resume = resume
    return _full(a)


@router.get("/analyses", response_model=list[AnalysisSummary])
def list_analyses(resume_id: int | None = None, q: str | None = Query(default=None, max_length=100),
                  limit: int = Query(default=50, ge=1, le=200), user: User = Depends(current_user),
                  db: Session = Depends(get_db)) -> list[AnalysisSummary]:
    stmt = (select(Analysis).options(joinedload(Analysis.resume)).where(Analysis.user_id == user.id)
            .order_by(Analysis.created_at.desc(), Analysis.id.desc()).limit(limit))
    if resume_id is not None:
        stmt = stmt.where(Analysis.resume_id == resume_id)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.join(Resume).where((Resume.title.ilike(like)) | (Analysis.job_title.ilike(like)))
    return [_summary(a) for a in db.scalars(stmt).unique().all()]


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> AnalysisOut:
    return _full(_owned(db, user, analysis_id))


@router.delete("/analyses/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(_owned(db, user, analysis_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/compare")
def compare_analyses(body: CompareIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    a, b = _owned(db, user, body.a), _owned(db, user, body.b)
    return {"a": _summary(a).model_dump(mode="json"), "b": _summary(b).model_dump(mode="json"), **compare(a.result, b.result)}


@router.post("/studio/rewrite", response_model=RewriteOut)
def rewrite_bullet(body: RewriteIn, user: User = Depends(current_user)) -> RewriteOut:
    provider = get_provider()
    if not (user.preferences or {}).get("ai_enhancement", True):
        provider = DeterministicProvider()
    try:
        options = provider.rewrite_bullet(body.bullet, body.context)
    except AIProviderError:
        provider = DeterministicProvider()
        options = provider.rewrite_bullet(body.bullet, body.context)
    return RewriteOut(provider=provider.name, options=options)


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> DashboardOut:
    analyses = db.scalars(select(Analysis).options(joinedload(Analysis.resume)).where(Analysis.user_id == user.id)
                          .order_by(Analysis.created_at.desc(), Analysis.id.desc()).limit(200)).unique().all()
    resume_count = len(db.scalars(select(Resume.id).where(Resume.user_id == user.id)).all())
    latest = analyses[0] if analyses else None
    trend = [{"id": a.id, "date": a.created_at.isoformat(), "overall": a.overall_score, "ats": a.ats_score,
              "match": a.match_score, "label": a.resume.title} for a in reversed(analyses[:20])]
    recs = (latest.result.get("recommendations", [])[:4]) if latest else []
    return DashboardOut(resume_count=resume_count, analysis_count=len(analyses),
                        best_score=max((a.overall_score for a in analyses), default=None),
                        latest=_summary(latest) if latest else None, trend=trend,
                        recent=[_summary(a) for a in analyses[:6]], top_recommendations=recs)
