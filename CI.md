# Continuous Integration

This project uses GitHub Actions for continuous integration. The CI workflow automatically runs linting and testing whenever code is pushed to the repository.

## Workflow Overview

The GitHub Actions workflow (`ci.yml`) runs on:
- Pushes to the `main` branch
- Pull requests targeting the `main` branch

## Jobs

The workflow consists of two main jobs:

### Lint

The linting job checks code quality using several tools:

- **flake8**: Checks for syntax errors and undefined names
- **black**: Verifies consistent code formatting
- **isort**: Ensures imports are properly sorted

### Test

The testing job runs all tests, including unit and integration tests:

- Starts required services (Redis and MinIO) using docker-compose
- Initializes required MinIO buckets with the init_minio service
- Runs unit tests with code coverage reporting
- Runs integration tests with the appropriate environment variables
- Uploads code coverage reports to Codecov
- Cleans up Docker resources after completion

## CI Badge

The CI status is shown in the project README:

[![CI Status](https://github.com/username/neuralk-technical-assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/username/neuralk-technical-assessment/actions/workflows/ci.yml)

*Note: Make sure to replace "username" with your actual GitHub username in the README.*

## Local Development

To run the same checks locally before committing:

```bash
# Install development dependencies
pip install flake8 black isort pytest pytest-cov

# Run linting checks
flake8 .
black --check .
isort --check .

# Start required services
docker-compose up -d redis minio init_minio

# Run tests
pytest tests/ --cov=src
pytest tests/integration/ -v

# Clean up
docker-compose down -v
```

## Environment Setup

The CI uses docker-compose to spin up the following services:

- Redis for task queuing
- MinIO for object storage

These services match your development environment exactly since the same docker-compose.yml file is used in both CI and local development.
