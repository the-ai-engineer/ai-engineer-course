"""
Production Polish

Connection pooling, caching, error handling, and logging.
"""

import logging
import time
import hashlib
import json
from contextlib import contextmanager
from functools import lru_cache
from typing import Generator

from pydantic_settings import BaseSettings
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Configuration
# =============================================================================


class Settings(BaseSettings):
    """Application settings from environment."""

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost/ragdb"

    # OpenAI
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    generation_model: str = "gpt-4o-mini"

    # Search
    default_search_limit: int = 5

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


# =============================================================================
# Logging Setup
# =============================================================================


def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )


logger = logging.getLogger(__name__)


# =============================================================================
# Connection Pooling
# =============================================================================

# In production, use psycopg_pool:
#
# from psycopg_pool import ConnectionPool
# from pgvector.psycopg import register_vector
#
# pool = ConnectionPool(
#     settings.database_url,
#     min_size=2,
#     max_size=10,
#     open=True,
# )
#
# @contextmanager
# def get_connection():
#     with pool.connection() as conn:
#         register_vector(conn)
#         yield conn


@contextmanager
def get_connection():
    """Get database connection (placeholder)."""
    # In production, use the pooled connection above
    logger.info("Opening database connection")
    yield None  # Placeholder
    logger.info("Closing database connection")


# =============================================================================
# Embedding Cache
# =============================================================================

client = OpenAI()


@lru_cache(maxsize=1000)
def embed_query_cached(text: str) -> tuple[float, ...]:
    """Generate embedding with in-memory caching.

    Returns tuple (hashable) for LRU cache compatibility.
    """
    logger.debug(f"Generating embedding for: {text[:50]}...")

    response = client.embeddings.create(
        model=get_settings().embedding_model,
        input=text,
    )
    return tuple(response.data[0].embedding)


def embed_query(text: str) -> list[float]:
    """Generate embedding, using cache."""
    return list(embed_query_cached(text))


# For production with Redis:
#
# import redis
#
# redis_client = redis.Redis(host="localhost", port=6379)
# CACHE_TTL = 86400  # 24 hours
#
# def embed_query_redis(text: str) -> list[float]:
#     cache_key = f"embed:{hashlib.md5(text.encode()).hexdigest()}"
#
#     cached = redis_client.get(cache_key)
#     if cached:
#         logger.debug("Cache hit for embedding")
#         return json.loads(cached)
#
#     logger.debug("Cache miss, generating embedding")
#     response = client.embeddings.create(
#         model=get_settings().embedding_model,
#         input=text,
#     )
#     embedding = response.data[0].embedding
#
#     redis_client.setex(cache_key, CACHE_TTL, json.dumps(embedding))
#     return embedding


# =============================================================================
# Error Handling
# =============================================================================


def ask_agent_safe(question: str, search_limit: int = 5) -> tuple[str, list]:
    """Ask the agent with error handling."""
    logger.info(f"Processing question: {question[:50]}...")

    try:
        # In real implementation, this calls the PydanticAI agent
        # result = hr_agent.run_sync(question, deps=deps)
        # return result.output, deps.sources

        # Placeholder
        return "Mock response", []

    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I'm having trouble connecting. Please try again.", []

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return "An unexpected error occurred.", []


# =============================================================================
# Request Timing Middleware
# =============================================================================


async def timing_middleware(request, call_next):
    """Log request timing for FastAPI."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} duration={duration:.3f}s"
    )
    return response


# Usage with FastAPI:
# app.middleware("http")(timing_middleware)


# =============================================================================
# Health Check
# =============================================================================


def health_check() -> dict:
    """Health check for monitoring."""
    db_status = "ok"

    try:
        with get_connection() as conn:
            if conn:
                conn.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
    }


# =============================================================================
# Rate Limiting
# =============================================================================

from collections import defaultdict

request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10  # requests
RATE_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit.

    Returns True if allowed, False if rate limited.
    """
    now = time.time()

    # Clean old requests
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if now - t < RATE_WINDOW
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return False

    request_counts[client_ip].append(now)
    return True


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    setup_logging("DEBUG")

    # Test caching
    print("Testing embedding cache...")
    text = "What is the vacation policy?"

    start = time.perf_counter()
    embed_query(text)
    first_call = time.perf_counter() - start

    start = time.perf_counter()
    embed_query(text)
    second_call = time.perf_counter() - start

    print(f"First call: {first_call:.3f}s")
    print(f"Second call (cached): {second_call:.6f}s")

    # Test health check
    print("\nHealth check:", health_check())

    # Test rate limiting
    print("\nTesting rate limit...")
    for i in range(12):
        allowed = check_rate_limit("127.0.0.1")
        print(f"Request {i+1}: {'allowed' if allowed else 'blocked'}")
