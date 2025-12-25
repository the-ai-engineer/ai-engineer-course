"""
Your First API Call

Basic OpenAI Responses API usage: client setup, simple calls, and system instructions.
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Client Setup
# =============================================================================

# The OpenAI client uses OPENAI_API_KEY from environment by default
# Get your API key at: https://platform.openai.com/api-keys

client = OpenAI()

# You can also pass the API key explicitly:
# client = OpenAI(api_key="sk-...")

# For Azure OpenAI, use the same client with a custom base_url:
# endpoint = "https://your-resource.openai.azure.com/openai/v1/"
# client = OpenAI(
#     base_url=endpoint,
#     api_key="your-azure-key",
# )

# =============================================================================
# Simple Call
# =============================================================================

# The Responses API is OpenAI's most advanced interface
# Use client.responses.create() instead of chat.completions.create()

response = client.responses.create(
    model="gpt-5-mini",
    input="Explain what an API is in one sentence.",
)

response.output_text

# =============================================================================
# System Instructions
# =============================================================================

# Use `instructions` for system-level guidance (replaces system messages)

response = client.responses.create(
    model="gpt-5-mini",
    input="What's the best programming language?",
    instructions="You are a helpful assistant. Respond in exactly one sentence.",
    temperature=0.0,
)

response.output_text
