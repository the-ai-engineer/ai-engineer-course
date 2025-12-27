"""
LangFuse Tracing with PydanticAI

Demonstrates how to trace PydanticAI agents with LangFuse.

Setup:
1. Sign up at cloud.langfuse.com
2. Create a project and get API keys
3. Add to .env:
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   OPENAI_API_KEY=sk-...
"""

from dotenv import load_dotenv
from langfuse import get_client, observe
from pydantic_ai import Agent

load_dotenv()

langfuse = get_client()


# =============================================================================
# Agents
# =============================================================================


agent = Agent(
    "openai:gpt-5-mini",
    system_prompt="You are a helpful assistant. Be concise.",
    instrument=True,
)

math_agent = Agent(
    "openai:gpt-5-mini",
    system_prompt="You help with calculations. Use the tools provided.",
    instrument=True,
)


@math_agent.tool_plain
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@math_agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# =============================================================================
# Traced wrappers - @observe() + update_current_trace() captures I/O
# =============================================================================


@observe()
def ask_question(question: str) -> str:
    """Run agent with traced input/output."""
    result = agent.run_sync(question)
    langfuse.update_current_trace(input=question, output=result.output)
    return result.output


@observe()
def calculate(question: str) -> str:
    """Run math agent with traced input/output."""
    result = math_agent.run_sync(question)
    langfuse.update_current_trace(input=question, output=result.output)
    return result.output


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Running PydanticAI tracing examples...\n")

    print("1. Basic agent:")
    result = ask_question("What is the capital of England?")
    print(f"   Answer: {result}\n")

    print("2. Agent with tools:")
    result = calculate("What is 8 times 8, plus 10?")
    print(f"   Answer: {result}\n")

    langfuse.flush()

    print("Done! Check cloud.langfuse.com for your traces.")
