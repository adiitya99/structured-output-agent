# Structured Output Agent

A Python project that validates structured AI outputs using Pydantic, validates tool inputs and results, retries invalid responses, and logs validation failures.

## Features

- Structured output validation with Pydantic
- Strict schema validation using `extra="forbid"`
- Retry logic with validation feedback
- Tool argument and result validation
- Logging to console and a rotating log file
- Automated tests using pytest
- Mock mode for local testing without paid API calls
- Optional OpenAI API integration

## Tech Stack

- Python 3.10+
- Pydantic
- OpenAI Python SDK
- python-dotenv
- pytest

## Project Structure

```text
structured-output-agent/
├── structured_agent/
│   ├── __init__.py
│   ├── schemas.py
│   ├── agent.py
│   ├── tools.py
│   └── logging_config.py
├── tests/
│   └── test_agent.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run in Mock Mode

Mock mode uses predefined responses and does not make API calls:

```powershell
python main.py --mode mock --prompt "Help me study computer networks"
```

## Run Tests

```powershell
python -m pytest -v
```

## Optional OpenAI API Mode

Set your API key in a local `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Keep `.env` private and never commit your API key to GitHub.

Run API mode only if you have API access and available credits:

```powershell
python main.py --mode api --prompt "Help me study computer networks"
```

## Current Status

The project includes schema validation, retry logic, tool validation, logging, mock mode, and automated tests.

Mock mode and automated tests can be used without paid API calls.