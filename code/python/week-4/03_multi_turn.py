"""
Multi-turn Conversations

Managing message history and conversation state with PydanticAI.
"""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Basic Multi-turn
# =============================================================================

agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are a helpful assistant. Remember what the user tells you.",
)


def basic_conversation():
    """Demonstrate basic multi-turn conversation."""
    # First turn
    result1 = agent.run_sync("My name is Alice and I work in Engineering.")

    # Second turn - pass message history
    result2 = agent.run_sync(
        "What's my name and department?",
        message_history=result1.all_messages(),
    )

    return result2.output


# basic_conversation()


# =============================================================================
# Conversation Helper Class
# =============================================================================


class Conversation:
    """Helper class for managing multi-turn conversations."""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.messages: list[ModelMessage] = []

    def send(self, message: str) -> str:
        """Send a message and get a response."""
        result = self.agent.run_sync(message, message_history=self.messages)
        self.messages = list(result.all_messages())
        return result.output

    def reset(self):
        """Clear conversation history."""
        self.messages = []


# conv = Conversation(agent)
# conv.send("My favorite color is blue.")
# conv.send("What's my favorite color?")


# =============================================================================
# Dynamic System Prompts
# =============================================================================


@dataclass
class UserContext:
    """User-specific context for personalization."""

    user_name: str
    department: str


def get_personalized_prompt(ctx: RunContext[UserContext]) -> str:
    """Generate a system prompt based on user context."""
    return f"""You are an assistant helping {ctx.deps.user_name}.
They work in {ctx.deps.department}.
Personalize your responses to their department."""


personalized_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt=get_personalized_prompt,
    deps_type=UserContext,
)

# ctx = UserContext(user_name="Bob", department="Sales")
# personalized_agent.run_sync("What should I focus on?", deps=ctx)


# =============================================================================
# Conversation with Tools
# =============================================================================


@dataclass
class HRDeps:
    """Dependencies for HR assistant."""

    user_id: str
    topics_discussed: list[str] = field(default_factory=list)


hr_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are an HR assistant. Use tools to find policy information.",
    deps_type=HRDeps,
)


@hr_agent.tool
def search_policies(ctx: RunContext[HRDeps], query: str) -> str:
    """Search HR policies."""
    ctx.deps.topics_discussed.append(query)

    policies = {
        "vacation": "Employees receive 20 days PTO annually. Up to 5 days carry over.",
        "remote": "Remote work allowed 3 days per week with manager approval.",
        "benefits": "Health, dental, vision insurance. 401k with 6% match.",
    }

    for key, value in policies.items():
        if key in query.lower():
            return value

    return "No specific policy found. Please contact HR directly."


class HRConversation:
    """Stateful HR conversation with topic tracking."""

    def __init__(self, user_id: str):
        self.deps = HRDeps(user_id=user_id)
        self.messages: list[ModelMessage] = []

    def ask(self, question: str) -> str:
        """Ask an HR question."""
        result = hr_agent.run_sync(
            question,
            deps=self.deps,
            message_history=self.messages,
        )
        self.messages = list(result.all_messages())
        return result.output

    @property
    def topics(self) -> list[str]:
        """Topics discussed in this conversation."""
        return self.deps.topics_discussed


# hr = HRConversation(user_id="emp-123")
# hr.ask("How much vacation do I get?")
# hr.ask("Can I carry unused days to next year?")
# hr.topics
