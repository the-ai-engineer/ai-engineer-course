"""PydanticAI RAG Agent with search tool."""

import logging
from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from app.config import get_settings
from app.services.search import search

logger = logging.getLogger(__name__)

settings = get_settings()

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using the provided documentation.

Rules:
- Always search the documentation before answering
- Base your answers on the search results
- If the information isn't in the docs, say so clearly
- Be concise and direct
- Cite the source document when relevant
"""


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    sources: list[dict] = field(default_factory=list)


rag_agent = Agent(
    f"openai:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


@rag_agent.tool
def search_docs(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
    """Search the documentation for relevant information.

    Args:
        query: The search query to find relevant documentation.

    Returns:
        List of relevant document excerpts with source and score.
    """
    logger.info(f"[TOOL] search_docs called with query: {query!r}")
    try:
        results = search(query, limit=5)
        logger.info(f"[TOOL] search_docs returned {len(results)} results")
        ctx.deps.sources = results

        formatted = [
            {
                "source": r["source"],
                "content": r["content"],
                "score": round(r["score"], 3),
            }
            for r in results
        ]
        return formatted
    except Exception as e:
        logger.exception(f"[TOOL] search_docs error: {e}")
        raise


async def ask(question: str) -> tuple[str, list[dict]]:
    """Ask the RAG agent a question.

    Args:
        question: The question to ask.

    Returns:
        Tuple of (answer, sources).
    """
    deps = AgentDeps()
    result = await rag_agent.run(question, deps=deps)
    return result.output, deps.sources
