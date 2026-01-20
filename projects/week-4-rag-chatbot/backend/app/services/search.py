"""Search service for RAG retrieval."""

import logging

from app.database import get_connection
from app.services.embeddings import get_embedding

logger = logging.getLogger(__name__)


def vector_search(query: str, limit: int = 5) -> list[dict]:
    """Search using vector similarity."""
    embedding = get_embedding(query)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, source, content, score FROM vector_search(%s::vector, %s::int)",
                (embedding, limit),
            )
            rows = cur.fetchall()

    return [
        {"id": row[0], "source": row[1], "content": row[2], "score": row[3]}
        for row in rows
    ]


def keyword_search(query: str, limit: int = 5) -> list[dict]:
    """Search using keyword matching."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, source, content, score FROM keyword_search(%s, %s)",
                (query, limit),
            )
            rows = cur.fetchall()

    return [
        {"id": row[0], "source": row[1], "content": row[2], "score": row[3]}
        for row in rows
    ]


def hybrid_search(query: str, limit: int = 5) -> list[dict]:
    """Search using hybrid (vector + keyword) with RRF."""
    logger.info(f"[SEARCH] hybrid_search called with query: {query!r}, limit: {limit}")
    try:
        embedding = get_embedding(query)
        logger.info(f"[SEARCH] Got embedding of length {len(embedding)}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, source, content, score FROM hybrid_search(%s, %s::vector, %s::int)",
                    (query, embedding, limit),
                )
                rows = cur.fetchall()

        results = [
            {"id": row[0], "source": row[1], "content": row[2], "score": row[3]}
            for row in rows
        ]
        logger.info(f"[SEARCH] hybrid_search returning {len(results)} results")
        return results
    except Exception as e:
        logger.exception(f"[SEARCH] hybrid_search error: {e}")
        raise


def search(query: str, limit: int = 5, method: str = "hybrid") -> list[dict]:
    """Search documents using specified method.

    Args:
        query: Search query text.
        limit: Maximum number of results.
        method: One of "vector", "keyword", or "hybrid".

    Returns:
        List of matching documents with scores.
    """
    if method == "vector":
        return vector_search(query, limit)
    elif method == "keyword":
        return keyword_search(query, limit)
    else:
        return hybrid_search(query, limit)
