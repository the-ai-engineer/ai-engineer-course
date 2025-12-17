# Week 3: RAG Fundamentals

Code examples for Module 3 of the AI Architect Program.

## Prerequisites

Postgres with pgvector:
```bash
# Docker (recommended)
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Create database
psql postgresql://postgres:postgres@localhost -c "CREATE DATABASE ragdb"
```

## Setup

```bash
cd code/week-3
uv sync
```

Create a `.env` file:
```
GOOGLE_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/ragdb
```

## Running Examples

```bash
uv run python 02_embeddings.py
```

## Code Index

| File | Lesson | Description |
|------|--------|-------------|
| `02_embeddings.py` | Embeddings | Generate and compare embeddings |
| `03_docling.py` | Document Processing | Parse documents, chunking strategies |
| `04_pgvector.py` | Vector Storage | Schema, indexes, storing vectors |
| `05_vector_search.py` | Vector Search | Similarity search, filtering, reranking |
| `06_hybrid_search.py` | Hybrid Search | Vector + full-text with RRF |

## Project

The week 3 project (Document Search CLI) is in `projects/week-3-doc-search/`.
