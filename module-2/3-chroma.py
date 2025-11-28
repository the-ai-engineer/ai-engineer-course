#!/usr/bin/env python3
"""
Lab 3: Vector Database with Chroma

Apply lessons from Labs 1 & 2:
- Lab 1: Document chunking with Docling
- Lab 2: Creating embeddings
- Lab 3: Store and query with Chroma
"""

import chromadb
import tiktoken
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer

# Setup Chroma client
client = chromadb.Client()  # In-memory
# client = chromadb.PersistentClient(path="./chroma-database")  # Persistent

# Create collection (Chroma handles embeddings automatically)
collection = client.create_collection(name="papers")

# Step 1: Convert and chunk document (from Lab 1)
print("Converting document...")
converter = DocumentConverter()
doc = converter.convert("https://arxiv.org/pdf/2408.09869").document

print(f"✓ Converted {len(doc.pages)} pages")

# Step 2: Chunk the document
EMBED_MODEL = "text-embedding-3-large"
MAX_TOKENS = 1024
encoder = tiktoken.encoding_for_model(EMBED_MODEL)
tokenizer = OpenAITokenizer(tokenizer=encoder, max_tokens=MAX_TOKENS)
chunker = HybridChunker(tokenizer=tokenizer)

print("Chunking document...")
chunks = list(chunker.chunk(dl_doc=doc))
print(f"✓ Created {len(chunks)} chunks\n")

# Step 3: Add chunks to Chroma
# Use contextualized text for better retrieval (as shown in Lab 1)
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

print(f"✓ Added {len(documents)} chunks to Chroma\n")

# Step 4: Query the collection (semantic search)
query = "What is Docling and what can it do?"
results = collection.query(query_texts=[query], n_results=3)

print(f"Query: '{query}'\n")
print("Top 3 results:")
for i, (doc, distance) in enumerate(
    zip(results["documents"][0], results["distances"][0]), 1
):
    similarity = 1 - distance  # Convert distance to similarity
    print(f"  {i}. [{similarity:.3f}] {doc[:60]}...")

# Key advantages over Lab 2:
# - No manual embedding creation
# - No manual similarity calculation
# - Built-in persistence option
# - Metadata filtering support
# - Production-ready for RAG systems
