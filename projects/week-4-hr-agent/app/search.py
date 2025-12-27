"""Search service for document retrieval."""

from openai import OpenAI

from app.config import get_settings
from app.database import get_connection

settings = get_settings()
client = OpenAI()


def embed_query(query: str) -> list[float]:
    """Get embedding for a query."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=query,
    )
    return response.data[0].embedding


def search(query: str, search_type: str = "hybrid", limit: int = 5) -> list[dict]:
    """Search documents.

    Args:
        query: Search query
        search_type: "vector", "keyword", or "hybrid" (default)
        limit: Max results

    Returns:
        List of search results with chunk_id, source, content, score.
    """
    with get_connection() as conn:
        if search_type == "vector":
            embedding = embed_query(query)
            rows = conn.execute(
                "SELECT * FROM vector_search(%s::vector, %s::int)",
                (embedding, limit),
            ).fetchall()
        elif search_type == "keyword":
            rows = conn.execute(
                "SELECT * FROM keyword_search(%s::text, %s::int)",
                (query, limit),
            ).fetchall()
        else:  # hybrid
            embedding = embed_query(query)
            rows = conn.execute(
                "SELECT * FROM hybrid_search(%s::text, %s::vector, %s::int)",
                (query, embedding, limit),
            ).fetchall()

    return [
        {
            "chunk_id": row[0],
            "source": row[1],
            "content": row[2],
            "score": row[3],
        }
        for row in rows
    ]
