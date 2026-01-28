"""Intent-based query router using structured output."""

import logging
from enum import Enum

from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

client = OpenAI()


class QueryIntent(str, Enum):
    """Supported query intents."""

    CUSTOMER_SUPPORT = "customer_support"
    OFF_TOPIC = "off_topic"


class QueryClassification(BaseModel):
    """Structured output for query classification."""

    intent: QueryIntent = Field(
        description="The classified intent of the user's query"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )
    reason: str = Field(
        description="Brief explanation for the classification"
    )


CLASSIFICATION_PROMPT = """Classify the user's query intent.

CUSTOMER_SUPPORT: Questions about e-commerce, orders, shipping, returns, refunds,
payments, products, account issues, or general customer service topics.

OFF_TOPIC: Questions unrelated to customer support, such as general knowledge,
politics, celebrities, science, math, coding help, or personal advice.

Be strict - only classify as CUSTOMER_SUPPORT if clearly related to shopping or service issues."""


def classify_query(query: str) -> QueryClassification:
    """Classify a user query to determine routing.

    Args:
        query: The user's input query.

    Returns:
        QueryClassification with intent, confidence, and reason.
    """
    logger.info(f"[ROUTER] Classifying query: {query!r}")

    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=CLASSIFICATION_PROMPT,
        input=f"Query: {query}",
        text_format=QueryClassification,
    )

    classification = response.output_parsed
    logger.info(
        f"[ROUTER] Classification: intent={classification.intent}, "
        f"confidence={classification.confidence:.2f}, reason={classification.reason!r}"
    )

    return classification
