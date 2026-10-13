# Structured Output Agent

[![Python Tests](https://github.com/adiitya99/structured-output-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/adiitya99/structured-output-agent/actions/workflows/tests.yml)

[![Python Tests](https://github.com/adiitya99/structured-output-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/adiitya99/structured-output-agent/actions/workflows/tests.yml)

A Python-based agent that generates validated, structured task outputs using Pydantic, with a FastAPI interface and automated testing.

## Features

- Strict output validation using Pydantic
- Retry handling for invalid generated responses
- Mock provider for local development
- FastAPI endpoints for health checks and task processing
- API-key authentication
- Request IDs for request tracing
- Rate limiting with SlowAPI
- Automated tests using pytest
- GitHub Actions CI workflow

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic
- SlowAPI
- pytest
- GitHub Actions

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```text
AGENT_API_KEY=replace-with-a-local-development-key
```

Use your own local development key. Never commit `.env` or publish API keys.

## Run the API

```powershell
uvicorn structured_agent.api:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.

## API Endpoints

### Health check

`GET /health`

### Create a task

`POST /tasks`

This endpoint requires an `X-API-Key` header.

Example JSON body:

```json
{
  "prompt": "Help me study computer networks"
}
```

## Run Tests

```powershell
python -m pytest -v
```

## Continuous Integration

GitHub Actions runs the test suite on pushes and pull requests.

## Current Limitations

- The API uses a mock provider by default.
- The default in-memory rate limiter is intended for local development and single-process deployments.
- Production deployment requires appropriate secret management, shared rate-limit storage, monitoring, and deployment configuration.

## License

No license has been specified yet.



