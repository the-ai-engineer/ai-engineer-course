"""PydanticAI Customer Support Agent for Zen HR."""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from app.config import get_settings
from app.search import search

settings = get_settings()

SYSTEM_PROMPT = """You are a Customer Support Agent for Zen HR, a SaaS HR management platform.

Your role is to help customers find information about the product, billing,
integrations, and troubleshooting. You have access to the support documentation
through a search tool.

Guidelines:
- Always search the documentation before answering questions
- Cite specific docs when providing information
- If you cannot find relevant information, say so clearly
- Be helpful and professional in your responses
- Do not make up features or pricing that don't exist in the docs
- For account-specific issues, recommend contacting support@zenhr.com

When answering:
1. Search for relevant documentation first
2. Provide accurate information based on what you find
3. Quote or reference specific documents when helpful
4. Acknowledge limitations if information is incomplete
"""


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    search_limit: int = 5
    sources: list[dict] = field(default_factory=list)


support_agent = Agent(
    f"openai:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


@support_agent.tool
def search_docs(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
    """Search support documentation for relevant information.

    Args:
        query: The search query to find relevant product information.

    Returns:
        List of relevant documentation excerpts with source and relevance score.
    """
    results = search(query, limit=ctx.deps.search_limit)
    ctx.deps.sources = results

    # Return simplified view to LLM
    return [
        {
            "source": r["source"].split("/")[-1],
            "content": r["content"],
            "score": r["score"],
        }
        for r in results
    ]


def ask(question: str, search_limit: int = 5) -> tuple[str, list[dict]]:
    """Ask the support agent a question.

    Args:
        question: The question to ask.
        search_limit: Number of search results to retrieve.

    Returns:
        Tuple of (answer, sources).
    """
    deps = AgentDeps(search_limit=search_limit)
    result = support_agent.run_sync(question, deps=deps)
    return result.output, deps.sources
