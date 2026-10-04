from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db import get_db
from ..deps import current_user
from ..engine.extract import ExtractionError, extract, from_paste
from ..models import Resume, User
from ..schemas import PasteIn, RenameIn, ResumeDetail, ResumeOut
from ..services import parsed_snapshot, resume_stats

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_EXT = (".pdf", ".docx", ".txt")


def _out(r: Resume, stats: dict[int, tuple[int, int | None]], detail: bool = False) -> ResumeOut:
    count, latest = stats.get(r.id, (0, None))
    base = dict(id=r.id, title=r.title, source=r.source, filename=r.filename, page_count=r.page_count,
                created_at=r.created_at, word_count=(r.parsed or {}).get("word_count", 0),
                latest_score=latest, analysis_count=count)
    if detail:
        return ResumeDetail(**base, text=r.text, parsed=r.parsed or {})
    return ResumeOut(**base)


def _owned(db: Session, user: User, resume_id: int) -> Resume:
    r = db.get(Resume, resume_id)
    if not r or r.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return r


def _bad(exc: ExtractionError) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, {"code": exc.code, "message": exc.message})


@router.post("/upload", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...), title: str | None = Form(default=None),
                 user: User = Depends(current_user), db: Session = Depends(get_db)) -> ResumeOut:
    s = get_settings()
    name = file.filename or "resume"
    if not name.lower().endswith(ALLOWED_EXT):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, {"code": "unsupported", "message": "Upload a PDF, DOCX or TXT file."})
    data = await file.read(s.max_upload_bytes + 1)  # capped read: never buffer an oversized file in full
    if len(data) > s.max_upload_bytes:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, {"code": "too_large", "message": f"Files are limited to {s.max_upload_bytes // (1024 * 1024)} MB."})
    if not data:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, {"code": "empty_file", "message": "The file is empty."})
    try:
        ex = extract(name, data, max_pages=s.max_pdf_pages)
    except ExtractionError as exc:
        raise _bad(exc) from exc
    text = ex.text[: s.max_text_chars]
    clean_title = (title or "").strip()[:200] or name.rsplit(".", 1)[0][:200]
    r = Resume(user_id=user.id, title=clean_title, source=ex.source, filename=name[:255], text=text,
               page_count=ex.page_count, parsed=parsed_snapshot(text))
    db.add(r)
    db.commit()
    db.refresh(r)
    return _out(r, {}, detail=True)


@router.post("/paste", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
def paste(body: PasteIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ResumeOut:
    try:
        ex = from_paste(body.text)
    except ExtractionError as exc:
        raise _bad(exc) from exc
    r = Resume(user_id=user.id, title=body.title.strip(), source="paste", filename=None, text=ex.text,
               page_count=None, parsed=parsed_snapshot(ex.text))
    db.add(r)
    db.commit()
    db.refresh(r)
    return _out(r, {}, detail=True)


@router.get("", response_model=list[ResumeOut])
def list_resumes(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ResumeOut]:
    rows = db.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc(), Resume.id.desc())).all()
    stats = resume_stats(db, [r.id for r in rows])
    return [_out(r, stats) for r in rows]


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ResumeOut:
    r = _owned(db, user, resume_id)
    return _out(r, resume_stats(db, [r.id]), detail=True)


@router.patch("/{resume_id}", response_model=ResumeOut)
def rename_resume(resume_id: int, body: dict, user: User = Depends(current_user), db: Session = Depends(get_db)) -> ResumeOut:
    r = _owned(db, user, resume_id)
    title = str(body.get("title", "")).strip()
    if not title or len(title) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Title must be 1–200 characters")
    r.title = title
    db.commit()
    return _out(r, resume_stats(db, [r.id]))


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(_owned(db, user, resume_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
