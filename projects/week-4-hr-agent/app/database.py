"""Database connection management."""

from contextlib import contextmanager

import psycopg
from pgvector.psycopg import register_vector

from app.config import get_settings

settings = get_settings()


@contextmanager
def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(settings.database_url)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()


def get_stats(conn: psycopg.Connection) -> dict:
    """Get database statistics."""
    count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    return {"chunks": count}
