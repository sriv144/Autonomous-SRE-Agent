# Research Log

This file tracks autonomous research and improvement runs against this
repository.

## 2026-04-27 — Auto-Researcher v4

**Resume score at start of run:** 76 / 100 — top 3 of 6 across the portfolio.

**Branch:** `claude/fervent-edison-snPHW`.

### Implemented

- Added `.github/workflows/ci.yml` that installs Poetry, restores a cached
  virtualenv, and runs the mocked pytest suite (`test_agent_flow`, `test_api`,
  `test_rag`, `test_tools`) on Python 3.11 and 3.12 against every push and
  pull request. The job sets `OPENAI_API_KEY=dummy-key-for-mocked-tests` to
  satisfy any client constructor that reads it at import time — the README
  states all tests are mocked.
- Added a top-level `Makefile` with the common dev targets used in the README
  (`install`, `test`, `dev`, `down`, `ingest`, `clean`). This shortens the
  onboarding loop and makes the README's docker-compose / poetry commands
  discoverable from `make help`.
- Seeded this `RESEARCH_LOG.md`.

### Why this was prioritized

KubeSentient already has the strongest *operational* surface in the portfolio
(LangGraph agent, Weaviate-backed runbook RAG, FastAPI, Helm chart, mocked test
suite, multi-stage Dockerfile). The remaining gaps were both signal-only:
there was no CI badge on the README and no ergonomic Makefile despite ~10
recurring `docker compose ...` and `poetry run ...` invocations in the README.
Both are zero-risk additions that materially raise interview-grade polish.

### Evaluated and skipped

- **Refactoring `agent_core/tools.py:8` to read `local_mode` from env instead
  of a hard-coded constant:** small but behavioral, deferred to a focused PR.
- **Adding a GitHub Actions workflow that runs Helm chart linting (`helm
  lint helm/`):** worth doing in a follow-up; skipped this run to keep the
  diff focused on test signal.
- **Adding pre-commit hooks (ruff/black/mypy):** repo doesn't currently pin
  any of those tools; introducing them would either fail immediately on
  formatting drift or silently no-op. Punted to a config-pinning pass.

### Next-run candidates

- Add `helm lint helm/` and `docker compose config` validation to CI.
- Pre-commit + ruff/mypy config in `pyproject.toml`.
- Replace the `local_mode=True` constant in `src/agent_core/tools.py` with an
  env-var-controlled toggle so the same image can run dev and prod.
- Add a short demo screenshot or asciinema recording of the LangGraph workflow
  to the README.
