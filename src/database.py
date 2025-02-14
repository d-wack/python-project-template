"""
Database configuration and session management.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.config import config

# Create database URL
DATABASE_URL = (
    f"postgresql://{config.database.DB_USER}:{config.database.DB_PASSWORD}"
    f"@{config.database.DB_HOST}:{config.database.DB_PORT}/{config.database.DB_NAME}"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=config.app.DEBUG,  # Log SQL statements when in debug mode
    pool_size=5,  # Default connection pool size
    max_overflow=10,  # Maximum number of connections to overflow
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_pre_ping=True,  # Enable connection health checks
    poolclass=QueuePool,  # Use QueuePool for connection pooling
)

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with context management.
    
    Yields:
        Session: Database session
        
    Example:
        with get_db() as db:
            db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_engine() -> Engine:
    """Get SQLAlchemy engine instance.
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine

def init_db() -> None:
    """Initialize database with required tables."""
    # Import all models here to ensure they are registered
    from src.models import Base  # noqa

    Base.metadata.create_all(bind=engine) 