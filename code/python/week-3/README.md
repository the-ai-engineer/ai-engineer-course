# Week 3: RAG Fundamentals

Code examples for building retrieval-augmented generation systems.

## Code Samples

| File | Topic | Description |
|------|-------|-------------|
| `01_file_loading.py` | File Loading | Simple RAG loading faqs.md into prompt |
| `faqs.md` | Sample Data | Fictional store FAQ for file loading demo |
| `02_embeddings.py` | Embeddings | Understanding and using text embeddings |
| `03_connection.py` | PostgreSQL | Connecting to Postgres with pgvector |
| `04_vector_search.py` | Vector Search | Semantic search with embeddings |
| `05_hybrid_search.py` | Hybrid Search | Vector + keyword search with RRF |
| `06_agentic_rag.py` | Agentic RAG | Document-oriented retrieval with tool use |
| `runbooks/` | Sample Data | Sample runbooks for agentic RAG demo |

## Prerequisites

For PostgreSQL examples (03-05), start Postgres with pgvector:

```bash
docker compose up -d
```

This starts PostgreSQL with pgvector and creates the `vectordb` database.

## Setup

```bash
cd code/python/week-3
uv sync
cp .env-sample .env
# Add your OPENAI_API_KEY to .env
```

## Running Examples

```bash
# 1. File Loading (simple RAG)
uv run python 01_file_loading.py

# 2. Embeddings
uv run python 02_embeddings.py

# 3. PostgreSQL Connection (requires Docker)
uv run python 03_connection.py

# 4. Vector Search (requires Docker)
uv run python 04_vector_search.py

# 5. Hybrid Search (requires Docker)
uv run python 05_hybrid_search.py

# 6. Agentic RAG (no Docker required)
uv run python 06_agentic_rag.py
```

## Project

The Week 3 project (Document Search) is in `projects/week-3-doc-search/`.
