"""
RAG Strategy 3: Vector Search with Postgres

Complete pipeline for semantic search using Gemini embeddings,
Docling for document processing, and pgvector for storage.
"""

import os
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# =============================================================================
# Configuration
# =============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb"
)

# Embedding dimensions: 768 (fast), 1536 (balanced), 3072 (best quality)
# 768 recommended for most RAG use cases
EMBEDDING_DIMENSIONS = 768

# Gemini recommends ~300 tokens for optimal retrieval
# Using 400 as conservative limit (no local tokenizer like tiktoken)
MAX_CHUNK_TOKENS = 400


# =============================================================================
# Database Connection
# =============================================================================


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def init_schema(conn, dimensions: int = EMBEDDING_DIMENSIONS):
    """Create tables for RAG storage."""
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            page_numbers INTEGER[],
            headings TEXT[],
            embedding vector({dimensions}),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # HNSW index - better than IVFFlat for most cases
    # Create AFTER bulk loading for better performance
    conn.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    conn.commit()


# =============================================================================
# Embeddings
# =============================================================================

# Key concept: Use different task types for documents vs queries.
# This optimizes the embedding for its intended use.


def embed_document(
    text: str,
    title: str | None = None,
    dimensions: int = EMBEDDING_DIMENSIONS,
) -> list[float]:
    """Embed a document for storage."""
    config = types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=dimensions,
    )
    if title:
        config.title = title

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=config,
    )
    return response.embeddings[0].values


def embed_query(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Embed a query for searching."""
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=dimensions,
        ),
    )
    return response.embeddings[0].values


# =============================================================================
# Document Processing
# =============================================================================


def process_document(source: str, max_tokens: int = MAX_CHUNK_TOKENS) -> list[dict]:
    """
    Parse and chunk a document using Docling's HybridChunker.

    HybridChunker provides structure-aware chunking:
    - Respects headings, sections, paragraphs
    - Token-aware sizing
    - Preserves metadata for citations
    """
    converter = DocumentConverter()
    chunker = HybridChunker(max_tokens=max_tokens)

    print(f"Processing: {source}")
    result = converter.convert(source)
    chunks = list(chunker.chunk(dl_doc=result.document))
    print(f"Created {len(chunks)} chunks")

    processed = []
    for i, chunk in enumerate(chunks):
        # contextualize() includes surrounding context (headings)
        text = chunker.contextualize(chunk)

        # Extract page numbers
        page_numbers = sorted(
            set(
                prov.page_no
                for item in chunk.meta.doc_items
                for prov in item.prov
                if hasattr(prov, "page_no") and prov.page_no is not None
            )
        )

        # Extract headings
        headings = getattr(chunk.meta, "headings", []) or []

        processed.append({
            "content": text,
            "chunk_index": i,
            "page_numbers": page_numbers,
            "headings": headings,
        })

    return processed


# =============================================================================
# Indexing Pipeline
# =============================================================================


def index_document(conn, source: str, title: str | None = None) -> int:
    """
    Index a document for search.

    Full pipeline: parse -> chunk -> embed -> store
    """
    # Insert document record
    result = conn.execute(
        "INSERT INTO documents (source, title) VALUES (%s, %s) RETURNING id",
        (source, title),
    ).fetchone()
    doc_id = result[0]

    # Process into chunks
    chunks = process_document(source)

    # Embed and store each chunk
    for chunk in chunks:
        embedding = embed_document(
            chunk["content"],
            title=chunk["headings"][0] if chunk["headings"] else None,
        )

        conn.execute(
            """
            INSERT INTO chunks (document_id, content, chunk_index, page_numbers, headings, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                doc_id,
                chunk["content"],
                chunk["chunk_index"],
                chunk["page_numbers"],
                chunk["headings"],
                embedding,
            ),
        )

    conn.commit()
    print(f"Indexed {len(chunks)} chunks from {source}")
    return doc_id


def index_directory(conn, directory: str, extensions: list[str] | None = None) -> int:
    """Index all documents in a directory."""
    if extensions is None:
        extensions = [".pdf", ".md", ".txt", ".docx"]

    path = Path(directory)
    total = 0

    for ext in extensions:
        for file in path.glob(f"**/*{ext}"):
            index_document(conn, str(file), title=file.stem)
            total += 1

    return total


# =============================================================================
# Search
# =============================================================================


def search(conn, query: str, limit: int = 5) -> list[dict]:
    """
    Search for relevant chunks.

    Uses cosine distance (<=> operator) - lower = more similar.
    """
    query_embedding = embed_query(query)

    results = conn.execute(
        """
        SELECT c.id, c.content, d.source, c.page_numbers, c.headings,
               c.embedding <=> %s AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, limit),
    ).fetchall()

    return [
        {
            "content": r[1],
            "source": r[2],
            "page_numbers": r[3] or [],
            "headings": r[4] or [],
            "distance": r[5],
        }
        for r in results
    ]


# =============================================================================
# RAG Query
# =============================================================================


def rag_query(conn, question: str, k: int = 5) -> str:
    """Answer a question using RAG."""
    results = search(conn, question, limit=k)

    if not results:
        return "No relevant information found."

    # Build context with citations
    context_parts = []
    for r in results:
        source_info = f"[Source: {r['source']}"
        if r["page_numbers"]:
            source_info += f", Pages: {r['page_numbers']}"
        source_info += "]"
        context_parts.append(f"{source_info}\n{r['content']}")

    context = "\n\n---\n\n".join(context_parts)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""Answer the question based on the context provided.
Cite your sources.

Context:
{context}

Question: {question}""",
    )

    return response.text


# =============================================================================
# Utilities
# =============================================================================


def drop_tables(conn):
    """Drop all tables (for testing/reset)."""
    conn.execute("DROP TABLE IF EXISTS chunks CASCADE")
    conn.execute("DROP TABLE IF EXISTS documents CASCADE")
    conn.commit()


def get_stats(conn) -> dict:
    """Get database statistics."""
    docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    return {"documents": docs, "chunks": chunks}


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Setup
    conn = get_connection()
    init_schema(conn)

    print("Database initialized")
    print(f"Stats: {get_stats(conn)}")

    # To index documents:
    # index_document(conn, "employee_handbook.pdf", "Employee Handbook")
    # index_directory(conn, "./documents")

    # To search:
    # results = search(conn, "vacation policy", limit=5)
    # for r in results:
    #     print(f"Distance: {r['distance']:.3f}")
    #     print(f"Source: {r['source']}, Pages: {r['page_numbers']}")
    #     print(f"Content: {r['content'][:100]}...")
    #     print()

    # To run RAG:
    # answer = rag_query(conn, "How many vacation days do I get?")
    # print(answer)

    conn.close()
