"""Database connection and session management - SQLite"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from .config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


# Create sync engine (SQLite)
engine = create_engine(
    settings.database_url.replace("+aiosqlite", "").replace("postgresql+asyncpg", "sqlite"),
    echo=settings.debug,
    connect_args={"check_same_thread": False},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create all tables"""
    from .models import chemical, facility, scenario, result  # noqa
    Base.metadata.create_all(bind=engine)


def close_db() -> None:
    """Close database connection"""
    engine.dispose()
