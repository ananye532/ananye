"""Authentication and upload validation."""

from __future__ import annotations

import hashlib
import re
import secrets
from pathlib import PurePath

from fastapi import Depends, HTTPException, Security, UploadFile, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import User

ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._ -]+")


def new_api_key() -> str:
    return secrets.token_urlsafe(32)  # 256 bits of entropy


def hash_api_key(key: str) -> str:
    # A fast hash is adequate: the key is random and high-entropy, unlike a password.
    return hashlib.sha256(key.encode()).hexdigest()


def current_user(api_key: str | None = Security(_api_key_header), db: Session = Depends(get_db)) -> User:
    if not api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-API-Key header.")
    user = db.scalar(select(User).where(User.api_key_hash == hash_api_key(api_key)))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key.")
    return user


def safe_filename(name: str | None) -> str:
    """Strip directories and unusual characters. The name is only displayed, never used as a path."""
    base = PurePath((name or "").replace("\\", "/")).name
    cleaned = _UNSAFE_FILENAME.sub("_", base).strip(" .") or "resume.pdf"
    return cleaned[-255:]


def http_error(code: int, error_code: str, message: str) -> HTTPException:
    return HTTPException(code, detail={"code": error_code, "message": message})


async def read_validated_pdf(upload: UploadFile) -> tuple[str, bytes]:
    """Validate extension, declared type and size. Magic bytes are checked by the extractor.

    The read is capped at limit + 1 bytes, so an oversized upload is never held
    in memory in full.
    """
    settings = get_settings()
    filename = safe_filename(upload.filename)
    if not filename.lower().endswith(".pdf"):
        raise http_error(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "bad_extension", "Only .pdf files are accepted.")
    if (upload.content_type or "").split(";")[0].strip().lower() not in ALLOWED_CONTENT_TYPES:
        raise http_error(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "bad_content_type", "Content-Type must be application/pdf.")
    data = await upload.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise http_error(
            413, "too_large", f"File exceeds {settings.max_upload_mb:g} MB."
        )
    if not data:
        raise http_error(status.HTTP_400_BAD_REQUEST, "empty_file", "The uploaded file is empty.")
    return filename, data
