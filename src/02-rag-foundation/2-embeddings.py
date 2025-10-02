#!/usr/bin/env python3
"""
Lab 2: Creating Embeddings with OpenAI

Learn how to convert text chunks into embeddings and measure similarity.
"""

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Sample chunks (in real usage, these come from Lab 1)
chunks = [
    "Python is a high-level programming language known for its simplicity.",
    "JavaScript is widely used for web development and runs in browsers.",
    "Machine learning models can identify patterns in large datasets.",
    "Neural networks are inspired by the structure of the human brain.",
    "Data preprocessing is essential before training any ML model.",
]


def create_embeddings(texts, model="text-embedding-3-small", dimensions=None):
    """Create embeddings for a list of texts."""
    response = client.embeddings.create(input=texts, model=model, dimensions=dimensions)

    embeddings = [data.embedding for data in response.data]
    total_tokens = response.usage.total_tokens

    print(f"{model}: {len(embeddings[0])} dimensions, {total_tokens} tokens")
    return embeddings


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (mag1 * mag2)


def find_most_similar(query, chunks, embeddings):
    """Find the most similar chunk to a query."""
    print(f"\nQuery: '{query}'")
    query_embedding = create_embeddings([query], model="text-embedding-3-small")[0]

    similarities = [
        (i, cosine_similarity(query_embedding, emb), chunk)
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)

    for rank, (idx, score, chunk) in enumerate(similarities[:3], 1):
        print(f"  {rank}. [{score:.3f}] {chunk[:60]}...")


def main():
    print("Lab 2: Creating Embeddings with OpenAI\n")

    # Compare different configurations
    print("Creating embeddings:")
    embeddings_default = create_embeddings(chunks, model="text-embedding-3-small")

    # Semantic search demo
    print("\nSemantic Search Demo:")
    queries = [
        "What's a good programming language for web dev?",
    ]

    for query in queries:
        find_most_similar(query, chunks, embeddings_default)
