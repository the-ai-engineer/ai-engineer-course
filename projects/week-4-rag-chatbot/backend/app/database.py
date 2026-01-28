"""Database connection pool for pgvector operations."""

from contextlib import contextmanager
from typing import Generator

import psycopg
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector

from app.config import get_settings

settings = get_settings()

# Connection pool with min/max connections
_pool: ConnectionPool | None = None


def _configure_connection(conn: psycopg.Connection) -> None:
    """Configure a connection from the pool."""
    register_vector(conn)


def get_pool() -> ConnectionPool:
    """Get or create the connection pool.

    Returns:
        The connection pool instance.
    """
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            settings.database_url,
            min_size=2,
            max_size=10,
            configure=_configure_connection,
        )
    return _pool


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Get a psycopg connection from the pool with pgvector support.

    Yields:
        A database connection with pgvector types registered.
    """
    pool = get_pool()
    with pool.connection() as conn:
        yield conn


def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
