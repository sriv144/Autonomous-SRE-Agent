# Research Log

This file tracks Auto-Researcher passes against this repository: what was
implemented, what was evaluated and skipped, and what is queued for next run.

## 2026-06-05 — Auto-Researcher v4

**Resume score at start of run:** 67 / 100

KubeSentient already had a strong README (8.5kb, ARCHITECTURE.md, Helm
chart, Dockerfile, docker-compose, runbooks, a real pytest suite). The
two conspicuous gaps were a missing LICENSE and no CI workflow — both
are cheap, high-trust additions that lift the public-facing impression
without touching agent code.

### Implemented (branch `claude/fervent-edison-eZfYm`)

- `LICENSE` (MIT) so the repo is legally usable / forkable.
- `.github/workflows/ci.yml`:
    - **ruff** `E9,F63,F7,F82` over `src/` and `tests/` for real syntax
      and undefined-name bugs.
    - `python -m compileall` belt-and-braces import-time smoke check.

### Why this was prioritized

LICENSE + CI signal are the two universal trust markers reviewers scan
for first. Zero behavior changes, zero new runtime dependencies. The
existing pytest suite calls into LangGraph + LangChain + Weaviate +
Kubernetes — wiring that into CI without API keys and a live cluster
would produce a permanently-red badge, so this run intentionally limits
CI to static checks that pass deterministically.

### Evaluated and skipped

- **Run pytest in CI.** `tests/test_rag.py` and `tests/test_agent_flow.py`
  hit live LangChain / Weaviate / LangGraph paths that need API keys and
  external services to be healthy. Adding them without service stubs
  guarantees a red badge. Deferred until a `tests/conftest.py` adds the
  right `pytest.importorskip` / monkeypatch shims.
- **Migrate from `langchain-openai` to an Anthropic-first provider.** Real
  value for the project, but it touches the prompt graph and rewires the
  agent's tool-calling contract. Out of scope for a safe-only run.
- **Add a `helm install` smoke test in CI.** Requires booting kind +
  rendering the chart; achievable but tangentially related to code quality.
  Deferred.

### Candidates for next run

1. Wire pytest into CI behind a `tests/conftest.py` that skips tests
   needing live external services when their env vars are missing.
2. Add a `helm lint && helm template` step that validates the chart on
   every PR — catches values.yaml drift without needing a cluster.
3. Add an Anthropic provider option behind `LLM_PROVIDER` env var; keep
   OpenAI as the default to avoid breaking existing deployments.
4. Add a Mermaid sequence diagram to ARCHITECTURE.md showing the
   alert → plan → act → verify control loop, then link it from README.
