"""
Production RAG - Ingestion Pipeline

Document parsing, chunking strategies, and database ingestion.
"""

from pathlib import Path
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"


# =============================================================================
# Tokenization
# =============================================================================

tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens in a text string."""
    return len(tokenizer.encode(text))


# =============================================================================
# Chunking Strategies
# =============================================================================


def chunk_by_chars(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Simple fixed-size chunking by characters.

    Pros: Simple, predictable size
    Cons: Breaks mid-sentence, ignores document structure
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_by_paragraphs(text: str, max_tokens: int = 500) -> list[str]:
    """
    Chunk by paragraph boundaries with token limit.

    Pros: Respects natural boundaries
    Cons: Paragraph size varies
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if count_tokens(current + para) > max_tokens and current:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para

    if current:
        chunks.append(current.strip())

    return chunks


def chunk_by_tokens(
    text: str,
    min_tokens: int = 100,
    max_tokens: int = 500,
) -> list[str]:
    """
    Token-based chunking with paragraph respect.

    This is the recommended approach for most use cases.

    Args:
        text: The text to chunk
        min_tokens: Minimum tokens per chunk (skip tiny chunks)
        max_tokens: Maximum tokens per chunk

    Returns:
        List of text chunks
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = count_tokens(para)

        # Would exceed max? Start new chunk
        if current and (current_tokens + para_tokens) > max_tokens:
            chunks.append(current.strip())
            current = para
            current_tokens = para_tokens
        else:
            current = f"{current}\n\n{para}" if current else para
            current_tokens += para_tokens

    # Add final chunk if it meets minimum
    if current and current_tokens >= min_tokens:
        chunks.append(current.strip())

    return chunks


# =============================================================================
# Document Parsing
# =============================================================================


def parse_document(path: str) -> str:
    """
    Parse a document to plain text using Docling.

    Supports: PDF, DOCX, PPTX, HTML, Markdown
    """
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(path)
        return result.document.export_to_markdown()
    except ImportError:
        # Fallback for simple text files
        with open(path, "r") as f:
            return f.read()


# =============================================================================
# Embedding
# =============================================================================


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


# =============================================================================
# Ingestion Pipeline
# =============================================================================


def ingest_document(path: str, conn) -> int:
    """
    Ingest a single document into the database.

    Args:
        path: Path to the document
        conn: Database connection

    Returns:
        Number of chunks ingested
    """
    print(f"Processing: {path}")

    # Parse document to text
    text = parse_document(path)
    if not text.strip():
        print(f"  Warning: Empty document")
        return 0

    # Chunk the text
    chunks = chunk_by_tokens(text, min_tokens=100, max_tokens=500)
    if not chunks:
        print(f"  Warning: No chunks generated")
        return 0

    print(f"  Generated {len(chunks)} chunks")

    # Generate embeddings (batch for efficiency)
    embeddings = embed_texts(chunks)

    # Store in database
    for content, embedding in zip(chunks, embeddings):
        conn.execute(
            """INSERT INTO chunks (source, content, embedding)
               VALUES (%s, %s, %s)""",
            (path, content, embedding),
        )
    conn.commit()

    print(f"  Stored {len(chunks)} chunks")
    return len(chunks)


def ingest_directory(directory: str, conn) -> dict:
    """
    Ingest all documents in a directory.

    Args:
        directory: Path to directory containing documents
        conn: Database connection

    Returns:
        Statistics about the ingestion
    """
    stats = {"files": 0, "chunks": 0, "errors": []}
    supported_extensions = {".pdf", ".docx", ".pptx", ".md", ".html", ".txt"}

    for path in Path(directory).glob("**/*"):
        if path.suffix.lower() in supported_extensions:
            try:
                chunk_count = ingest_document(str(path), conn)
                stats["files"] += 1
                stats["chunks"] += chunk_count
            except Exception as e:
                stats["errors"].append({"file": str(path), "error": str(e)})
                print(f"  Error: {e}")

    return stats


# =============================================================================
# Database Schema
# =============================================================================

SCHEMA_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Document chunks with embeddings and full-text search
CREATE TABLE IF NOT EXISTS chunks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    fts TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_fts_idx
    ON chunks USING gin (fts);
"""


def init_schema(conn):
    """Initialize the database schema."""
    conn.execute(SCHEMA_SQL)
    conn.commit()
    print("Schema initialized")


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python 04_ingestion.py <directory>")
        print("Example: python 04_ingestion.py ./docs/")
        sys.exit(1)

    directory = sys.argv[1]

    # This would use the actual database connection
    # from app.db import get_connection
    # with get_connection() as conn:
    #     stats = ingest_directory(directory, conn)
    #     print(f"\nDone: {stats['files']} files, {stats['chunks']} chunks")
    #     if stats['errors']:
    #         print(f"Errors: {len(stats['errors'])}")

    print(f"Would ingest documents from: {directory}")
    print("(Run with actual database connection in the project)")
