.PHONY: db-up db-down backend frontend ingest test clean

# Database
db-up:
	docker compose up -d

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d

# Backend
backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
frontend:
	cd frontend && bun dev

# Document ingestion
ingest:
	cd backend && uv run python scripts/ingest.py ../docs

# Testing
test:
	cd backend && uv run pytest -v

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
