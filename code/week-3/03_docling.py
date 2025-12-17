"""
Document Processing with Docling

Parse documents and chunk them for RAG.
"""

from docling.document_converter import DocumentConverter
from pydantic import BaseModel
from pathlib import Path

# =============================================================================
# Document Parsing
# =============================================================================

converter = DocumentConverter()


def parse_document(source: str) -> str:
    """Parse a document and return markdown text."""
    result = converter.convert(source)
    return result.document.export_to_markdown()


def parse_pdf(path: str) -> str:
    """Parse a PDF file."""
    return parse_document(path)


def parse_url(url: str) -> str:
    """Parse a document from URL."""
    return parse_document(url)


# =============================================================================
# Chunk Models
# =============================================================================


class Chunk(BaseModel):
    """A chunk of text with metadata."""

    content: str
    source: str
    chunk_index: int
    page: int | None = None
    section: str | None = None


# =============================================================================
# Chunking Strategies
# =============================================================================


def chunk_fixed_size(
    text: str,
    source: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[Chunk]:
    """Split text into fixed-size overlapping chunks."""
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size
        content = text[start:end].strip()

        if content:
            chunks.append(
                Chunk(
                    content=content,
                    source=source,
                    chunk_index=index,
                )
            )
            index += 1

        start = end - overlap

    return chunks


def chunk_by_paragraphs(
    text: str,
    source: str,
    max_chunk_size: int = 1500,
    min_chunk_size: int = 100,
) -> list[Chunk]:
    """Split text on paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    index = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds max size, save current chunk
        if current_chunk and len(current_chunk) + len(para) > max_chunk_size:
            chunks.append(
                Chunk(
                    content=current_chunk.strip(),
                    source=source,
                    chunk_index=index,
                )
            )
            index += 1
            current_chunk = para
        else:
            current_chunk = (
                current_chunk + "\n\n" + para if current_chunk else para
            )

    # Don't forget the last chunk
    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append(
            Chunk(
                content=current_chunk.strip(),
                source=source,
                chunk_index=index,
            )
        )

    return chunks


def chunk_by_sentences(
    text: str,
    source: str,
    sentences_per_chunk: int = 5,
) -> list[Chunk]:
    """Split text by sentences."""
    import re

    # Simple sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    index = 0

    for i in range(0, len(sentences), sentences_per_chunk):
        content = " ".join(sentences[i : i + sentences_per_chunk]).strip()
        if content:
            chunks.append(
                Chunk(
                    content=content,
                    source=source,
                    chunk_index=index,
                )
            )
            index += 1

    return chunks


# =============================================================================
# Pipeline: Parse and Chunk
# =============================================================================


def process_document(
    source: str,
    chunk_size: int = 1500,
    strategy: str = "paragraphs",
) -> list[Chunk]:
    """Parse a document and split into chunks."""
    # Parse
    text = parse_document(source)

    # Chunk based on strategy
    if strategy == "fixed":
        return chunk_fixed_size(text, source, chunk_size)
    elif strategy == "paragraphs":
        return chunk_by_paragraphs(text, source, chunk_size)
    elif strategy == "sentences":
        return chunk_by_sentences(text, source)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def process_directory(
    directory: str,
    extensions: list[str] = [".pdf", ".md", ".txt"],
    **kwargs,
) -> list[Chunk]:
    """Process all documents in a directory."""
    path = Path(directory)
    all_chunks = []

    for ext in extensions:
        for file in path.glob(f"**/*{ext}"):
            chunks = process_document(str(file), **kwargs)
            all_chunks.extend(chunks)

    return all_chunks


# =============================================================================
# Example Usage
# =============================================================================

# Parse a single document
# text = parse_document("example.pdf")
# text[:500]

# Chunk with different strategies
sample_text = """
# Introduction

This is the first paragraph of our document. It contains important information
about the topic we're discussing.

## Background

Here we provide background context. This section explains the history and
development of the subject matter. It's quite detailed and spans multiple
sentences to give readers a comprehensive understanding.

## Methods

The methodology section describes our approach. We used several techniques
including data collection, analysis, and validation. Each step was carefully
documented.

## Results

Our findings show significant improvements. The data indicates a 50% increase
in efficiency. These results were consistent across all test cases.

## Conclusion

In conclusion, our work demonstrates the effectiveness of the proposed approach.
Future work should focus on scalability and real-world applications.
"""

# Fixed-size chunks
fixed_chunks = chunk_fixed_size(sample_text, "sample.md", chunk_size=500, overlap=50)
len(fixed_chunks)

# Paragraph-based chunks
para_chunks = chunk_by_paragraphs(sample_text, "sample.md", max_chunk_size=800)
len(para_chunks)

# View a chunk
para_chunks[0]
