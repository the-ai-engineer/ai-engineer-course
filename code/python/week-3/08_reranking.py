"""
Reranking: Improving Retrieval Quality

Vector search returns results by embedding similarity, but similarity isn't
always relevance. Reranking adds a second pass that scores results against
the actual query using a more sophisticated model.

The pattern: Retrieve many → Rerank → Keep top few

Two approaches:
1. Dedicated reranker (Cohere) - fast, accurate, purpose-built
2. LLM-based reranking - flexible, no extra API, uses your existing model
"""

from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI()

# =============================================================================
# Sample Search Results (simulating vector search output)
# =============================================================================

# Imagine these came from your vector search. They're sorted by embedding
# similarity, but that doesn't mean they're in the best order for the query.

SAMPLE_RESULTS = [
    {
        "id": 1,
        "content": "To return an item, go to your orders page and click 'Return Item'. "
        "You have 30 days from delivery to initiate a return.",
        "source": "returns.md",
    },
    {
        "id": 2,
        "content": "Our return policy allows returns within 30 days of purchase. "
        "Items must be unused and in original packaging.",
        "source": "policy.md",
    },
    {
        "id": 3,
        "content": "For international orders, return shipping costs are the "
        "responsibility of the customer unless the item is defective.",
        "source": "international.md",
    },
    {
        "id": 4,
        "content": "Gift cards and final sale items cannot be returned. "
        "See our full policy for other exceptions.",
        "source": "exceptions.md",
    },
    {
        "id": 5,
        "content": "Track your return status in the Orders section of your account. "
        "Refunds are processed within 5-7 business days.",
        "source": "tracking.md",
    },
]

# =============================================================================
# Approach 1: Cohere Reranker (Recommended for Production)
# =============================================================================

# Cohere's rerank model is purpose-built for this task. It's fast and accurate.
# Uncomment and add your COHERE_API_KEY to use.

# import cohere
#
# co = cohere.Client()  # Uses COHERE_API_KEY env var
#
# def rerank_with_cohere(
#     query: str,
#     documents: list[dict],
#     top_n: int = 3,
# ) -> list[dict]:
#     """Rerank documents using Cohere's rerank model."""
#     results = co.rerank(
#         model="rerank-english-v3.0",
#         query=query,
#         documents=[doc["content"] for doc in documents],
#         top_n=top_n,
#     )
#     return [
#         {**documents[r.index], "rerank_score": r.relevance_score}
#         for r in results.results
#     ]


# =============================================================================
# Approach 2: LLM-Based Reranking
# =============================================================================

# Use your existing LLM to score relevance. More flexible, no extra API needed.
# Trade-off: slower and uses more tokens than dedicated rerankers.


class RelevanceScore(BaseModel):
    """Structured output for document relevance scoring."""

    score: int = Field(ge=1, le=10, description="Relevance score from 1-10")
    reason: str = Field(description="Brief explanation for the score")


def score_document(query: str, content: str) -> RelevanceScore:
    """Score a single document's relevance to the query."""
    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=(
            "Score how relevant this document is to answering the user's question. "
            "10 = directly answers the question, 1 = completely irrelevant. "
            "Be strict - only high scores for documents that actually help answer the question."
        ),
        input=f"Question: {query}\n\nDocument: {content}",
        text_format=RelevanceScore,
    )
    return response.output_parsed


def rerank_with_llm(
    query: str,
    documents: list[dict],
    top_n: int = 3,
) -> list[dict]:
    """Rerank documents using LLM-based scoring.

    Scores each document individually, then sorts by score.
    """
    scored = []
    for doc in documents:
        result = score_document(query, doc["content"])
        scored.append({
            **doc,
            "rerank_score": result.score,
            "rerank_reason": result.reason,
        })

    # Sort by score descending, return top_n
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_n]


# =============================================================================
# Approach 3: Batch LLM Reranking (More Efficient)
# =============================================================================

# Score all documents in one call. Faster but requires careful prompting.


class BatchRelevanceScores(BaseModel):
    """Scores for multiple documents."""

    scores: list[int] = Field(description="Relevance scores 1-10 for each document in order")


def rerank_with_llm_batch(
    query: str,
    documents: list[dict],
    top_n: int = 3,
) -> list[dict]:
    """Rerank documents using a single LLM call.

    More efficient than scoring one at a time.
    """
    # Format documents with indices
    docs_text = "\n\n".join(
        f"[Document {i+1}]: {doc['content']}"
        for i, doc in enumerate(documents)
    )

    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=(
            "Score each document's relevance to the question from 1-10. "
            "10 = directly answers the question, 1 = irrelevant. "
            "Return scores in the same order as the documents."
        ),
        input=f"Question: {query}\n\n{docs_text}",
        text_format=BatchRelevanceScores,
    )

    # Combine scores with documents
    scored = [
        {**doc, "rerank_score": score}
        for doc, score in zip(documents, response.output_parsed.scores)
    ]

    # Sort and return top_n
    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_n]


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    query = "How do I return a defective item?"

    print(f"Query: {query}")
    print(f"\n{'='*60}")
    print("Original order (by vector similarity):")
    print(f"{'='*60}")
    for i, doc in enumerate(SAMPLE_RESULTS, 1):
        print(f"{i}. [{doc['source']}] {doc['content'][:60]}...")

    print(f"\n{'='*60}")
    print("After LLM reranking (individual scoring):")
    print(f"{'='*60}")
    reranked = rerank_with_llm(query, SAMPLE_RESULTS, top_n=3)
    for i, doc in enumerate(reranked, 1):
        print(f"{i}. [Score: {doc['rerank_score']}/10] [{doc['source']}]")
        print(f"   {doc['content'][:60]}...")
        print(f"   Reason: {doc['rerank_reason']}")

    print(f"\n{'='*60}")
    print("After LLM reranking (batch scoring):")
    print(f"{'='*60}")
    reranked_batch = rerank_with_llm_batch(query, SAMPLE_RESULTS, top_n=3)
    for i, doc in enumerate(reranked_batch, 1):
        print(f"{i}. [Score: {doc['rerank_score']}/10] [{doc['source']}]")
        print(f"   {doc['content'][:60]}...")
