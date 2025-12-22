"""
Workflows

Multi-step AI pipelines: sequential, parallel, and conditional patterns.
"""

import asyncio
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# =============================================================================
# Sequential Workflow
# =============================================================================


def summarize(text: str) -> str:
    """Step 1: Summarize the text."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Summarize in 2-3 sentences:\n\n{text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return response.text


def extract_keywords(text: str) -> list[str]:
    """Step 2: Extract keywords."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Extract 5 keywords, comma-separated:\n\n{text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return [k.strip() for k in response.text.split(",")]


def generate_title(summary: str, keywords: list[str]) -> str:
    """Step 3: Generate a title."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Generate a short title.\nSummary: {summary}\nKeywords: {keywords}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return response.text.strip()


def sequential_workflow(article: str) -> dict:
    """Run steps in sequence, each feeding into the next."""
    summary = summarize(article)
    keywords = extract_keywords(article)
    title = generate_title(summary, keywords)

    return {
        "title": title,
        "summary": summary,
        "keywords": keywords,
    }


# =============================================================================
# Parallel Workflow
# =============================================================================


async def async_summarize(text: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Summarize in 2-3 sentences:\n\n{text}",
    )
    return response.text


async def async_sentiment(text: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Analyze sentiment (positive/negative/neutral):\n\n{text}",
    )
    return response.text.strip().lower()


async def async_keywords(text: str) -> list[str]:
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Extract 5 keywords, comma-separated:\n\n{text}",
    )
    return [k.strip() for k in response.text.split(",")]


async def parallel_workflow(text: str) -> dict:
    """Run independent steps in parallel for speed."""
    summary, sentiment, keywords = await asyncio.gather(
        async_summarize(text),
        async_sentiment(text),
        async_keywords(text),
    )

    return {
        "summary": summary,
        "sentiment": sentiment,
        "keywords": keywords,
    }


# =============================================================================
# Conditional Workflow
# =============================================================================


def classify_email(email: str) -> str:
    """Classify email type."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""Classify this email as exactly one of: support, sales, spam

Email:
{email}

Category:""",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return response.text.strip().lower()


def handle_support(email: str) -> str:
    """Generate support response."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Draft a helpful support response:\n\n{email}",
    )
    return response.text


def handle_sales(email: str) -> str:
    """Generate sales follow-up."""
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Draft a sales follow-up response:\n\n{email}",
    )
    return response.text


def conditional_workflow(email: str) -> dict:
    """Route based on classification."""
    category = classify_email(email)

    if category == "support":
        response = handle_support(email)
        action = "respond"
    elif category == "sales":
        response = handle_sales(email)
        action = "forward_to_sales"
    else:
        response = None
        action = "discard"

    return {
        "category": category,
        "action": action,
        "response": response,
    }


# =============================================================================
# Structured Workflow with Pydantic
# =============================================================================


class ProcessedDocument(BaseModel):
    original: str
    summary: str
    keywords: list[str]
    sentiment: str
    title: str


def structured_workflow(text: str) -> ProcessedDocument:
    """Full workflow returning a structured result."""
    summary = summarize(text)
    keywords = extract_keywords(text)
    title = generate_title(summary, keywords)

    # Get sentiment separately
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Sentiment (positive/negative/neutral): {text[:500]}",
    )
    sentiment = response.text.strip().lower()

    return ProcessedDocument(
        original=text,
        summary=summary,
        keywords=keywords,
        sentiment=sentiment,
        title=title,
    )


# =============================================================================
# Example Usage
# =============================================================================

article = """
Artificial intelligence is transforming healthcare in unprecedented ways.
From diagnostic imaging to drug discovery, AI systems are helping doctors
make faster, more accurate decisions. Recent studies show AI can detect
certain cancers earlier than human radiologists. However, challenges remain
around data privacy, algorithmic bias, and the need for human oversight.
"""

# Sequential
result = sequential_workflow(article)
result

# Parallel (in notebook: await parallel_workflow(article))
# asyncio.run(parallel_workflow(article))

# Conditional
email = "Hi, I'm having trouble logging into my account. Can you help?"
result = conditional_workflow(email)
result

# Structured
doc = structured_workflow(article)
doc
