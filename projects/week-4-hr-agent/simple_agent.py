"""Long-Context RAG Agent - The Simplest Approach.

This demonstrates "Long-Context RAG" where we stuff ALL documents into the
system prompt and let the model's attention mechanism find relevant information.

When to use this approach:
- Document set is under ~100k tokens (~75 pages)
- You want maximum accuracy (model sees everything)
- Simplicity is more important than cost optimization

When to use Vector RAG instead (see app/agent/):
- Document set exceeds context window
- Cost-sensitive (pay per token)
- Need fast responses on large corpora

Usage:
    python simple_agent.py "What is the vacation policy?"
    python simple_agent.py  # Interactive mode
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from openai import OpenAI

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

DOCS_DIR = Path(__file__).parent / "docs"
MODEL = "gpt-5-mini"

# =============================================================================
# Document Loading
# =============================================================================


def load_all_documents(docs_dir: Path) -> str:
    """Load and concatenate all documents into a single markdown string.

    Uses Docling to convert various formats (PDF, DOCX, MD, TXT) to markdown.
    """
    converter = DocumentConverter()
    all_content = []

    extensions = [".pdf", ".md", ".txt", ".docx"]
    files = []
    for ext in extensions:
        files.extend(docs_dir.glob(f"*{ext}"))

    for file_path in sorted(files):
        result = converter.convert(str(file_path))
        markdown = result.document.export_to_markdown()
        # Add filename as section header for citation
        all_content.append(f"## Source: {file_path.name}\n\n{markdown}")

    return "\n\n---\n\n".join(all_content)


# =============================================================================
# System Prompt with Grounding Rules
# =============================================================================

SYSTEM_PROMPT_TEMPLATE = """You are an HR Policy Assistant for Acme Corporation.

## Grounding Rules

1. **Source Fidelity**: Answer ONLY using information from the documents below.
   If the answer is not present, state: "I cannot find this information in the HR documents."

2. **Citations**: Reference the source document when providing information.
   Format: (Source: filename.md)

3. **No External Knowledge**: Do not use outside facts or assumptions about
   company policies. Only use what's explicitly stated in the documents.

4. **Completeness**: If information spans multiple documents, synthesize it
   and cite all relevant sources.

## HR Policy Documents

<documents>
{documents}
</documents>

## Instructions

Answer employee questions about HR policies based solely on the documents above.
Be helpful, professional, and cite your sources.
"""


# =============================================================================
# Agent
# =============================================================================


def create_agent():
    """Create a long-context RAG agent with all documents in system prompt."""
    # Load all documents
    print("Loading documents...")
    documents = load_all_documents(DOCS_DIR)

    # Count approximate tokens (4 chars = 1 token roughly)
    approx_tokens = len(documents) // 4
    print(f"Loaded {approx_tokens:,} tokens (~{approx_tokens * 4:,} chars)")

    if approx_tokens > 100_000:
        print("WARNING: Document size approaching context limit!")

    # Create system prompt with documents embedded
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(documents=documents)

    # Initialize client
    client = OpenAI()

    return client, system_prompt


def ask(client: OpenAI, system_prompt: str, question: str) -> str:
    """Ask a question using long-context RAG."""
    response = client.responses.create(
        model=MODEL,
        instructions=system_prompt,
        input=question,
    )
    return response.output_text


# =============================================================================
# Main
# =============================================================================


def main():
    client, system_prompt = create_agent()

    # Single question mode
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}\n")
        answer = ask(client, system_prompt, question)
        print(f"Answer:\n{answer}")
        return

    # Interactive mode
    print("\nHR Policy Assistant (Long-Context RAG)")
    print("Type 'quit' to exit\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        answer = ask(client, system_prompt, question)
        print(f"\nAssistant: {answer}\n")


if __name__ == "__main__":
    main()
