.PHONY: help install test dev down ingest clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies via Poetry
	poetry install

test: ## Run the fully-mocked pytest suite
	poetry run pytest tests/ -v

dev: ## Build and start the local docker-compose stack
	docker compose up --build

down: ## Stop and remove the docker-compose stack
	docker compose down

ingest: ## Ingest runbooks into the running Weaviate instance
	docker compose exec api python -m scripts.ingest_runbooks

clean: ## Remove Python caches and test artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache
