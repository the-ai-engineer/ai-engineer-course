"""
Passing State

Managing state through workflows and agent loops using Pydantic models.
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

load_dotenv()

client = genai.Client()

# =============================================================================
# State Models
# =============================================================================


class DocumentState(BaseModel):
    """State for document processing workflow."""

    doc_id: str
    raw_text: str
    summary: str | None = None
    keywords: list[str] = []
    sentiment: str | None = None
    processed: bool = False


class AgentState(BaseModel):
    """State for agent loop."""

    goal: str
    iterations: int = 0
    tool_calls: list[dict] = []
    observations: list[str] = []
    final_answer: str | None = None
    completed: bool = False


# =============================================================================
# Workflow with State
# =============================================================================


def step_summarize(state: DocumentState) -> DocumentState:
    """Step 1: Generate summary."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Summarize in 2 sentences:\n\n{state.raw_text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return state.model_copy(update={"summary": response.text})


def step_keywords(state: DocumentState) -> DocumentState:
    """Step 2: Extract keywords."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Extract 5 keywords, comma-separated:\n\n{state.raw_text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    keywords = [k.strip() for k in response.text.split(",")]
    return state.model_copy(update={"keywords": keywords})


def step_sentiment(state: DocumentState) -> DocumentState:
    """Step 3: Analyze sentiment."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Sentiment (positive/negative/neutral):\n\n{state.raw_text}",
        config=types.GenerateContentConfig(temperature=0.0),
    )
    return state.model_copy(
        update={"sentiment": response.text.strip().lower(), "processed": True}
    )


def run_document_workflow(doc_id: str, text: str) -> DocumentState:
    """Run the full workflow, passing state between steps."""
    state = DocumentState(doc_id=doc_id, raw_text=text)
    state = step_summarize(state)
    state = step_keywords(state)
    state = step_sentiment(state)
    return state


# =============================================================================
# Persistence: JSON
# =============================================================================


def save_state_json(state: DocumentState, path: str = "state.json"):
    """Save state to JSON file."""
    with open(path, "w") as f:
        f.write(state.model_dump_json(indent=2))


def load_state_json(path: str = "state.json") -> DocumentState | None:
    """Load state from JSON file."""
    try:
        with open(path) as f:
            return DocumentState.model_validate_json(f.read())
    except FileNotFoundError:
        return None


# =============================================================================
# Persistence: SQLite
# =============================================================================


def init_db(db_path: str = "state.db"):
    """Initialize the database."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_states (
            doc_id TEXT PRIMARY KEY,
            state_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_state_db(state: DocumentState, db_path: str = "state.db"):
    """Save state to SQLite."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO document_states (doc_id, state_json, updated_at) VALUES (?, ?, ?)",
        (state.doc_id, state.model_dump_json(), datetime.now()),
    )
    conn.commit()
    conn.close()


def load_state_db(doc_id: str, db_path: str = "state.db") -> DocumentState | None:
    """Load state from SQLite."""
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT state_json FROM document_states WHERE doc_id = ?", (doc_id,)
    ).fetchone()
    conn.close()
    if row:
        return DocumentState.model_validate_json(row[0])
    return None


# =============================================================================
# Workflow with Checkpointing
# =============================================================================


def run_workflow_with_checkpoints(
    doc_id: str, text: str, db_path: str = "state.db"
) -> DocumentState:
    """Run workflow with checkpoints for resumability."""
    init_db(db_path)

    # Try to resume from checkpoint
    state = load_state_db(doc_id, db_path)

    if state is None:
        state = DocumentState(doc_id=doc_id, raw_text=text)
        save_state_db(state, db_path)

    # Run steps, checkpointing after each
    if state.summary is None:
        state = step_summarize(state)
        save_state_db(state, db_path)

    if not state.keywords:
        state = step_keywords(state)
        save_state_db(state, db_path)

    if state.sentiment is None:
        state = step_sentiment(state)
        save_state_db(state, db_path)

    return state


# =============================================================================
# Agent State Example
# =============================================================================


def update_agent_state(
    state: AgentState, tool_call: dict, observation: str
) -> AgentState:
    """Update agent state after a tool call."""
    return state.model_copy(
        update={
            "iterations": state.iterations + 1,
            "tool_calls": state.tool_calls + [tool_call],
            "observations": state.observations + [observation],
        }
    )


def complete_agent(state: AgentState, answer: str) -> AgentState:
    """Mark agent as completed with final answer."""
    return state.model_copy(update={"final_answer": answer, "completed": True})


# =============================================================================
# Example Usage
# =============================================================================

# Process a document through the workflow
text = """
Machine learning is revolutionizing drug discovery. AI models can screen
millions of compounds in hours instead of years. This accelerates the path
from lab to clinic, potentially saving billions in development costs.
"""

# Basic workflow
result = run_document_workflow("doc_001", text)
result

# Inspect state at any point
result.summary
result.keywords
result.sentiment

# Save to JSON
save_state_json(result, "doc_001.json")

# Load it back
loaded = load_state_json("doc_001.json")
loaded

# Workflow with checkpoints (can resume if interrupted)
result = run_workflow_with_checkpoints("doc_002", text)
result

# Agent state example
agent_state = AgentState(goal="What is 15% of 200?")
agent_state = update_agent_state(
    agent_state, {"tool": "calculate", "args": {"expr": "200 * 0.15"}}, "30"
)
agent_state = complete_agent(agent_state, "15% of 200 is 30")
agent_state
