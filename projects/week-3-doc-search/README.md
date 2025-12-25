# Week 3 Project: Document Search CLI

A command-line document search tool demonstrating RAG concepts with PostgreSQL and pgvector.

## What You'll Learn

- Document parsing with Docling
- Token-based chunking for consistent embedding sizes
- Vector search with pgvector
- Hybrid search combining vectors + keywords (RRF)

## Quick Start

```bash
# Start Postgres with pgvector
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database
docker exec pgvector psql -U postgres -c "CREATE DATABASE ragdb"

# Install dependencies
uv sync

# Initialize schema
uv run python db.py

# Ingest sample documents
uv run python ingest.py ./docs

# Search!
uv run python search.py "What is the vacation policy?"
uv run python search.py --hybrid "error code XYZ-123"
```

## Project Structure

```
week-3-doc-search/
├── db.py          # Database connection and schema setup
├── ingest.py      # Document parsing, chunking, and storage
├── search.py      # Vector, keyword, and hybrid search
├── docs/          # Sample documents (copy from week-4-hr-agent)
└── pyproject.toml
```

## Configuration

Set environment variables in `.env`:

```
GEMINI_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/ragdb
```

## Usage Examples

```bash
# Vector search (semantic similarity)
uv run python search.py "How do I request time off?"

# Hybrid search (semantic + keywords)
uv run python search.py --hybrid "401k match percentage"

# Specify number of results
uv run python search.py --limit 10 "remote work policy"
```

## Next Steps

After completing this project, move to Week 4 where you'll build a production-ready RAG system with:
- FastAPI web interface
- PydanticAI agent with tools
- Chat UI
- Structured responses
