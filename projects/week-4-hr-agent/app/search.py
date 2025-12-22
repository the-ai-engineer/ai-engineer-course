"""Search functionality using PostgreSQL functions."""

import psycopg

from app.embeddings import embed_query
from app.models import SearchResult


def search(
    conn: psycopg.Connection,
    query: str,
    limit: int = 5,
    search_type: str = "hybrid",
) -> list[SearchResult]:
    """Search chunks using PostgreSQL functions.

    Args:
        conn: Database connection.
        query: Search query text.
        limit: Maximum number of results.
        search_type: One of "vector", "keyword", or "hybrid".

    Returns:
        List of search results.
    """
    if search_type == "vector":
        query_embedding = embed_query(query)
        results = conn.execute(
            "SELECT * FROM vector_search(%s, %s)",
            (query_embedding, limit),
        ).fetchall()

    elif search_type == "keyword":
        results = conn.execute(
            "SELECT * FROM keyword_search(%s, %s)",
            (query, limit),
        ).fetchall()

    else:  # hybrid
        query_embedding = embed_query(query)
        results = conn.execute(
            "SELECT * FROM hybrid_search(%s, %s, %s)",
            (query, query_embedding, limit),
        ).fetchall()

    return [
        SearchResult(
            chunk_id=r[0],
            source=r[1],
            content=r[2],
            metadata=r[3] or {},
            score=r[4],
        )
        for r in results
    ]
