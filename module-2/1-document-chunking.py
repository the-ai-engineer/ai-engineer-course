#!/usr/bin/env python3
"""
Docling 101: Process and Chunk Documents

A beginner-friendly introduction to using Docling for document processing.
Learn how to convert documents and split them into chunks for vector databases.
"""

import tiktoken
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer

# Step 1: Convert a document (PDF, DOCX, HTML, etc.)
converter = DocumentConverter()
doc = converter.convert("https://arxiv.org/pdf/2408.09869").document

print(f"✓ Converted {len(doc.pages)} pages\n")

# Choose your embedding model - this affects token counting
EMBED_MODEL = "text-embedding-3-large"  # OpenAI's latest embedding model
MAX_TOKENS = 1024  # Recommended chunk size for embeddings

# Why 1024 tokens?
# - OpenAI embedding models support up to 8,191 tokens per input
# - But smaller chunks (512-1024) work better for retrieval
# - 1024 gives you room for context enrichment (explained below)
# - Balances between semantic coherence and retrieval precision
encoder = tiktoken.encoding_for_model(EMBED_MODEL)
tokenizer = OpenAITokenizer(tokenizer=encoder, max_tokens=MAX_TOKENS)

# Create the HybridChunker
# - Uses document structure (headings, paragraphs, tables)
# - Respects token limits for your embedding model
# - Merges small chunks when possible (merge_peers=True by default)
chunker = HybridChunker(tokenizer=tokenizer)

# Step 3: Split document into chunks
print("Chunking document...")
chunks = list(chunker.chunk(dl_doc=doc))
print(f"✓ Created {len(chunks)} chunks\n")

# Tip: Use contextualized text for better retrieval accuracy

for i, chunk in enumerate(chunks[:3]):
    # Raw text from the chunk
    raw_text = chunk.text
    raw_tokens = len(encoder.encode(raw_text))

    # Contextualized text includes heading/section info
    # This helps the embedding model understand the chunk's context
    contextualized = chunker.contextualize(chunk=chunk)
    context_tokens = len(encoder.encode(contextualized))

    print(f"\nChunk {i + 1}: {raw_tokens} → {context_tokens} tokens")
    print(f"  {raw_text[:100]}...")
