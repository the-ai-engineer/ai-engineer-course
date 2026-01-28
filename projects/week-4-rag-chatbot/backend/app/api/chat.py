"""Chat endpoint with SSE streaming and intent-based routing."""

import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.agent.agent import AgentDeps, rag_agent
from app.agent.router import QueryIntent, classify_query
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter()

OFF_TOPIC_RESPONSE = (
    "I'm a customer support assistant and can only help with questions about "
    "orders, shipping, returns, payments, and our products. "
    "Is there something I can help you with in those areas?"
)


async def stream_response(message: str) -> AsyncIterator[dict]:
    """Stream chat response tokens as SSE events.

    Args:
        message: The user's question.

    Yields:
        SSE events with tokens and final sources.
    """
    logger.info(f"[CHAT] Starting stream for message: {message!r}")

    # Classify query intent before searching
    classification = classify_query(message)

    if classification.intent == QueryIntent.OFF_TOPIC:
        logger.info(f"[CHAT] Query classified as off-topic: {classification.reason}")
        yield {"event": "token", "data": json.dumps({"content": OFF_TOPIC_RESPONSE})}
        yield {"event": "done", "data": json.dumps({"sources": []})}
        return

    # Proceed with RAG for customer support queries
    response_chunks: list[str] = []
    deps = AgentDeps()

    try:
        async with rag_agent.run_stream(message, deps=deps) as response:
            async for chunk in response.stream_text(delta=True):
                response_chunks.append(chunk)
                yield {"event": "token", "data": json.dumps({"content": chunk})}

        full_response = "".join(response_chunks)
        logger.info(f"[CHAT] Stream complete. Response length: {len(full_response)}, Sources: {len(deps.sources)}")
        yield {
            "event": "done",
            "data": json.dumps({
                "sources": [
                    {"source": s["source"], "content": s["content"], "score": s["score"]}
                    for s in deps.sources
                ],
            }),
        }
    except Exception as e:
        logger.exception(f"[CHAT] Error during streaming: {e}")
        yield {"event": "error", "data": json.dumps({"error": str(e)})}


@router.post("/chat")
async def chat(request: ChatRequest):
    """Streaming chat endpoint using Server-Sent Events.

    Accepts a question and streams back the response token-by-token,
    followed by a final event containing source citations.
    """
    return EventSourceResponse(stream_response(request.message))
