"""FastAPI route definitions."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.agent import ask_agent, embed_query
from app.db import get_connection, get_stats
from app.models import (
    RAGRequest,
    RAGResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    StatsResponse,
)

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

router = APIRouter()


# =============================================================================
# UI
# =============================================================================


@router.get("/", response_class=HTMLResponse)
def chat_ui():
    """Serve the chat interface."""
    return (TEMPLATES_DIR / "chat.html").read_text()


# =============================================================================
# Health & Stats
# =============================================================================


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/stats", response_model=StatsResponse)
def stats():
    """Get database statistics."""
    with get_connection() as conn:
        return get_stats(conn)


# =============================================================================
# Search
# =============================================================================


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    """Search documents.

    Search types:
    - vector: Semantic similarity search
    - keyword: Full-text keyword search
    - hybrid: Combines vector and keyword with RRF (default)
    """
    with get_connection() as conn:
        if request.search_type == "vector":
            query_embedding = embed_query(request.query)
            rows = conn.execute(
                "SELECT * FROM vector_search(%s::vector, %s::int)",
                (query_embedding, request.limit),
            ).fetchall()

        elif request.search_type == "keyword":
            rows = conn.execute(
                "SELECT * FROM keyword_search(%s::text, %s::int)",
                (request.query, request.limit),
            ).fetchall()

        else:  # hybrid
            query_embedding = embed_query(request.query)
            rows = conn.execute(
                "SELECT * FROM hybrid_search(%s::text, %s::vector, %s::int)",
                (request.query, query_embedding, request.limit),
            ).fetchall()

    results = [
        SearchResult(
            chunk_id=row[0],
            source=row[1],
            content=row[2],
            metadata=row[3] or {},
            score=row[4],
        )
        for row in rows
    ]

    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
    )


# =============================================================================
# Ask
# =============================================================================


@router.post("/ask", response_model=RAGResponse)
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
