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
cd docker
docker compose up -d

# Install dependencies
cd ..
uv sync

# Ingest sample documents
uv run python ingest.py ./docs

# Search!
uv run python search.py "What is the vacation policy?"
uv run python search.py --hybrid "error code XYZ-123"
```

## Project Structure

```
week-3-doc-search/
├── docker/
│   ├── docker-compose.yml
│   └── init.sql
├── db.py          # Database connection
├── ingest.py      # Document parsing, chunking, and storage
├── search.py      # Vector, keyword, and hybrid search
└── pyproject.toml
```

## Configuration

Set environment variables in `.env`:

```
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/week3_doc_search
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
