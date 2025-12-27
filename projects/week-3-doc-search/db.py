"""Database connection management."""

import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/week3_doc_search")


@contextmanager
def get_connection():
    """Get a database connection with pgvector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    try:
        yield conn
    finally:
        conn.close()
