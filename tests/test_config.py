"""
Test cases for the configuration module.
"""
import os
import pytest
from src.config import Config, config

@pytest.fixture(autouse=True)
def reset_config():
    """Reset config after each test."""
    # Store original environment
    original_env = {}
    for key in os.environ:
        original_env[key] = os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
    
    # Recreate config instance
    config.__init__()

@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to set up test environment variables."""
    env_vars = {
        "APP_NAME": "test_service",
        "ENVIRONMENT": "testing",
        "DEBUG": "False",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "json",
        "LOG_OUTPUT": "stdout",
        "SECRET_KEY": "test_secret_key",
        "ALLOWED_HOSTS": "test.com,api.test.com",
        "DB_PASSWORD": "test_password",
        "REDIS_PASSWORD": "test_redis_password"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    # Recreate config instance with new environment
    config.__init__()
    return env_vars

def test_config_loads_environment_variables(mock_env):
    """Test that configuration properly loads environment variables."""
    assert config.app.APP_NAME == "test_service"
    assert config.app.ENVIRONMENT == "testing"
    assert not config.app.DEBUG
    assert config.app.LOG_LEVEL == "DEBUG"

def test_config_uses_defaults_for_missing_variables():
    """Test that configuration uses default values for missing environment variables."""
    config.__init__()
    assert config.app.APP_NAME == "logging_service"
    assert config.app.ENVIRONMENT == "development"
    assert config.app.DEBUG
    assert config.server.PORT == 8000

def test_config_validation_production():
    """Test configuration validation in production environment."""
    os.environ.update({
        "ENVIRONMENT": "production",
        "DEBUG": "True",
        "SECRET_KEY": "",
        "DB_PASSWORD": "",
        "REDIS_PASSWORD": ""
    })
    with pytest.raises(AssertionError, match="DEBUG should be False in production"):
        config.__init__()

def test_logging_configuration_validation():
    """Test logging configuration validation."""
    os.environ["LOG_FORMAT"] = "invalid"
    with pytest.raises(AssertionError, match="Invalid LOG_FORMAT"):
        config.__init__()

def test_security_configuration():
    """Test security configuration parsing."""
    os.environ.update({
        "ALLOWED_HOSTS": "test1.com,test2.com",
        "CORS_ORIGINS": "http://test1.com,http://test2.com"
    })
    config.__init__()
    assert config.security.ALLOWED_HOSTS == ["test1.com", "test2.com"]
    assert config.security.CORS_ORIGINS == ["http://test1.com", "http://test2.com"]

def test_feature_flags():
    """Test feature flag configuration."""
    os.environ.update({
        "ENABLE_BATCH_PROCESSING": "true",
        "ENABLE_ASYNC_LOGGING": "false"
    })
    config.__init__()
    assert config.features.ENABLE_BATCH_PROCESSING
    assert not config.features.ENABLE_ASYNC_LOGGING

def test_performance_settings():
    """Test performance configuration parsing."""
    os.environ.update({
        "WORKER_PROCESSES": "8",
        "THREAD_POOL_SIZE": "20",
        "MAX_QUEUE_SIZE": "2000"
    })
    config.__init__()
    assert config.performance.WORKER_PROCESSES == 8
    assert config.performance.THREAD_POOL_SIZE == 20
    assert config.performance.MAX_QUEUE_SIZE == 2000

def test_backup_configuration():
    """Test backup configuration validation."""
    os.environ.update({
        "BACKUP_ENABLED": "true",
        "BACKUP_RETENTION_DAYS": "14",
        "BACKUP_S3_BUCKET": "test-bucket"
    })
    config.__init__()
    assert config.backup.BACKUP_ENABLED
    assert config.backup.BACKUP_RETENTION_DAYS == 14
    assert config.backup.BACKUP_S3_BUCKET == "test-bucket"

def test_invalid_port_numbers():
    """Test validation of invalid port numbers."""
    # Save current environment
    original_port = os.environ.get("PORT")
    original_db_port = os.environ.get("DB_PORT")
    original_redis_port = os.environ.get("REDIS_PORT")
    
    try:
        os.environ.update({
            "PORT": "-1",
            "DB_PORT": "999999",
            "REDIS_PORT": "abc"
        })
        with pytest.raises(ValueError, match="invalid literal for int()"):
            config.__init__()
    finally:
        # Restore environment
        if original_port:
            os.environ["PORT"] = original_port
        if original_db_port:
            os.environ["DB_PORT"] = original_db_port
        if original_redis_port:
            os.environ["REDIS_PORT"] = original_redis_port

def test_production_localhost_validation():
    """Test validation of localhost in production ALLOWED_HOSTS."""
    # Save current environment
    original_env = {
        "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
        "DEBUG": os.environ.get("DEBUG"),
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD"),
        "REDIS_PASSWORD": os.environ.get("REDIS_PASSWORD"),
        "ALLOWED_HOSTS": os.environ.get("ALLOWED_HOSTS")
    }
    
    try:
        os.environ.update({
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "SECRET_KEY": "test_key",
            "DB_PASSWORD": "test_pass",
            "REDIS_PASSWORD": "test_pass",
            "ALLOWED_HOSTS": "prod.example.com,localhost"
        })
        with pytest.raises(AssertionError, match="localhost should not be in ALLOWED_HOSTS in production"):
            config.__init__()
    finally:
        # Restore environment
        for key, value in original_env.items():
            if value:
                os.environ[key] = value

def test_log_file_validation():
    """Test validation of log file configuration."""
    # Save current environment
    original_output = os.environ.get("LOG_OUTPUT")
    original_path = os.environ.get("LOG_FILE_PATH")
    
    try:
        os.environ.update({
            "LOG_OUTPUT": "file",
            "LOG_FILE_PATH": ""
        })
        with pytest.raises(AssertionError, match="LOG_FILE_PATH must be set when LOG_OUTPUT is file"):
            config.__init__()
    finally:
        # Restore environment
        if original_output:
            os.environ["LOG_OUTPUT"] = original_output
        if original_path:
            os.environ["LOG_FILE_PATH"] = original_path

def test_rate_limit_configuration():
    """Test rate limit configuration parsing."""
    os.environ.update({
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_DEFAULT": "200/minute"
    })
    config.__init__()
    assert config.rate_limit.RATE_LIMIT_ENABLED
    assert config.rate_limit.RATE_LIMIT_DEFAULT == "200/minute"

def test_monitoring_configuration():
    """Test monitoring configuration parsing."""
    os.environ.update({
        "ENABLE_METRICS": "true",
        "METRICS_PORT": "9091"
    })
    config.__init__()
    assert config.monitoring.ENABLE_METRICS
    assert config.monitoring.METRICS_PORT == 9091

def test_dependency_configuration():
    """Test dependency service configuration."""
    os.environ.update({
        "DEPENDENT_SERVICE_URL": "http://api.example.com",
        "DEPENDENT_SERVICE_TIMEOUT": "60"
    })
    config.__init__()
    assert config.dependencies.DEPENDENT_SERVICE_URL == "http://api.example.com"
    assert config.dependencies.DEPENDENT_SERVICE_TIMEOUT == 60 