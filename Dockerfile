# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=development \
    DEBUG=True \
    LOG_LEVEL=INFO \
    LOG_FORMAT=json \
    LOG_OUTPUT=stdout \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/logging_service && \
    chmod 777 /var/log/logging_service

# Run tests during build to ensure everything is working
# RUN pytest tests/

# Expose ports for the application, metrics, and debugger
EXPOSE 8000 9090 5678

# Create a non-root user and switch to it
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/log/logging_service
USER appuser

# Start the application with uvicorn and enable debugger
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 