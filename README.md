# Logging Service

A Python-based logging service application.

## Project Structure
```
.
├── src/            # Application source code
├── tests/          # Test files
├── .github/        # GitHub Actions workflows
├── Dockerfile      # Docker configuration
├── requirements.txt # Python dependencies
└── README.md       # Project documentation
```

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

4. Run linting:
```bash
flake8 src tests
black src tests
```

## Docker

Build the image:
```bash
docker build -t logging-service .
```

Run the container:
```bash
docker run -d logging-service
```

## CI/CD

This project uses GitHub Actions for:
- Running tests
- Code linting
- Code coverage reporting
- Automated builds

## License

[MIT License](LICENSE) 