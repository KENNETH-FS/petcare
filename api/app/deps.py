from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.users import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing user context",
    )


def get_current_user(
    x_user_id: Annotated[str | None, Header()] = None,
    db: DbSession = None,
) -> User:
    if x_user_id is None:
        raise _unauthorized()

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise _unauthorized()

    user = db.get(User, user_id)
    if user is None:
        raise _unauthorized()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
