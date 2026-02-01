"""
Sample FastAPI Application for Deployment

This is a minimal example showing the structure needed for Cloud Run deployment.
Replace with your actual RAG agent from Module 4.
"""

import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI App")


# =============================================================================
# Request/Response Models
# =============================================================================


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str


# =============================================================================
# Routes
# =============================================================================


@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask the AI a question.

    In production, this would:
    1. Search your vector database for relevant context
    2. Call the LLM with the question and context
    3. Return the generated answer

    For now, returns a placeholder.
    """
    # TODO: Replace with actual RAG implementation
    answer = f"This is a placeholder answer for: {request.question}"

    return AnswerResponse(
        question=request.question,
        answer=answer,
    )


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI App is running",
        "docs": "/docs",
        "health": "/health",
    }


# =============================================================================
# Run (for local development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
