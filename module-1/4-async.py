"""
Async and Parallel LLM Calls

Key concept: Use asyncio.gather to run multiple LLM calls in parallel.
This is much faster than calling them one at a time.
"""

import asyncio
import time
from openai import AsyncOpenAI

client = AsyncOpenAI()


async def call_llm(message: str) -> str:
    """Single async LLM call."""
    response = await client.responses.create(
        model="gpt-5-mini",
        input=message,
    )
    return response.output_text


async def main():
    questions = [
        "What is Python?",
        "What is JavaScript?",
        "What is Rust?",
    ]

    # Sequential - one at a time (slow)
    print("Sequential (one at a time)...")
    start = time.time()
    for q in questions:
        await call_llm(q)
    sequential_time = time.time() - start
    print(f"Time: {sequential_time:.2f}s")

    # Parallel - all at once (fast)
    print("\nParallel (all at once)...")
    start = time.time()
    results = await asyncio.gather(*[call_llm(q) for q in questions])
    parallel_time = time.time() - start
    print(f"Time: {parallel_time:.2f}s")

    # Result
    speedup = sequential_time / parallel_time
    print(f"\nSpeedup: {speedup:.1f}x faster")


if __name__ == "__main__":
    asyncio.run(main())
