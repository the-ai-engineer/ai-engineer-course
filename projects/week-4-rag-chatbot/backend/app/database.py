"""Database connection for pgvector operations."""

from contextlib import contextmanager
from typing import Generator

import psycopg
from pgvector.psycopg import register_vector

from app.config import get_settings

settings = get_settings()


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Get a psycopg connection with pgvector support.

    Yields:
        A database connection with pgvector types registered.
    """
    conn = psycopg.connect(settings.database_url)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()
