"""PydanticAI HR Policy Agent."""

from dataclasses import dataclass, field

from pydantic_ai import Agent, RunContext

from app.config import get_settings
from app.search import search

settings = get_settings()

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


@dataclass
class AgentDeps:
    """Dependencies injected into the agent."""

    search_limit: int = 5
    sources: list[dict] = field(default_factory=list)


hr_agent = Agent(
    f"openai:{settings.generation_model}",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


@hr_agent.tool
def search_policies(ctx: RunContext[AgentDeps], query: str) -> list[dict]:
    """Search HR policy documents for relevant information.

    Args:
        query: The search query to find relevant policy information.

    Returns:
        List of relevant policy excerpts with source and relevance score.
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
