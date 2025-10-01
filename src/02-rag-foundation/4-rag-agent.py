#!/usr/bin/env python3
"""
Lab 4: RAG-Powered AI Agent

Build an AI agent that answers questions using the vector database from Lab 3.
This combines retrieval (Chroma) with generation (OpenAI) to create a
Retrieval-Augmented Generation (RAG) system.
"""

import chromadb
import tiktoken
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
from openai import OpenAI

# Initialize clients
openai_client = OpenAI()
chroma_client = chromadb.Client()

# Setup vector database (from Lab 3)
print("Setting up RAG pipeline...")
collection = chroma_client.create_collection(name="papers")

# Convert and chunk document
converter = DocumentConverter()
doc = converter.convert("https://arxiv.org/pdf/2408.09869").document

EMBED_MODEL = "text-embedding-3-large"
MAX_TOKENS = 1024
encoder = tiktoken.encoding_for_model(EMBED_MODEL)
tokenizer = OpenAITokenizer(tokenizer=encoder, max_tokens=MAX_TOKENS)
chunker = HybridChunker(tokenizer=tokenizer)

chunks = list(chunker.chunk(dl_doc=doc))
documents = [chunker.contextualize(chunk=chunk) for chunk in chunks]
metadatas = [
    {
        "source": "arxiv:2408.09869",
        "page": getattr(chunk, "page", 0),
        "tokens": len(encoder.encode(chunk.text)),
    }
    for chunk in chunks
]

collection.add(
    documents=documents,
    ids=[f"chunk_{i}" for i in range(len(documents))],
    metadatas=metadatas,
)

print(f"✓ Indexed {len(documents)} chunks\n")


def retrieve_context(query: str, n_results: int = 3) -> tuple[list[str], list[dict]]:
    """Retrieve relevant chunks from the vector database."""
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0], results["metadatas"][0]


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """Generate answer using OpenAI with retrieved context."""
    # Format context for the LLM
    context = "\n\n".join(
        [f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)]
    )

    # Create prompt with context
    prompt = f"""Answer the question based on the following context from a research paper.
If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Answer:"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


def ask_question(query: str, show_context: bool = False) -> None:
    """RAG pipeline: retrieve context, generate answer, show citations."""
    print(f"\nQuestion: {query}")
    print("-" * 80)

    # Step 1: Retrieve relevant chunks
    context_chunks, metadatas = retrieve_context(query, n_results=3)

    if show_context:
        print("\nRetrieved context:")
        for i, (chunk, meta) in enumerate(zip(context_chunks, metadatas), 1):
            print(f"\n[Chunk {i}] (Page {meta['page']}, {meta['tokens']} tokens)")
            print(f"{chunk[:200]}...")

    # Step 2: Generate answer with LLM
    answer = generate_answer(query, context_chunks)

    # Step 3: Show answer with citations
    print(f"\nAnswer:\n{answer}")

    print("\n📚 Sources:")
    for i, meta in enumerate(metadatas, 1):
        print(f"  {i}. {meta['source']}, page {meta['page']}")


def main():
    print("RAG Agent Demo - Ask questions about the Docling paper\n")

    # Demo questions
    questions = [
        "What is Docling and what problem does it solve?",
        "What are the key features of Docling?",
        "How does Docling handle tables in documents?",
    ]

    # Answer first question with context shown
    ask_question(questions[0], show_context=True)

    # Answer remaining questions
    for question in questions[1:]:
        ask_question(question)

    # Interactive mode
    print("\n" + "=" * 80)
    print("Interactive mode - Type 'quit' to exit")
    print("=" * 80)

    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() in ["quit", "exit", "q"]:
            break
        if user_query:
            ask_question(user_query)


if __name__ == "__main__":
    main()
