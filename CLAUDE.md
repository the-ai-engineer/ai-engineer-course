# CLAUDE.md

## Project Overview

This is an AI engineering course teaching from first principles. No frameworks until Module 4 (PydanticAI).

## Course Structure

```
ai-engineer-course/
├── docs/                 # Course outline, templates
├── code/
│   ├── week-1/           # Module 1: Foundations (public)
│   ├── week-2/           # Module 2: Workflows & Agents
│   ├── week-3/           # Module 3: RAG Fundamentals
│   ├── week-4/           # Module 4: RAG Agent with PydanticAI
│   ├── week-5/           # Module 5: Evals & Monitoring
│   └── week-6/           # Module 6: Deployment
├── lessons/              # Lesson content (gitignored)
│   ├── week-1/
│   ├── week-2/
│   └── ...
└── projects/             # End-of-module projects
```

Each week folder has its own `pyproject.toml` for isolated dependencies.

See `docs/course.md` for full course outline.

## Lesson Structure

Every lesson follows this template (see `docs/lesson-template.md`):

```markdown
# Lesson Title

## What You'll Learn
- Bullet points of outcomes

## Why This Matters
- Real-world context
- How this fits the bigger picture

## Concepts
- Explanation with diagrams/examples
- Keep it practical, not academic

## Code Walkthrough
- Annotated explanation of the example code

## Common Mistakes
- What goes wrong, how to fix it

## Further Reading (Optional)
- Links for those who want depth
```

## Lesson Formatting

Keep formatting minimal for readability:

- Use headings, paragraphs, and lists only
- No excessive bold/italic
- No tables unless comparing options
- Use Mermaid for diagrams (renders on GitHub):

```mermaid
graph LR
    A[Input] --> B[Process] --> C[Output]
```

## Reference Documentation

Always consult these docs when writing code examples:

- **Google GenAI SDK**: https://googleapis.github.io/python-genai/
- **PydanticAI (Module 4+)**: https://ai.pydantic.dev/

## Code Guidelines

### Keep It Simple
- One concept per file
- Under 150 lines preferred
- Demo-friendly (can be run live)

### Python Style
- Python 3.11+
- Type hints on function signatures
- Docstrings on modules and key functions
- snake_case for functions, PascalCase for classes

### Formatting
- ruff format (88 char lines)
- Double quotes
- Imports: stdlib, then third-party, then local

### Comments
- Use section headers:
  ```python
  # =============================================================================
  # Section Name
  # =============================================================================
  ```
- Explain WHY, not WHAT

### Avoid
- Emojis in code or lessons
- f-strings without substitutions
- Unnecessary complexity
- Over-abstraction

## Running Code

```bash
cd code/week-1
uv sync
uv run python 01_hello_gemini.py
```

## Writing Style

All lesson content must follow the writing style guide: `docs/writing-style-guide.md`

Key rules:
- Write like you're talking to a smart friend
- Short paragraphs, one idea each
- Show code first, explain second
- No em dashes, no hedging, no academic tone
- Clear, not clever

## Key Files

- `docs/course.md` - Complete course outline
- `docs/writing-style-guide.md` - How to write lessons
- `code/week-*/` - Code samples (public)
- `lessons/week-*/` - Lesson markdown files (gitignored)
