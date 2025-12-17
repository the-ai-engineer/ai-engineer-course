# Email Classifier Pipeline

Email classification and routing using Gmail API and Gemini.

## Setup

1. Create a Google Cloud project and enable Gmail API
2. Create OAuth 2.0 credentials (Desktop app)
3. Download `credentials.json` to this folder
4. Create `.env` with your Gemini API key:
   ```
   GOOGLE_API_KEY=your_key_here
   ```

## Run

```bash
uv sync
uv run python pipeline.py
```

First run will open a browser for Gmail authentication.

## Files

- `gmail.py` - Gmail API authentication and email fetching
- `pipeline.py` - Classification and routing pipeline
