"""
Introduction to the OpenAI API

This lesson covers:
- Creating a client
- Making basic API calls
- Using system prompts (instructions)

Note: The OpenAI client has built-in retries for transient errors
(rate limits, timeouts, etc.). You don't need to add retry logic yourself.
"""

from openai import OpenAI

# Ensure you have OPENAI_API_KEY environment variable set.
client = OpenAI()

response = client.responses.create(
    model="gpt-5-mini",
    input="What is the capital of the UK?",
)

print(response.output_text)

# Example 2: Using instructions (system prompt)
response2 = client.responses.create(
    model="gpt-5-mini",
    instructions="Speak like a pirate",
    input="What is the capital of the UK?",
)

print(response2.output_text)
