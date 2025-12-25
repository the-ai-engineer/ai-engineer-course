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


# Run with: basic_conversation()


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

    @property
    def turn_count(self) -> int:
        """Number of user turns in the conversation."""
        return sum(1 for m in self.messages if m.kind == "request")


# Usage:
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
    role: str


def get_personalized_prompt(ctx: RunContext[UserContext]) -> str:
    """Generate a system prompt based on user context."""
    return f"""You are an assistant helping {ctx.deps.user_name}.
They work in {ctx.deps.department} as a {ctx.deps.role}.
Personalize your responses to their role and department."""


personalized_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt=get_personalized_prompt,
    deps_type=UserContext,
)


def personalized_conversation():
    """Show dynamic system prompts."""
    ctx = UserContext(
        user_name="Bob",
        department="Sales",
        role="Account Executive",
    )

    result = personalized_agent.run_sync(
        "What should I focus on this quarter?",
        deps=ctx,
    )
    return result.output


# =============================================================================
# Conversation with Tools
# =============================================================================


@dataclass
class HRDeps:
    """Dependencies for HR assistant."""

    user_id: str
    topics_discussed: list[str] = field(default_factory=list)
    search_count: int = 0


hr_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are an HR assistant. Use tools to find policy information.",
    deps_type=HRDeps,
)


@hr_agent.tool
def search_policies(ctx: RunContext[HRDeps], query: str) -> str:
    """Search HR policies.

    Args:
        query: What to search for.

    Returns:
        Relevant policy information.
    """
    # Track what topics have been discussed
    ctx.deps.topics_discussed.append(query)
    ctx.deps.search_count += 1

    # Simulated policy database
    policies = {
        "vacation": "Employees receive 20 days PTO annually. Up to 5 days carry over.",
        "remote": "Remote work allowed 3 days per week with manager approval.",
        "benefits": "Health, dental, vision insurance. 401k with 6% match.",
        "parental": "12 weeks paid parental leave for all new parents.",
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


# Usage:
# hr = HRConversation(user_id="emp-123")
# hr.ask("How much vacation do I get?")
# hr.ask("Can I carry unused days to next year?")
# hr.topics  # ['vacation', ...]


# =============================================================================
# Context Window Management
# =============================================================================


def truncate_history(
    messages: list[ModelMessage],
    max_messages: int = 20,
) -> list[ModelMessage]:
    """Keep only recent messages, preserving system prompt.

    Args:
        messages: Full message history.
        max_messages: Maximum number of messages to keep.

    Returns:
        Truncated message list.
    """
    if len(messages) <= max_messages:
        return messages

    # Separate system messages from conversation
    system_messages = [m for m in messages if m.kind == "system"]
    conversation = [m for m in messages if m.kind != "system"]

    # Keep only recent conversation
    recent = conversation[-(max_messages - len(system_messages)) :]

    return system_messages + recent


class ManagedConversation:
    """Conversation with automatic context management."""

    def __init__(self, agent: Agent, max_messages: int = 20):
        self.agent = agent
        self.max_messages = max_messages
        self.messages: list[ModelMessage] = []

    def send(self, message: str) -> str:
        """Send a message with automatic truncation."""
        # Truncate before sending to avoid context overflow
        truncated = truncate_history(self.messages, self.max_messages)

        result = self.agent.run_sync(message, message_history=truncated)
        self.messages = list(result.all_messages())

        return result.output


# =============================================================================
# Multiple System Prompt Sources
# =============================================================================


@dataclass
class ContextualDeps:
    """Dependencies with multiple context sources."""

    user_name: str
    current_date: str
    active_projects: list[str] = field(default_factory=list)


contextual_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are a project management assistant.",
    deps_type=ContextualDeps,
)


@contextual_agent.system_prompt
def add_user_context(ctx: RunContext[ContextualDeps]) -> str:
    """Add user-specific context."""
    return f"You are helping {ctx.deps.user_name}."


@contextual_agent.system_prompt
def add_date_context(ctx: RunContext[ContextualDeps]) -> str:
    """Add temporal context."""
    return f"Today's date is {ctx.deps.current_date}."


@contextual_agent.system_prompt
def add_project_context(ctx: RunContext[ContextualDeps]) -> str:
    """Add project context."""
    if ctx.deps.active_projects:
        projects = ", ".join(ctx.deps.active_projects)
        return f"Active projects: {projects}."
    return "No active projects."


# All system_prompt decorators are combined into the final prompt
# Usage:
# deps = ContextualDeps(
#     user_name="Alice",
#     current_date="2024-12-25",
#     active_projects=["Website Redesign", "API Migration"],
# )
# contextual_agent.run_sync("What should I work on today?", deps=deps)
