# Internet Research Agent

A locally runnable research API. It searches DuckDuckGo, fetches and extracts
source pages, asks a local Ollama model to draft a cited report, and stores
completed reports in SQLite.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) with the configured model pulled locally

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Runtime settings are loaded from environment variables; when present, the
project-root `.env` file is loaded without overriding variables already set in
the process environment. Adjust `.env` to configure the server, model, database,
timeouts, response limits, and `PROMPT_FILE`. The YAML file at
`src/research_agent/agent/prompts.yaml` contains the report prompt template.

## Run

```bash
python scripts/run_local.py
```

The API is available at `http://127.0.0.1:8000`.

### Research endpoint

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -d '{"query":"How do heat pumps work?","depth":"standard"}'
```

The request accepts `query` (5–500 characters) and optional `depth` (`quick`,
`standard`, or `deep`). The response contains the report, findings, source
citations, and a basic evidence coverage score. Research requests require
internet access and a running Ollama server. Completed reports are stored at
`DATABASE_PATH` (default `data/research_agent.sqlite3`).

Check whether Ollama is reachable with:

```bash
python scripts/check_ollama.py
```

## Test

```bash
pytest
```
