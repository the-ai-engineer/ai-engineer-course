# Week 4 Project: HR Policy Agent

AI-powered HR policy assistant using PydanticAI with hybrid RAG search.

## What You'll Learn

- PydanticAI agent with tools
- Vector + keyword hybrid search (RRF)
- FastAPI REST API with chat UI
- Document ingestion pipeline

## Quick Start

```bash
# Start Postgres with pgvector
cd docker
docker compose up -d

# Install dependencies
cd ..
uv sync

# Ingest sample documents
uv run python ingest.py ./docs

# Start the server
uv run uvicorn app.main:app --reload

# Open http://localhost:8000 for chat UI
```

## Project Structure

```
week-4-hr-agent/
├── docker/
│   ├── docker-compose.yml
│   └── init.sql
├── app/
│   ├── main.py        # FastAPI app
│   ├── config.py      # Settings
│   ├── agent.py       # PydanticAI agent + search tool
│   ├── search.py      # Vector, keyword, hybrid search
│   ├── database.py    # Connection management
│   ├── models.py      # Pydantic schemas
│   └── routes.py      # API endpoints
├── templates/
│   └── chat.html      # Chat UI
├── docs/              # Sample HR documents
├── ingest.py          # Document ingestion
└── pyproject.toml
```

## Configuration

Set environment variables in `.env`:

```
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/week4_hr_agent
```

## API Endpoints

```bash
# Chat with the HR agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many vacation days do I get?"}'

# Health check
curl http://localhost:8000/health

# Database stats
curl http://localhost:8000/stats
```

## Sample Questions

- "How many vacation days do I get?"
- "What is the company 401k match?"
- "Can I work from home?"
- "How do I submit expense reports?"
- "What is the parental leave policy?"
