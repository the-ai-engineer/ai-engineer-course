"""
Image Generation

Generate images using OpenAI's gpt-image-1 model.
"""

import base64
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Generate an Image
# =============================================================================

prompt = """
A children's book drawing of a veterinarian using a stethoscope
to listen to the heartbeat of a baby otter.
"""

result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("otter.png", "wb") as f:
    f.write(image_bytes)


# =============================================================================
# Generate with Options
# =============================================================================


def generate_image(prompt: str, output_path: str = "generated.png", size: str = "1024x1024") -> Path:
    """Generate an image and save it to a file.

    Args:
        prompt: Text description of the image to generate.
        output_path: Where to save the generated image.
        size: Image size (1024x1024, 1536x1024, or 1024x1536).

    Returns:
        Path to the saved image.
    """
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)
    path = Path(output_path)
    path.write_bytes(image_bytes)

    return path


# Usage:
# generate_image("A sunset over mountains, watercolor style", "sunset.png")
# generate_image("Product photo of headphones on white background", "headphones.png", "1536x1024")
