"""
Main application module for the logging service.
"""
import logging
import logging.config
from datetime import datetime
from typing import Dict, Any

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.config import config

# Configure logging
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if config.logging.LOG_FORMAT == "json" else "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": config.app.LOG_LEVEL,
    },
})

logger = structlog.get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=config.app.APP_NAME,
    description="A Python-based logging service",
    version="0.1.0",
    debug=config.app.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint returning service information."""
    logger.info("Root endpoint accessed")
    return {
        "service": config.app.APP_NAME,
        "environment": config.app.ENVIRONMENT,
        "status": "operational"
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": config.app.ENVIRONMENT,
        "version": "0.1.0"
    }

@app.get("/config")
async def get_config() -> Dict[str, Any]:
    """Return non-sensitive configuration information."""
    if not config.app.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="Configuration endpoint only available in debug mode"
        )
    
    logger.info("Configuration endpoint accessed")
    return {
        "app_name": config.app.APP_NAME,
        "environment": config.app.ENVIRONMENT,
        "debug": config.app.DEBUG,
        "log_level": config.app.LOG_LEVEL,
        "metrics_enabled": config.monitoring.ENABLE_METRICS,
        "features": {
            "batch_processing": config.features.ENABLE_BATCH_PROCESSING,
            "async_logging": config.features.ENABLE_ASYNC_LOGGING
        }
    }

@app.on_event("startup")
async def startup_event() -> None:
    """Handle application startup events."""
    logger.info(
        "Application starting",
        app_name=config.app.APP_NAME,
        environment=config.app.ENVIRONMENT
    )

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Handle application shutdown events."""
    logger.info(
        "Application shutting down",
        app_name=config.app.APP_NAME,
        environment=config.app.ENVIRONMENT
    ) 