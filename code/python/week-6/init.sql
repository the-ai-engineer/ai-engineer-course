-- Initialize database with pgvector extension
-- This runs automatically on first container start

-- Enable the vector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Example table for document embeddings (customize for your app)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source VARCHAR(255),
    embedding vector(1536),  -- OpenAI ada-002 dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Example: Full-text search support
ALTER TABLE documents ADD COLUMN IF NOT EXISTS content_tsv tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS documents_content_tsv_idx
ON documents USING GIN (content_tsv);
