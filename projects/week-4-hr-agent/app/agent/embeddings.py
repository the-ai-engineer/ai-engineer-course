"""Embedding generation using OpenAI."""

from openai import OpenAI

from app.config import get_settings

settings = get_settings()

_client = OpenAI()


def embed_query(text: str) -> list[float]:
    """Generate embedding for a search query."""
    response = _client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    return response.data[0].embedding
