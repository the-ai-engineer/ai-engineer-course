"""
Hybrid Search

Combine vector and full-text search for better retrieval.
"""

import psycopg
from pgvector.psycopg import register_vector
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb")


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def embed_text(text: str) -> list[float]:
    """Generate an embedding for text."""
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    return response.embeddings[0].values


# =============================================================================
# Full-Text Search Setup
# =============================================================================


def add_fulltext_column(conn):
    """Add tsvector column for full-text search."""
    conn.execute("""
        ALTER TABLE chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector
        GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS chunks_content_tsv_idx
        ON chunks USING gin(content_tsv)
    """)
    conn.commit()


# =============================================================================
# Individual Search Methods
# =============================================================================


def search_vector(
    conn,
    query_embedding: list[float],
    limit: int = 10,
) -> list[dict]:
    """Vector similarity search."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source,
               c.embedding <=> %s AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "score": 1 - r[3]}  # Convert distance to score
        for r in results
    ]


def search_fulltext(
    conn,
    query: str,
    limit: int = 10,
) -> list[dict]:
    """Full-text search using Postgres tsvector."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source,
               ts_rank(c.content_tsv, websearch_to_tsquery('english', %s)) AS rank
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.content_tsv @@ websearch_to_tsquery('english', %s)
        ORDER BY rank DESC
        LIMIT %s
        """,
        (query, query, limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "score": r[3]}
        for r in results
    ]


# =============================================================================
# Reciprocal Rank Fusion
# =============================================================================


def reciprocal_rank_fusion(
    rankings: list[list[int]],
    k: int = 60,
) -> list[tuple[int, float]]:
    """
    Combine multiple rankings using Reciprocal Rank Fusion.

    Args:
        rankings: List of rankings, where each ranking is a list of IDs
        k: RRF constant (default 60)

    Returns:
        List of (id, score) tuples sorted by score descending
    """
    scores = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0.0
            scores[doc_id] += 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# =============================================================================
# Hybrid Search
# =============================================================================


def search_hybrid(
    conn,
    query: str,
    limit: int = 5,
    candidates: int = 20,
) -> list[dict]:
    """
    Hybrid search combining vector and full-text.

    Gets candidates from both methods, combines with RRF.
    """
    # Embed the query
    query_embedding = embed_text(query)

    # Get candidates from both methods
    vector_results = search_vector(conn, query_embedding, limit=candidates)
    fulltext_results = search_fulltext(conn, query, limit=candidates)

    # Extract IDs for ranking
    vector_ids = [r["id"] for r in vector_results]
    fulltext_ids = [r["id"] for r in fulltext_results]

    # Combine with RRF
    combined = reciprocal_rank_fusion([vector_ids, fulltext_ids])

    # Get top IDs
    top_ids = [doc_id for doc_id, score in combined[:limit]]

    if not top_ids:
        return []

    # Fetch full results
    return fetch_chunks_by_ids(conn, top_ids)


def fetch_chunks_by_ids(conn, ids: list[int]) -> list[dict]:
    """Fetch chunks by their IDs, preserving order."""
    if not ids:
        return []

    # Create a values list for ordering
    placeholders = ",".join(["%s"] * len(ids))

    results = conn.execute(
        f"""
        SELECT c.id, c.content, d.source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.id IN ({placeholders})
        """,
        ids,
    ).fetchall()

    # Build lookup
    id_to_result = {r[0]: {"id": r[0], "content": r[1], "source": r[2]} for r in results}

    # Return in original order
    return [id_to_result[id] for id in ids if id in id_to_result]


# =============================================================================
# Weighted Hybrid Search
# =============================================================================


def search_hybrid_weighted(
    conn,
    query: str,
    limit: int = 5,
    vector_weight: float = 0.5,
    candidates: int = 20,
) -> list[dict]:
    """
    Hybrid search with configurable weights.

    Args:
        vector_weight: Weight for vector search (0-1). Full-text gets 1 - vector_weight.
    """
    query_embedding = embed_text(query)
    fulltext_weight = 1.0 - vector_weight

    # Get candidates
    vector_results = search_vector(conn, query_embedding, limit=candidates)
    fulltext_results = search_fulltext(conn, query, limit=candidates)

    # Calculate weighted scores
    scores = {}

    for rank, r in enumerate(vector_results, start=1):
        doc_id = r["id"]
        scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (60 + rank)) * vector_weight

    for rank, r in enumerate(fulltext_results, start=1):
        doc_id = r["id"]
        scores[doc_id] = scores.get(doc_id, 0) + (1.0 / (60 + rank)) * fulltext_weight

    # Sort by score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:limit]

    return fetch_chunks_by_ids(conn, sorted_ids)


# =============================================================================
# RAG with Hybrid Search
# =============================================================================


def rag_hybrid(conn, query: str, k: int = 5) -> str:
    """RAG using hybrid search."""
    results = search_hybrid(conn, query, limit=k)

    if not results:
        return "No relevant information found."

    context = "\n\n---\n\n".join(r["content"] for r in results)

    prompt = f"""Answer the question based on the context provided.

Context:
{context}

Question: {query}

Answer:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


# =============================================================================
# Example Usage
# =============================================================================

# conn = get_connection()

# Add full-text search column (run once)
# add_fulltext_column(conn)

# Vector-only search
# query = "password reset"
# embedding = embed_text(query)
# vector_results = search_vector(conn, embedding, limit=5)

# Full-text only search
# fulltext_results = search_fulltext(conn, query, limit=5)

# Hybrid search (combines both)
# hybrid_results = search_hybrid(conn, query, limit=5)

# Weighted hybrid (more emphasis on keywords)
# weighted_results = search_hybrid_weighted(conn, query, vector_weight=0.3, limit=5)

# Full RAG with hybrid search
# answer = rag_hybrid(conn, "What is the refund policy?")
# answer

# conn.close()
