from __future__ import annotations

import hashlib
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..models import Analysis, Job, Resume, User
from ..nlp.pdf_extract import PDFExtractionError, extract_text_from_pdf
from ..nlp.preprocessing import clean_text
from ..nlp.sections import detect_sections
from ..nlp.skills import extract_skills
from ..schemas import AnalysisCreate, AnalysisOut, JobCreate, JobOut, ResumeOut, UserCreate, UserCreated
from ..security import current_user, hash_api_key, http_error, new_api_key, read_validated_pdf
from ..services import report
from ..services.analyzer import analyze

router = APIRouter(prefix="/api")


def _owned(db: Session, model, obj_id: uuid.UUID, user: User):
    """Fetch a row owned by `user`. Other users' rows return 404 so their existence isn't revealed."""
    obj = db.get(model, obj_id)
    if obj is None or obj.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{model.__name__} not found.")
    return obj


def _resume_out(r: Resume) -> ResumeOut:
    return ResumeOut(
        id=r.id,
        filename=r.filename,
        page_count=r.page_count,
        word_count=len(r.text.split()),
        sections=r.sections,
        skills=r.skills,
        text_preview=r.text[:1500],
        created_at=r.created_at,
    )


def _analysis_out(a: Analysis) -> AnalysisOut:
    return AnalysisOut(id=a.id, resume_id=a.resume_id, job_id=a.job_id, created_at=a.created_at, result=a.result)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Users --------------------------------------------------------------------


@router.post("/users", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> UserCreated:
    key = new_api_key()
    user = User(email=body.email.lower(), api_key_hash=hash_api_key(key))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered.") from None
    return UserCreated(id=user.id, email=user.email, api_key=key)


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    """Permanently delete the account and, by cascade, all resumes, jobs and analyses."""
    db.delete(db.merge(user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Resumes ------------------------------------------------------------------


@router.post("/resumes", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)
) -> ResumeOut:
    filename, data = await read_validated_pdf(file)
    try:
        extracted = await run_in_threadpool(extract_text_from_pdf, data, get_settings().max_pdf_pages)
    except PDFExtractionError as exc:
        raise http_error(422, exc.code, exc.message) from None

    sections = detect_sections(extracted.text)
    skills = [h.to_dict() for h in extract_skills(extracted.text).values()]
    resume = Resume(
        user_id=user.id,
        filename=filename,
        file_sha256=hashlib.sha256(data).hexdigest(),
        page_count=extracted.page_count,
        text=extracted.text,
        sections=sections,
        skills=skills,
    )
    db.add(resume)
    db.commit()
    return _resume_out(resume)


@router.get("/resumes", response_model=list[ResumeOut])
def list_resumes(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ResumeOut]:
    rows = db.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    return [_resume_out(r) for r in rows]


@router.get("/resumes/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ResumeOut:
    return _resume_out(_owned(db, Resume, resume_id, user))


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(_owned(db, Resume, resume_id, user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Jobs ---------------------------------------------------------------------


@router.post("/jobs", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(body: JobCreate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Job:
    s = get_settings()
    description = clean_text(body.description)
    if not s.min_job_chars <= len(description) <= s.max_job_chars:
        raise http_error(
            422,
            "bad_job_length",
            f"Job description must be {s.min_job_chars}-{s.max_job_chars} characters.",
        )
    job = Job(
        user_id=user.id,
        title=body.title.strip(),
        company=(body.company or "").strip() or None,
        description=description,
        skills=[h.to_dict() for h in extract_skills(description).values()],
    )
    db.add(job)
    db.commit()
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Job:
    return _owned(db, Job, job_id, user)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(_owned(db, Job, job_id, user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Analyses -----------------------------------------------------------------


@router.post("/analyses", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    body: AnalysisCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> AnalysisOut:
    resume = _owned(db, Resume, body.resume_id, user)
    job = _owned(db, Job, body.job_id, user)
    result = await run_in_threadpool(analyze, resume.text, job.description, get_settings().top_n_keywords)
    m = result["metrics"]
    analysis = Analysis(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id,
        skill_coverage=m["skill_coverage"]["value"],
        keyword_coverage=m["keyword_coverage"]["value"],
        cosine_similarity=m["cosine_similarity"]["value"],
        taxonomy_version=result["taxonomy_version"],
        result=result,
    )
    db.add(analysis)
    db.commit()
    return _analysis_out(analysis)


@router.get("/analyses/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: uuid.UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> AnalysisOut:
    return _analysis_out(_owned(db, Analysis, analysis_id, user))


@router.get("/analyses/{analysis_id}/report")
def download_report(
    analysis_id: uuid.UUID,
    format: Literal["md", "json"] = Query("md"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Response:
    a = _owned(db, Analysis, analysis_id, user)
    meta = {
        "analysis_id": str(a.id),
        "resume_filename": a.resume.filename,
        "job_title": a.job.title,
        "created_at": a.created_at,
    }
    if format == "json":
        body, media = report.to_json(a.result, meta), "application/json"
    else:
        body, media = report.to_markdown(a.result, meta), "text/markdown; charset=utf-8"
    return Response(
        content=body,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="resume-analysis-{a.id}.{format}"'},
    )
