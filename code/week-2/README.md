# Week 2: Workflows & Agents

Code examples for Module 2 of the AI Architect Program.

## Setup

```bash
cd code/week-2
uv sync
```

Create a `.env` file with your Gemini API key:

```
GOOGLE_API_KEY=your-key-here
```

## Running Examples

```bash
uv run python 02_workflows.py
```

## Code Index

| File | Lesson | Description |
|------|--------|-------------|
| `02_workflows.py` | Workflows | Sequential, parallel, conditional patterns |
| `03_queues.py` | Queues and Async | Background processing with Redis Queue |
| `04_agent_loop.py` | The Agent Loop | ReAct pattern agent from scratch |
| `05_state.py` | Passing State | Pydantic models, persistence, checkpointing |

## Project

The week 2 project (Email Classifier) is in `projects/week-2-email-classifier/`.
