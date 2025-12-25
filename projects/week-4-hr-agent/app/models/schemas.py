"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field


# =============================================================================
# Search
# =============================================================================


class SearchRequest(BaseModel):
    """Search request parameters."""

    query: str
    limit: int = 5
    search_type: str = "hybrid"  # vector, keyword, hybrid


class SearchResult(BaseModel):
    """A single search result."""

    chunk_id: int
    source: str
    content: str
    metadata: dict = Field(default_factory=dict)
    score: float


class SearchResponse(BaseModel):
    """Search response with results."""

    query: str
    results: list[SearchResult]
    total: int


# =============================================================================
# Agent Tool Response
# =============================================================================


class PolicyResult(BaseModel):
    """A policy search result returned by the agent tool."""

    source: str
    content: str
    score: float


# =============================================================================
# RAG
# =============================================================================


class RAGRequest(BaseModel):
    """RAG query request."""

    question: str
    limit: int = 5
    search_type: str = "hybrid"


class RAGResponse(BaseModel):
    """RAG response with answer and sources."""

    question: str
    answer: str
    sources: list[SearchResult]


# =============================================================================
# Stats
# =============================================================================


class StatsResponse(BaseModel):
    """Database statistics response."""

    chunks: int
