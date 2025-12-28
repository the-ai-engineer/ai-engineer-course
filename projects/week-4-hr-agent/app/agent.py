"""PydanticAI Customer Support Agent for Zen HR."""

from dataclasses import dataclass, field

from langfuse import get_client, observe
from pydantic_ai import Agent, RunContext

from app.config import get_settings
from app.search import search

settings = get_settings()
langfuse = get_client() if settings.langfuse_enabled else None

SYSTEM_PROMPT = """You are a support agent for Zen HR. Be helpful, polite, and concise.

Rules:
- Search docs before answering
- Give direct answers in 2-3 sentences
- Only include details the customer actually needs
- If info isn't in the docs, say so briefly and suggest support@zenhr.com
- Never make up features or pricing
- Don't offer to do things (draft emails, walk through steps, etc.) - just answer the question
- For off-topic questions, just say "I can only help with Zen HR questions."
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
    instrument=True,
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


@observe()
async def ask(question: str, search_limit: int = 5) -> tuple[str, list[dict]]:
    """Ask the support agent a question.

    Args:
        question: The question to ask.
        search_limit: Number of search results to retrieve.

    Returns:
        Tuple of (answer, sources).
    """
    deps = AgentDeps(search_limit=search_limit)
    result = await support_agent.run(question, deps=deps)

    if langfuse:
        langfuse.update_current_trace(input=question, output=result.output)

    return result.output, deps.sources
