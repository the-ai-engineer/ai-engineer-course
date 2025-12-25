"""
Production Concerns

Streaming and async with the OpenAI Responses API.
"""

import asyncio
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Client Configuration
# =============================================================================

# Default client (2 retries with exponential backoff built-in)
client = OpenAI()

# Client with custom timeout and retries
client_custom = OpenAI(
    timeout=60.0,  # 60 second timeout for requests
    max_retries=5,  # Retry up to 5 times (default is 2)
)

# Disable retries entirely (for testing or when you handle retries yourself)
client_no_retry = OpenAI(
    max_retries=0,
)

# Async client for concurrent operations
async_client = AsyncOpenAI(
    max_retries=3,
)

# =============================================================================
# Streaming
# =============================================================================

# Streaming shows text as it's generated - better UX for chat interfaces

stream = client.responses.create(
    model="gpt-5-mini",
    input="Write a short story about a robot.",
    stream=True,
)

for event in stream:
    # Events contain different types of data as the response streams
    print(event)

# =============================================================================
# Async for Concurrent Calls
# =============================================================================


async def analyze_topic(topic: str) -> str:
    """Analyze a single topic."""
    response = await async_client.responses.create(
        model="gpt-5-mini",
        input=f"Explain {topic} in one sentence.",
    )
    return response.output_text


async def concurrent_example():
    """Run multiple calls concurrently."""
    topics = ["REST APIs", "GraphQL", "WebSockets"]
    results = await asyncio.gather(*[analyze_topic(t) for t in topics])
    return results


# Run: asyncio.run(concurrent_example())

# =============================================================================
# Multi-turn Conversations
# =============================================================================

# OpenAI provides multiple ways to manage conversation state:
# 1. previous_response_id - Chain responses together (OpenAI stores context)
# 2. Manual message history - Build your own history array (full control)


def chat_with_previous_id():
    """Use previous_response_id to chain responses (OpenAI manages state)."""
    # First message
    response1 = client.responses.create(
        model="gpt-5-mini",
        input="My name is Alice and I'm learning Python.",
        instructions="You are a helpful programming tutor.",
    )
    print(f"Assistant: {response1.output_text}\n")

    # Follow-up using previous_response_id
    response2 = client.responses.create(
        model="gpt-5-mini",
        input="What should I learn first?",
        previous_response_id=response1.id,
    )
    print(f"Assistant: {response2.output_text}\n")

    return response2


def chat_with_manual_history():
    """Manually manage conversation history (you control the state)."""
    history = [
        {"role": "user", "content": "My name is Alice and I'm learning Python."}
    ]

    # First response
    response1 = client.responses.create(
        model="gpt-5-mini",
        input=history,
        instructions="You are a helpful programming tutor.",
        store=False,  # Don't store on OpenAI's servers
    )
    print(f"Assistant: {response1.output_text}\n")

    # Add assistant response to history
    history.append({"role": "assistant", "content": response1.output_text})

    # Add next user message
    history.append({"role": "user", "content": "What should I learn first?"})

    # Second response with full history
    response2 = client.responses.create(
        model="gpt-5-mini",
        input=history,
        instructions="You are a helpful programming tutor.",
        store=False,
    )
    print(f"Assistant: {response2.output_text}\n")

    return response2, history


# chat_with_previous_id()
# chat_with_manual_history()
