"""
Setup Verification - Run to confirm your environment works.

Usage: uv run python 1-setup.py
"""

import os

from openai import OpenAI


def verify():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[FAIL] OPENAI_API_KEY not set")
        return

    print("[OK] API key found")

    client = OpenAI()
    response = client.responses.create(
        model="gpt-5-mini",
        input="Say 'Hello' and nothing else.",
    )
    print(f"[OK] API working: {response.output_text}")


if __name__ == "__main__":
    verify()
