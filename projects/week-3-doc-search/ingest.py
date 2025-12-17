"""
Document ingestion for search.

Parse documents, chunk them, generate embeddings, store in Postgres.
"""

import sys
from pathlib import Path
from docling.document_converter import DocumentConverter
from google import genai
from dotenv import load_dotenv
from db import get_connection, init_schema, create_indexes, insert_document, insert_chunks, get_stats

load_dotenv()

client = genai.Client()
converter = DocumentConverter()


def parse_document(path: str) -> str:
    """Parse a document and return markdown text."""
    result = converter.convert(path)
    return result.document.export_to_markdown()


def chunk_text(
    text: str,
    max_chunk_size: int = 1500,
    min_chunk_size: int = 100,
) -> list[str]:
    """Split text into chunks on paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_chunk and len(current_chunk) + len(para) > max_chunk_size:
            if len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append(current_chunk.strip())

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    if not texts:
        return []

    # Batch in groups of 100 to avoid API limits
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=batch,
        )
        all_embeddings.extend([e.values for e in response.embeddings])

    return all_embeddings


def ingest_file(conn, file_path: Path) -> int:
    """Ingest a single file. Returns number of chunks created."""
    print(f"  Parsing {file_path.name}...")

    try:
        text = parse_document(str(file_path))
    except Exception as e:
        print(f"  Error parsing {file_path}: {e}")
        return 0

    if not text.strip():
        print(f"  Skipping {file_path.name} (empty)")
        return 0

    # Chunk
    chunks = chunk_text(text)
    if not chunks:
        print(f"  Skipping {file_path.name} (no chunks)")
        return 0

    print(f"  Chunked into {len(chunks)} pieces")

    # Embed
    print(f"  Generating embeddings...")
    embeddings = embed_texts(chunks)

    # Store
    doc_id = insert_document(conn, str(file_path), file_path.stem)
    chunk_data = [
        (content, idx, emb)
        for idx, (content, emb) in enumerate(zip(chunks, embeddings))
    ]
    insert_chunks(conn, doc_id, chunk_data)

    print(f"  Stored {len(chunks)} chunks")
    return len(chunks)


def ingest_directory(directory: str, extensions: list[str] = None):
    """Ingest all documents in a directory."""
    if extensions is None:
        extensions = [".pdf", ".md", ".txt", ".docx"]

    path = Path(directory)
    if not path.exists():
        print(f"Directory not found: {directory}")
        return

    # Find all matching files
    files = []
    for ext in extensions:
        files.extend(path.glob(f"**/*{ext}"))

    if not files:
        print(f"No documents found in {directory}")
        return

    print(f"Found {len(files)} documents")

    # Initialize database
    conn = get_connection()
    init_schema(conn)

    total_chunks = 0
    for file_path in files:
        chunks = ingest_file(conn, file_path)
        total_chunks += chunks

    # Create indexes after bulk insert
    print("\nCreating indexes...")
    create_indexes(conn)

    stats = get_stats(conn)
    print(f"\nIngestion complete!")
    print(f"  Documents: {stats['documents']}")
    print(f"  Chunks: {stats['chunks']}")

    conn.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <directory>")
        print("Example: python ingest.py ./docs")
        sys.exit(1)

    directory = sys.argv[1]
    ingest_directory(directory)


if __name__ == "__main__":
    main()
