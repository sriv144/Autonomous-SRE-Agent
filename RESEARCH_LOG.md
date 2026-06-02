# Research Log

This log tracks autonomous-research / auto-improvement passes over the
repository. Each entry records what was scored, what was implemented,
and what was deliberately skipped, so future runs can avoid re-doing
work that has already shipped.

## 2026-06-02 — Auto-Researcher v4

### Resume-worthiness score at start of run

`82 / 100` — ranked #3 of 6.

Breakdown:

- Tech stack prestige: 22 / 25 — LangGraph agent workflow, Weaviate
  RAG with `text2vec-openai`, Kubernetes / Helm deploy story.
- Commit recency: 20 / 25.
- Feature completeness: 18 / 20 — End-to-end demo (AlertManager
  webhook → triage → investigator → planner → approval) is wired up
  and there is a fully-mocked test suite.
- Stars / visibility: 8 / 15.
- README quality: 14 / 15 — Clear architecture diagram, Docker /
  Helm / local-dev paths, env var reference, verification checklist.

### Implemented on branch `claude/fervent-edison-MN9a4`

- **ci: add `.github/workflows/ci.yml`.** Installs Poetry, caches the
  in-project `.venv` keyed on `poetry.lock`, then runs the existing
  mocked pytest suite (`tests/test_agent_flow.py`, `test_api.py`,
  `test_rag.py`, `test_tools.py`) on Python 3.11 and 3.12. The
  README already documents `poetry run pytest tests/ -v` as the
  supported command, and the suite is described as "all mocked, no
  external services needed" — so wiring it into CI is a free quality
  signal. `OPENAI_API_KEY` is set to a placeholder so any code that
  reads it during import does not crash, but real OpenAI calls remain
  mocked.
- **docs: seed this `RESEARCH_LOG.md`.**

### Evaluated and skipped

- Adding a `helm lint` job. Skipped this pass because the chart layout
  was not deeply inspected; queued.
- Adding a Dockerfile build / `docker compose config` validation job.
  Skipped to keep this commit minimal; queued.
- Migrating the LLM call from OpenAI `gpt-4-turbo-preview` to Claude.
  This would change runtime behavior and is exactly the kind of
  change that needs a deliberate PR with parallel runs, not an
  auto-researcher edit. Queued.
- Touching any `src/` code. Skipped to keep this commit risk-free.

### Candidates for next run

1. Add a `helm lint` + `helm template` job so the chart is validated
   on every push.
2. Add a Docker build job that builds the image but does not push, so
   `Dockerfile` regressions surface in CI.
3. Migrate the agent's LLM client to Claude (`langchain-anthropic` or
   the official `anthropic` SDK) behind a provider-selector env var,
   with parallel mocked tests for both providers.
4. Swap Weaviate's `text2vec-openai` for an Anthropic-friendly
   embedding path (sentence-transformers or `text2vec-cohere`) so the
   stack is not OpenAI-coupled at the embedding layer either.
5. Add a small load-test workflow (`hey` or `locust`) that fires N
   synthetic AlertManager webhooks at the local API and asserts the
   p99 stays under a budget.
