"""Document ingestion script using Docling with hierarchical chunking."""

import sys
from pathlib import Path

import psycopg
from docling.chunking import HierarchicalChunker
from docling.document_converter import DocumentConverter
from pgvector.psycopg import register_vector

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.services.embeddings import get_embeddings

settings = get_settings()


def ingest_document(file_path: Path, conn: psycopg.Connection) -> int:
    """Ingest a single document using Docling's hierarchical chunking."""
    converter = DocumentConverter()
    result = converter.convert(str(file_path))

    chunker = HierarchicalChunker()
    doc_chunks = list(chunker.chunk(result.document))

    if not doc_chunks:
        return 0

    # Build chunk texts with heading context
    chunk_texts = []
    for chunk in doc_chunks:
        # Include heading hierarchy as context
        if chunk.meta.headings:
            context = " > ".join(chunk.meta.headings)
            text = f"[{context}]\n\n{chunk.text}"
        else:
            text = chunk.text
        chunk_texts.append(text)

    embeddings = get_embeddings(chunk_texts)
    source = file_path.name

    with conn.cursor() as cur:
        for text, embedding in zip(chunk_texts, embeddings):
            cur.execute(
                "INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
                (source, text, embedding),
            )

    conn.commit()
    return len(chunk_texts)


def ingest_directory(docs_dir: Path) -> None:
    """Ingest all documents from a directory."""
    supported_extensions = {".md", ".txt", ".pdf", ".docx"}

    conn = psycopg.connect(settings.database_url)
    register_vector(conn)

    try:
        total_chunks = 0
        for file_path in docs_dir.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                print(f"Processing: {file_path.name}")
                count = ingest_document(file_path, conn)
                total_chunks += count
                print(f"  Added {count} chunks")

        print(f"\nTotal: {total_chunks} chunks ingested")
    finally:
        conn.close()


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <docs_directory>")
        sys.exit(1)

    docs_dir = Path(sys.argv[1])
    if not docs_dir.is_dir():
        print(f"Error: {docs_dir} is not a directory")
        sys.exit(1)

    ingest_directory(docs_dir)


if __name__ == "__main__":
    main()
