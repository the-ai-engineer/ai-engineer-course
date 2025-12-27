# Week 3 Project: Document Search

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

# Ingest sample document (Nike 2025 Annual Report)
uv run python ingest.py

# Search via CLI
uv run python search.py --ask "What was Nike's revenue in fiscal 2025?"

# Or launch the chat UI
uv run chainlit run app.py
```

## Project Structure

```
week-3-doc-search/
├── docker/
│   ├── docker-compose.yml
│   └── init.sql
├── app.py         # Chainlit chat UI
├── db.py          # Database connection
├── ingest.py      # Document parsing, chunking, and storage
├── search.py      # Vector, keyword, and hybrid search (CLI)
└── pyproject.toml
```

## Configuration

Set environment variables in `.env`:

```
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost/week3_doc_search
```

## Sample Questions

The default document is Nike's 2025 Annual Report (10-K filing). Try these questions:

**Financial Performance**
- "What was Nike's total revenue in fiscal 2025?"
- "How much did Nike's revenue decline compared to last year?"
- "What was Nike's gross margin in fiscal 2025?"
- "What were Nike's earnings per share?"

**Business Segments**
- "How much revenue came from North America?"
- "What is Nike's direct-to-consumer revenue?"
- "How did the EMEA region perform?"
- "What percentage of revenue comes from footwear vs apparel?"

**Strategy & Operations**
- "Who is Nike's CEO?"
- "What are Nike's main risk factors?"
- "How many employees does Nike have?"
- "What is Nike's inventory strategy?"

**Specific Numbers (good for verifying RAG accuracy)**
- "What was Nike's Q4 revenue?" → $11.1 billion
- "What was the full year revenue?" → $46.3 billion
- "What was the revenue decline percentage?" → 10%

## CLI Usage

```bash
# RAG: search + generate answer
uv run python search.py --ask "What was Nike's gross margin?"

# Hybrid search with answer
uv run python search.py --hybrid --ask "What are Nike's risk factors?"

# Retrieval only (no answer generation)
uv run python search.py "direct to consumer"

# Keyword search (exact term matching)
uv run python search.py --keyword "CONVERSE"

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
