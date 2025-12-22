# Week 2: Workflows & Agents

Code examples for Module 2 of the AI Architect Program.

## Setup

```bash
cd code/python/week-2
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
uv run python 02_workflows.py
```

## Code Index

| File | Description |
|------|-------------|
| `02_workflows.py` | Sequential, parallel, conditional patterns |
| `04_agent_loop.py` | Agent class + human-in-the-loop approval |

## Project

The week 2 project (Email Classifier) is in `projects/week-2-email-classifier/`.
