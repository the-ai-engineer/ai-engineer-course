# CLAUDE.md

## Project Overview

This is an AI engineering course teaching from first principles. No frameworks.

## Structure

```
ai-engineer-course/
├── module-1/          # LLM Fundamentals
├── module-2/          # RAG Systems
├── project-1-*/       # Hands-on projects
└── docs/              # Course documentation
```

Each module has its own `pyproject.toml` for uv.

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
- Emojis in code
- f-strings without substitutions
- Unnecessary complexity
- Over-abstraction

## Running Code

```bash
cd module-1
uv sync
uv run python 1-setup.py
```

## Key Files

- `docs/ROADMAP.md` - Master plan
- `docs/LESSON_WRITING_GUIDE.md` - How to write lessons
- `.cursorrules` - AI assistant guidelines
