"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request."""

    message: str
    limit: int = 5


class ChatResponse(BaseModel):
    """Chat response with answer and sources."""

    message: str
    response: str
    sources: list[dict]


class StatsResponse(BaseModel):
    """Database statistics response."""

    chunks: int
