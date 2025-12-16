"""
Production Concerns

Streaming, async, and error handling with retry.
"""

import asyncio
import time
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

client = genai.Client()

# =============================================================================
# Streaming
# =============================================================================

# Streaming shows text as it's generated - better UX for chat interfaces

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a haiku about coding.",
):
    print(chunk.text, end="", flush=True)

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


# In a notebook, use: await concurrent_example()
# In a script, use: asyncio.run(concurrent_example())

# =============================================================================
# Retry with Exponential Backoff
# =============================================================================


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
)
def robust_call(prompt: str) -> str:
    """API call with automatic retry on transient failures."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


# =============================================================================
# Error Handling
# =============================================================================


def safe_call(prompt: str) -> tuple[str | None, str | None]:
    """API call with error handling. Returns (result, error)."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0),
        )
        return response.text, None

    except google_exceptions.ResourceExhausted:
        return None, "Rate limited. Retry with backoff."

    except google_exceptions.InvalidArgument as e:
        return None, f"Invalid request: {e}"

    except Exception as e:
        return None, f"Unexpected error: {e}"


result, error = safe_call("What is 2 + 2?")
result
