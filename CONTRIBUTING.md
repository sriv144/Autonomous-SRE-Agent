# Contributing to KubeSentient

KubeSentient is an autonomous remediation agent that runs against real
Kubernetes clusters and live runbooks. Contributions must keep two properties
intact:

1. **Read-only by default.** Any new K8s tool added to `src/agent_core/tools.py`
   must default to read-only verbs (`get`, `list`, `watch`, `logs`, `events`).
   Anything that mutates cluster state (scale, restart, patch, delete) must be
   gated behind the human-approval node and an explicit allow-list.
2. **Plan-only output for unapproved actions.** The planner must emit a plan;
   it must not invoke remediation tools without passing through `human_approval`.

## Local setup

```bash
# With Docker (recommended)
cp .env.example .env       # set OPENAI_API_KEY
docker compose up --build
docker compose exec api python -m scripts.ingest_runbooks

# Without Docker (Poetry)
pip install poetry
poetry install
export OPENAI_API_KEY=sk-...
export WEAVIATE_URL=http://localhost:8080
poetry run uvicorn src.api.main:app --reload --port 8000
```

Run tests (fully mocked, no external services needed):

```bash
poetry run pytest tests/ -v
```

## Workflow

1. Open or claim an issue. Architecture-changing PRs (new node in the
   LangGraph workflow, new RAG store, replacing the LLM provider) need a
   short design discussion first.
2. Branch off `main`. Use Conventional Commits:
   - `feat:` new tool, node, or runbook source
   - `fix:` bug fix in agent / API / ingestion
   - `perf:` measurable latency or token reduction
   - `refactor:` no behaviour change
   - `docs:`  docs only
3. If you add a new agent tool, add a unit test that mocks the K8s client
   and asserts the tool is read-only.
4. If you add or change a runbook, re-run `python -m scripts.ingest_runbooks`
   and include the resulting chunk count in the PR description.

## Code style

- Python 3.11+. Type-hint public functions.
- Keep LangGraph node functions short — push business logic into helpers
  under `src/agent_core/`.
- Never log raw `OPENAI_API_KEY` or `KUBECONFIG` contents.

## Reporting security issues

See `SECURITY.md`. Do not file public issues for vulnerabilities that affect
the K8s tool surface or credential handling.
