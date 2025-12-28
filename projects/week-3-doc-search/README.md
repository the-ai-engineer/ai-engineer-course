# Week 3 Project: Support Knowledge Base Search

A document search tool demonstrating RAG with PostgreSQL and pgvector.

## What You'll Learn

- Document parsing with Docling
- Token-based chunking for embeddings
- Vector search with pgvector
- Hybrid search (vector + keyword with RRF)
- RAG: retrieval + generation

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

# Search via CLI
uv run python search.py --ask "What plans do you offer?"

# Or launch the chat UI
uv run chainlit run app.py
```

## Project Structure

```
week-3-doc-search/
├── docker/
│   ├── docker-compose.yml
│   └── init.sql
├── docs/             # Zen HR support documentation
├── app.py            # Chainlit chat UI
├── db.py             # Database connection
├── ingest.py         # Document parsing, chunking, and storage
├── search.py         # Vector, keyword, and hybrid search (CLI)
└── pyproject.toml
```

## Configuration

Set environment variables in `.env`:

```
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/week3_doc_search
```

## Sample Questions

The default documents are Zen HR's customer support documentation. Try these questions:

**Getting Started**
- "How do I create an account?"
- "What's included in the free trial?"
- "How do I add employees?"

**Billing & Plans**
- "What plans do you offer?"
- "How much does the Professional plan cost?"
- "Do you offer annual billing discounts?"

**Integrations**
- "What payroll systems do you integrate with?"
- "How do I connect to Gusto?"
- "Do you have a REST API?"

**Troubleshooting**
- "Why can't I log in?"
- "What does error E401 mean?"
- "How do I reset my password?"

## CLI Usage

```bash
# RAG: search + generate answer
uv run python search.py --ask "What plans do you offer?"

# Hybrid search with answer
uv run python search.py --hybrid --ask "How do I integrate with ADP?"

# Retrieval only (no answer generation)
uv run python search.py "password reset"

# Keyword search (exact term matching)
uv run python search.py --keyword "E401"

# Ingest your own documents
uv run python ingest.py /path/to/your/documents
```

## Chat UI

Launch the Chainlit interface:

```bash
uv run chainlit run app.py
```

Opens at http://localhost:8000 with:
- Interactive chat interface
- Hybrid search + RAG
- Source citations for each answer
