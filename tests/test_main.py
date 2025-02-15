"""
Test cases for the main module.
"""
import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app, startup_event, shutdown_event
from src.config import Config, config

@pytest.fixture(autouse=True)
def reset_config():
    """Reset config after each test."""
    yield
    # Reset environment variables to default values
    os.environ.update({
        "APP_NAME": "logging_service",
        "ENVIRONMENT": "development",
        "DEBUG": "True",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "LOG_OUTPUT": "stdout"
    })

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
    
    # Recreate config instance with new environment variables
    config.__init__()
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
    os.environ.update({
        "ENVIRONMENT": "production",
        "DEBUG": "False",
        "SECRET_KEY": "test_production_key",
        "DB_PASSWORD": "test_db_password",
        "REDIS_PASSWORD": "test_redis_password",
        "ALLOWED_HOSTS": "prod1.example.com,prod2.example.com"
    })
    # Recreate config instance with new environment
    config.__init__()
    
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
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

@pytest.mark.asyncio
async def test_startup_event():
    """Test the startup event handler."""
    # Call the startup event handler
    await startup_event()
    # No assertion needed as we're just ensuring it runs without errors

@pytest.mark.asyncio
async def test_shutdown_event():
    """Test the shutdown event handler."""
    # Call the shutdown event handler
    await shutdown_event()
    # No assertion needed as we're just ensuring it runs without errors

def test_cors_headers_preflight(client):
    """Test CORS preflight request headers."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization",
    }
    response = client.options("/", headers=headers)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]
    assert "Authorization" in response.headers["access-control-allow-headers"]

def test_metrics_endpoint_content(client):
    """Test the metrics endpoint returns proper Prometheus metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    # Check for common Prometheus metric types
    assert "# HELP" in content
    assert "# TYPE" in content
    assert "process_" in content  # Common process metrics
    assert "python_" in content   # Python runtime metrics 