.PHONY: setup db migrate seed api web test lint

setup:  ## Install backend and web dependencies
	cd backend && uv sync
	cd web && pnpm install

db:  ## Start Postgres in Docker
	docker compose up -d db

migrate:  ## Apply database migrations
	cd backend && uv run alembic upgrade head

seed:  ## Load reference data and demo asks/bids/price history
	cd backend && uv run pvf seed-reference && uv run pvf seed-demo

api:  ## Run the API on :8000
	cd backend && uv run uvicorn pvf.api.main:app --reload --port 8000

web:  ## Run the web app on :3000
	cd web && pnpm dev

test:  ## Run all tests and checks
	cd backend && uv run ruff check . && uv run pytest -q
	cd web && pnpm lint && pnpm build
