"""
LangFuse Tracing Examples

Demonstrates how to instrument LLM applications with LangFuse for observability.
Uses the drop-in OpenAI replacement for automatic tracing.

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
from langfuse.openai import openai  # Drop-in replacement

load_dotenv()


# =============================================================================
# Basic Tracing
# =============================================================================


@observe()
def answer_question(question: str) -> str:
    """Simple traced function. Token usage and costs are captured automatically."""
    response = openai.responses.create(
        model="gpt-5-mini",
        input=question,
    )
    return response.output_text


# =============================================================================
# Multi-Step Pipeline (Nested Traces)
# =============================================================================


@observe()
def search_documents(query: str) -> list[str]:
    """Simulate document retrieval (traced as a span)."""
    return [
        "Vacation Policy: Employees receive 15 days PTO per year.",
        "Remote Work: Up to 3 days per week with manager approval.",
    ]


@observe()
def generate_answer(question: str, context: list[str]) -> str:
    """Generate answer from context."""
    context_text = "\n".join(f"- {doc}" for doc in context)

    response = openai.responses.create(
        model="gpt-5-mini",
        instructions=f"Answer based on this context:\n{context_text}",
        input=question,
    )
    return response.output_text


@observe()
def rag_pipeline(question: str) -> str:
    """Complete RAG pipeline with nested traces."""
    docs = search_documents(question)
    answer = generate_answer(question, docs)
    return answer


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Running LangFuse tracing examples...")
    print("Check your LangFuse dashboard to see the traces.\n")

    # Basic trace
    print("1. Basic trace:")
    result = answer_question("What is the capital of France?")
    print(f"   Answer: {result}\n")

    # Multi-step pipeline
    print("2. RAG pipeline (nested traces):")
    result = rag_pipeline("How many vacation days do I get?")
    print(f"   Answer: {result}\n")

    # Flush to ensure all events are sent before exit
    get_client().flush()

    print("Done! Check cloud.langfuse.com for your traces.")
