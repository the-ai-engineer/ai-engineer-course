"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single search result."""

    chunk_id: int
    source: str
    content: str
    score: float


class PolicyResult(BaseModel):
    """A policy search result returned by the agent tool."""

    source: str
    content: str
    score: float


class RAGRequest(BaseModel):
    """RAG query request."""

    question: str
    limit: int = 5


class RAGResponse(BaseModel):
    """RAG response with answer and sources."""

    question: str
    answer: str
    sources: list[SearchResult]
