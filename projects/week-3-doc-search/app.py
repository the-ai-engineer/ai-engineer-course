"""Chainlit chat interface for document search."""

import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"


def embed_query(text: str) -> list[float]:
    """Generate embedding for a search query."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def vector_search(query: str, limit: int = 5) -> list[dict]:
    """Search using vector similarity."""
    query_embedding = embed_query(query)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM vector_search(%s::vector, %s::int)",
            (query_embedding, limit),
        ).fetchall()
    return [{"id": r[0], "source": r[1], "content": r[2], "score": r[3]} for r in rows]


def keyword_search(query: str, limit: int = 5) -> list[dict]:
    """Search using full-text search."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM keyword_search(%s::text, %s::int)",
            (query, limit),
        ).fetchall()
    return [{"id": r[0], "source": r[1], "content": r[2], "score": r[3]} for r in rows]


def hybrid_search_with_provenance(query: str, limit: int = 5) -> list[dict]:
    """Search using both methods and track which found each result."""
    vector_results = vector_search(query, limit * 2)
    keyword_results = keyword_search(query, limit * 2)

    vector_ids = {r["id"] for r in vector_results}
    keyword_ids = {r["id"] for r in keyword_results}

    # Combine with RRF scoring
    scores = {}
    all_results = {}
    k = 60  # RRF constant

    for rank, r in enumerate(vector_results, 1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)
        all_results[r["id"]] = r

    for rank, r in enumerate(keyword_results, 1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)
        all_results[r["id"]] = r

    # Sort by combined score and add provenance
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:limit]

    results = []
    for id in sorted_ids:
        r = all_results[id]
        in_vector = id in vector_ids
        in_keyword = id in keyword_ids

        if in_vector and in_keyword:
            provenance = "both"
        elif in_vector:
            provenance = "vector"
        else:
            provenance = "keyword"

        results.append({
            "id": r["id"],
            "source": r["source"],
            "content": r["content"],
            "score": scores[id],
            "found_by": provenance,
        })

    return results


def generate_answer(query: str, results: list[dict]) -> str:
    """Generate answer using RAG."""
    if not results:
        return "I couldn't find any relevant information in the documents."

    context = "\n\n---\n\n".join(
        f"[Source: {r['source'].split('/')[-1]}]\n{r['content']}" for r in results
    )

    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't have information about that."
Quote relevant passages and cite sources.""",
        input=f"Context:\n{context}\n\nQuestion: {query}",
    )
    return response.output_text


@cl.on_chat_start
async def start():
    """Send welcome message."""
    await cl.Message(
        content="Hi! Ask me questions about Nike's 2025 Annual Report. Try: 'What was Nike's revenue?' or 'Who is the CEO?'"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages."""
    query = message.content

    # Show thinking indicator
    msg = cl.Message(content="")
    await msg.send()

    # Search and generate answer
    results = hybrid_search_with_provenance(query, limit=5)
    answer = generate_answer(query, results)

    # Update message with answer
    msg.content = answer
    await msg.update()

    # Show sources with provenance
    if results:
        sources = "\n".join(
            f"- {r['source'].split('/')[-1]} [{r['found_by']}]"
            for r in results[:5]
        )
        await cl.Message(content=f"**Sources:**\n{sources}").send()
