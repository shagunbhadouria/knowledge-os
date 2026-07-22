.PHONY: dev test lint seed build pull-models

dev:
	docker compose up --build

test:
	docker compose run --rm omnirag-api pytest

lint:
	docker compose run --rm omnirag-api ruff check app tests conftest.py
	docker compose run --rm omnirag-api ruff format --check app tests conftest.py
	docker compose run --rm omnirag-api mypy app

seed:
	docker compose run --rm omnirag-api python -m app.database.seeds

build:
	docker build --target production -t omnirag-api:latest .

pull-models:
	docker compose exec ollama ollama pull llama3
