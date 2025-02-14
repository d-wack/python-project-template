"""
Test cases for the configuration module.
"""
import os
import pytest
from src.config import Config

@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to set up test environment variables."""
    env_vars = {
        "APP_NAME": "test_service",
        "ENVIRONMENT": "testing",
        "DEBUG": "False",
        "LOG_LEVEL": "DEBUG",
        "HOST": "127.0.0.1",
        "PORT": "9000",
        "LOG_FORMAT": "json",
        "LOG_OUTPUT": "stdout",
        "SECRET_KEY": "test_secret_key",
        "ALLOWED_HOSTS": "test.com,api.test.com",
        "DB_PASSWORD": "test_password",
        "REDIS_PASSWORD": "test_redis_password"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

def test_config_loads_environment_variables(mock_env):
    """Test that configuration properly loads environment variables."""
    config = Config()
    
    assert config.app.APP_NAME == "test_service"
    assert config.app.ENVIRONMENT == "testing"
    assert not config.app.DEBUG
    assert config.app.LOG_LEVEL == "DEBUG"
    assert config.server.HOST == "127.0.0.1"
    assert config.server.PORT == 9000

def test_config_uses_defaults_for_missing_variables():
    """Test that configuration uses default values for missing environment variables."""
    config = Config()
    
    assert config.app.APP_NAME == "logging_service"
    assert config.app.ENVIRONMENT == "development"
    assert config.app.DEBUG
    assert config.server.PORT == 8000

def test_config_validation_production():
    """Test configuration validation in production environment."""
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "True"
    
    with pytest.raises(AssertionError, match="DEBUG should be False in production"):
        Config()
    
    os.environ["DEBUG"] = "False"
    os.environ["ALLOWED_HOSTS"] = "localhost"
    
    with pytest.raises(AssertionError, match="localhost should not be in ALLOWED_HOSTS in production"):
        Config()

def test_logging_configuration_validation():
    """Test logging configuration validation."""
    os.environ["LOG_FORMAT"] = "invalid"
    
    with pytest.raises(AssertionError, match="Invalid LOG_FORMAT"):
        Config()
    
    os.environ["LOG_FORMAT"] = "json"
    os.environ["LOG_OUTPUT"] = "file"
    
    with pytest.raises(AssertionError, match="LOG_FILE_PATH must be set when LOG_OUTPUT is file"):
        Config()

def test_security_configuration():
    """Test security configuration parsing."""
    os.environ["ALLOWED_HOSTS"] = "test1.com,test2.com"
    os.environ["CORS_ORIGINS"] = "http://test1.com,http://test2.com"
    
    config = Config()
    
    assert config.security.ALLOWED_HOSTS == ["test1.com", "test2.com"]
    assert config.security.CORS_ORIGINS == ["http://test1.com", "http://test2.com"]

def test_feature_flags():
    """Test feature flag configuration."""
    os.environ["ENABLE_BATCH_PROCESSING"] = "true"
    os.environ["ENABLE_ASYNC_LOGGING"] = "false"
    
    config = Config()
    
    assert config.features.ENABLE_BATCH_PROCESSING
    assert not config.features.ENABLE_ASYNC_LOGGING

def test_performance_settings():
    """Test performance configuration parsing."""
    os.environ["WORKER_PROCESSES"] = "8"
    os.environ["THREAD_POOL_SIZE"] = "20"
    os.environ["MAX_QUEUE_SIZE"] = "2000"
    
    config = Config()
    
    assert config.performance.WORKER_PROCESSES == 8
    assert config.performance.THREAD_POOL_SIZE == 20
    assert config.performance.MAX_QUEUE_SIZE == 2000 