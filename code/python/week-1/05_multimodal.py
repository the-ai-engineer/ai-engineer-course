"""
Multi-Modal Inputs

Analyze images using OpenAI's vision capabilities.
"""

import base64
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Analyze Image from URL
# =============================================================================

image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/300px-PNG_transparency_demonstration_1.png"

response = client.responses.create(
    model="gpt-5-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Describe what you see in this image."},
                {"type": "input_image", "image_url": image_url},
            ],
        }
    ],
)

response.output_text


# =============================================================================
# Structured Image Analysis
# =============================================================================


class ImageAnalysis(BaseModel):
    description: str
    objects: list[str]
    colors: list[str]


response = client.responses.create(
    model="gpt-5-mini",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Analyze this image."},
                {"type": "input_image", "image_url": image_url},
            ],
        }
    ],
    text={
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "image_analysis",
                "schema": ImageAnalysis.model_json_schema(),
            },
        }
    },
)

analysis = ImageAnalysis.model_validate_json(response.output_text)
analysis


# =============================================================================
# Analyze Local Image (Base64)
# =============================================================================


def analyze_local_image(image_path: str, prompt: str) -> str:
    """Analyze a local image file using base64 encoding."""
    path = Path(image_path)
    if not path.exists():
        return f"Image not found: {image_path}"

    # Encode image as base64 data URL
    image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    data_url = f"data:image/png;base64,{image_data}"

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    return response.output_text


# Usage: analyze_local_image("screenshot.png", "What's in this screenshot?")
