"""
Your First API Call

Basic Gemini API usage: client setup, simple calls, and system instructions.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Client Setup
# =============================================================================

# Option 1: Google AI Studio (direct API)
# Best for: learning, prototyping
# Get your API key at: https://aistudio.google.com/apikey

client = genai.Client()  # Uses GEMINI_API_KEY from environment

# Option 2: Vertex AI (Google Cloud)
# Best for: production
# Requires: Google Cloud project with Vertex AI API enabled
#
# Authentication uses Application Default Credentials (ADC):
#   - Local dev: run `gcloud auth application-default login`
#   - Production: uses attached service account automatically (Cloud Run, GCE, GKE)
#   - Service account key: set GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# client = genai.Client(
#     vertexai=True,
#     project="your-gcp-project-id",
#     location="us-central1",
# )

# The API is identical after setup - same code works with both.

# =============================================================================
# Simple Call
# =============================================================================

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain what an API is in one sentence.",
)

response.text

# =============================================================================
# System Instructions
# =============================================================================

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What's the best programming language?",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant. Respond in exactly one sentence.",
        temperature=0.0,
    ),
)

response.text
