"""
FastAPI Chat Application

Web interface for the HR Policy Agent.
"""

from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Models
# =============================================================================


class RAGRequest(BaseModel):
    """Request to the RAG agent."""

    question: str
    limit: int = 5
    search_type: str = "hybrid"


class SearchResult(BaseModel):
    """A single search result."""

    chunk_id: int
    source: str
    content: str
    score: float


class RAGResponse(BaseModel):
    """Response from the RAG agent."""

    question: str
    answer: str
    sources: list[SearchResult]


# =============================================================================
# Agent (Simplified for Demo)
# =============================================================================


def ask_agent(question: str, search_limit: int = 5) -> tuple[str, list[SearchResult]]:
    """Ask the agent a question. Returns (answer, sources).

    In the real implementation, this calls the PydanticAI agent.
    Here we return mock data for demonstration.
    """
    # Mock response
    answer = f"Based on the HR policies, here's what I found about: {question}"
    sources = [
        SearchResult(
            chunk_id=1,
            source="employee-handbook.pdf",
            content="Full-time employees receive 15 days of paid vacation per year.",
            score=0.92,
        ),
    ]
    return answer, sources


# =============================================================================
# FastAPI Setup
# =============================================================================

app = FastAPI(title="HR Policy Agent")
router = APIRouter()


# =============================================================================
# API Routes
# =============================================================================


@router.post("/ask", response_model=RAGResponse)
def ask_question(request: RAGRequest):
    """Ask the HR Policy Agent a question."""
    answer, sources = ask_agent(
        question=request.question,
        search_limit=request.limit,
    )

    return RAGResponse(
        question=request.question,
        answer=answer,
        sources=sources,
    )


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# =============================================================================
# HTML Chat Interface
# =============================================================================

CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HR Policy Assistant</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f5; }
        header { background: #1a1a2e; color: white; padding: 1rem; text-align: center; }
        .chat-container { max-width: 800px; margin: 0 auto; padding: 1rem; height: calc(100vh - 160px); overflow-y: auto; }
        .message { display: flex; gap: 1rem; margin-bottom: 1rem; padding: 1rem; background: white; border-radius: 8px; }
        .message.user { background: #e3f2fd; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #1a1a2e; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }
        .message.user .avatar { background: #2196f3; }
        .content { flex: 1; }
        .sources { margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #eee; font-size: 0.85rem; color: #666; }
        .input-container { position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem; background: white; border-top: 1px solid #ddd; display: flex; gap: 0.5rem; }
        .input-container input { flex: 1; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        .input-container button { padding: 0.75rem 1.5rem; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .input-container button:hover { background: #2d2d4a; }
        .loading { display: flex; gap: 4px; padding: 1rem; }
        .loading span { width: 8px; height: 8px; background: #666; border-radius: 50%; animation: bounce 1.4s infinite; }
        .loading span:nth-child(2) { animation-delay: 0.2s; }
        .loading span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%, 80%, 100% { transform: translateY(0); } 40% { transform: translateY(-10px); } }
    </style>
</head>
<body>
    <header>
        <h1>HR Policy Assistant</h1>
    </header>

    <div id="chat" class="chat-container">
        <div class="message">
            <div class="avatar">AI</div>
            <div class="content">
                <p>Welcome! I can help you find information about HR policies, benefits, vacation, and more. What would you like to know?</p>
            </div>
        </div>
    </div>

    <form id="form" class="input-container">
        <input type="text" id="input" placeholder="Ask about HR policies..." autocomplete="off">
        <button type="submit">Send</button>
    </form>

    <script>
        const chat = document.getElementById('chat');
        const form = document.getElementById('form');
        const input = document.getElementById('input');

        function addMessage(role, content, sources = []) {
            const div = document.createElement('div');
            div.className = `message ${role}`;

            const renderedContent = role === 'assistant' ? marked.parse(content) : content;
            let sourcesHtml = '';
            if (sources.length > 0) {
                const names = [...new Set(sources.map(s => s.source.split('/').pop()))];
                sourcesHtml = `<div class="sources">Sources: ${names.join(', ')}</div>`;
            }

            div.innerHTML = `
                <div class="avatar">${role === 'user' ? 'You' : 'AI'}</div>
                <div class="content">${renderedContent}${sourcesHtml}</div>
            `;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function addLoading() {
            const div = document.createElement('div');
            div.id = 'loading';
            div.className = 'loading';
            div.innerHTML = '<span></span><span></span><span></span>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function removeLoading() {
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const question = input.value.trim();
            if (!question) return;

            addMessage('user', question);
            input.value = '';
            addLoading();

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });

                const data = await response.json();
                removeLoading();
                addMessage('assistant', data.answer, data.sources);
            } catch (error) {
                removeLoading();
                addMessage('assistant', 'Sorry, I could not connect to the server.');
            }
        });

        input.focus();
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def chat_ui():
    """Serve the chat interface."""
    return CHAT_HTML


# Include router
app.include_router(router)


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("Starting HR Policy Agent...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
