"""
Multi-Modal Inputs

Analyze and generate images using OpenAI's multimodal capabilities.
"""

import base64
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path

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
                {"type": "input_text", "text": "Describe what you see in this image in one sentence."},
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

    # Encode image as base64
    image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    data_url = f"data:{mime_type};base64,{image_data}"

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


# Example: analyze_local_image("screenshot.png", "What's in this screenshot?")


# =============================================================================
# Image Classification
# =============================================================================


class ImageClassification(BaseModel):
    category: str
    confidence: str
    reasoning: str


def classify_image(image_url: str, categories: list[str]) -> ImageClassification:
    """Classify an image into one of the provided categories."""
    categories_str = ", ".join(categories)

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Classify this image into one of these categories: {categories_str}",
                    },
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "image_classification",
                    "schema": ImageClassification.model_json_schema(),
                },
            }
        },
    )
    return ImageClassification.model_validate_json(response.output_text)


# Example usage:
# result = classify_image(
#     "https://example.com/photo.jpg",
#     ["landscape", "portrait", "product", "document", "screenshot"]
# )


# =============================================================================
# Generate Images with GPT-Image-1
# =============================================================================


def generate_image(prompt: str, output_path: str = "generated.png") -> str:
    """Generate an image from a text prompt using GPT-Image-1."""
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
    )

    # Get the image URL or base64 data
    image_data = response.data[0]

    if image_data.b64_json:
        # Save base64 image
        import base64
        image_bytes = base64.b64decode(image_data.b64_json)
        Path(output_path).write_bytes(image_bytes)
    elif image_data.url:
        # Download from URL
        image_bytes = httpx.get(image_data.url).content
        Path(output_path).write_bytes(image_bytes)

    return output_path


# Generate a simple image
# generate_image("A serene mountain landscape at sunset, photorealistic")

# Generate a product photo
# generate_image(
#     "Professional product photo of a modern laptop on a clean white desk, "
#     "soft studio lighting, minimalist style",
#     "laptop.png"
# )


# =============================================================================
# Edit Images with GPT-Image-1
# =============================================================================


def edit_image(
    image_path: str,
    prompt: str,
    output_path: str = "edited.png",
    mask_path: str | None = None,
) -> str:
    """Edit an existing image based on a text prompt."""
    with open(image_path, "rb") as image_file:
        kwargs = {
            "model": "gpt-image-1",
            "image": image_file,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        if mask_path:
            with open(mask_path, "rb") as mask_file:
                kwargs["mask"] = mask_file
                response = client.images.edit(**kwargs)
        else:
            response = client.images.edit(**kwargs)

    # Save the edited image
    image_data = response.data[0]
    if image_data.b64_json:
        image_bytes = base64.b64decode(image_data.b64_json)
        Path(output_path).write_bytes(image_bytes)
    elif image_data.url:
        image_bytes = httpx.get(image_data.url).content
        Path(output_path).write_bytes(image_bytes)

    return output_path


# Example: edit_image("photo.png", "Add a sunset sky in the background")
