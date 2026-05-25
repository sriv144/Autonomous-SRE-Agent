.PHONY: help install test lint up down logs ingest health

help:
	@echo "KubeSentient dev targets:"
	@echo "  make install   poetry install (local dev)"
	@echo "  make test      poetry run pytest tests/ -v"
	@echo "  make lint      ruff check src tests scripts"
	@echo "  make up        docker compose up --build (api + weaviate)"
	@echo "  make down      docker compose down"
	@echo "  make logs      docker compose logs -f api"
	@echo "  make ingest    docker compose exec api python -m scripts.ingest_runbooks"
	@echo "  make health    curl /health and /v1/.well-known/ready"

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check src tests scripts

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

ingest:
	docker compose exec api python -m scripts.ingest_runbooks

health:
	@curl -fsS http://localhost:8000/health && echo
	@curl -fsS http://localhost:8080/v1/.well-known/ready && echo
