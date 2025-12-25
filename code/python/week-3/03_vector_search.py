"""
RAG Strategy 2: Vector Search with Postgres

Complete pipeline for semantic search using OpenAI embeddings,
Docling for document processing, and pgvector for storage.
"""

import os
from pathlib import Path

import tiktoken
import psycopg
from pgvector.psycopg import register_vector
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# =============================================================================
# Configuration
# =============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb"
)

# OpenAI text-embedding-3-small produces 1536 dimensions by default
EMBEDDING_DIMENSIONS = 1536

# Target ~300 tokens per chunk for optimal retrieval
MAX_CHUNK_TOKENS = 400

# Tokenizer for counting tokens
tokenizer = tiktoken.get_encoding("cl100k_base")


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

# OpenAI uses the same model for both document and query embeddings.
# Unlike Gemini, there are no separate task types.


def embed_text(text: str) -> list[float]:
    """Embed text using OpenAI embeddings."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single API call."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


# =============================================================================
# Token Counting
# =============================================================================


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(tokenizer.encode(text))


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
        embedding = embed_text(chunk["content"])

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
    query_embedding = embed_text(query)

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

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""Answer the question based on the context provided.
Cite your sources.

Context:
{context}

Question: {question}""",
    )

    return response.output_text


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
