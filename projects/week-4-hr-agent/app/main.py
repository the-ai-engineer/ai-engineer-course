"""FastAPI application for HR Policy Agent."""

from fastapi import FastAPI

from app.database import get_connection, get_stats
from app.models import (
    SearchRequest,
    SearchResponse,
    RAGRequest,
    RAGResponse,
    StatsResponse,
)
from app.search import search
from app.agent import ask_agent


app = FastAPI(
    title="HR Policy Agent API",
    description="AI-powered HR policy assistant with document search",
    version="1.0.0",
)


# =============================================================================
# Health & Stats
# =============================================================================


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/stats", response_model=StatsResponse)
def stats():
    """Get database statistics."""
    with get_connection() as conn:
        return get_stats(conn)


# =============================================================================
# Search
# =============================================================================


@app.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    """Search documents.

    Search types:
    - vector: Semantic similarity search
    - keyword: Full-text keyword search
    - hybrid: Combines vector and keyword with RRF (default)
    """
    with get_connection() as conn:
        results = search(
            conn,
            query=request.query,
            limit=request.limit,
            search_type=request.search_type,
        )

    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
    )


# =============================================================================
# Ask
# =============================================================================


@app.post("/ask", response_model=RAGResponse)
def ask_question(request: RAGRequest):
    """Ask the HR Policy Agent a question.

    Uses PydanticAI agent with RAG to find relevant
    policies and generate an answer.
    """
    answer, sources = ask_agent(
        question=request.question,
        search_limit=request.limit,
        search_type=request.search_type,
    )

    return RAGResponse(
        question=request.question,
        answer=answer,
        sources=sources,
    )
