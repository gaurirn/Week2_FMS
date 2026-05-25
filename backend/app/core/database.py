"""
Database Setup

Creates the SQLAlchemy engine, session factory, and declarative base class.
Also exposes `get_db()` which is a FastAPI dependency that yields a database
session and guarantees that it is closed once the request finishes.

The structure here is deliberately kept generic so the underlying database
can be swapped (e.g., from SQLite to PostgreSQL) without code changes
elsewhere in the application.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _create_engine() -> Engine:
    """Build the SQLAlchemy engine with database-specific kwargs."""
    connect_args = {}
    if settings.DATABASE_URL.startswith("sqlite"):
        # Required by SQLite when used with multiple threads (FastAPI workers).
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.DATABASE_URL,
        echo=settings.SQL_ECHO,
        connect_args=connect_args,
        future=True,
    )


# ---- Engine / Session --------------------------------------------------
engine: Engine = _create_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base class shared by every ORM model."""

    pass


# ---- FastAPI dependency -----------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    Usage in a router:
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called once on application startup."""
    # Importing models here ensures they are registered with Base.metadata
    # before tables are created.
    from app.models import feedback_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
