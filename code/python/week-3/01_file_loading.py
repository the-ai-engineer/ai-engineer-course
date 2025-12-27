"""
RAG Strategy 1: File Loading

The simplest approach - load the entire file into the prompt.
No embeddings, no database, no chunking. Works great for small documents.
"""

from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def load_file(file_path: str) -> str:
    """Load a file's contents."""
    return Path(file_path).read_text()


def answer_question(question: str, context: str) -> str:
    """Answer a question using the provided context."""
    response = client.responses.create(
        model="gpt-5-mini",
        instructions="""You are a friendly customer service assistant.
Be concise and direct. Answer based on the FAQ document provided.""",
        input=f"""FAQ Document:
{context}

Customer Question: {question}""",
    )
    return response.output_text


def run_demo():
    """Demo: Answer questions from a FAQ file."""
    print("=== File Loading RAG Demo ===\n")

    # Load the FAQ document
    faq_content = load_file("faqs.md")
    print(f"Loaded FAQ document ({len(faq_content)} characters)\n")

    # Sample questions
    questions = [
        "What is your return policy?",
        "How much does express shipping cost?",
        "Do you accept Bitcoin?",
        "How do I contact support?",
    ]

    for question in questions:
        print(f"Q: {question}")
        answer = answer_question(question, faq_content)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    run_demo()
