"""
Vector Storage with pgvector

Store and query embeddings in Postgres.
"""

import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
import os

load_dotenv()

# =============================================================================
# Database Connection
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb")


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


# =============================================================================
# Schema Setup
# =============================================================================


def init_schema(conn):
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            embedding vector(768),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()


def create_index(conn, index_type: str = "ivfflat"):
    """Create a vector index for faster search."""
    if index_type == "ivfflat":
        conn.execute("""
            CREATE INDEX IF NOT EXISTS chunks_embedding_idx
            ON chunks
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
    elif index_type == "hnsw":
        conn.execute("""
            CREATE INDEX IF NOT EXISTS chunks_embedding_idx
            ON chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """)
    conn.commit()


def drop_tables(conn):
    """Drop all tables (for testing)."""
    conn.execute("DROP TABLE IF EXISTS chunks CASCADE")
    conn.execute("DROP TABLE IF EXISTS documents CASCADE")
    conn.commit()


# =============================================================================
# Document Operations
# =============================================================================


def insert_document(conn, source: str, title: str = None) -> int:
    """Insert a document and return its ID."""
    result = conn.execute(
        """
        INSERT INTO documents (source, title)
        VALUES (%s, %s)
        RETURNING id
        """,
        (source, title),
    ).fetchone()
    conn.commit()
    return result[0]


def insert_chunk(
    conn,
    document_id: int,
    content: str,
    chunk_index: int,
    embedding: list[float],
) -> int:
    """Insert a chunk with its embedding."""
    result = conn.execute(
        """
        INSERT INTO chunks (document_id, content, chunk_index, embedding)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (document_id, content, chunk_index, embedding),
    ).fetchone()
    conn.commit()
    return result[0]


def insert_chunks_batch(
    conn,
    document_id: int,
    chunks: list[tuple[str, int, list[float]]],
):
    """Insert multiple chunks efficiently."""
    conn.executemany(
        """
        INSERT INTO chunks (document_id, content, chunk_index, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        [(document_id, content, idx, emb) for content, idx, emb in chunks],
    )
    conn.commit()


# =============================================================================
# Search Operations
# =============================================================================


def search_similar(
    conn,
    query_embedding: list[float],
    limit: int = 5,
    source_filter: str = None,
) -> list[dict]:
    """Search for similar chunks."""
    if source_filter:
        results = conn.execute(
            """
            SELECT c.id, c.content, d.source, c.chunk_index,
                   c.embedding <=> %s AS distance
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.source LIKE %s
            ORDER BY distance
            LIMIT %s
            """,
            (query_embedding, f"%{source_filter}%", limit),
        ).fetchall()
    else:
        results = conn.execute(
            """
            SELECT c.id, c.content, d.source, c.chunk_index,
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
            "id": r[0],
            "content": r[1],
            "source": r[2],
            "chunk_index": r[3],
            "distance": r[4],
        }
        for r in results
    ]


def count_chunks(conn) -> int:
    """Count total chunks in database."""
    result = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
    return result[0]


def count_documents(conn) -> int:
    """Count total documents in database."""
    result = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
    return result[0]


# =============================================================================
# Example Usage
# =============================================================================

# Initialize database
# conn = get_connection()
# init_schema(conn)

# Insert a document
# doc_id = insert_document(conn, "example.pdf", "Example Document")

# Insert chunks (you would generate these from docling + embeddings)
# fake_embedding = [0.1] * 768
# insert_chunk(conn, doc_id, "This is chunk 1 content", 0, fake_embedding)
# insert_chunk(conn, doc_id, "This is chunk 2 content", 1, fake_embedding)

# Search
# query_embedding = [0.1] * 768
# results = search_similar(conn, query_embedding, limit=5)
# results

# Create index after bulk loading
# create_index(conn, "ivfflat")

# conn.close()
