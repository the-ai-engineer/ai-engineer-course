"""
Query Routing: Intent-Based RAG

Not every question needs RAG. Before searching your knowledge base, classify
the query to determine if it's even relevant. This saves compute, reduces
latency, and improves user experience for off-topic questions.

This pattern is called "query routing" or "intent classification."
"""

from enum import Enum

from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI()

# =============================================================================
# Define Query Intents
# =============================================================================

# Use an enum for type safety. Add intents as your system grows.


class QueryIntent(str, Enum):
    """Possible intents for incoming queries."""

    KNOWLEDGE_BASE = "knowledge_base"  # Needs RAG search
    OFF_TOPIC = "off_topic"  # Outside our domain
    GREETING = "greeting"  # "Hi", "Hello", etc.
    CLARIFICATION = "clarification"  # User asking for clarification


# =============================================================================
# Structured Output for Classification
# =============================================================================

# Pydantic model ensures we get valid, typed responses.


class QueryClassification(BaseModel):
    """Classification result with reasoning."""

    intent: QueryIntent = Field(description="The classified intent")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0-1")
    reason: str = Field(description="Brief explanation for the classification")


# =============================================================================
# Classification Prompt
# =============================================================================

# Be specific about your domain. This example is for a customer support system.

CLASSIFICATION_PROMPT = """Classify the user's query intent.

KNOWLEDGE_BASE: Questions about orders, shipping, returns, refunds, payments,
products, or account issues. These need to search our documentation.

OFF_TOPIC: Questions unrelated to our business - general knowledge, politics,
math, coding help, or anything outside customer support.

GREETING: Simple greetings like "Hi", "Hello", "Hey there".

CLARIFICATION: User asking you to explain your previous response.

Be strict. Only use KNOWLEDGE_BASE for clear customer support questions."""


# =============================================================================
# The Classifier
# =============================================================================


def classify_query(query: str) -> QueryClassification:
    """Classify a query before deciding whether to search.

    Uses structured output to guarantee a valid classification.
    """
    response = client.responses.parse(
        model="gpt-5-mini",
        instructions=CLASSIFICATION_PROMPT,
        input=f"Query: {query}",
        text_format=QueryClassification,
    )
    return response.output_parsed


# =============================================================================
# Route Based on Intent
# =============================================================================


def handle_query(query: str) -> str:
    """Route query based on classified intent."""

    classification = classify_query(query)
    print(f"[Router] Intent: {classification.intent.value}")
    print(f"[Router] Confidence: {classification.confidence:.0%}")
    print(f"[Router] Reason: {classification.reason}")

    match classification.intent:
        case QueryIntent.KNOWLEDGE_BASE:
            # This is where you'd call your RAG pipeline
            return f"[Would search knowledge base for: {query}]"

        case QueryIntent.OFF_TOPIC:
            return (
                "I'm a customer support assistant and can only help with "
                "orders, shipping, returns, and product questions. "
                "Is there something in those areas I can help with?"
            )

        case QueryIntent.GREETING:
            return "Hello! How can I help you today?"

        case QueryIntent.CLARIFICATION:
            return "Could you tell me which part you'd like me to clarify?"


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    test_queries = [
        # Should route to knowledge base
        "How do I return an item?",
        "Where is my order?",
        "What payment methods do you accept?",
        # Should be off-topic
        "Who is the president of the United States?",
        "Write me a Python function",
        "What's 2 + 2?",
        # Should be greeting
        "Hello!",
        "Hi there",
        # Should be clarification
        "Can you explain that last part?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        response = handle_query(query)
        print(f"\nResponse: {response}")
