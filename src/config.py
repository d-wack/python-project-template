"""
Configuration management for the logging service.

This module handles loading and validating environment variables,
providing a centralized configuration for the application.
"""
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration settings."""
    APP_NAME: str
    ENVIRONMENT: str
    DEBUG: bool
    LOG_LEVEL: str

@dataclass
class ServerConfig:
    """Server configuration settings."""
    HOST: str
    PORT: int

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    LOG_FORMAT: str
    LOG_OUTPUT: str
    LOG_FILE_PATH: Optional[str]
    LOG_ROTATION_SIZE: str
    LOG_RETENTION_DAYS: int

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

@dataclass
class RedisConfig:
    """Redis configuration settings."""
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str]
    CORS_ORIGINS: List[str]

@dataclass
class RateLimitConfig:
    """Rate limiting configuration settings."""
    RATE_LIMIT_ENABLED: bool
    RATE_LIMIT_DEFAULT: str

@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    ENABLE_METRICS: bool
    METRICS_PORT: int

@dataclass
class DependencyConfig:
    """Service dependency configuration settings."""
    DEPENDENT_SERVICE_URL: str
    DEPENDENT_SERVICE_TIMEOUT: int

@dataclass
class FeatureConfig:
    """Feature flag configuration settings."""
    ENABLE_BATCH_PROCESSING: bool
    ENABLE_ASYNC_LOGGING: bool

@dataclass
class PerformanceConfig:
    """Performance tuning configuration settings."""
    WORKER_PROCESSES: int
    THREAD_POOL_SIZE: int
    MAX_QUEUE_SIZE: int

@dataclass
class BackupConfig:
    """Backup configuration settings."""
    BACKUP_ENABLED: bool
    BACKUP_RETENTION_DAYS: int
    BACKUP_S3_BUCKET: str

class Config:
    """Main configuration class that aggregates all config sections."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.app = AppConfig(
            APP_NAME=os.getenv("APP_NAME", "logging_service"),
            ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
            DEBUG=os.getenv("DEBUG", "True").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO")
        )

        self.server = ServerConfig(
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8000"))
        )

        self.logging = LoggingConfig(
            LOG_FORMAT=os.getenv("LOG_FORMAT", "json"),
            LOG_OUTPUT=os.getenv("LOG_OUTPUT", "stdout"),
            LOG_FILE_PATH=os.getenv("LOG_FILE_PATH"),
            LOG_ROTATION_SIZE=os.getenv("LOG_ROTATION_SIZE", "10MB"),
            LOG_RETENTION_DAYS=int(os.getenv("LOG_RETENTION_DAYS", "30"))
        )

        self.database = DatabaseConfig(
            DB_HOST=os.getenv("DB_HOST", "localhost"),
            DB_PORT=int(os.getenv("DB_PORT", "5432")),
            DB_NAME=os.getenv("DB_NAME", "logging_db"),
            DB_USER=os.getenv("DB_USER", "logger"),
            DB_PASSWORD=os.getenv("DB_PASSWORD", "")
        )

        self.redis = RedisConfig(
            REDIS_HOST=os.getenv("REDIS_HOST", "localhost"),
            REDIS_PORT=int(os.getenv("REDIS_PORT", "6379")),
            REDIS_DB=int(os.getenv("REDIS_DB", "0")),
            REDIS_PASSWORD=os.getenv("REDIS_PASSWORD", "")
        )

        self.security = SecurityConfig(
            SECRET_KEY=os.getenv("SECRET_KEY", ""),
            ALLOWED_HOSTS=os.getenv("ALLOWED_HOSTS", "localhost").split(","),
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        )

        self.rate_limit = RateLimitConfig(
            RATE_LIMIT_ENABLED=os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true",
            RATE_LIMIT_DEFAULT=os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
        )

        self.monitoring = MonitoringConfig(
            ENABLE_METRICS=os.getenv("ENABLE_METRICS", "True").lower() == "true",
            METRICS_PORT=int(os.getenv("METRICS_PORT", "9090"))
        )

        self.dependencies = DependencyConfig(
            DEPENDENT_SERVICE_URL=os.getenv("DEPENDENT_SERVICE_URL", "http://localhost:8001"),
            DEPENDENT_SERVICE_TIMEOUT=int(os.getenv("DEPENDENT_SERVICE_TIMEOUT", "30"))
        )

        self.features = FeatureConfig(
            ENABLE_BATCH_PROCESSING=os.getenv("ENABLE_BATCH_PROCESSING", "False").lower() == "true",
            ENABLE_ASYNC_LOGGING=os.getenv("ENABLE_ASYNC_LOGGING", "True").lower() == "true"
        )

        self.performance = PerformanceConfig(
            WORKER_PROCESSES=int(os.getenv("WORKER_PROCESSES", "4")),
            THREAD_POOL_SIZE=int(os.getenv("THREAD_POOL_SIZE", "10")),
            MAX_QUEUE_SIZE=int(os.getenv("MAX_QUEUE_SIZE", "1000"))
        )

        self.backup = BackupConfig(
            BACKUP_ENABLED=os.getenv("BACKUP_ENABLED", "True").lower() == "true",
            BACKUP_RETENTION_DAYS=int(os.getenv("BACKUP_RETENTION_DAYS", "7")),
            BACKUP_S3_BUCKET=os.getenv("BACKUP_S3_BUCKET", "logging-service-backups")
        )

    def validate(self) -> None:
        """Validate the configuration settings."""
        if self.app.ENVIRONMENT == "production":
            assert self.security.SECRET_KEY, "SECRET_KEY must be set in production"
            assert not self.app.DEBUG, "DEBUG should be False in production"
            assert "localhost" not in self.security.ALLOWED_HOSTS, "localhost should not be in ALLOWED_HOSTS in production"
            assert self.database.DB_PASSWORD, "Database password must be set in production"
            assert self.redis.REDIS_PASSWORD, "Redis password must be set in production"

        assert self.logging.LOG_FORMAT in ["json", "text"], "Invalid LOG_FORMAT"
        assert self.logging.LOG_OUTPUT in ["stdout", "file"], "Invalid LOG_OUTPUT"
        if self.logging.LOG_OUTPUT == "file":
            assert self.logging.LOG_FILE_PATH, "LOG_FILE_PATH must be set when LOG_OUTPUT is file"

# Create a global config instance
config = Config()

# Validate configuration on import
config.validate() 