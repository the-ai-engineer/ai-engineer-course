# AI Architect Course

Learn to build production-ready AI applications from first principles. No frameworks until you understand what they abstract. No magic - just engineering.

## What You'll Learn

Over 6 weeks, you'll go from your first API call to building a fully functional RAG agent:

| Week | Focus | What You'll Build |
|------|-------|-------------------|
| [Week 1](week-1/) | **Foundations** | Your first Gemini API call |
| [Week 2](week-2/) | **SDK Mastery** | Timezone assistant with tools |
| [Week 3](week-3/) | **Patterns** | Email processing pipeline |
| [Week 4](week-4/) | **Agents** | Terminal agent that runs commands |
| [Week 5](week-5/) | **RAG Systems** | Document retrieval pipeline |
| [Week 6](week-6/) | **RAG Agent** | Document Q&A with citations |

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/owainlewis/ai-engineer-course.git
cd ai-engineer-course
```

### 2. Install uv (Python Package Manager)

We use [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management.

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Get Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key" and create a new key
3. Copy the key somewhere safe

### 4. Run Your First Example

```bash
cd week-1
uv sync
export GOOGLE_API_KEY="your-api-key-here"
uv run python code/01_hello_gemini.py
```

If you see a poem about AI, you're all set.

## How the Course Works

Each week has its own folder with:
- A **README** explaining the concepts
- **Code examples** you can run and modify
- A **project** that brings it all together

The process for each week:
1. Read through the concepts in the README
2. Run each code example and see what it does
3. Modify the code and experiment
4. Build the week's project
5. Move to the next week

### Pacing

We recommend completing one week per week to build momentum. That said, life happens - the materials aren't going anywhere. Go at whatever pace works for you.

Each week takes roughly 5-10 hours depending on your experience. Some weeks are lighter (Week 1), others heavier (Week 4-6).

### What's in Each Week

Every week combines conceptual understanding with hands-on practice:

- **Concepts** - Short explanations of what you're learning and why it matters
- **Code examples** - Working code you run locally, organized from simple to complex
- **Projects** - A practical application combining everything from that week

The code examples are designed to be read and modified. Don't just run them - change things, break them, see what happens. That's where the real learning happens.

## Prerequisites

- **Python basics** - functions, classes, dictionaries
- **Command line comfort** - cd, ls, running scripts
- **A Google account** - for your API key
- **~$5-10** for API costs (generous free tier available)

## Tech Stack

- **Python 3.11+** with uv for dependency management
- **Gemini API** via google-genai SDK
- **PostgreSQL + pgvector** for vector storage (weeks 5-6)

## Need Help?

Join the community at **https://skool.com/aiengineer** for:
- Help when you're stuck
- Code reviews and feedback
- Discussion with other AI engineers

## Philosophy

**Build real systems, not demos.** Every project runs and goes in your portfolio.

**Principles over frameworks.** Frameworks change. Understanding doesn't.

**Learn by doing.** Write code, break things, fix them.

---

Ready? Head to [Week 1](week-1/) and make your first API call.
