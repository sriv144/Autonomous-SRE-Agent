# Research Log

This file tracks autonomous research and improvement runs against this
repository.

## 2026-05-21 — Auto-Researcher v4

**Resume score at start of run:** ~83 / 100 — top 3 of 6 across the portfolio.

**Branch:** `claude/fervent-edison-InUHR` (from `main`).

### Implemented

- **`.github/workflows/ci.yml`** — installs Poetry, restores a cached
  virtualenv, and runs the fully-mocked pytest suite (`test_agent_flow`,
  `test_api`, `test_rag`, `test_tools`) on Python 3.11 and 3.12 against every
  push and pull request to `main`. Sets `OPENAI_API_KEY=dummy-key-for-mocked-tests`
  so any client constructor reading it at import time succeeds. `main`
  previously had no CI signal.
- **`Makefile`** — wraps the recurring `poetry` / `docker compose` commands
  from the README (`install`, `test`, `dev`, `down`, `ingest`, `clean`)
  behind a discoverable `make help`.
- **MIT `LICENSE`** — the repo was previously unlicensed.
- **README status badges**, a CI section, and a Makefile reference.
- **Seeded this `RESEARCH_LOG.md`.**

### Why this was prioritized

KubeSentient already has the strongest operational surface in the portfolio
(LangGraph agent, Weaviate-backed runbook RAG, FastAPI, Helm chart, mocked
test suite, multi-stage Dockerfile). The remaining gaps on `main` were both
signal-only: no CI badge and no ergonomic task runner despite ~10 recurring
`docker compose` / `poetry run` invocations in the README. Both are
zero-risk additive changes that materially raise interview-grade polish.

### Evaluated and skipped

- **`helm lint helm/` + `docker compose config` validation in CI.** Worth
  doing in a follow-up; kept this run's diff focused on the test signal.
- **Pre-commit hooks (ruff/black/mypy).** `black`, `isort`, and `mypy` are
  in the dev group but no config is pinned; introducing hooks now would
  either fail on formatting drift or silently no-op. Punted to a config pass.
- **Env-var toggle for `local_mode` in `src/agent_core/tools.py:8`.** A small
  but behavioral change — belongs in a focused PR, not an additive run.

### Next-run candidates

- Add `helm lint helm/` and `docker compose config` validation to CI.
- Pin pre-commit + ruff/mypy config in `pyproject.toml`.
- Replace the hard-coded `local_mode` constant with an env-var toggle so the
  same image runs dev and prod.
- Add a demo screenshot or asciinema recording of the LangGraph workflow.
