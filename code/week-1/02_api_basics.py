"""
Your First API Call

Basic Gemini API usage: simple calls, parameters, and system instructions.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# =============================================================================
# Simple Call
# =============================================================================

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain what an API is in one sentence.",
)

response.text

# =============================================================================
# Temperature
# =============================================================================

# Low = deterministic, High = creative

prompt = "Write a one-line tagline for a coffee shop."

# Temperature 0.0 - same output every time
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(temperature=0.0),
)
response.text

# Temperature 1.5 - varied, creative outputs
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(temperature=1.5),
)
response.text

# =============================================================================
# System Instructions
# =============================================================================

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the best programming language?",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant. Respond in exactly one sentence.",
        temperature=0.0,
    ),
)
response.text

# =============================================================================
# Max Output Tokens
# =============================================================================

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain machine learning.",
    config=types.GenerateContentConfig(max_output_tokens=30),
)
response.text
