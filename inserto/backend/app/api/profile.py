from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..core.security import hash_password, verify_password
from ..db import get_db
from ..deps import current_user
from ..models import User
from ..schemas import PasswordChange, Preferences, ProfileUpdate, UserOut

router = APIRouter(prefix="/me", tags=["profile"])


@router.patch("", response_model=UserOut)
def update_profile(body: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
    for field, value in body.model_dump(exclude_unset=True).items():
        if isinstance(value, str):
            value = value.strip() or None
        if field == "name" and not value:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Name cannot be empty")
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.put("/preferences", response_model=UserOut)
def update_preferences(body: Preferences, user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
    user.preferences = body.model_dump()
    db.commit()
    db.refresh(user)
    return user


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(body: PasswordChange, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
