"""
Database initialization script for Render deployment.

Render's managed PostgreSQL doesn't run init.sql automatically, so this script
sets up the pgvector extension, tables, indexes, and functions.

Usage:
    uv run python scripts/init_db.py
"""

import os
import sys

import psycopg


def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    return url


def init_database(database_url: str) -> None:
    """Initialize the database with pgvector and required schema."""
    print("Connecting to database...")
    conn = psycopg.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    print("Enabling pgvector extension...")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    print("Creating chunks table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536),
            content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    print("Creating HNSW index for vector search...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    """)

    print("Creating GIN index for full-text search...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS chunks_content_tsv_idx
        ON chunks USING gin(content_tsv);
    """)

    print("Creating vector_search function...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION vector_search(
            query_embedding vector(1536),
            match_count INT DEFAULT 5
        )
        RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
        LANGUAGE sql AS $$
        SELECT
            c.id,
            c.source,
            c.content,
            (1 - (c.embedding <=> query_embedding))::FLOAT AS score
        FROM chunks c
        WHERE c.embedding IS NOT NULL
        ORDER BY c.embedding <=> query_embedding
        LIMIT match_count;
        $$;
    """)

    print("Creating keyword_search function...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION keyword_search(
            query_text TEXT,
            match_count INT DEFAULT 5
        )
        RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
        LANGUAGE sql AS $$
        SELECT
            c.id,
            c.source,
            c.content,
            ts_rank_cd(c.content_tsv, websearch_to_tsquery('english', query_text))::FLOAT AS score
        FROM chunks c
        WHERE c.content_tsv @@ websearch_to_tsquery('english', query_text)
        ORDER BY score DESC
        LIMIT match_count;
        $$;
    """)

    print("Creating hybrid_search function...")
    cursor.execute("""
        CREATE OR REPLACE FUNCTION hybrid_search(
            query_text TEXT,
            query_embedding vector(1536),
            match_count INT DEFAULT 5,
            rrf_k INT DEFAULT 60
        )
        RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
        LANGUAGE sql AS $$
        WITH semantic AS (
            SELECT c.id, ROW_NUMBER() OVER (ORDER BY c.embedding <=> query_embedding) AS rank
            FROM chunks c
            WHERE c.embedding IS NOT NULL
            LIMIT match_count * 2
        ),
        keyword AS (
            SELECT c.id, ROW_NUMBER() OVER (
                ORDER BY ts_rank_cd(c.content_tsv, websearch_to_tsquery('english', query_text)) DESC
            ) AS rank
            FROM chunks c
            WHERE c.content_tsv @@ websearch_to_tsquery('english', query_text)
            LIMIT match_count * 2
        )
        SELECT
            c.id,
            c.source,
            c.content,
            (COALESCE(1.0 / (rrf_k + s.rank), 0.0) +
             COALESCE(1.0 / (rrf_k + k.rank), 0.0))::FLOAT AS score
        FROM semantic s
        FULL OUTER JOIN keyword k ON s.id = k.id
        JOIN chunks c ON c.id = COALESCE(s.id, k.id)
        ORDER BY score DESC
        LIMIT match_count;
        $$;
    """)

    cursor.close()
    conn.close()
    print("Database initialization complete!")


if __name__ == "__main__":
    database_url = get_database_url()
    init_database(database_url)
