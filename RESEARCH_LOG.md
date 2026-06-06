# Auto-Researcher Research Log — Autonomous SRE Agent (KubeSentient)

This file is the persistent memory for the auto-researcher agent. Each run
appends a new section describing what was evaluated, what was implemented
(and on which branch), and what is on deck for the next run.

---

## 2026-06-06 — Auto-Researcher v4

**Resume score at start of run:** 80 / 100

- Tech stack prestige: 22/25 (LangGraph agent + Weaviate RAG + Kubernetes +
  FastAPI + AlertManager webhooks + Helm chart)
- Commit recency: 22/25 (updated 2026-05-11, ~26 days before this run)
- Feature completeness: 18/20 (Docker Compose stack, Helm chart, runbook
  ingestion CLI, fully-mocked tests, end-to-end alert demo curl)
- Stars + visibility: 4/15 (1 star)
- README quality: 14/15 (excellent — architecture ASCII diagram,
  step-by-step quickstart, verification checklist, env-var reference)

### Implemented this run

Branch: `claude/fervent-edison-TGFOp`

- `.github/workflows/ci.yml` — Poetry-based CI on PRs and pushes to `main`.
  - installs the locked Poetry env (cached on `poetry.lock`)
  - runs `black --check` and `isort --check-only` on `src` and `tests`
    (non-blocking — surfaces drift without breaking the build)
  - runs the full `pytest` suite with dummy OpenAI / Weaviate env vars
    so imports stay safe (tests are fully mocked per the README)

### Why this was prioritized

The repo already has the full Poetry dev dep group (`pytest`,
`pytest-asyncio`, `black`, `isort`, `mypy`) and 4 test files, and the
README explicitly says "tests are fully mocked, no external services
needed" — but `.github/workflows/` did not exist, so PRs and pushes were
unchecked. Adding CI is pure additive plumbing: no source code is
touched, existing functionality cannot break, and a green CI badge
materially strengthens the repo's resume signal as a production-grade SRE
project.

### Evaluated and skipped this run

- **Migrate LLM provider from OpenAI to Anthropic Claude.** Very high
  resume value (and aligns with the auto-researcher's Claude-only
  mandate), but touches `src/agent_core/nodes.py` and the Weaviate
  `text2vec-openai` module wiring — invasive enough to need paired tests
  and a thoughtful provider abstraction. Deferred to a future run.
- **Add mypy to CI.** Pinned but no typed baseline yet — would be a flood
  of errors on first run. Skip until a typing pass lands.
- **`.env.example` rework.** Already comprehensive and accurate.

### Next-run candidates

1. Introduce a `LLMProvider` abstraction in `src/agent_core/` so the
   triage / investigator / planner nodes can be backed by either
   `langchain-openai` or `langchain-anthropic` (Claude). Land with
   focused unit tests for each provider path.
2. Add a containerized smoke test in CI: `docker compose up`, wait for
   `/health`, POST a sample AlertManager payload, assert HTTP 202.
3. Add a `helm lint` + `helm template` job to keep the chart valid.
4. Add a `pre-commit` config so contributors catch black / isort drift
   locally.
