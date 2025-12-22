"""
Multi-Modal Inputs

Analyze images using Gemini's native multimodal capabilities.
Gemini supports images, audio, video, and PDFs in a unified API.
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

# Download image and create Part
image_data = httpx.get(image_url).content

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        types.Part.from_text("Describe what you see in this image in one sentence."),
        types.Part.from_bytes(data=image_data, mime_type="image/png"),
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
    model="gemini-3-flash-preview",
    contents=[
        types.Part.from_text("Analyze this image."),
        types.Part.from_bytes(data=image_data, mime_type="image/png"),
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
        ".gif": "image/gif",
    }
    mime_type = mime_types.get(path.suffix.lower(), "image/png")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_text(prompt),
            types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type),
        ],
    )
    return response.text


# Example: analyze_local_image("screenshot.png", "What's in this screenshot?")


# =============================================================================
# Generate Images with Imagen 4
# =============================================================================

# Available models:
#   - imagen-4.0-generate-001      (standard)
#   - imagen-4.0-ultra-generate-001 (highest quality)
#   - imagen-4.0-fast-generate-001  (fastest)


def generate_image(prompt: str, output_path: str = "generated.png") -> str:
    """Generate an image from a text prompt using Imagen 4."""
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
        ),
    )

    # Save the first generated image
    response.generated_images[0].image.save(output_path)
    return output_path


# Generate a simple image
# generate_image("A serene mountain landscape at sunset, photorealistic")

# Generate a product photo
# generate_image(
#     "Professional product photo of a modern laptop on a clean white desk, "
#     "soft studio lighting, minimalist style",
#     "laptop.png"
# )
