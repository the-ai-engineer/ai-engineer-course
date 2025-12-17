"""
Database module for document search.

Handles connection, schema, and basic operations.
"""

import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb")


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def init_schema(conn):
    """Create tables for document storage."""
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL UNIQUE,
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

    # Add full-text search column
    conn.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'chunks' AND column_name = 'content_tsv'
            ) THEN
                ALTER TABLE chunks ADD COLUMN content_tsv tsvector
                GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
            END IF;
        END $$;
    """)

    conn.commit()


def create_indexes(conn):
    """Create indexes for fast search."""
    # Vector index
    conn.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # Full-text index
    conn.execute("""
        CREATE INDEX IF NOT EXISTS chunks_content_tsv_idx
        ON chunks USING gin(content_tsv)
    """)

    conn.commit()


def insert_document(conn, source: str, title: str = None) -> int:
    """Insert a document and return its ID. Skip if already exists."""
    # Check if document already exists
    existing = conn.execute(
        "SELECT id FROM documents WHERE source = %s", (source,)
    ).fetchone()

    if existing:
        return existing[0]

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


def insert_chunks(conn, document_id: int, chunks: list[tuple[str, int, list[float]]]):
    """Insert multiple chunks for a document."""
    conn.executemany(
        """
        INSERT INTO chunks (document_id, content, chunk_index, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        [(document_id, content, idx, emb) for content, idx, emb in chunks],
    )
    conn.commit()


def get_stats(conn) -> dict:
    """Get database statistics."""
    docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    return {"documents": docs, "chunks": chunks}


def clear_all(conn):
    """Clear all data (for testing)."""
    conn.execute("DELETE FROM chunks")
    conn.execute("DELETE FROM documents")
    conn.commit()


if __name__ == "__main__":
    conn = get_connection()
    init_schema(conn)
    create_indexes(conn)
    print("Database initialized.")
    print(f"Stats: {get_stats(conn)}")
    conn.close()
