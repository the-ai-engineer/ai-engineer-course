"""
PostgreSQL Connection

Connect to PostgreSQL with pgvector and store real embeddings.

Prerequisites:
    docker compose up -d
"""

import os
from contextlib import contextmanager

import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/vectordb"
)

client = OpenAI()


# =============================================================================
# Embeddings
# =============================================================================


def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


# =============================================================================
# Connection
# =============================================================================


@contextmanager
def get_connection():
    """Get a database connection with pgvector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()


# =============================================================================
# Schema
# =============================================================================


def create_schema(conn):
    """Create table for storing chunks with embeddings."""
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            content TEXT NOT NULL,
            embedding vector(1536)
        )
    """)
    conn.commit()
    print("Schema created")


def drop_schema(conn):
    """Drop the table."""
    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.commit()
    print("Schema dropped")


# =============================================================================
# Demo
# =============================================================================


def run_demo():
    """Demonstrate PostgreSQL connection with real embeddings."""
    print("=== PostgreSQL Connection Demo ===\n")

    with get_connection() as conn:
        # Setup
        drop_schema(conn)
        create_schema(conn)

        # Sample texts
        texts = [
            "PostgreSQL is a powerful open source relational database.",
            "Vector databases store embeddings for similarity search.",
            "Python is a popular programming language for AI applications.",
        ]

        # Insert with real embeddings
        print("Inserting chunks with embeddings...")
        for text in texts:
            embedding = get_embedding(text)
            conn.execute(
                "INSERT INTO chunks (content, embedding) VALUES (%s, %s)",
                (text, embedding),
            )
            print(f"  Inserted: {text[:50]}...")
        conn.commit()

        # Query
        count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        print(f"\nTotal chunks: {count}")

        # Show contents
        print("\nStored chunks:")
        rows = conn.execute("SELECT id, content FROM chunks").fetchall()
        for row in rows:
            print(f"  [{row[0]}] {row[1]}")

        # Verify embeddings exist
        row = conn.execute(
            "SELECT id, embedding IS NOT NULL as has_embedding FROM chunks LIMIT 1"
        ).fetchone()
        print(f"\nEmbedding stored: {row[1]}")

    print("\nDemo complete!")


if __name__ == "__main__":
    run_demo()
