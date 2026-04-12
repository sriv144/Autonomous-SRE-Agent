# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system deps for building if needed (e.g. gcc)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Application Code (optional in builder if just for venv, but good for caching)
# We won't copy src yet to keep layer cache optimized for deps
# COPY src ./src
# RUN poetry install --only-root

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create non-root user
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Copy virtualenv from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser src ./src

USER appuser

# Expose port (assuming FastAPI default)
EXPOSE 8000

# Default command (can be overridden in K8s)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
