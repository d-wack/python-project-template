"""
Test cases for the database module.
"""
import pytest
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.schema import CreateTable
from pytest_asyncio import fixture

from src.database import get_db, init_db, AsyncSessionLocal
from src.models.base import Base

@fixture(scope="function")
async def db():
    """Initialize database and provide a session.
    
    Returns:
        AsyncSession: Database session for testing
    """
    # Initialize database
    engine = await init_db()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_database_initialization():
    """Test database initialization."""
    engine = await init_db()
    assert engine is not None
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    finally:
        await engine.dispose()

@pytest.mark.asyncio
async def test_database_session_management(db):
    """Test database session management."""
    assert isinstance(db, AsyncSession)
    result = await db.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_database_transaction_rollback(db):
    """Test database transaction rollback."""
    # Start a transaction
    async with db.begin():
        await db.execute(text("SELECT 1"))
        with pytest.raises(Exception, match="Test rollback"):
            raise Exception("Test rollback")
    
    # Verify session is still usable after rollback
    result = await db.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_database_model_operations(db):
    """Test database model operations."""
    # Create a test table
    class TestModel(Base):
        __tablename__ = "test_model"
        name = Column(String)
    
    # Create the table
    async with db.begin():
        await db.execute(CreateTable(TestModel.__table__))
    
    # Test CRUD operations
    test_model = TestModel(name="test")
    db.add(test_model)
    await db.commit()
    
    # Query the model
    result = await db.execute(
        select(TestModel).where(TestModel.name == "test")
    )
    model = result.scalar_one()
    assert model.name == "test"
    
    # Update the model
    model.name = "updated"
    await db.commit()
    
    # Delete the model
    await db.delete(model)
    await db.commit()
    
    # Verify deletion
    result = await db.execute(
        select(TestModel).where(TestModel.name == "updated")
    )
    assert result.first() is None 