"""
Multi-Modal Inputs

Analyze images using Gemini's vision capabilities.
"""

import httpx
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path

load_dotenv()

client = genai.Client()

# =============================================================================
# Analyze Image from URL
# =============================================================================

image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png"
image_data = httpx.get(image_url).content

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=image_data, mime_type="image/png"),
        "Describe what you see in this image in one sentence.",
    ],
)
response.text

# =============================================================================
# Structured Image Analysis
# =============================================================================


class ImageAnalysis(BaseModel):
    description: str
    objects: list[str]
    colors: list[str]


response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=image_data, mime_type="image/png"),
        "Analyze this image.",
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ImageAnalysis,
    ),
)

analysis = ImageAnalysis.model_validate_json(response.text)
analysis

# =============================================================================
# Analyze Local Image
# =============================================================================


def analyze_local_image(image_path: str, prompt: str) -> str:
    """Analyze a local image file."""
    path = Path(image_path)
    if not path.exists():
        return f"Image not found: {image_path}"

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(path.suffix.lower(), "image/png")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type),
            prompt,
        ],
    )
    return response.text


# Example: analyze_local_image("screenshot.png", "What's in this screenshot?")
