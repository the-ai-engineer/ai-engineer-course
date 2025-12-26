"""
Structured Responses & Validation

Define result types with Pydantic for type-safe, validated agent output.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Basic Result Type
# =============================================================================


class SimpleAnswer(BaseModel):
    """A simple answer with confidence score."""

    response: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence from 0 to 1")


simple_agent = Agent(
    "openai:gpt-4o-mini",
    result_type=SimpleAnswer,
)

# simple_agent.run_sync("What is the capital of Japan?")
# result.output.response, result.output.confidence


# =============================================================================
# Nested Models
# =============================================================================


class Source(BaseModel):
    """A source citation."""

    document: str
    page: Optional[int] = None
    relevance: float = Field(ge=0.0, le=1.0)


class AnswerWithSources(BaseModel):
    """An answer with supporting sources."""

    answer: str = Field(description="The answer to the question")
    sources: list[Source] = Field(description="Sources supporting the answer")
    needs_clarification: bool = Field(default=False)


sourced_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Answer questions and cite your sources.",
    result_type=AnswerWithSources,
)

# sourced_agent.run_sync("What is the vacation policy?")


# =============================================================================
# Enums for Constrained Values
# =============================================================================


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    OTHER = "other"


class SupportTicket(BaseModel):
    """A classified support ticket."""

    title: str = Field(description="Brief title for the ticket")
    category: Category
    priority: Priority
    summary: str = Field(description="One sentence summary")


ticket_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Classify support tickets by category and priority.",
    result_type=SupportTicket,
)

# ticket_agent.run_sync("I can't log into my account and I have a presentation in 1 hour!")


# =============================================================================
# Complex Analysis with Optional Fields
# =============================================================================


class Entity(BaseModel):
    """An extracted entity."""

    name: str
    entity_type: str = Field(description="person, organization, location, etc.")


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class TextAnalysis(BaseModel):
    """Complete text analysis result."""

    summary: str = Field(description="One paragraph summary")
    sentiment: Sentiment
    entities: list[Entity] = Field(default_factory=list)
    keywords: list[str] = Field(description="Key topics mentioned")
    language: str = Field(default="english")


analysis_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Analyze the given text comprehensively.",
    result_type=TextAnalysis,
)

# text = "Apple announced new products at their Cupertino headquarters."
# analysis_agent.run_sync(text)
