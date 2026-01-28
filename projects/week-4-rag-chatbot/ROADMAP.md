# RAG Chatbot Improvement Roadmap

This document outlines proposed improvements to the RAG chatbot, focusing on data pipeline reliability and retrieval quality.

## Phase 1: Data Pipeline Fixes

### 1.1 Add Document Deduplication on Ingest

**Problem**: Re-running ingest creates duplicate chunks, polluting search results.

**File**: `backend/scripts/ingest.py`

**Solution**: Delete existing chunks for a source before re-ingesting:

```python
cur.execute("DELETE FROM chunks WHERE source = %s", (source,))
```

### 1.2 Add Metadata Columns to Schema

**Problem**: Document hierarchy is only preserved as a text prefix. We can't filter by document or section.

**Files**: `init.sql`, `backend/scripts/ingest.py`

**Solution**: Add structured metadata columns:

```sql
ALTER TABLE chunks ADD COLUMN document_id TEXT;
ALTER TABLE chunks ADD COLUMN section_title TEXT;
ALTER TABLE chunks ADD COLUMN chunk_index INT;
```

Update the ingest script to populate these fields during chunking.

### 1.3 Add Chunk Overlap

**Problem**: HierarchicalChunker may lose context at chunk boundaries.

**File**: `backend/scripts/ingest.py`

**Solution**: Add configurable overlap between chunks (50-100 tokens) to preserve context at boundaries.

### 1.4 Improve Ingest Error Handling

**Problem**: One bad document fails the entire batch.

**File**: `backend/scripts/ingest.py`

**Solution**: Wrap each document in try/except, log failures, and continue processing remaining documents.

## Phase 2: Retrieval Quality

### 2.1 Add Reranking Layer

**Problem**: No semantic reranking after initial retrieval. RRF alone may miss nuanced relevance.

**Files**:
- New: `backend/app/services/reranker.py`
- Modify: `backend/app/services/search.py`

**Approach**: Use Cohere Rerank API:

```python
import cohere

co = cohere.Client(api_key)

def rerank(query: str, documents: list[dict], top_n: int = 5) -> list[dict]:
    results = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=[d["content"] for d in documents],
        top_n=top_n,
    )
    return [documents[r.index] for r in results.results]
```

**Alternative** (no external API): Use an OpenAI scoring prompt to re-score top-10 results.

### 2.2 Configurable Retrieval Parameters

**Problem**: Hardcoded `limit=5` and `rrf_k=60`.

**Files**: `backend/app/config.py`, `backend/app/agent/agent.py`

**Solution**: Add to Settings:

```python
search_limit: int = 5
rerank_limit: int = 10  # Fetch more, then rerank
rrf_k: int = 60
```

### 2.3 Normalize Scores in Backend

**Problem**: Frontend hardcodes `maxRrfScore = 0.033` for display normalization.

**Files**: `backend/app/services/search.py`

**Solution**: Return normalized `relevance_percent` (0-100) from backend:

```python
def normalize_score(score: float, max_score: float = 0.033) -> int:
    return min(100, int((score / max_score) * 100))
```

### 2.4 Query Expansion (Optional)

**Problem**: User queries may not match document terminology.

**File**: `backend/app/agent/agent.py`

**Solution**: Add a query expansion tool that generates synonyms and related terms before search.

## Phase 3: Index Optimization

### 3.1 Tune HNSW Index Parameters

**File**: `init.sql`

**Current**: `m = 16, ef_construction = 64`

**Solution**: For better recall (at cost of index size):

```sql
CREATE INDEX chunks_embedding_idx
ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 24, ef_construction = 128);
```

### 3.2 Add Search-Time Parameters

**File**: `backend/app/services/search.py`

**Solution**: Set `ef_search` at query time for recall/speed tradeoff:

```sql
SET hnsw.ef_search = 100;
```

## Files to Modify

| File | Changes |
|------|---------|
| `init.sql` | Add metadata columns, tune HNSW params |
| `backend/app/config.py` | Add retrieval config options |
| `backend/app/services/search.py` | Score normalization, ef_search |
| `backend/app/services/reranker.py` | New file for Cohere reranking |
| `backend/scripts/ingest.py` | Deduplication, metadata, overlap, error handling |
| `backend/pyproject.toml` | Add `cohere` dependency |

## Verification

### Deduplication Test

```bash
# Ingest twice, verify chunk count unchanged
uv run python scripts/ingest.py
uv run python scripts/ingest.py
psql -c "SELECT source, COUNT(*) FROM chunks GROUP BY source"
```

### Reranking Test

- Query with ambiguous terms
- Verify reranked results are more relevant than raw hybrid search

### Metadata Test

```sql
SELECT DISTINCT document_id, section_title FROM chunks;
```

### End-to-End Test

1. Start containers: `docker compose up --build`
2. Test chat at http://localhost:4567
3. Verify sources show normalized scores (0-100%)
