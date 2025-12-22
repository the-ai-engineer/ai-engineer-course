"""
Production Concerns

Streaming and async with the Gemini API.
"""

import asyncio

import nest_asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Allow nested event loops (needed for Jupyter/ipykernel)
nest_asyncio.apply()

# =============================================================================
# Client Configuration
# =============================================================================

# Default client - uses built-in retry logic
client = genai.Client()

# Client with custom timeout (in seconds)
# The SDK uses httpx, so you can pass httpx client args
client_with_timeout = genai.Client(
    http_options=types.HttpOptions(
        timeout=60.0,  # 60 second timeout
    )
)

# =============================================================================
# Streaming
# =============================================================================

# Streaming shows text as it's generated - better UX for chat interfaces

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a story.",
)
for chunk in response:
    print(chunk.text, end="")

# =============================================================================
# Async for Concurrent Calls
# =============================================================================


async def analyze_topic(topic: str) -> str:
    """Analyze a single topic."""
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Explain {topic} in one sentence.",
    )
    return response.text


async def concurrent_example():
    """Run multiple calls concurrently."""
    topics = ["REST APIs", "GraphQL", "WebSockets"]
    results = await asyncio.gather(*[analyze_topic(t) for t in topics])
    return results
