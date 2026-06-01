# Research Log

This log tracks autonomous-research improvements applied to this repository.
Each run records what was implemented, what was considered and skipped, and
what the next candidate improvements are. Do not delete entries; append new ones.

## 2026-06-01 — Auto-Researcher v4

**Resume-worthiness score at start of run:** ~78 / 100

KubeSentient is in great shape end-to-end: LangGraph workflow,
FastAPI + AlertManager webhook integration, Weaviate RAG runbook search,
Docker Compose + Helm chart, a thorough README, an `ARCHITECTURE.md`,
a `.env.example`, and a `tests/` directory described as fully mocked.
The one missing piece that would visibly validate all of the above on PR
was a CI workflow.

### What was implemented

Branch: `claude/fervent-edison-nPZT4`

- **`.github/workflows/ci.yml`** — Poetry-based CI that:
  - runs on push/PR to `main`
  - cancels superseded runs via the standard `concurrency` group
  - installs Python 3.11, Poetry 1.7.1, and the `dev` dependency group
    (pytest, pytest-asyncio, black, isort, mypy — all already declared in
    `pyproject.toml`)
  - caches the in-project `.venv` keyed off `poetry.lock` + `pyproject.toml`
  - exports placeholder `OPENAI_API_KEY` / `WEAVIATE_URL` so any client that
    asserts on environment presence still imports cleanly. Tests are
    described in the README as fully mocked, so no real services are needed.
  - runs black `--check`, isort `--check-only`, and `mypy src` with
    `continue-on-error: true` while style/typing converge
  - runs `pytest tests/ -v` as the gating step
- **`RESEARCH_LOG.md`** — seeded (this file).

### Why this was prioritized

For an SRE-adjacent showcase project the absence of CI is the single
loudest negative signal — the whole point is reliability. The fix is
purely additive: it does not touch application code, and every tool it
calls (black, isort, mypy, pytest) is already declared in `pyproject.toml`.

### What was evaluated and skipped

- **Docker build smoke test in CI.** Promising but slow on every PR. Better
  as a `workflow_dispatch` or release-only job; deferred.
- **Helm lint / `kubeval`.** Same reasoning — cheap to add later, not blocking.
- **Live Weaviate via service container.** Skipped because the test suite is
  documented as fully mocked. Spinning up Weaviate per-PR would burn minutes
  for no signal.
- **Tightening to fail-on-style.** Out of scope for the same reason as on the
  embodied-skill-composer repo — land CI first, ratchet later.
- **README badge.** Will be a one-liner follow-up once the first green run
  exists on `main`.

### Next-run candidates

1. Add a `workflow_dispatch` job that builds the Docker image and runs the
   `scripts/ingest_runbooks.py` smoke against an ephemeral Weaviate service
   container.
2. Add `helm lint helm/` + `kubeval` against the rendered manifests.
3. Remove `continue-on-error` from the black / isort / mypy steps once the
   first run shows their current status.
4. Add coverage reporting (`pytest-cov` + Codecov upload) and a README badge.
5. Feature work: real human-approval flow (currently mocked at `human_approval`
   node) wired to a Slack interactivity webhook — turns the project from a
   plan generator into a closed-loop SRE.
