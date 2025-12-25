"""PydanticAI HR Policy Agent with RAG."""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from app.agent.embeddings import embed_query
from app.agent.prompts import SYSTEM_PROMPT
from app.config import get_settings
from app.db import get_connection
from app.models import PolicyResult, SearchResult

settings = get_settings()


# =============================================================================
# Dependencies
# =============================================================================


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    search_limit: int = 5
    search_type: str = "hybrid"
    # Populated by tool to track sources for API response
    sources: list[SearchResult] = field(default_factory=list)


# =============================================================================
# Agent
# =============================================================================


hr_agent = Agent(
    f"openai:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


# =============================================================================
# Search Tool
# =============================================================================


@hr_agent.tool
def search_policies(
    ctx: RunContext[AgentDeps], query: str
) -> list[PolicyResult]:
    """Search HR policy documents for relevant information.

    Args:
        query: The search query to find relevant policy information.

    Returns:
        List of relevant policy excerpts with source and relevance score.
    """
    with get_connection() as conn:
        search_type = ctx.deps.search_type
        limit = ctx.deps.search_limit

        if search_type == "vector":
            query_embedding = embed_query(query)
            rows = conn.execute(
                "SELECT * FROM vector_search(%s::vector, %s::int)",
                (query_embedding, limit),
            ).fetchall()

        elif search_type == "keyword":
            rows = conn.execute(
                "SELECT * FROM keyword_search(%s::text, %s::int)",
                (query, limit),
            ).fetchall()

        else:  # hybrid (default)
            query_embedding = embed_query(query)
            rows = conn.execute(
                "SELECT * FROM hybrid_search(%s::text, %s::vector, %s::int)",
                (query, query_embedding, limit),
            ).fetchall()

    # Convert to SearchResult for storage (used in API response)
    results = [
        SearchResult(
            chunk_id=row[0],
            source=row[1],
            content=row[2],
            metadata=row[3] or {},
            score=row[4],
        )
        for row in rows
    ]

    # Store full results for API response
    ctx.deps.sources = results

    if not results:
        return []

    # Return structured results to LLM (simplified view)
    return [
        PolicyResult(
            source=r.source.split("/")[-1],  # Just filename
            content=r.content,
            score=r.score,
        )
        for r in results
    ]


# =============================================================================
# Query Function
# =============================================================================


def ask_agent(
    question: str,
    search_limit: int = 5,
    search_type: str = "hybrid",
) -> tuple[str, list[SearchResult]]:
    """Ask the HR agent a question.

    Args:
        question: The question to ask.
        search_limit: Number of search results to retrieve.
        search_type: Type of search (vector, keyword, hybrid).

    Returns:
        Tuple of (answer, sources).
    """
    deps = AgentDeps(search_limit=search_limit, search_type=search_type)
    result = hr_agent.run_sync(question, deps=deps)
    return result.output, deps.sources
