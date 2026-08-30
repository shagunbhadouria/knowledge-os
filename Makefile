.PHONY: dev test test-integration lint seed migrate build pull-models

dev:
	docker compose up --build

test:
	docker compose run --rm omnirag-api pytest -m "not integration"

test-integration:
	docker compose run --rm omnirag-api pytest -m integration

lint:
	docker compose run --rm omnirag-api ruff check app tests conftest.py
	docker compose run --rm omnirag-api ruff format --check app tests conftest.py
	docker compose run --rm omnirag-api mypy app

seed:
	docker compose run --rm omnirag-api python -m app.database.seeds

migrate:
	docker compose run --rm omnirag-api python -c \
		"import asyncio; from app.database.schema import apply_schema; from app.database.mongodb import ensure_vector_search_index; from app.database.redis import ensure_streams; \
asyncio.run(apply_schema()); asyncio.run(ensure_vector_search_index()); asyncio.run(ensure_streams())"

build:
	docker build --target production -t omnirag-api:latest .

pull-models:
	docker compose exec ollama ollama pull llama3
