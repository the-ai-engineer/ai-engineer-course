"""Chat request and response schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's question or message",
    )


class Source(BaseModel):
    """A source document used in a response."""

    source: str
    content: str
    score: float
