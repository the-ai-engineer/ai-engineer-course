# HR Policy Agent

AI-powered HR policy assistant using PydanticAI with production RAG.

## Overview

This project demonstrates building a production-ready AI agent that helps employees find information about company policies. It combines:

- **PydanticAI** for agent abstraction
- **Postgres + pgvector** for vector and hybrid search
- **FastAPI** for REST API
- **Docling** for document parsing

## Features

- PydanticAI agent with RAG tool
- Vector search (semantic similarity)
- Full-text search (keyword matching)
- Hybrid search (vector + full-text with RRF)
- FastAPI REST API
- CLI interface
- JSONB metadata filtering

## Project Structure

```
week-4-hr-agent/
├── app/
│   ├── __init__.py
│   ├── config.py       # Settings with pydantic-settings
│   ├── database.py     # Connection, schema, indexes
│   ├── models.py       # Pydantic models
│   ├── embeddings.py   # Gemini embeddings
│   ├── search.py       # Vector, fulltext, hybrid search
│   ├── ingest.py       # Document ingestion
│   ├── agent.py        # PydanticAI HR agent
│   ├── rag.py          # RAG with Jinja2 prompts
│   ├── main.py         # FastAPI application
│   └── prompts/
│       └── rag.j2      # RAG prompt template
├── docs/               # Sample HR policy documents
│   ├── employee_handbook.md
│   ├── benefits_guide.md
│   ├── vacation_policy.md
│   ├── expense_policy.md
│   └── remote_work_policy.md
├── cli.py              # Command-line interface
├── pyproject.toml
└── .env-sample
```

## Setup

1. Start Postgres with pgvector:

```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database
psql postgresql://postgres:postgres@localhost -c "CREATE DATABASE ragdb"
```

2. Install dependencies:

```bash
cd projects/week-4-hr-agent
uv sync
```

3. Configure environment:

```bash
cp .env-sample .env
# Edit .env with your GEMINI_API_KEY
```

## Quick Start

```bash
# Initialize database
uv run python cli.py init

# Ingest the sample HR documents
uv run python cli.py ingest ./docs

# Ask questions
uv run python cli.py ask "How many vacation days do I get?"
uv run python cli.py ask "What is the 401k match?"
uv run python cli.py ask "Can I work from home?"
```

## CLI Usage

```bash
# Initialize database
uv run python cli.py init

# Ingest documents
uv run python cli.py ingest ./docs
uv run python cli.py ingest -f document.pdf

# Search
uv run python cli.py search "vacation policy"
uv run python cli.py search "benefits" -t hybrid
uv run python cli.py search "remote work" -t fulltext

# Ask questions (uses PydanticAI agent)
uv run python cli.py ask "How many vacation days do I get?"

# Stats
uv run python cli.py stats
```

## API Usage

Start the server:

```bash
uv run uvicorn app.main:app --reload
```

Endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Search documents
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "vacation policy", "search_type": "hybrid"}'

# Ask the HR agent
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'

# Ingest a document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source": "./docs/handbook.pdf", "title": "Employee Handbook"}'

# Get stats
curl http://localhost:8000/stats
```

API docs available at: http://localhost:8000/docs

## How It Works

The HR Policy Agent uses PydanticAI to create an agent with a search tool:

```python
from pydantic_ai import Agent, RunContext

hr_agent = Agent(
    "google-gla:gemini-3-flash-preview",
    system_prompt="You are an HR assistant...",
    deps_type=AgentDeps,
)

@hr_agent.tool
def search_policies(ctx: RunContext[AgentDeps], query: str) -> str:
    """Search HR policy documents."""
    with get_connection() as conn:
        results = search(conn, query, limit=ctx.deps.search_limit)
    return format_results(results)
```

When you ask a question:

1. The agent receives the question
2. It decides to call the `search_policies` tool
3. The tool performs hybrid search against the document database
4. Search results are returned to the agent
5. The agent generates a response based on the policies found

## Configuration

Environment variables (see `.env-sample`):

- `DATABASE_URL` - Postgres connection string
- `GEMINI_API_KEY` - Gemini API key
- `EMBEDDING_MODEL` - Model for embeddings (default: gemini-embedding-001)
- `GENERATION_MODEL` - Model for agent (default: gemini-3-flash-preview)

## Sample Questions

Try asking the HR agent:

- "How many vacation days do I get?"
- "What is the company 401k match?"
- "Can I work from home?"
- "How do I submit expense reports?"
- "What is the parental leave policy?"
- "What are the core work hours for remote employees?"
