"""Document ingestion script.

Parses documents, chunks text, generates embeddings, and stores in PostgreSQL.

Usage:
    python ingest.py ./docs              # Ingest all documents in a directory
    python ingest.py ./docs/policy.pdf   # Ingest a single file
"""

import sys
from pathlib import Path

import tiktoken
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI

from db import get_connection

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# Token-based chunking
MIN_CHUNK_TOKENS = 100
MAX_CHUNK_TOKENS = 500

# =============================================================================
# Clients
# =============================================================================

converter = DocumentConverter()
client = OpenAI()
tokenizer = tiktoken.get_encoding("cl100k_base")


# =============================================================================
# Token Counting
# =============================================================================


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken."""
    return len(tokenizer.encode(text))


# =============================================================================
# Document Processing
# =============================================================================


def parse_document(source: str) -> str:
    """Parse a document and return markdown text."""
    result = converter.convert(source)
    return result.document.export_to_markdown()


def chunk_text(text: str) -> list[str]:
    """Split text into chunks respecting token limits.

    Uses paragraph boundaries for natural breaks.
    Target: 300-500 tokens per chunk for optimal retrieval.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = count_tokens(para)

        if current_chunk and (current_tokens + para_tokens) > MAX_CHUNK_TOKENS:
            chunks.append(current_chunk.strip())
            current_chunk = para
            current_tokens = para_tokens
        else:
            current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            current_tokens += para_tokens

    # Handle final chunk
    if current_chunk:
        current_chunk = current_chunk.strip()
        if current_tokens < MIN_CHUNK_TOKENS and chunks:
            chunks[-1] = f"{chunks[-1]}\n\n{current_chunk}"
        else:
            chunks.append(current_chunk)

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for document chunks."""
    if not texts:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# =============================================================================
# Ingestion
# =============================================================================


def ingest_document(source: str) -> int:
    """Ingest a single document. Returns number of chunks created."""
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    # Parse document
    print(f"  Parsing {path.name}...")
    text = parse_document(source)
    if not text.strip():
        return 0

    # Chunk text
    chunks = chunk_text(text)
    if not chunks:
        return 0

    # Generate embeddings
    print(f"  Embedding {len(chunks)} chunks...")
    embeddings = embed_texts(chunks)

    # Store in database
    with get_connection() as conn:
        # Delete existing chunks from this source (for re-ingestion)
        conn.execute("DELETE FROM chunks WHERE source = %s", (source,))

        # Insert new chunks
        for content, embedding in zip(chunks, embeddings):
            conn.execute(
                "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
                (source, content, embedding),
            )

        conn.commit()

    return len(chunks)


def ingest_directory(directory: str) -> dict:
    """Ingest all documents in a directory."""
    extensions = [".pdf", ".md", ".txt", ".docx"]
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = []
    for ext in extensions:
        files.extend(path.glob(f"**/*{ext}"))

    stats = {"total": len(files), "success": 0, "failed": 0, "chunks": 0}

    for file_path in files:
        try:
            n = ingest_document(str(file_path))
            stats["success"] += 1
            stats["chunks"] += n
            print(f"  {file_path.name}: {n} chunks")
        except Exception as e:
            stats["failed"] += 1
            print(f"  {file_path.name}: FAILED - {e}")

    return stats


# =============================================================================
# Main
# =============================================================================


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    path = Path(target)

    if path.is_file():
        print(f"Ingesting file: {target}")
        chunks = ingest_document(target)
        print(f"Created {chunks} chunks")
    elif path.is_dir():
        print(f"Ingesting directory: {target}")
        stats = ingest_directory(target)
        print(f"\nDone: {stats['success']}/{stats['total']} files, {stats['chunks']} chunks")
    else:
        print(f"Error: {target} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
