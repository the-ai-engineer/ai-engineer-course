# Week 1: Foundations

Code examples for Module 1 of the AI Architect Program.

## Setup

```bash
cd code/week-1
uv sync
```

Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your-key-here
```

## Running Examples

```bash
uv run python 02_api_basics.py
```

## Code Index

| File | Lesson | Description |
|------|--------|-------------|
| `02_api_basics.py` | Your First API Call | Basic calls, temperature, system instructions |
| `03_prompt_patterns.py` | Prompt Engineering | Extraction, classification, few-shot, delimiters |
| `04_structured_output.py` | Structured Outputs | Pydantic models, enums, nested objects |
| `05_multimodal.py` | Multi-Modal Inputs | Image analysis with Gemini |
| `06_production.py` | Production Concerns | Streaming, async, retry, error handling |
| `07_tools.py` | Tool Calling | Function tools and automatic calling |

## Project

The week 1 project (Timezone Agent) is in `projects/week-1-timezone-agent/`.
