"""PydanticAI HR Policy Agent."""

from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from app.config import get_settings
from app.database import get_connection
from app.search import search

settings = get_settings()


# =============================================================================
# Dependencies
# =============================================================================


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    search_limit: int = 5
    search_type: str = "hybrid"
    # Populated by tool to track sources
    sources: list = None

    def __post_init__(self):
        self.sources = []


# =============================================================================
# Agent
# =============================================================================

SYSTEM_PROMPT = """You are an HR Policy Assistant for Acme Corporation.

Your role is to help employees find information about company policies, benefits,
and procedures. You have access to the company's HR policy documents through
a search tool.

Guidelines:
- Always search the policy documents before answering questions
- Cite specific policies when providing information
- If you cannot find relevant information, say so clearly
- Be helpful and professional in your responses
- Do not make up policies that don't exist in the documents
- For complex HR issues, recommend speaking with the HR department directly

When answering:
1. Search for relevant policies first
2. Provide accurate information based on what you find
3. Quote or reference specific documents when helpful
4. Acknowledge limitations if information is incomplete
"""

hr_agent = Agent(
    f"google-gla:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


@hr_agent.tool
def search_policies(ctx: RunContext[AgentDeps], query: str) -> str:
    """Search HR policy documents for relevant information.

    Args:
        query: The search query to find relevant policy information.

    Returns:
        Relevant policy excerpts from the document database.
    """
    with get_connection() as conn:
        results = search(
            conn,
            query=query,
            limit=ctx.deps.search_limit,
            search_type=ctx.deps.search_type,
        )

    # Store sources for later retrieval
    ctx.deps.sources = results

    if not results:
        return "No relevant policies found for this query."

    # Format results for the LLM
    formatted = []
    for i, result in enumerate(results, 1):
        source = result.source.split("/")[-1]
        formatted.append(f"[{i}] Source: {source}\n{result.content}")

    return "\n\n---\n\n".join(formatted)


# =============================================================================
# Query Function
# =============================================================================


def ask_agent(
    question: str,
    search_limit: int = 5,
    search_type: str = "hybrid",
) -> tuple[str, list]:
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
    return result.data, deps.sources
