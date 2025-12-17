"""
Document search CLI.

Search ingested documents using vector, full-text, or hybrid search.
"""

import sys
import argparse
from google import genai
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

client = genai.Client()


def embed_text(text: str) -> list[float]:
    """Generate an embedding for text."""
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    return response.embeddings[0].values


def search_vector(conn, query_embedding: list[float], limit: int = 5) -> list[dict]:
    """Vector similarity search."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source, c.chunk_index,
               c.embedding <=> %s AS distance
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, limit),
    ).fetchall()

    return [
        {
            "id": r[0],
            "content": r[1],
            "source": r[2],
            "chunk_index": r[3],
            "score": 1 - r[4],
        }
        for r in results
    ]


def search_fulltext(conn, query: str, limit: int = 5) -> list[dict]:
    """Full-text search."""
    results = conn.execute(
        """
        SELECT c.id, c.content, d.source, c.chunk_index,
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
        {
            "id": r[0],
            "content": r[1],
            "source": r[2],
            "chunk_index": r[3],
            "score": r[4],
        }
        for r in results
    ]


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Combine rankings using RRF."""
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def search_hybrid(conn, query: str, limit: int = 5) -> list[dict]:
    """Hybrid search combining vector and full-text."""
    query_embedding = embed_text(query)

    # Get candidates from both methods
    vector_results = search_vector(conn, query_embedding, limit=limit * 2)
    fulltext_results = search_fulltext(conn, query, limit=limit * 2)

    # Combine with RRF
    vector_ids = [r["id"] for r in vector_results]
    fulltext_ids = [r["id"] for r in fulltext_results]
    combined = reciprocal_rank_fusion([vector_ids, fulltext_ids])

    # Get top IDs
    top_ids = [doc_id for doc_id, score in combined[:limit]]

    if not top_ids:
        return []

    # Fetch full content
    placeholders = ",".join(["%s"] * len(top_ids))
    results = conn.execute(
        f"""
        SELECT c.id, c.content, d.source, c.chunk_index
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.id IN ({placeholders})
        """,
        top_ids,
    ).fetchall()

    # Build lookup and preserve order
    id_to_result = {
        r[0]: {"id": r[0], "content": r[1], "source": r[2], "chunk_index": r[3]}
        for r in results
    }
    return [id_to_result[id] for id in top_ids if id in id_to_result]


def format_results(results: list[dict], query: str):
    """Format and print search results."""
    if not results:
        print("No results found.")
        return

    print(f"\nResults for: {query}")
    print("=" * 60)

    for i, r in enumerate(results, 1):
        source = r["source"].split("/")[-1]  # Just filename
        score = r.get("score", "N/A")

        print(f"\n[{i}] {source} (chunk {r['chunk_index']})")
        if score != "N/A":
            print(f"    Score: {score:.4f}")
        print("-" * 40)

        # Truncate long content
        content = r["content"]
        if len(content) > 500:
            content = content[:500] + "..."
        print(content)

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Search documents")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--hybrid", action="store_true", help="Use hybrid search")
    parser.add_argument("--fulltext", action="store_true", help="Use full-text only")
    parser.add_argument("-n", "--limit", type=int, default=5, help="Number of results")

    args = parser.parse_args()

    conn = get_connection()

    if args.fulltext:
        print("Using full-text search...")
        results = search_fulltext(conn, args.query, limit=args.limit)
    elif args.hybrid:
        print("Using hybrid search...")
        results = search_hybrid(conn, args.query, limit=args.limit)
    else:
        print("Using vector search...")
        query_embedding = embed_text(args.query)
        results = search_vector(conn, query_embedding, limit=args.limit)

    format_results(results, args.query)
    conn.close()


if __name__ == "__main__":
    main()
