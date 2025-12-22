"""
RAG Strategy 2: Managed RAG with Gemini File Search

Zero infrastructure RAG - Google handles chunking, embedding, and search.
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


# =============================================================================
# File Search Store Management
# =============================================================================


def create_store(name: str) -> str:
    """Create a File Search store and return its name."""
    store = client.file_search_stores.create(config={"display_name": name})
    print(f"Created store: {store.name}")
    return store.name


def list_stores() -> list:
    """List all File Search stores."""
    stores = client.file_search_stores.list()
    return list(stores)


def delete_store(store_name: str):
    """Delete a File Search store."""
    client.file_search_stores.delete(name=store_name)
    print(f"Deleted store: {store_name}")


# =============================================================================
# Document Upload
# =============================================================================


def upload_document(
    store_name: str,
    file_path: str,
    display_name: str | None = None,
    metadata: dict | None = None,
    max_tokens_per_chunk: int | None = None,
):
    """Upload a document to a File Search store."""
    config = {"display_name": display_name or file_path}

    if metadata:
        config["metadata"] = metadata
    if max_tokens_per_chunk:
        config["max_tokens_per_chunk"] = max_tokens_per_chunk

    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config=config,
    )

    print(f"Uploaded: {file_path}")
    return operation


# =============================================================================
# Querying
# =============================================================================


def query_store(
    question: str,
    store_name: str,
    metadata_filter: str | None = None,
    model: str = "gemini-3-flash-preview",
) -> str:
    """Query documents using File Search."""
    file_search_config = None
    if metadata_filter:
        file_search_config = types.FileSearchConfig(filter=metadata_filter)

    response = client.models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name],
                        file_search_config=file_search_config,
                    )
                )
            ]
        ),
    )

    return response.text


def query_with_citations(
    question: str,
    store_name: str,
    model: str = "gemini-3-flash-preview",
) -> dict:
    """Query and return response with source citations."""
    response = client.models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(file_search_store_names=[store_name])
                )
            ]
        ),
    )

    result = {"answer": response.text, "sources": []}

    # Extract citations if available
    if response.candidates and response.candidates[0].grounding_metadata:
        grounding = response.candidates[0].grounding_metadata
        if grounding.grounding_chunks:
            for chunk in grounding.grounding_chunks:
                if chunk.retrieved_context:
                    result["sources"].append(
                        {
                            "title": chunk.retrieved_context.title,
                            "text": chunk.retrieved_context.text[:500],
                        }
                    )

    return result


# =============================================================================
# Complete Example
# =============================================================================


def demo_file_search():
    """Demonstrate File Search with a sample document."""
    # Create a sample document
    sample_content = """
    # Company Policies

    ## Vacation Policy
    Employees receive 20 days of paid vacation per year.
    Vacation days must be requested at least 2 weeks in advance.
    Unused vacation days can be carried over to the next year, up to a maximum of 5 days.

    ## Remote Work Policy
    Employees may work remotely up to 3 days per week.
    Remote work requires manager approval.
    All remote employees must be available during core hours (10am-3pm).

    ## Expense Policy
    Business expenses over $100 require pre-approval.
    Expense reports must be submitted within 30 days.
    Receipts are required for all expenses over $25.
    """

    # Write sample file
    with open("sample_policies.md", "w") as f:
        f.write(sample_content)

    try:
        # Create store
        store_name = create_store("demo-policies")

        # Upload document
        upload_document(
            store_name=store_name,
            file_path="sample_policies.md",
            display_name="Company Policies",
            metadata={"department": "hr", "year": "2024"},
        )

        # Wait for indexing (in production, check status)
        import time

        print("Waiting for indexing...")
        time.sleep(5)

        # Query
        questions = [
            "How many vacation days do I get?",
            "Can I work from home?",
            "Do I need a receipt for a $50 expense?",
        ]

        for q in questions:
            print(f"\nQ: {q}")
            answer = query_store(q, store_name)
            print(f"A: {answer}")

        # Clean up
        delete_store(store_name)

    finally:
        import os

        os.remove("sample_policies.md")


# =============================================================================
# Run Demo
# =============================================================================

if __name__ == "__main__":
    demo_file_search()
