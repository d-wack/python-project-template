"""
Test cases for the main module.
"""
import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.config import Config

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def mock_env(monkeypatch):
    """Set up test environment variables."""
    env_vars = {
        "APP_NAME": "test_service",
        "ENVIRONMENT": "testing",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "json",
        "LOG_OUTPUT": "stdout"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

def test_root_endpoint(client, mock_env):
    """Test the root endpoint returns correct service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "test_service"
    assert data["environment"] == "testing"
    assert data["status"] == "operational"

def test_health_check_endpoint(client):
    """Test the health check endpoint returns correct status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Verify timestamp is in ISO format
    datetime.fromisoformat(data["timestamp"])

def test_config_endpoint_debug_mode(client, mock_env):
    """Test the config endpoint in debug mode."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "test_service"
    assert data["environment"] == "testing"
    assert data["debug"] is True

def test_config_endpoint_production_mode(client):
    """Test the config endpoint is disabled in production mode."""
    os.environ["DEBUG"] = "False"
    response = client.get("/config")
    assert response.status_code == 403
    data = response.json()
    assert "Configuration endpoint only available in debug mode" in data["detail"]

def test_metrics_endpoint(client):
    """Test the metrics endpoint is accessible."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

def test_cors_headers(client):
    """Test CORS headers are properly set."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers 