# Week 4 Project: Zen HR Support Agent

AI-powered customer support assistant using PydanticAI with hybrid RAG search.

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

# Ingest support documentation
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
├── docs/              # Zen HR support documentation
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
# Chat with the support agent
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What plans do you offer?"}'

# Health check
curl http://localhost:8000/health

# Database stats
curl http://localhost:8000/stats
```

## Sample Questions

- "What plans do you offer?"
- "How do I integrate with Gusto?"
- "What does error E401 mean?"
- "Do you have an API?"
- "How do I contact support?"
