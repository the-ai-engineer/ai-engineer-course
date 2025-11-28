"""
Lesson 2: API Basics

Now that your environment is set up, let's make your first API calls.

This lesson covers:
- Creating a client
- Making basic API calls
- Using system prompts (instructions)
- Understanding the response object

Note: The OpenAI client has built-in retries for transient errors
(rate limits, timeouts, etc.). You don't need to add retry logic yourself.
"""

from openai import OpenAI

# =============================================================================
# Creating the Client
# =============================================================================

# The client reads OPENAI_API_KEY from your environment automatically.
# No need to pass it explicitly (and you shouldn't - keep it in env vars!)
client = OpenAI()

# =============================================================================
# Example 1: Basic API Call
# =============================================================================

response = client.responses.create(
    model="gpt-5-mini",
    input="What is the capital of the UK?",
)

print("Example 1: Basic call")
print(f"Response: {response.output_text}")
print()

# =============================================================================
# Example 2: Using System Prompts (instructions)
# =============================================================================

# The `instructions` parameter sets the system prompt.
# This tells the model how to behave.

response2 = client.responses.create(
    model="gpt-5-mini",
    instructions="Speak like a pirate",
    input="What is the capital of the UK?",
)

print("Example 2: With system prompt")
print(f"Response: {response2.output_text}")
print()

# =============================================================================
# Example 3: Examining the Response Object
# =============================================================================

# The response object contains useful information beyond just the text.

response3 = client.responses.create(
    model="gpt-5-mini",
    input="Say hello in exactly 3 words.",
)

print("Example 3: Response object")
print(f"Output text: {response3.output_text}")
print(f"Model used: {response3.model}")
print(f"Response ID: {response3.id}")

# You can also see the full response structure:
# print(response3.model_dump())
