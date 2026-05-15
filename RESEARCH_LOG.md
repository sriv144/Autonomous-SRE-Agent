# Research Log

This file tracks autonomous research and improvement runs against this repo.
Each run lists what was implemented, what was evaluated and skipped, and the
next-run candidate list.

## 2026-05-15 — Auto-Researcher v4

**Resume-worthiness score at start of run: 89 / 100**

Signal breakdown:
- Tech stack prestige: 24/25 (LangGraph + K8s + RAG over Weaviate + Helm + AlertManager)
- Commit recency: 24/25 (last push 2026-05-11)
- Feature completeness: 18/20 (full webhook -> triage -> RAG -> plan -> approval workflow)
- Stars + visibility: 8/15
- README quality: 15/15 (architecture diagram, quick-start, K8s deploy, env reference)

### Implemented this run

Branch: `claude/fervent-edison-dYRjh`

- `feat(ci)`: added `.github/workflows/ci.yml` that installs via Poetry, runs the mocked pytest suite (agent flow, API, RAG, tools) on every push and PR to `main`. The README explicitly states 'all tests pass with no external services needed' — wiring this into GH Actions converts a private promise into a publicly verifiable one. Includes Black and Isort as non-blocking style checks (the project already configures both in `pyproject.toml`).

### Why this was prioritized

KubeSentient is positioned as a production-ready SRE agent. A repo making that claim is judged hard on its own reliability story — absence of CI on a project named after autonomous reliability is the clearest possible signal to fix. CI is also the lowest-risk change available: it only changes the GH Actions surface, not the runtime code.

### Evaluated and skipped this run

- Add a Weaviate service container to CI for end-to-end RAG ingest — skipped: would require an OpenAI key in CI (text2vec-openai module), and the local mocks already cover the contract.
- Swap the OpenAI LLM call to Anthropic Claude — skipped: cross-cutting change touching `agent_core/`, embedding paths, and `text2vec-openai` Weaviate module config. Worth a dedicated branch.
- Tighten the K8s tool fallback (`K8s client not initialized`) into a structured error — skipped: low resume impact relative to risk of touching the agent state machine.
- Add Helm chart linting in CI — skipped: chart values reference user-specific image registry; would need a values-ci.yaml first.

### Next-run candidates

1. Anthropic Claude provider behind an env-gated switch (`LLM_PROVIDER=anthropic`) with shared prompt schema.
2. `helm lint` + `helm template` step in CI to catch chart regressions.
3. End-to-end test job using `docker compose up` and a recorded Weaviate fixture.
4. Add `pytest-cov` and publish a coverage badge.
