"""Document search CLI.

Supports vector search (semantic), keyword search, and hybrid search (RRF).

Usage:
    python search.py "your question here"
    python search.py --hybrid "error code XYZ-123"
    python search.py --keyword "vacation policy"
    python search.py --limit 10 "remote work"
"""

import argparse
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from db import get_connection

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI()


# =============================================================================
# Embedding
# =============================================================================


def embed_query(text: str) -> list[float]:
    """Generate embedding for a search query."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


# =============================================================================
# Search Functions
# =============================================================================


def vector_search(query: str, limit: int = 5) -> list[dict]:
    """Search by semantic similarity using embeddings."""
    query_embedding = embed_query(query)

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM vector_search(%s::vector, %s::int)",
            (query_embedding, limit),
        ).fetchall()

    return [
        {"id": r[0], "source": r[1], "content": r[2], "score": r[3]}
        for r in rows
    ]


def keyword_search(query: str, limit: int = 5) -> list[dict]:
    """Search by keyword matching using PostgreSQL full-text search."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM keyword_search(%s::text, %s::int)",
            (query, limit),
        ).fetchall()

    return [
        {"id": r[0], "source": r[1], "content": r[2], "score": r[3]}
        for r in rows
    ]


def hybrid_search(query: str, limit: int = 5) -> list[dict]:
    """Search using both vector and keyword, combined with RRF.

    Reciprocal Rank Fusion combines results from both methods,
    giving you semantic matches AND exact keyword hits.
    """
    query_embedding = embed_query(query)

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM hybrid_search(%s::text, %s::vector, %s::int)",
            (query, query_embedding, limit),
        ).fetchall()

    return [
        {"id": r[0], "source": r[1], "content": r[2], "score": r[3]}
        for r in rows
    ]


# =============================================================================
# Display
# =============================================================================


def display_results(query: str, results: list[dict], search_type: str):
    """Display search results in a readable format."""
    print(f"\nQuery: {query}")
    print(f"Search type: {search_type}")
    print("-" * 60)

    if not results:
        print("No results found.")
        return

    for i, r in enumerate(results, 1):
        source = Path(r["source"]).name
        score = r["score"]
        content = r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"]

        print(f"\n{i}. [{source}] Score: {score:.4f}")
        print(f"   {content}")

    print("-" * 60)
    print(f"Total: {len(results)} results")


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Search documents")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--hybrid", action="store_true", help="Use hybrid search (vector + keyword)")
    parser.add_argument("--keyword", action="store_true", help="Use keyword search only")
    parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")

    args = parser.parse_args()

    if args.keyword:
        results = keyword_search(args.query, args.limit)
        search_type = "keyword"
    elif args.hybrid:
        results = hybrid_search(args.query, args.limit)
        search_type = "hybrid"
    else:
        results = vector_search(args.query, args.limit)
        search_type = "vector"

    display_results(args.query, results, search_type)


if __name__ == "__main__":
    main()
