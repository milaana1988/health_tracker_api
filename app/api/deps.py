from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import session_context

__all__ = ["get_db"]


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session with rollback-on-exception."""
    with session_context() as db:
        yield db
