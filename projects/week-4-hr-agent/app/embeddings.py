"""Embedding generation using Gemini."""

from google import genai
from google.genai import types

from app.config import get_settings

settings = get_settings()
client = genai.Client()


def embed_query(text: str) -> list[float]:
    """Generate embedding for a search query.

    Uses RETRIEVAL_QUERY task type optimized for searching.
    """
    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=settings.embedding_dimensions,
        ),
    )
    return response.embeddings[0].values
