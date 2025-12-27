"""Document ingestion script.

Parses documents, chunks text, generates embeddings, and stores in PostgreSQL.

Usage:
    python ingest.py docs/              # Ingest all documents in a directory
    python ingest.py docs/policy.pdf    # Ingest a single file
"""

import sys
from pathlib import Path

import tiktoken
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from openai import OpenAI

from app.config import get_settings
from app.database import get_connection

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

settings = get_settings()
client = OpenAI()
converter = DocumentConverter()
tokenizer = tiktoken.get_encoding("cl100k_base")

MIN_CHUNK_TOKENS = 100
MAX_CHUNK_TOKENS = 500


# =============================================================================
# Pipeline Functions
# =============================================================================


def parse_document(source: str) -> str:
    """Parse a document and return markdown text."""
    result = converter.convert(source)
    return result.document.export_to_markdown()


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken."""
    return len(tokenizer.encode(text))


def chunk_text(text: str) -> list[str]:
    """Split text into chunks respecting token limits."""
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

    if current_chunk:
        current_chunk = current_chunk.strip()
        if current_tokens < MIN_CHUNK_TOKENS and chunks:
            chunks[-1] = f"{chunks[-1]}\n\n{current_chunk}"
        else:
            chunks.append(current_chunk)

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if not texts:
        return []
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]


def ingest_document(conn, source: str) -> int:
    """Ingest a single document. Returns number of chunks created."""
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    text = parse_document(source)
    if not text.strip():
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    # Delete existing chunks from this source (for re-ingestion)
    conn.execute("DELETE FROM chunks WHERE source = %s", (source,))

    for content, embedding in zip(chunks, embeddings):
        conn.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
            (source, content, embedding),
        )

    conn.commit()
    return len(chunks)


def ingest_directory(conn, directory: str) -> dict:
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
            n = ingest_document(conn, str(file_path))
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

    print("Connecting to database...")
    with get_connection() as conn:
        if path.is_file():
            print(f"Ingesting file: {target}")
            chunks = ingest_document(conn, target)
            print(f"Created {chunks} chunks")
        elif path.is_dir():
            print(f"Ingesting directory: {target}")
            stats = ingest_directory(conn, target)
            print(f"\nDone: {stats['success']}/{stats['total']} files, {stats['chunks']} chunks")
        else:
            print(f"Error: {target} not found")
            sys.exit(1)

    print("Complete.")


if __name__ == "__main__":
    main()
