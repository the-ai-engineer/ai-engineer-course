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
# Basic Result Types
# =============================================================================


class SimpleAnswer(BaseModel):
    """A simple answer with confidence score."""

    response: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence from 0 to 1")


simple_agent = Agent(
    "openai:gpt-4o-mini",
    result_type=SimpleAnswer,
)

# Run with: simple_agent.run_sync("What is the capital of Japan?")
# Access: result.output.response, result.output.confidence


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
    needs_clarification: bool = Field(
        default=False, description="Whether the question needs clarification"
    )


sourced_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Answer questions and cite your sources. Make up plausible sources for this demo.",
    result_type=AnswerWithSources,
)

# Run with: sourced_agent.run_sync("What is the vacation policy?")
# Access: result.output.answer, result.output.sources


# =============================================================================
# Enums for Constrained Values
# =============================================================================


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Category(str, Enum):
    """Support ticket categories."""

    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    OTHER = "other"


class SupportTicket(BaseModel):
    """A classified support ticket."""

    title: str = Field(description="Brief title for the ticket")
    category: Category = Field(description="The ticket category")
    priority: Priority = Field(description="How urgent is this issue")
    summary: str = Field(description="One sentence summary of the issue")


ticket_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Classify support tickets. Determine the category and priority based on the content.",
    result_type=SupportTicket,
)

# Run with: ticket_agent.run_sync("I can't log into my account and I have a presentation in 1 hour!")
# Access: result.output.priority == Priority.URGENT


# =============================================================================
# Validation with Constraints
# =============================================================================


class Rating(BaseModel):
    """A validated rating."""

    score: int = Field(ge=1, le=5, description="Rating from 1 to 5 stars")
    explanation: str = Field(min_length=10, description="Why this rating was given")


rating_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Rate the sentiment of the given text on a 1-5 scale.",
    result_type=Rating,
    retries=3,  # Retry if validation fails
)

# Run with: rating_agent.run_sync("This product is amazing! Best purchase ever!")
# The agent will retry if it returns a score outside 1-5


# =============================================================================
# Complex Analysis
# =============================================================================


class Entity(BaseModel):
    """An extracted entity."""

    name: str
    entity_type: str = Field(description="Type: person, organization, location, etc.")
    context: str = Field(description="How this entity relates to the text")


class Sentiment(str, Enum):
    """Sentiment classification."""

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
    language: str = Field(default="english", description="Detected language")


analysis_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Analyze the given text comprehensively.",
    result_type=TextAnalysis,
)

# Run with:
# text = "Apple announced new products at their Cupertino headquarters. CEO Tim Cook presented the iPhone 16."
# analysis_agent.run_sync(text)


# =============================================================================
# Optional and Default Fields
# =============================================================================


class FlexibleResponse(BaseModel):
    """A response with optional fields."""

    answer: str
    confidence: Optional[float] = None  # Only if the model can estimate
    follow_up_questions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    caveats: Optional[str] = Field(
        default=None, description="Any caveats or limitations to the answer"
    )


flexible_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Answer questions. Include confidence if you can estimate it, and suggest follow-ups.",
    result_type=FlexibleResponse,
)

# Run with: flexible_agent.run_sync("What causes rain?")


# =============================================================================
# Extraction Tasks
# =============================================================================


class ContactInfo(BaseModel):
    """Extracted contact information."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class MeetingDetails(BaseModel):
    """Extracted meeting information."""

    participants: list[str] = Field(default_factory=list)
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    agenda: Optional[str] = None


extraction_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="Extract meeting details from the given text. Use null for missing information.",
    result_type=MeetingDetails,
)

# Run with:
# text = "Let's meet tomorrow at 3pm in the conference room. I'll bring John and Sarah."
# extraction_agent.run_sync(text)
