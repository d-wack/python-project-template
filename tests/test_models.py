"""
Test cases for the models module.
"""
from datetime import datetime
import uuid
import pytest
from sqlalchemy import Column, String, event
from sqlalchemy.sql import functions

from src.models.base import Base

class TestModel(Base):
    """Test model for testing base functionality."""
    __tablename__ = "test_models"
    name = Column(String)

@pytest.fixture(autouse=True)
def setup_model_events():
    """Set up model events for testing."""
    @event.listens_for(TestModel, "init")
    def init_model(target, args, kwargs):
        target.id = kwargs.get("id", uuid.uuid4())
        target.created_at = kwargs.get("created_at", datetime.utcnow())
        target.updated_at = kwargs.get("updated_at", datetime.utcnow())
    
    yield
    
    # Remove the event listener after the test
    event.remove(TestModel, "init", init_model)

def test_model_initialization():
    """Test model initialization with timestamps."""
    now = datetime.utcnow()
    test_id = uuid.uuid4()
    model = TestModel(
        id=test_id,
        name="test",
        created_at=now,
        updated_at=now
    )
    assert model.name == "test"
    assert isinstance(model.created_at, datetime)
    assert isinstance(model.updated_at, datetime)
    assert model.created_at == now
    assert model.updated_at == now
    assert isinstance(model.id, uuid.UUID)
    assert model.id == test_id

def test_model_to_dict():
    """Test model serialization to dictionary."""
    test_id = uuid.uuid4()
    now = datetime.utcnow()
    model = TestModel(
        id=test_id,
        name="test",
        created_at=now,
        updated_at=now,
        created_by="user1",
        updated_by="user1"
    )
    data = model.to_dict()
    assert data["id"] == test_id
    assert data["name"] == "test"
    assert data["created_at"] == now
    assert data["updated_at"] == now
    assert data["created_by"] == "user1"
    assert data["updated_by"] == "user1"

def test_model_update():
    """Test model update method."""
    now = datetime.utcnow()
    test_id = uuid.uuid4()
    model = TestModel(
        id=test_id,
        name="test",
        created_at=now,
        updated_at=now
    )
    original_created_at = model.created_at
    
    # Update with new values
    model.update(
        name="updated",
        created_by="user1",
        updated_by="user2"
    )
    
    assert model.name == "updated"
    assert model.id == test_id  # Should not change
    assert model.created_at == original_created_at  # Should not change
    assert model.created_by == "user1"
    assert model.updated_by == "user2"

def test_model_tablename():
    """Test automatic table name generation."""
    assert TestModel.__tablename__ == "test_models"

def test_model_default_values():
    """Test model default values."""
    model = TestModel(name="test")
    assert model.id is not None
    assert isinstance(model.id, uuid.UUID)
    assert model.created_at is not None
    assert isinstance(model.created_at, datetime)
    assert model.updated_at is not None
    assert isinstance(model.updated_at, datetime)
    assert model.created_by is None
    assert model.updated_by is None 