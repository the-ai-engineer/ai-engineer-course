# Email Classifier

Classify emails using structured output. Works with sample data or real Gmail.

## Quick Start

```bash
cd projects/week-2-email-classifier
uv sync

# Run with sample emails (no setup needed)
uv run python pipeline.py

# Run with real Gmail (requires OAuth setup)
uv run python pipeline.py --gmail
```

## What It Does

- Classifies emails into: support, sales, spam, newsletter, personal
- Uses Gemini's structured output for reliable JSON
- Includes sample emails so you can test without Gmail

## Gmail Setup (Optional)

1. Create a Google Cloud project and enable Gmail API
2. Create OAuth 2.0 credentials (Desktop app)
3. Download `credentials.json` to this folder
4. Copy `.env-sample` to `.env` and add your API key
5. First run opens browser for Gmail consent

## Files

- `pipeline.py` - Classification logic and sample emails
- `gmail.py` - Gmail API authentication and fetching
