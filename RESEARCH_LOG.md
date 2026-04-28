# Research Log

A running log of automated improvement runs against this repo.

## 2026-04-28 — Auto-Researcher v4

**Resume score (start of run):** 77 / 100

- Tech stack prestige: 22 (LangGraph, Weaviate, Kubernetes, RAG, Helm chart, AlertManager integration)
- Commit recency: 17 (pushed 2026-04-12)
- Feature completeness: 17 (real Docker stack, Helm chart, RAG ingestion, mocked tests, multi-stage Dockerfile)
- Stars / visibility: 7
- README quality: 14 (already excellent: architecture diagram, end-to-end smoke test, K8s deploy, env table)

### Implemented on `claude/fervent-edison-jnSqo`

1. **`.github/workflows/tests.yml`** — a Poetry-based CI workflow that:
   - Runs on push and PR to `main`, plus manual dispatch.
   - Sets up Python 3.11 and installs Poetry 1.8.3 via pipx.
   - Configures Poetry to use an in-project `.venv/` and caches it keyed on `poetry.lock` + `pyproject.toml`.
   - Runs `poetry install` then `poetry run pytest tests/ -v`.
   - Provides safe dummy values for `OPENAI_API_KEY`, `WEAVIATE_URL`, and `LOG_LEVEL` (the README explicitly states tests are fully mocked, no external services needed).
   - Uses a concurrency group so superseded pushes auto-cancel.
2. **This `RESEARCH_LOG.md`**.

### Why these were prioritized

- The README documents the exact `poetry run pytest tests/ -v` invocation as the canonical way to run tests. Wiring that into CI is a one-file change.
- Tests are fully mocked per the README — no need for a Weaviate or OpenAI service in CI.
- Pure additive change — no existing files modified, no behaviour change locally.
- Adds a green test signal to a project that already looks production-grade in the README; the CI badge will be a strong recruiter signal.

### Evaluated and skipped this run

- **Helm chart lint step** (`helm lint helm/`). Worth adding, but requires installing Helm in the runner. Logged for next run.
- **Docker image build smoke test** (`docker build -f Dockerfile .`). Real value, but adds 5+ minutes to CI runtime. Logged.
- **Switching the agent's LLM provider to Claude / Anthropic.** The codebase is already wired around `langchain-openai` / OpenAI embeddings + Weaviate's `text2vec-openai` module. A provider swap would touch the agent core and the Weaviate schema. Too risky for an unattended run.
- **README badges.** Will be added once the workflow produces a stable run.

### Next-run candidates

- Add CI status badge + Python-version badge to README after `tests.yml` runs at least once.
- Add a `helm lint` step to the existing CI workflow.
- Add a `docker build` smoke test (no push) to catch Dockerfile regressions.
- Add an Anthropic / Claude provider option behind an env flag, keeping OpenAI as the default to preserve existing behaviour.
- Document the runbook ingestion sources used in `runbooks/` (currently the README points outward but doesn't list what's already loaded).
