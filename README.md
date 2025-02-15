# Python FastAPI Project Template

A production-ready Python FastAPI template with PostgreSQL, Redis, monitoring, and development tools pre-configured.

## Features

### Core Technologies
- FastAPI for high-performance API development
- PostgreSQL with SQLAlchemy ORM
- Redis for caching and rate limiting
- Docker and Docker Compose for containerization

### Development Tools
- VS Code configuration with debugging support
- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- Pytest for testing
- Coverage reporting
- IPython for interactive development

### Monitoring & Observability
- Prometheus metrics
- Grafana dashboards
- Structured JSON logging
- OpenTelemetry tracing
- Health check endpoints

### Database Features
- Automatic migrations with Alembic
- Connection pooling
- Audit logging
- Schema separation
- UUID support
- Full-text search
- Type hints

### Security
- Environment-based configuration
- CORS configuration
- Rate limiting
- Secure headers
- Authentication ready

### Development Experience
- Hot reload
- Docker development environment
- VS Code debugging
- Comprehensive testing setup
- Database GUI tools

## Project Structure
```
.
├── src/                    # Application source code
│   ├── models/            # SQLAlchemy models
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── scripts/               # Utility scripts
├── init-scripts/          # Database initialization
├── prometheus/            # Prometheus configuration
├── .github/               # GitHub Actions workflows
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Quick Start

1. Create a new repository from this template:
   ```bash
   git clone https://github.com/yourusername/python-fastapi-template.git my-project
   cd my-project
   ```

2. Set up development environment:
   ```bash
   ./scripts/dev-setup.sh
   ```

3. Start the development environment:
   ```bash
   docker-compose up --build
   ```

4. Access the services:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics
   - PgAdmin: http://localhost:5050
   - Redis Commander: http://localhost:8081
   - Prometheus: http://localhost:9091
   - Grafana: http://localhost:3000

## Development

### VS Code Configuration
- Debugging configurations included
- Extensions recommendations
- Task configurations
- Settings for formatting and linting

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test
pytest tests/test_specific.py

# Run tests with detailed coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Test Coverage
The project maintains high test coverage to ensure code quality and reliability. Current coverage metrics:

- Overall coverage: 93%
- Key areas covered:
  - Database operations and session management
  - Model functionality and base class features
  - Configuration management
  - API endpoints and middleware
  - Logging and monitoring

Coverage reports can be generated in multiple formats:
```bash
# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml
```

The CI/CD pipeline automatically runs tests and uploads coverage reports to Codecov for tracking coverage trends over time.

Coverage requirements:
- Minimum overall coverage: 90%
- Critical paths (database, API, auth): 95%
- New code changes must maintain or improve coverage

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head
```

### Code Quality
```bash
# Format code
black src tests

# Run linting
flake8 src tests

# Run type checking
mypy src
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and adjust the values:
```bash
cp .env.example .env
```

Key configurations:
- `ENVIRONMENT`: development/staging/production
- `DEBUG`: Enable/disable debug mode
- `LOG_LEVEL`: Logging level
- `DB_*`: Database configurations
- `REDIS_*`: Redis configurations

### Docker Configuration
- Development setup in `docker-compose.yml`
- Production configuration in `Dockerfile`
- Volume management for persistence
- Health checks configured

## Monitoring

### Metrics
- Application metrics at `/metrics`
- Custom metrics support
- Prometheus configuration
- Grafana dashboards

### Logging
- Structured JSON logging
- Log rotation
- Environment-based configuration
- Correlation IDs

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This template is MIT licensed. 