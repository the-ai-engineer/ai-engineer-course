-- ============================================================================
-- PostgreSQL Schema for RAG with Vector & Hybrid Search
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS chunks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    fts TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_fts_idx
    ON chunks USING gin (fts);

CREATE INDEX IF NOT EXISTS chunks_metadata_idx
    ON chunks USING gin (metadata);

CREATE INDEX IF NOT EXISTS chunks_source_idx
    ON chunks (source);

-- ============================================================================
-- Search Functions
-- ============================================================================

-- Vector (semantic) search
CREATE OR REPLACE FUNCTION vector_search(
    query_embedding vector(768),
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    source TEXT,
    content TEXT,
    metadata JSONB,
    score FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        source,
        content,
        metadata,
        1 - (embedding <=> query_embedding) AS score
    FROM chunks
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Keyword (full-text) search
CREATE OR REPLACE FUNCTION keyword_search(
    query_text TEXT,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    source TEXT,
    content TEXT,
    metadata JSONB,
    score FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        source,
        content,
        metadata,
        ts_rank_cd(fts, websearch_to_tsquery('english', query_text))::FLOAT AS score
    FROM chunks
    WHERE fts @@ websearch_to_tsquery('english', query_text)
    ORDER BY score DESC
    LIMIT match_count;
$$;

-- Hybrid search using Reciprocal Rank Fusion (RRF)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(768),
    match_count INT DEFAULT 5,
    rrf_k INT DEFAULT 60
)
RETURNS TABLE (
    id BIGINT,
    source TEXT,
    content TEXT,
    metadata JSONB,
    score FLOAT
)
LANGUAGE sql STABLE
AS $$
    WITH vector_results AS (
        SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank
        FROM chunks
        WHERE embedding IS NOT NULL
        LIMIT match_count * 2
    ),
    keyword_results AS (
        SELECT id, ROW_NUMBER() OVER (
            ORDER BY ts_rank_cd(fts, websearch_to_tsquery('english', query_text)) DESC
        ) AS rank
        FROM chunks
        WHERE fts @@ websearch_to_tsquery('english', query_text)
        LIMIT match_count * 2
    )
    SELECT
        c.id,
        c.source,
        c.content,
        c.metadata,
        (
            COALESCE(1.0 / (rrf_k + v.rank), 0.0) +
            COALESCE(1.0 / (rrf_k + k.rank), 0.0)
        )::FLOAT AS score
    FROM vector_results v
    FULL OUTER JOIN keyword_results k ON v.id = k.id
    JOIN chunks c ON c.id = COALESCE(v.id, k.id)
    ORDER BY score DESC
    LIMIT match_count;
$$;
