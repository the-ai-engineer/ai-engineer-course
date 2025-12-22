# Timezone Agent

Week 1 Project: A terminal-based chat assistant for timezone questions.

## Setup

```bash
cd projects/week-1-timezone-agent
uv sync
```

Copy the sample env file and add your API key:

```bash
cp .env-sample .env
```

Get your API key at: https://aistudio.google.com/apikey

## Run

```bash
uv run python agent.py
```

## Example

```
Timezone Agent
Type 'quit' to exit

You: What time is it in Tokyo?
Assistant: It's currently 14:32 JST in Tokyo.

You: And in London?
Assistant: It's 05:32 GMT in London.

You: Convert 3pm Tokyo to New York time
Assistant: 15:00 Asia/Tokyo = 01:00 America/New_York
```
