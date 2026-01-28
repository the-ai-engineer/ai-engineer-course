# Customer Support Q&A System

A production-ready RAG (Retrieval-Augmented Generation) Q&A system for customer support. Built as a teaching example for the AI Engineering course.

See `docs/PRD.md` for the full specification.

## Tech Stack

**Backend**
- Python + FastAPI
- PydanticAI (agent framework)
- PostgreSQL + pgvector (vector database)
- OpenAI API (embeddings + generation)

**Frontend**
- Next.js 16+
- TypeScript
- ShadCN/UI components
- Tailwind CSS

## Features

- Streaming responses via Server-Sent Events (SSE)
- Hybrid search (vector + keyword) with Reciprocal Rank Fusion
- Source citations for transparency
- Clean, responsive chat UI

## Prerequisites

- Python 3.11+
- Node.js 18+ or Bun
- Docker and Docker Compose
- OpenAI API key

## Quick Start

### 1. Setup Environment

```bash
cd projects/week-4-rag-chatbot

# Copy environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start the Database

```bash
docker compose up -d
```

This starts PostgreSQL 16 with pgvector extension.

### 3. Install Dependencies

```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
bun install
```

### 4. Ingest Documents

```bash
cd backend
uv run python scripts/ingest.py ../docs
```

This processes the sample documents and creates embeddings.

### 5. Start the Application

In separate terminals:

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
bun dev
```

Visit http://localhost:4567 to use the chatbot.

## Project Structure

```
week-4-rag-chatbot/
├── docs/
│   ├── PRD.md                 # Product requirements
│   └── support/               # Sample support documentation
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Settings
│   │   ├── database.py        # Database connection
│   │   ├── api/
│   │   │   ├── chat.py        # Chat endpoint (SSE)
│   │   │   └── health.py      # Health check
│   │   ├── services/
│   │   │   ├── search.py      # Hybrid search
│   │   │   └── embeddings.py  # OpenAI embeddings
│   │   └── agent/
│   │       └── agent.py       # PydanticAI agent
│   └── scripts/
│       └── ingest.py          # Document ingestion
├── frontend/
│   └── src/
│       ├── app/               # Next.js pages
│       ├── components/        # React + ShadCN components
│       └── lib/               # API client
└── docker-compose.yml
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Streaming chat (SSE) |

### POST /api/chat

**Request:**
```json
{
  "message": "What pricing plans do you offer?"
}
```

**Response:** Server-Sent Events stream
```
event: token
data: {"content": "We"}

event: token
data: {"content": " offer"}

...

event: done
data: {"sources": [{"source": "billing.md", "content": "...", "score": 0.85}]}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `DATABASE_URL` | `postgresql://...` | Database connection URL |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `GENERATION_MODEL` | `gpt-4o-mini` | Generation model |

## How It Works

1. User asks a question
2. PydanticAI agent receives the question
3. Agent calls `search_docs` tool with a search query
4. Hybrid search retrieves relevant chunks from PostgreSQL
5. Agent generates an answer based on retrieved context
6. Response streams back to the UI via SSE
7. Sources are displayed after the response

## Adding Your Own Documents

1. Place documents in `docs/` (supports `.md`, `.txt`, `.pdf`, `.docx`)
2. Run `uv run python scripts/ingest.py ../docs` from the backend directory
3. The chatbot will now answer questions about your documents

## Deploy to Render

This project includes a `render.yaml` blueprint for one-click deployment.

### Steps

1. Push this repo to GitHub
2. Create a Render account at [render.com](https://render.com)
3. Click "New" > "Blueprint" and connect your repo
4. Render auto-detects `render.yaml` and provisions:
   - PostgreSQL database with pgvector
   - Backend API service
   - Frontend web service
5. Set `OPENAI_API_KEY` in the backend service environment variables
6. After deployment, initialize the database:

```bash
# Option 1: Use Render Shell (in dashboard)
cd /app && python scripts/init_db.py

# Option 2: Use Render CLI
render ssh rag-chatbot-backend
python scripts/init_db.py
```

7. Ingest your documents:

```bash
python scripts/ingest.py docs/
```

8. Visit your frontend URL (e.g., `https://rag-chatbot-frontend.onrender.com`)

### Environment Variables

The blueprint configures most variables automatically. You only need to set:

| Variable | Where to Set | Description |
|----------|--------------|-------------|
| `OPENAI_API_KEY` | Backend service | Your OpenAI API key |

### Notes

- Free tier Postgres includes pgvector support
- Services get HTTPS automatically
- Auto-deploy triggers on push to main branch
- First deploy may take a few minutes while Docker images build

## Out of Scope

This example intentionally excludes:
- User authentication
- Conversation history/sessions
- Multi-tenancy
- Rate limiting
- Caching

See `docs/PRD.md` for rationale and the "Further Work" lesson for how to add these features.
