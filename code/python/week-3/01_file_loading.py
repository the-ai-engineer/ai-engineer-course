"""
RAG Strategy 1: File Loading

The simplest approach - load the entire file into the prompt.
No embeddings, no database, no chunking.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

client = genai.Client()


# =============================================================================
# Basic File Q&A
# =============================================================================


def answer_from_file(question: str, file_path: str) -> str:
    """Answer a question using a file as context."""
    with open(file_path) as f:
        content = f.read()

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""Use the following document to answer the question.
If the answer isn't in the document, say so.

Document:
{content}

Question: {question}""",
    )
    return response.text


def answer_from_files(question: str, file_paths: list[str]) -> str:
    """Answer using multiple files as context."""
    contents = []
    for path in file_paths:
        with open(path) as f:
            contents.append(f"--- {path} ---\n{f.read()}")

    combined = "\n\n".join(contents)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""Use these documents to answer the question.

Documents:
{combined}

Question: {question}""",
    )
    return response.text


# =============================================================================
# FAQ Q&A
# =============================================================================


def answer_faq(question: str, faq_path: str) -> str:
    """Answer questions from a FAQ JSON file."""
    with open(faq_path) as f:
        faqs = json.load(f)

    # Format FAQs for the prompt
    faq_text = "\n\n".join(
        f"Q: {item['question']}\nA: {item['answer']}" for item in faqs["faqs"]
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""You are a helpful customer service assistant.
Answer the customer's question using ONLY the FAQ information below.
If the question isn't covered, say you don't have that information.

FAQ:
{faq_text}

Customer question: {question}""",
    )
    return response.text


# =============================================================================
# Reusable Q&A Agent
# =============================================================================


def create_file_qa_agent(file_path: str):
    """Create a Q&A function for a specific file."""
    with open(file_path) as f:
        content = f.read()

    def ask(question: str) -> str:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=f"""You are a helpful assistant that answers questions
about the following document. Only use information from this document.
If something isn't covered, say so clearly.

Document:
{content}"""
            ),
        )
        return response.text

    return ask


# =============================================================================
# Example Usage
# =============================================================================

# Create sample FAQ file for demo
sample_faqs = {
    "faqs": [
        {
            "question": "What is your return policy?",
            "answer": "You can return any item within 30 days of purchase for a full refund.",
        },
        {
            "question": "How long does shipping take?",
            "answer": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days.",
        },
        {
            "question": "Do you ship internationally?",
            "answer": "Yes, we ship to over 50 countries. International shipping takes 10-14 business days.",
        },
        {
            "question": "What payment methods do you accept?",
            "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay.",
        },
        {
            "question": "How do I track my order?",
            "answer": "Once your order ships, you'll receive an email with a tracking number and link.",
        },
    ]
}

# Write sample FAQ file
with open("sample_faqs.json", "w") as f:
    json.dump(sample_faqs, f, indent=2)

# Test FAQ Q&A
print("Testing FAQ Q&A...")
print("-" * 50)

questions = [
    "Can I get my money back if I don't like the product?",
    "How fast is express shipping?",
    "Do you accept Bitcoin?",
]

for q in questions:
    print(f"Q: {q}")
    answer = answer_faq(q, "sample_faqs.json")
    print(f"A: {answer}")
    print()

# Clean up
import os

os.remove("sample_faqs.json")
