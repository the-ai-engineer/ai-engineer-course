-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Chunks table (simplified schema for HR agent)
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMP DEFAULT NOW()
);

-- HNSW index for vector similarity search
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS chunks_content_tsv_idx
ON chunks USING gin(content_tsv);

-- Vector search function
CREATE OR REPLACE FUNCTION vector_search(
    query_embedding vector(1536),
    match_count INT DEFAULT 5
)
RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
LANGUAGE sql AS $$
SELECT
    c.id,
    c.source,
    c.content,
    (1 - (c.embedding <=> query_embedding))::FLOAT AS score
FROM chunks c
WHERE c.embedding IS NOT NULL
ORDER BY c.embedding <=> query_embedding
LIMIT match_count;
$$;

-- Keyword search function
CREATE OR REPLACE FUNCTION keyword_search(
    query_text TEXT,
    match_count INT DEFAULT 5
)
RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
LANGUAGE sql AS $$
SELECT
    c.id,
    c.source,
    c.content,
    ts_rank_cd(c.content_tsv, websearch_to_tsquery('english', query_text))::FLOAT AS score
FROM chunks c
WHERE c.content_tsv @@ websearch_to_tsquery('english', query_text)
ORDER BY score DESC
LIMIT match_count;
$$;

-- Hybrid search function using Reciprocal Rank Fusion
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    rrf_k INT DEFAULT 60
)
RETURNS TABLE (id BIGINT, source TEXT, content TEXT, score FLOAT)
LANGUAGE sql AS $$
WITH semantic AS (
    SELECT c.id, ROW_NUMBER() OVER (ORDER BY c.embedding <=> query_embedding) AS rank
    FROM chunks c
    WHERE c.embedding IS NOT NULL
    LIMIT match_count * 2
),
keyword AS (
    SELECT c.id, ROW_NUMBER() OVER (
        ORDER BY ts_rank_cd(c.content_tsv, websearch_to_tsquery('english', query_text)) DESC
    ) AS rank
    FROM chunks c
    WHERE c.content_tsv @@ websearch_to_tsquery('english', query_text)
    LIMIT match_count * 2
)
SELECT
    c.id,
    c.source,
    c.content,
    (COALESCE(1.0 / (rrf_k + s.rank), 0.0) +
     COALESCE(1.0 / (rrf_k + k.rank), 0.0))::FLOAT AS score
FROM semantic s
FULL OUTER JOIN keyword k ON s.id = k.id
JOIN chunks c ON c.id = COALESCE(s.id, k.id)
ORDER BY score DESC
LIMIT match_count;
$$;
