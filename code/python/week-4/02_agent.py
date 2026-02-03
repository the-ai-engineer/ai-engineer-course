"""
Building the RAG Agent

Complete RAG agent with search tool, system prompt, and source tracking.
"""

from dataclasses import dataclass, field
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Models
# =============================================================================


class PolicyResult(BaseModel):
    """Search result returned to the model."""

    source: str
    content: str
    score: float


@dataclass
class AgentDeps:
    """Dependencies for the RAG agent."""

    search_limit: int = 5
    search_type: str = "hybrid"  # "hybrid", "vector", "keyword"
    sources: list = field(default_factory=list)


# =============================================================================
# System Prompt
# =============================================================================

SYSTEM_PROMPT = """You are an HR Policy Assistant for Acme Corporation.

Your job is to help employees find information about company policies, benefits,
and procedures. You have access to the company's HR policy documents through
a search tool.

IMPORTANT GUIDELINES:
- Always search before answering. Do not rely on general knowledge.
- Cite specific policies when providing information.
- If you cannot find relevant information, say so clearly.
- Do not make up policies that don't exist in the documents.
- For complex HR issues, recommend speaking with HR directly.

When answering:
1. Search for relevant policies first
2. Read the search results carefully
3. Answer based only on what you find
4. Quote or reference specific documents when helpful
"""


# =============================================================================
# Agent Definition
# =============================================================================

hr_agent = Agent(
    "openai:gpt-5-mini",
    system_prompt=SYSTEM_PROMPT,
    deps_type=AgentDeps,
)


# =============================================================================
# Search Tool
# =============================================================================


def embed_query(query: str) -> list[float]:
    """Generate embedding for a query."""
    from openai import OpenAI

    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    return response.data[0].embedding


def get_connection():
    """Get database connection (placeholder)."""
    # In the real project, this uses psycopg with pgvector
    raise NotImplementedError("Use the project's db module")


@hr_agent.tool
def search_policies(ctx: RunContext[AgentDeps], query: str) -> list[PolicyResult]:
    """Search HR policy documents for relevant information.

    Args:
        query: The search query to find relevant policy information.

    Returns:
        List of relevant policy excerpts with source and score.
    """
    # For demonstration, using mock data
    # Real implementation uses the database functions from lesson 02
    MOCK_RESULTS = [
        {
            "id": 1,
            "source": "employee-handbook.pdf",
            "content": "Vacation Policy: Full-time employees receive 15 days of paid vacation per year.",
            "score": 0.92,
        },
        {
            "id": 2,
            "source": "employee-handbook.pdf",
            "content": "Sick Leave: Employees receive 10 paid sick days per year.",
            "score": 0.88,
        },
        {
            "id": 3,
            "source": "remote-work-policy.pdf",
            "content": "Remote Work: Employees may work remotely up to 3 days per week.",
            "score": 0.85,
        },
    ]

    # Filter based on query (simple mock)
    query_lower = query.lower()
    results = [
        r
        for r in MOCK_RESULTS
        if any(word in r["content"].lower() for word in query_lower.split())
    ]

    if not results:
        results = MOCK_RESULTS  # Return all if no match

    results = results[: ctx.deps.search_limit]

    # Store full results for API response
    ctx.deps.sources = results

    # Return simplified view to model
    return [
        PolicyResult(source=r["source"], content=r["content"], score=r["score"])
        for r in results
    ]


# =============================================================================
# Agent Interface
# =============================================================================


def ask_agent(
    question: str,
    search_limit: int = 5,
    search_type: str = "hybrid",
) -> tuple[str, list[dict]]:
    """
    Ask the HR agent a question.

    Args:
        question: The question to ask
        search_limit: Maximum number of search results
        search_type: "hybrid", "vector", or "keyword"

    Returns:
        Tuple of (answer, sources)
    """
    deps = AgentDeps(
        search_limit=search_limit,
        search_type=search_type,
    )

    result = hr_agent.run_sync(question, deps=deps)

    return result.output, deps.sources


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Test the agent
    questions = [
        "How many vacation days do I get?",
        "What's the remote work policy?",
        "Can I work from home on Fridays?",
    ]

    for question in questions:
        print(f"Q: {question}")
        answer, sources = ask_agent(question)
        print(f"A: {answer}")
        print(f"Sources: {[s['source'] for s in sources]}")
        print()
