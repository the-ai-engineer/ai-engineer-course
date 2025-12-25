"""
Understanding Embeddings

Embeddings convert text into vectors for semantic search.
"""

import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# =============================================================================
# Basic Embedding
# =============================================================================


def embed_text(text: str) -> list[float]:
    """Embed a single text using OpenAI embeddings."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single API call."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


# =============================================================================
# Similarity Calculation
# =============================================================================


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two embeddings.

    Returns a value between -1 and 1:
    - 1.0 = identical meaning
    - 0.0 = unrelated
    - -1.0 = opposite meaning
    """
    a_arr, b_arr = np.array(a), np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))


# =============================================================================
# Similarity Demo
# =============================================================================


def demonstrate_similarity():
    """Show how similar texts have similar embeddings."""
    texts = [
        "The cat sat on the mat",
        "A kitten rested on the rug",
        "Stock prices rose sharply",
        "The feline lounged on the carpet",
    ]

    print("Embedding texts...")
    embeddings = embed_batch(texts)

    print(f"\nEmbedding dimensions: {len(embeddings[0])}")
    print(f"First 5 values of embedding 1: {embeddings[0][:5]}")

    print("\nSimilarity matrix:")
    print("-" * 60)

    for i, text_i in enumerate(texts):
        for j, text_j in enumerate(texts):
            if i < j:
                sim = cosine_similarity(embeddings[i], embeddings[j])
                print(f"{sim:.3f} | '{text_i[:30]}...' vs '{text_j[:30]}...'")


# =============================================================================
# Simple Search
# =============================================================================


class SimpleSearch:
    """A basic in-memory semantic search implementation."""

    def __init__(self):
        self.texts: list[str] = []
        self.embeddings: list[list[float]] = []

    def add(self, texts: list[str]):
        """Add texts to the search index."""
        new_embeddings = embed_batch(texts)
        self.texts.extend(texts)
        self.embeddings.extend(new_embeddings)
        print(f"Indexed {len(texts)} texts. Total: {len(self.texts)}")

    def search(self, query: str, top_k: int = 3) -> list[tuple[float, str]]:
        """Find the most similar texts to the query."""
        query_embedding = embed_text(query)

        # Calculate similarity to all stored embeddings
        results = []
        for i, emb in enumerate(self.embeddings):
            sim = cosine_similarity(query_embedding, emb)
            results.append((sim, self.texts[i]))

        # Sort by similarity (highest first) and return top_k
        results.sort(reverse=True)
        return results[:top_k]


def demonstrate_search():
    """Show semantic search in action."""
    # Create search index
    search = SimpleSearch()

    # Add some documents
    documents = [
        "Python is a popular programming language for data science.",
        "Machine learning models learn patterns from data.",
        "The weather today is sunny with a high of 75 degrees.",
        "Neural networks are inspired by biological neurons.",
        "My favorite recipe is chocolate chip cookies.",
        "Deep learning requires large amounts of training data.",
        "The stock market closed higher today.",
        "Natural language processing helps computers understand text.",
    ]
    search.add(documents)

    # Search for related content
    queries = [
        "How do AI systems learn?",
        "What's the temperature outside?",
        "Tell me about programming",
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 50)
        results = search.search(query, top_k=3)
        for score, text in results:
            print(f"  {score:.3f} | {text}")


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SIMILARITY DEMO")
    print("=" * 60)
    demonstrate_similarity()

    print("\n" + "=" * 60)
    print("SEARCH DEMO")
    print("=" * 60)
    demonstrate_search()
