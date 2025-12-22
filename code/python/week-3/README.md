# Week 3: RAG Fundamentals

Code examples for Module 3 of the AI Architect Program.

## Four RAG Strategies

| Strategy | File | Use Case |
|----------|------|----------|
| 1. File Loading | `01_file_loading.py` | Small docs, <50k tokens |
| 2. Managed RAG | `02_file_search.py` | Quick prototypes, zero infrastructure |
| 3. Vector Search | `03_vector_search.py` | Larger collections, semantic search |
| 4. Hybrid Search | `04_hybrid_search.py` | Exact terms + semantic, production systems |

## Prerequisites

For Strategies 3-4, you need Postgres with pgvector:

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
cd code/python/week-3
uv sync
```

Copy the sample env file and configure:

```bash
cp .env-sample .env
```

Get your API key at: https://aistudio.google.com/apikey

For Vertex AI (Google Cloud), see `.env-sample` for ADC configuration.

## Running Examples

```bash
# Strategy 1: File Loading
uv run python 01_file_loading.py

# Strategy 2: Managed RAG
uv run python 02_file_search.py

# Strategy 3: Vector Search (requires Postgres)
uv run python 03_vector_search.py

# Strategy 4: Hybrid Search (requires Postgres)
uv run python 04_hybrid_search.py
```

## Project

The week 3 project (Document Search CLI) is in `projects/week-3-doc-search/`.
