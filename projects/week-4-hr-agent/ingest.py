"""Document ingestion script.

Standalone script for parsing documents, chunking text,
generating embeddings, and storing in PostgreSQL.

Usage:
    python ingest.py docs/              # Ingest all documents in a directory
    python ingest.py docs/policy.pdf    # Ingest a single file
"""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from google import genai
from google.genai import types
from pgvector.psycopg import register_vector

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/ragdb")
MIN_CHUNK_SIZE = 200
MAX_CHUNK_SIZE = 1000
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768

# =============================================================================
# Clients
# =============================================================================

converter = DocumentConverter()
client = genai.Client()


# =============================================================================
# Pipeline Functions
# =============================================================================


def get_connection():
    """Get a database connection with vector support."""
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def parse_document(source: str) -> str:
    """Parse a document and return markdown text."""
    result = converter.convert(source)
    return result.document.export_to_markdown()


def chunk_text(text: str) -> list[str]:
    """Split text into chunks on paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_chunk and len(current_chunk) + len(para) > MAX_CHUNK_SIZE:
            if len(current_chunk) >= MIN_CHUNK_SIZE:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk and len(current_chunk) >= MIN_CHUNK_SIZE:
        chunks.append(current_chunk.strip())

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    return [e.values for e in response.embeddings]


def ingest_document(conn: psycopg.Connection, source: str) -> int:
    """Ingest a single document. Returns number of chunks created."""
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")

    # Parse document to markdown
    text = parse_document(source)
    if not text.strip():
        return 0

    # Split into chunks
    chunks = chunk_text(text)
    if not chunks:
        return 0

    # Generate embeddings
    embeddings = embed_texts(chunks)

    # Delete existing chunks from this source (for re-ingestion)
    conn.execute("DELETE FROM chunks WHERE source = %s", (source,))

    # Insert chunks
    for content, embedding in zip(chunks, embeddings):
        conn.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
            (source, content, embedding),
        )

    conn.commit()
    return len(chunks)


def ingest_directory(conn: psycopg.Connection, directory: str) -> dict:
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
    conn = get_connection()

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

    conn.close()
    print("Complete.")


if __name__ == "__main__":
    main()
