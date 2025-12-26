"""PydanticAI HR Policy Agent with RAG."""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from app.agent.embeddings import embed_query
from app.agent.prompts import SYSTEM_PROMPT
from app.config import get_settings
from app.db import get_connection
from app.models import PolicyResult, SearchResult

settings = get_settings()


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    search_limit: int = 5
    sources: list[SearchResult] = field(default_factory=list)


hr_agent = Agent(
    f"openai:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


@hr_agent.tool
def search_policies(ctx: RunContext[AgentDeps], query: str) -> list[PolicyResult]:
    """Search HR policy documents for relevant information.

    Args:
        query: The search query to find relevant policy information.

    Returns:
        List of relevant policy excerpts with source and relevance score.
    """
    with get_connection() as conn:
        query_embedding = embed_query(query)
        rows = conn.execute(
            "SELECT * FROM hybrid_search(%s::text, %s::vector, %s::int)",
            (query, query_embedding, ctx.deps.search_limit),
        ).fetchall()

    # Store results for API response
    ctx.deps.sources = [
        SearchResult(
            chunk_id=row[0],
            source=row[1],
            content=row[2],
            score=row[3],
        )
        for row in rows
    ]

    if not ctx.deps.sources:
        return []

    # Return simplified view to LLM
    return [
        PolicyResult(
            source=r.source.split("/")[-1],
            content=r.content,
            score=r.score,
        )
        for r in ctx.deps.sources
    ]


def ask_agent(question: str, search_limit: int = 5) -> tuple[str, list[SearchResult]]:
    """Ask the HR agent a question.

    Args:
        question: The question to ask.
        search_limit: Number of search results to retrieve.

    Returns:
        Tuple of (answer, sources).
    """
    deps = AgentDeps(search_limit=search_limit)
    result = hr_agent.run_sync(question, deps=deps)
    return result.output, deps.sources
