# Document Search CLI

Search your documents using vector similarity and hybrid search.

## Prerequisites

Postgres with pgvector:
```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database
psql postgresql://postgres:postgres@localhost -c "CREATE DATABASE ragdb"
```

## Setup

```bash
uv sync
```

Create `.env`:
```
GOOGLE_API_KEY=your_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost/ragdb
```

## Usage

Ingest documents:
```bash
uv run python ingest.py ./docs
```

Search:
```bash
# Vector search (default)
uv run python search.py "What is the refund policy?"

# Hybrid search (vector + full-text)
uv run python search.py --hybrid "password reset"

# Full-text only
uv run python search.py --fulltext "API key"
```

## Files

- `db.py` - Database connection and schema
- `ingest.py` - Document parsing and ingestion
- `search.py` - Search CLI with vector/hybrid modes
