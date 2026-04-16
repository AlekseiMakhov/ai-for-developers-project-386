.PHONY: setup test lint up down migrate seed test-api test-web test-e2e

# ── CI targets (run inside the built container) ───────────────────────────────

setup:
	@echo "Setup complete"

test:
	pytest tests/ -v

lint:
	ruff check .

# ── Local development (requires docker compose) ───────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec -T api alembic upgrade head

seed:
	docker compose exec -T api python scripts/seed.py

test-api:
	docker compose exec -T api pytest

test-web:
	cd apps/web && npm run test

test-e2e:
	cd apps/web && npx playwright test
