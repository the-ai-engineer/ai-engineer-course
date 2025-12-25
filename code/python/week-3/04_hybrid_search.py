"""
RAG Strategy 3: Hybrid Search

Combine vector similarity with keyword matching for better retrieval.
Vector search finds semantic matches; full-text finds exact terms.
"""

import os

import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb"
)

EMBEDDING_DIMENSIONS = 1536


# =============================================================================
# Database Connection
# =============================================================================


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


# =============================================================================
# Schema Extensions for Hybrid Search
# =============================================================================


def add_fulltext_column(conn):
    """
    Add tsvector column for full-text search.

    Run this once after creating the base schema from 03_vector_search.py.
    """
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
# Embeddings
# =============================================================================


def embed_text(text: str) -> list[float]:
    """Embed text using OpenAI embeddings."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


# =============================================================================
# Individual Search Methods
# =============================================================================


def search_vector(conn, query_embedding: list[float], limit: int = 10) -> list[dict]:
    """Vector similarity search."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        ORDER BY c.embedding <=> %s
        LIMIT %s
        """,
        (query_embedding, limit),
    ).fetchall()

    return [{"id": r[0], "content": r[1], "source": r[2]} for r in results]


def search_fulltext(conn, query: str, limit: int = 10) -> list[dict]:
    """
    Full-text keyword search using Postgres tsvector.

    websearch_to_tsquery handles natural language queries.
    ts_rank_cd provides relevance scoring.
    """
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.content_tsv @@ websearch_to_tsquery('english', %s)
        ORDER BY ts_rank_cd(c.content_tsv, websearch_to_tsquery('english', %s)) DESC
        LIMIT %s
        """,
        (query, query, limit),
    ).fetchall()

    return [{"id": r[0], "content": r[1], "source": r[2]} for r in results]


# =============================================================================
# Reciprocal Rank Fusion
# =============================================================================

# RRF combines rankings from multiple methods.
# Formula: score = 1/(k + rank_vector) + 1/(k + rank_keyword)
# Where k is a smoothing constant (typically 60).
#
# Example:
#   Doc A: rank 1 in both -> 1/61 + 1/61 = 0.0328
#   Doc B: rank 2 vector only -> 1/62 + 0 = 0.0161
#   Result: A beats B because it appeared in both searches.


def reciprocal_rank_fusion(
    rankings: list[list[int]],
    k: int = 60,
) -> list[tuple[int, float]]:
    """
    Combine rankings using RRF.

    Args:
        rankings: List of rankings (each is a list of IDs in rank order)
        k: Smoothing constant (higher = less emphasis on top ranks)

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
# Hybrid Search (Python Implementation)
# =============================================================================


def search_hybrid(conn, query: str, limit: int = 5) -> list[dict]:
    """
    Hybrid search combining vector and keyword.

    Gets candidates from both methods, combines with RRF.
    """
    query_embedding = embed_text(query)

    # Get candidates from both methods (2x limit for better fusion)
    vector_results = search_vector(conn, query_embedding, limit=limit * 2)
    fulltext_results = search_fulltext(conn, query, limit=limit * 2)

    # Extract IDs for ranking
    vector_ids = [r["id"] for r in vector_results]
    fulltext_ids = [r["id"] for r in fulltext_results]

    # Combine with RRF
    combined = reciprocal_rank_fusion([vector_ids, fulltext_ids])

    # Get top IDs
    top_ids = [doc_id for doc_id, score in combined[:limit]]

    if not top_ids:
        return []

    # Fetch content for top results
    placeholders = ",".join(["%s"] * len(top_ids))
    results = conn.execute(
        f"""
        SELECT c.id, c.content, d.source
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.id IN ({placeholders})
        """,
        top_ids,
    ).fetchall()

    # Preserve RRF order
    id_to_result = {r[0]: {"id": r[0], "content": r[1], "source": r[2]} for r in results}
    return [id_to_result[id] for id in top_ids if id in id_to_result]


# =============================================================================
# SQL-Native Hybrid Search (More Efficient)
# =============================================================================


def create_hybrid_search_function(conn):
    """
    Create SQL function for hybrid search.

    More efficient than Python implementation because everything
    happens in the database without round trips.
    """
    conn.execute(f"""
        CREATE OR REPLACE FUNCTION hybrid_search(
            query_text TEXT,
            query_embedding vector({EMBEDDING_DIMENSIONS}),
            match_count INT DEFAULT 10,
            rrf_k INT DEFAULT 60
        )
        RETURNS TABLE (id BIGINT, content TEXT, source TEXT, score FLOAT)
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
            c.content,
            d.source,
            (COALESCE(1.0 / (rrf_k + s.rank), 0.0) +
             COALESCE(1.0 / (rrf_k + k.rank), 0.0))::FLOAT AS score
        FROM semantic s
        FULL OUTER JOIN keyword k ON s.id = k.id
        JOIN chunks c ON c.id = COALESCE(s.id, k.id)
        JOIN documents d ON c.document_id = d.id
        ORDER BY score DESC
        LIMIT match_count;
        $$;
    """)
    conn.commit()


def search_hybrid_sql(conn, query: str, limit: int = 5) -> list[dict]:
    """Use the SQL-native hybrid search function."""
    query_embedding = embed_text(query)

    results = conn.execute(
        "SELECT * FROM hybrid_search(%s, %s, %s)",
        (query, query_embedding, limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "score": r[3]}
        for r in results
    ]


# =============================================================================
# RAG with Hybrid Search
# =============================================================================


def rag_hybrid(conn, question: str, k: int = 5) -> str:
    """RAG using hybrid search."""
    results = search_hybrid(conn, question, limit=k)

    if not results:
        return "No relevant information found."

    context = "\n\n---\n\n".join(
        f"[{r['source']}]\n{r['content']}" for r in results
    )

    response = client.responses.create(
        model="gpt-5-mini",
        input=f"""Answer based on the context. Cite sources.

Context:
{context}

Question: {question}""",
    )

    return response.output_text


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    conn = get_connection()

    # Add full-text column (run once after base schema setup)
    # add_fulltext_column(conn)

    # Create SQL function (optional, for better performance)
    # create_hybrid_search_function(conn)

    # Vector search only
    # embedding = embed_text("password reset")
    # vector_results = search_vector(conn, embedding, limit=5)

    # Full-text search only
    # fulltext_results = search_fulltext(conn, "error XYZ-123", limit=5)

    # Hybrid search (Python)
    # hybrid_results = search_hybrid(conn, "password reset", limit=5)

    # Hybrid search (SQL - faster)
    # hybrid_results = search_hybrid_sql(conn, "password reset", limit=5)

    # RAG with hybrid search
    # answer = rag_hybrid(conn, "What is the refund policy?")
    # print(answer)

    print("Hybrid search module loaded")
    conn.close()
