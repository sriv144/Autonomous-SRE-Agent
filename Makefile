.PHONY: help install test lint dev down ingest clean

help:
	@echo "KubeSentient — common dev targets"
	@echo "  make install   — poetry install"
	@echo "  make test      — run pytest suite (all mocked)"
	@echo "  make dev       — docker compose up --build (api + weaviate)"
	@echo "  make down      — docker compose down"
	@echo "  make ingest    — ingest runbooks/ into Weaviate"
	@echo "  make clean     — remove caches"

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run python -m compileall src tests scripts

dev:
	docker compose up --build

down:
	docker compose down

ingest:
	docker compose exec api python -m scripts.ingest_runbooks

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache __pycache__ \
	       src/**/__pycache__ tests/**/__pycache__
