"""API routes."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.agent import ask
from app.database import get_connection, get_stats
from app.models import ChatRequest, ChatResponse, StatsResponse

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@router.get("/", response_class=HTMLResponse)
def chat_ui():
    """Serve the chat interface."""
    return (TEMPLATES_DIR / "chat.html").read_text()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/stats", response_model=StatsResponse)
def stats():
    """Get database statistics."""
    with get_connection() as conn:
        return get_stats(conn)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat with the support agent."""
    answer, sources = ask(request.message, search_limit=request.limit)
    return ChatResponse(
        message=request.message,
        response=answer,
        sources=sources,
    )
