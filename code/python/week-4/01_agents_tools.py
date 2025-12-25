"""
PydanticAI Agents & Tools

Basic agent definition, tools with type hints, and dependency injection.
"""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Basic Agent
# =============================================================================

# Simplest possible agent - just a model and system prompt
basic_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are a helpful assistant. Be concise.",
)

# Run with: basic_agent.run_sync("What is the capital of France?")


# =============================================================================
# Agent with Tools
# =============================================================================

# Agent that can use tools to get information
time_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You help with time and date questions. Use your tools to get accurate information.",
)


@time_agent.tool_plain
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current time in a timezone.

    Args:
        timezone: The timezone name (e.g., 'America/New_York', 'Europe/London').

    Returns:
        The current time as a formatted string.
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error: Invalid timezone '{timezone}'. Use format like 'America/New_York'."


@time_agent.tool_plain
def get_timezone_offset(timezone: str) -> str:
    """Get the UTC offset for a timezone.

    Args:
        timezone: The timezone name.

    Returns:
        The UTC offset as a string.
    """
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        offset = now.strftime("%z")
        return f"{timezone} is UTC{offset[:3]}:{offset[3:]}"
    except Exception:
        return f"Error: Invalid timezone '{timezone}'."


# Run with: time_agent.run_sync("What time is it in Tokyo?")


# =============================================================================
# Dependency Injection
# =============================================================================


@dataclass
class UserDeps:
    """Dependencies for user-aware agents."""

    user_id: str
    user_name: str
    department: str


user_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You are a helpful assistant. Personalize responses using user context.",
    deps_type=UserDeps,
)


@user_agent.tool
def get_user_info(ctx: RunContext[UserDeps]) -> dict:
    """Get information about the current user.

    Returns:
        A dictionary with user details.
    """
    return {
        "user_id": ctx.deps.user_id,
        "name": ctx.deps.user_name,
        "department": ctx.deps.department,
    }


@user_agent.tool
def get_department_policies(ctx: RunContext[UserDeps]) -> str:
    """Get policies relevant to the user's department.

    Returns:
        Department-specific policy information.
    """
    policies = {
        "Engineering": "Remote work allowed. Core hours 10am-4pm.",
        "Sales": "Travel expenses reimbursed within 30 days.",
        "HR": "All employee data is confidential.",
    }
    return policies.get(ctx.deps.department, "No specific policies found.")


# Run with:
# deps = UserDeps(user_id="emp-123", user_name="Alice", department="Engineering")
# user_agent.run_sync("What's my department policy?", deps=deps)


# =============================================================================
# Structured Tool Returns
# =============================================================================


class SearchResult(BaseModel):
    """A search result from the document database."""

    title: str
    content: str
    relevance: float


@dataclass
class SearchDeps:
    """Dependencies for search-enabled agents."""

    max_results: int = 3


search_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You help users find information. Use the search tool, then summarize the results.",
    deps_type=SearchDeps,
)


@search_agent.tool
def search_documents(ctx: RunContext[SearchDeps], query: str) -> list[SearchResult]:
    """Search the document database.

    Args:
        query: The search query.

    Returns:
        A list of relevant documents with their content and relevance scores.
    """
    # Simulated search results
    all_results = [
        SearchResult(
            title="Vacation Policy",
            content="Employees get 20 days PTO per year. Unused days carry over up to 5 days.",
            relevance=0.95,
        ),
        SearchResult(
            title="Remote Work Guidelines",
            content="Employees may work remotely up to 3 days per week with manager approval.",
            relevance=0.87,
        ),
        SearchResult(
            title="Benefits Overview",
            content="Health insurance, 401k matching up to 6%, and annual wellness stipend.",
            relevance=0.82,
        ),
    ]

    # Filter based on query
    if "vacation" in query.lower() or "pto" in query.lower():
        results = [r for r in all_results if "vacation" in r.title.lower()]
    elif "remote" in query.lower():
        results = [r for r in all_results if "remote" in r.title.lower()]
    else:
        results = all_results

    return results[: ctx.deps.max_results]


# Run with:
# deps = SearchDeps(max_results=2)
# search_agent.run_sync("How many vacation days do I get?", deps=deps)
