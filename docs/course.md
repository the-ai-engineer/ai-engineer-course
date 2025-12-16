# The AI Architect Program

## Complete Course Outline (V1)

---

# Module 1: Foundations

**Goal:** Understand the landscape. Get running fast. Build your first tool-calling assistant.

**Lessons:**

### Lesson 1: Introduction to AI Engineering
- What is an AI Engineer? The progression: Software Engineer → AI Engineer → AI Architect
- The course philosophy: first principles before frameworks
- What kind of systems can you build with LLMs
- Real-world examples (Klarna, GitHub Copilot, Cursor, NotebookLM)
- What LLMs are (just enough theory to be dangerous)
- Overview of what you'll build in this course

### Lesson 2: Your First API Call
- Development environment setup (Python 3.11+, uv, VS Code/Cursor)
- Getting your Gemini API key
- Project structure
- First API call — hello world with Gemini
- Anatomy of request/response
- Model parameters (temperature, max tokens, top_p)

### Lesson 3: Prompt Engineering
- Prompt structure (system, user, assistant roles)
- Core patterns: extraction, classification, generation, transformation
- Few-shot examples
- Context engineering: managing what the model sees

### Lesson 4: Structured Outputs
- The problem: parsing free text is fragile
- Pydantic models for type-safe responses
- Schema design principles
- Handling validation errors

### Lesson 5: Multi-Modal Inputs
- Working with images
- Working with audio
- Working with PDFs/documents
- When to use multi-modal vs text extraction

### Lesson 6: Production Concerns
- Streaming for better UX
- Error handling and common failures
- Retry with exponential backoff
- Async for concurrent calls
- Rate limiting

### Lesson 7: Tool Calling
- What is tool calling and why it matters
- Defining tool schemas
- The tool call loop: request → tool call → execute → respond
- Handling multiple tool calls
- Error handling in tools

### Lesson 8: Building a Conversational Agent
- Managing conversation history
- Context window limits and truncation strategies
- System prompts for personality and constraints
- Putting it together: multi-turn + tools

**Project:** Timezone Meeting Assistant
- CLI chat interface
- Tools: get_current_time, convert_time, find_meeting_time
- Multi-turn conversation with history
- Structured output for meeting proposals

---

# Module 2: Workflows & Agents

**Goal:** Build multi-step systems and reasoning agents. All by hand, no frameworks.

**Lessons:**

### Lesson 1: From SDK Calls to Agents
- The progression: SDK calls → Workflows → Agents
- When to use each pattern
- Design patterns for AI systems
- Decision framework

### Lesson 2: Workflows
- Definition: deterministic, multi-step AI pipelines
- Sequential, parallel, and conditional patterns
- Passing data between steps

### Lesson 3: Event-Driven & Async Patterns
- Polling vs webhooks vs queues
- Async processing patterns
- Error handling and retries

### Lesson 4: The Agent Loop
- What is an agent?
- The loop: Perceive → Think → Act → Observe
- ReAct pattern
- Building from scratch (no frameworks)
- Exit conditions

### Lesson 5: Passing State
- Simple state patterns (Pydantic models, dataclasses)
- State through workflows
- State through agent loops
- Persisting state

**Project:** Email Classifier Pipeline — Ingest → Classify → Route → Respond

---

# Module 3: RAG Fundamentals

**Goal:** Master retrieval. Vector search and hybrid search with Postgres.

**Lessons:**

### Lesson 1: Why RAG Matters
- The problem: LLMs don't know your data
- RAG vs fine-tuning vs prompting
- RAG architecture overview

### Lesson 2: Embeddings
- What are embeddings?
- Generating embeddings with the SDK
- Similarity metrics

### Lesson 3: Document Processing & Chunking
- Document parsing (PDF, markdown, text)
- Chunking strategies
- Metadata preservation

### Lesson 4: Vector Storage with pgvector
- Setting up Postgres with pgvector
- Creating tables, inserting vectors
- Indexing (IVFFlat, HNSW)

### Lesson 5: Vector Search
- Similarity search with pgvector
- Top-k retrieval
- Filtering with metadata

### Lesson 6: Hybrid Search
- Why full-text search still matters
- Postgres tsvector and tsquery
- Combining vector and full-text
- Reciprocal Rank Fusion

**Project:** Document Search CLI — Ingest docs, vector search, hybrid search

---

# Module 4: RAG Agent with ADK

**Goal:** Introduce Google ADK. Build a production RAG agent.

**Lessons:**

### Lesson 1: Introduction to Google ADK
- What is ADK?
- ADK vs hand-built: trade-offs
- Setting up ADK

### Lesson 2: ADK Agents & Tools
- Defining agents
- Tool definition
- Agent configuration

### Lesson 3: ADK Memory & State
- Built-in memory
- Session management
- Persisting state

### Lesson 4: Generation with Retrieved Context
- Injecting documents into prompts
- Context window management
- Citations & attribution

### Lesson 5: Building the RAG Agent
- Retrieval as a tool
- Multi-turn conversations
- Query rewriting

**Project:** Postgres RAG Agent — Full RAG agent with ADK, hybrid search, citations

---

# Module 5: Evals, Testing & Monitoring

**Goal:** Make it production-grade. Test it, measure it, monitor it.

**Lessons:**

### Lesson 1: Why Evals Matter
- The eval mindset
- What to measure in AI systems

### Lesson 2: Types of Evals
- Unit, integration, end-to-end
- LLM-as-judge
- Building eval datasets

### Lesson 3: Observability & Tracing
- What to log
- Introduction to Langfuse
- Debugging with traces

### Lesson 4: Cost Tracking & Optimization
- Understanding LLM costs
- Optimization strategies
- Budgets and alerts

### Lesson 5: Safety & Guardrails
- Types of risks (prompt injection, data leakage, unintended actions)
- Input validation, output filtering
- Human-in-the-loop patterns

**Project:** Eval Suite — Golden dataset, LLM-as-judge, Langfuse integration

---

# Module 6: Deploying to Production

**Goal:** Ship it. Your system running in the cloud.

**Lessons:**

### Lesson 1: Cloud Architecture for AI Applications
- Designing for production
- Components and scaling

### Lesson 2: Containerization with Docker
- Dockerfile for your RAG agent
- Docker Compose for local dev

### Lesson 3: Deploying to Cloud
- Vertex AI deployment
- Azure deployment (alternative)
- Database in cloud

### Lesson 4: CI/CD & Monitoring
- GitHub Actions pipeline
- Automated tests
- Monitoring, alerting, health checks

**Project:** Production RAG Agent — Dockerized, deployed, CI/CD, monitoring

---

# Course Summary

| Module | Lessons | Project |
|--------|---------|---------|
| 1: Foundations | 8 | Timezone Meeting Assistant |
| 2: Workflows & Agents | 5 | Email Classifier Pipeline |
| 3: RAG Fundamentals | 6 | Document Search CLI |
| 4: RAG Agent with ADK | 5 | Postgres RAG Agent |
| 5: Evals & Monitoring | 5 | Eval Suite |
| 6: Deployment | 4 | Production RAG Agent |
