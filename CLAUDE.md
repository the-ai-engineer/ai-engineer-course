# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This project requires Python 3.13 and uses uv for dependency management.

To set up the development environment:
```bash
# Install dependencies using uv
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Set up environment variables
cp .env-sample .env
# Edit .env and add your OPENAI_API_KEY
```

## Running Examples

The project contains AI engineering examples that demonstrate OpenAI API usage:

```bash
# Run individual examples
python src/1-client.py          # Basic OpenAI client usage
python src/2-async-client.py    # Async client patterns
python src/3-structured-output.py  # Structured output with Pydantic
python src/4-function_calling.py   # Function calling with tools
```

## Project Architecture

This is an AI engineering course repository with practical examples organized as standalone scripts:

- **`src/`** - Contains numbered examples demonstrating progressive AI engineering concepts
- **Dependencies** - Uses OpenAI SDK, Pydantic for structured data, and requests for HTTP calls
- **Environment** - Requires OPENAI_API_KEY environment variable for API access

## Key Patterns

The examples demonstrate:
- OpenAI client instantiation and basic completions
- Async/await patterns for concurrent operations
- Structured output parsing using Pydantic models
- Function calling with external APIs (weather data)
- Error handling and response processing

When working with these examples, ensure the OpenAI API key is properly configured in the `.env` file.