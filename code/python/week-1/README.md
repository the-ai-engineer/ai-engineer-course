# Week 1: Foundations

Code examples for Module 1 of the AI Architect Program.

## Setup

```bash
cd code/python/week-1
uv sync
```

Copy the sample env file and add your API key:

```bash
cp .env-sample .env
```

Get your API key at: https://aistudio.google.com/apikey

For Vertex AI (Google Cloud), see `.env-sample` for ADC configuration.

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
| `05_multimodal.py` | Multi-Modal Inputs | Image analysis and generation |
| `06_production.py` | Production Concerns | Streaming, async, retry, error handling |
| `07_tools.py` | Tool Calling | Automatic function calling |

## Project

The week 1 project (Timezone Agent) is in `projects/week-1-timezone-agent/`.
