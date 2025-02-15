"""
Database configuration and session management.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import config

# Create database URL
DATABASE_URL = (
    f"postgresql+asyncpg://{config.database.DB_USER}:{config.database.DB_PASSWORD}"
    f"@{config.database.DB_HOST}:{config.database.DB_PORT}/{config.database.DB_NAME}"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=config.app.DEBUG,  # Log SQL statements when in debug mode
    pool_size=5,  # Default connection pool size
    max_overflow=10,  # Maximum number of connections to overflow
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_pre_ping=True,  # Enable connection health checks
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with async context management.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        async with get_db() as db:
            result = await db.execute(select(Model))
            models = result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_engine() -> AsyncEngine:
    """Get SQLAlchemy async engine instance.
    
    Returns:
        AsyncEngine: SQLAlchemy async engine instance
    """
    return engine

async def init_db() -> AsyncEngine:
    """Initialize database with required tables.
    
    Returns:
        AsyncEngine: SQLAlchemy async engine instance
    """
    # Import all models here to ensure they are registered
    from src.models import Base  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine 