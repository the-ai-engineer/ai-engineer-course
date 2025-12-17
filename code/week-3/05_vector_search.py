"""
Vector Search

Search strategies for RAG retrieval.
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
# Basic Search
# =============================================================================


def search_basic(
    conn,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict]:
    """Basic similarity search."""
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
        {"id": r[0], "content": r[1], "source": r[2], "distance": r[3]}
        for r in results
    ]


# =============================================================================
# Filtered Search
# =============================================================================


def search_by_source(
    conn,
    query_embedding: list[float],
    source_pattern: str,
    limit: int = 5,
) -> list[dict]:
    """Search with source filtering."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source,
               c.embedding <=> %s AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.source LIKE %s
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, f"%{source_pattern}%", limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "distance": r[3]}
        for r in results
    ]


def search_with_threshold(
    conn,
    query_embedding: list[float],
    max_distance: float = 0.5,
    limit: int = 10,
) -> list[dict]:
    """Search with distance threshold."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source,
               c.embedding <=> %s AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.embedding <=> %s < %s
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, query_embedding, max_distance, limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "distance": r[3]}
        for r in results
    ]


# =============================================================================
# Diverse Search
# =============================================================================


def search_diverse(
    conn,
    query_embedding: list[float],
    limit: int = 5,
    per_document: int = 2,
) -> list[dict]:
    """Search with diversity (limit chunks per document)."""
    results = conn.execute(
        """
        WITH ranked AS (
            SELECT c.id, c.content, d.source, c.document_id,
                   c.embedding <=> %s AS distance,
                   ROW_NUMBER() OVER (
                       PARTITION BY c.document_id
                       ORDER BY c.embedding <=> %s
                   ) AS rank_in_doc
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
        )
        SELECT id, content, source, distance
        FROM ranked
        WHERE rank_in_doc <= %s
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, query_embedding, per_document, limit),
    ).fetchall()

    return [
        {"id": r[0], "content": r[1], "source": r[2], "distance": r[3]}
        for r in results
    ]


# =============================================================================
# Reranking
# =============================================================================


def rerank_with_llm(query: str, chunks: list[str], top_k: int = 5) -> list[str]:
    """Use LLM to rerank chunks by relevance."""
    if not chunks:
        return []

    # Format chunks for the prompt
    chunk_list = "\n".join(
        f"{i+1}. {chunk[:300]}..." if len(chunk) > 300 else f"{i+1}. {chunk}"
        for i, chunk in enumerate(chunks)
    )

    prompt = f"""Rank these passages by relevance to the query.

Query: {query}

Passages:
{chunk_list}

Return ONLY the passage numbers in order of relevance, most relevant first.
Format: 1, 5, 3, 2, 4"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    # Parse the ranking
    try:
        ranking = [int(x.strip()) - 1 for x in response.text.strip().split(",")]
        reranked = [chunks[i] for i in ranking if 0 <= i < len(chunks)]
        return reranked[:top_k]
    except (ValueError, IndexError):
        # If parsing fails, return original order
        return chunks[:top_k]


def search_and_rerank(
    conn,
    query: str,
    final_k: int = 5,
    candidates: int = 20,
) -> list[dict]:
    """Search with reranking for better precision."""
    query_embedding = embed_text(query)

    # Get more candidates than needed
    results = search_basic(conn, query_embedding, limit=candidates)

    if not results:
        return []

    # Rerank
    chunks = [r["content"] for r in results]
    reranked_chunks = rerank_with_llm(query, chunks, top_k=final_k)

    # Match back to original results
    chunk_to_result = {r["content"]: r for r in results}
    return [chunk_to_result[c] for c in reranked_chunks if c in chunk_to_result]


# =============================================================================
# RAG Pipeline
# =============================================================================


def rag_search(conn, query: str, k: int = 5) -> list[str]:
    """Complete RAG search pipeline."""
    query_embedding = embed_text(query)
    results = search_basic(conn, query_embedding, limit=k)
    return [r["content"] for r in results]


def rag_answer(conn, query: str, k: int = 5) -> str:
    """Search and generate an answer."""
    chunks = rag_search(conn, query, k=k)

    if not chunks:
        return "No relevant information found."

    context = "\n\n---\n\n".join(chunks)

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

# Basic search
# query = "How do I reset my password?"
# embedding = embed_text(query)
# results = search_basic(conn, embedding, limit=5)
# results

# Search with source filter
# results = search_by_source(conn, embedding, ".pdf", limit=5)

# Search with diversity
# results = search_diverse(conn, embedding, limit=5, per_document=2)

# Search and rerank
# results = search_and_rerank(conn, query, final_k=5, candidates=20)

# Full RAG answer
# answer = rag_answer(conn, "What is the refund policy?")
# answer

# conn.close()
