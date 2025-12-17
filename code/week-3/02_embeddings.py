"""
Embeddings

Generate and compare text embeddings with Gemini.
"""

from google import genai
from dotenv import load_dotenv
import numpy as np

load_dotenv()

client = genai.Client()

# =============================================================================
# Generating Embeddings
# =============================================================================


def embed_text(text: str, model: str = "text-embedding-004") -> list[float]:
    """Generate an embedding for a single text."""
    response = client.models.embed_content(model=model, contents=text)
    return response.embeddings[0].values


def embed_texts(texts: list[str], model: str = "text-embedding-004") -> list[list[float]]:
    """Generate embeddings for multiple texts (batched)."""
    response = client.models.embed_content(model=model, contents=texts)
    return [e.values for e in response.embeddings]


# =============================================================================
# Similarity Metrics
# =============================================================================


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors. Range: -1 to 1."""
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def dot_product(a: list[float], b: list[float]) -> float:
    """Dot product of two vectors."""
    return float(np.dot(a, b))


def euclidean_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between two vectors. Lower = more similar."""
    return float(np.linalg.norm(np.array(a) - np.array(b)))


# =============================================================================
# Finding Similar Texts
# =============================================================================


def find_most_similar(
    query: str,
    documents: list[str],
    top_k: int = 3,
) -> list[tuple[str, float]]:
    """Find the most similar documents to a query."""
    query_embedding = embed_text(query)
    doc_embeddings = embed_texts(documents)

    similarities = [
        (doc, cosine_similarity(query_embedding, emb))
        for doc, emb in zip(documents, doc_embeddings)
    ]

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]


# =============================================================================
# Example Usage
# =============================================================================

# Generate a single embedding
text = "How do I reset my password?"
embedding = embed_text(text)
len(embedding)  # 768 dimensions

# Compare similar texts
similar_texts = [
    "I forgot my login credentials",
    "Reset my password please",
    "What's the weather today?",
    "How to change my account password",
]

query_emb = embed_text(text)
for t in similar_texts:
    t_emb = embed_text(t)
    sim = cosine_similarity(query_emb, t_emb)
    print(f"{sim:.3f}: {t}")

# Batch embedding
documents = [
    "Our refund policy allows returns within 30 days.",
    "Contact support at help@example.com for assistance.",
    "Business hours are 9am to 5pm Monday through Friday.",
    "Password reset can be done from the account settings page.",
    "We ship to all 50 US states and Canada.",
]

# Find similar documents
query = "How can I get my money back?"
results = find_most_similar(query, documents, top_k=3)
for doc, score in results:
    print(f"{score:.3f}: {doc}")
