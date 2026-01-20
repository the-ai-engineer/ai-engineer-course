"""Chat request and response schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str


class Source(BaseModel):
    """A source document used in a response."""

    source: str
    content: str
    score: float
