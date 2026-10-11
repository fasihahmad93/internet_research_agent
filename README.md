# Internet Research Agent

A Python scaffold for a locally runnable internet research agent. The initial
entry point exposes a health endpoint; the agent, research, tool, storage, and
observability modules are organized for incremental implementation.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) for local language-model inference when the LLM
  integration is implemented

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

## Run

```bash
python scripts/run_local.py
```

The API is available at `http://127.0.0.1:8000`; its initial health check is
`GET /health`.

## Test

```bash
pytest
```
