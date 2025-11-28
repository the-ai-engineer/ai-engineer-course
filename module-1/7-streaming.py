"""
Streaming Responses

Key concept: stream=True shows text as it generates, not all at once.
This makes your app feel faster and more responsive.
"""

from openai import OpenAI

client = OpenAI()

# =============================================================================
# Basic Streaming
# =============================================================================

print("Streaming response:")
print("-" * 40)

stream = client.responses.create(
    model="gpt-5-mini",
    input="Write a haiku about coding.",
    stream=True,
)

# Print each chunk as it arrives
full_response = ""
for event in stream:
    if hasattr(event, "delta") and event.delta:
        print(event.delta, end="", flush=True)
        full_response += event.delta

print("\n" + "-" * 40)
print(f"Complete response: {len(full_response)} characters")
