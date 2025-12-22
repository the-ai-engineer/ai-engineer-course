"""
Queues and Async Patterns

Background job processing with Redis Queue (rq).
Requires Redis running locally: brew install redis && redis-server
"""

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

# =============================================================================
# The Task to Queue
# =============================================================================


def summarize_document(doc_id: str, text: str) -> dict:
    """
    A slow task that should run in the background.
    In production, you'd fetch the doc from a database.
    """
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Summarize this document:\n\n{text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )

    return {
        "doc_id": doc_id,
        "summary": response.text,
        "status": "completed",
    }


# =============================================================================
# Using Redis Queue (rq)
# =============================================================================

# To use this, you need Redis running:
#   brew install redis
#   redis-server
#
# Then run a worker in a separate terminal:
#   rq worker

try:
    from redis import Redis
    from rq import Queue, Retry

    redis_conn = Redis()
    q = Queue(connection=redis_conn)

    def enqueue_summary(doc_id: str, text: str):
        """Enqueue a document for background processing."""
        job = q.enqueue(
            summarize_document,
            doc_id,
            text,
            retry=Retry(max=3, interval=[10, 30, 60]),
            job_timeout="5m",
        )
        return job.id

    def check_job_status(job_id: str) -> dict:
        """Check the status of a queued job."""
        from rq.job import Job

        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "id": job_id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
        }

except ImportError:
    # rq not installed or Redis not available
    def enqueue_summary(doc_id: str, text: str):
        return "rq-not-installed"

    def check_job_status(job_id: str):
        return {"error": "rq not installed"}


# =============================================================================
# Simple In-Memory Queue (for learning)
# =============================================================================

import queue
import threading
from typing import Callable

# A simple queue for demonstration without Redis
task_queue: queue.Queue = queue.Queue()
results: dict = {}


def worker():
    """Worker that processes tasks from the queue."""
    while True:
        task_id, func, args = task_queue.get()
        try:
            result = func(*args)
            results[task_id] = {"status": "completed", "result": result}
        except Exception as e:
            results[task_id] = {"status": "failed", "error": str(e)}
        task_queue.task_done()


def start_worker():
    """Start a background worker thread."""
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t


def enqueue_task(func: Callable, *args) -> str:
    """Add a task to the queue."""
    import uuid

    task_id = str(uuid.uuid4())
    results[task_id] = {"status": "queued"}
    task_queue.put((task_id, func, args))
    return task_id


def get_result(task_id: str) -> dict:
    """Get the result of a queued task."""
    return results.get(task_id, {"status": "not_found"})


# =============================================================================
# Example Usage
# =============================================================================

# Start a worker
start_worker()

# Enqueue a task
doc_text = "AI is transforming healthcare through better diagnostics and drug discovery."
task_id = enqueue_task(summarize_document, "doc_001", doc_text)
task_id

# Check status (may still be processing)
import time

time.sleep(3)
get_result(task_id)
