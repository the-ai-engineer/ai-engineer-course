"""
Agentic RAG: Document-Oriented Retrieval

Instead of chunking documents and searching fragments, give the agent:
1. An index of documents with descriptions
2. A tool to read full documents

The agent reasons about which document to read, then reads it whole.
This works well for runbooks, SOPs, and procedures where context matters.
"""

import json
from pathlib import Path

from openai import OpenAI

client = OpenAI()
runbooks_dir = Path(__file__).parent / "runbooks"

# =============================================================================
# System Prompt with Document Index
# =============================================================================

SYSTEM_PROMPT = """You're an on-call assistant that helps engineers resolve incidents.

Available runbooks:
- database-failover.md: PostgreSQL failover, connection pool issues, replication lag
- api-gateway.md: 502/503 errors, rate limiting, SSL certificate rotation
- kubernetes.md: Pod crashes, OOMKilled, node failures, deployment issues

Use read_runbook to get the full procedure when you identify the relevant runbook.
Don't guess at procedures - always read the runbook first.
Walk the engineer through the steps one at a time.
"""

# =============================================================================
# Tool Definition
# =============================================================================

tools = [
    {
        "type": "function",
        "name": "read_runbook",
        "description": "Read a runbook to get the full procedure for resolving an incident.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Runbook filename (e.g., 'database-failover.md')",
                }
            },
            "required": ["name"],
        },
    }
]


def read_runbook(name: str) -> str:
    """Read a runbook file and return its contents."""
    path = runbooks_dir / name
    if not path.exists():
        return f"Runbook '{name}' not found. Available: {', '.join(p.name for p in runbooks_dir.glob('*.md'))}"
    return path.read_text()


# =============================================================================
# Agent Loop
# =============================================================================


def ask(question: str) -> str:
    """Ask the on-call assistant a question."""
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=SYSTEM_PROMPT,
        input=question,
        tools=tools,
    )

    # Handle tool calls until we get a text response
    while response.output and response.output[0].type == "function_call":
        tool_call = response.output[0]
        args = json.loads(tool_call.arguments)

        print(f"[Agent] Reading runbook: {args['name']}")
        result = read_runbook(args["name"])

        # Continue conversation with tool result
        response = client.responses.create(
            model="gpt-4.1-mini",
            previous_response_id=response.id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result,
                }
            ],
        )

    return response.output_text


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    questions = [
        "The API is returning 503s and I see connection pool exhaustion in the logs",
        "One of our pods keeps getting OOMKilled",
        "We're seeing a lot of 429 rate limit errors",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Engineer: {question}")
        print(f"{'='*60}")
        answer = ask(question)
        print(f"\nAssistant: {answer}")
