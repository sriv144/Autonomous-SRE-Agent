# Research Log

This log tracks automated research and improvement runs by the
auto-researcher agent. Each entry captures the project's resume-worthiness
score at run start, what was implemented (with branch), why it was
prioritized, what was evaluated and skipped, and the next-run candidates.

---

## 2026-05-13 — Auto-Researcher v4

**Resume score at start of run:** 92 / 100
- Tech stack prestige: 25/25 (Kubernetes + LangGraph + RAG + Weaviate + Helm)
- Commit recency: 25/25 (active within the last 48 hours)
- Feature completeness: 19/20 (FastAPI + agent graph + Helm chart + Dockerfile)
- Stars + visibility: 7/15 (1 star, no forks)
- README quality: 15/15 (architecture diagram, quick start, k8s deploy, env table)

**Implemented (branch: `claude/fervent-edison-HHSYf`):**
- `.github/workflows/ci.yml` — GitHub Actions workflow that installs
  Poetry, caches `.venv` by `pyproject.toml` fingerprint, and runs
  `poetry run pytest tests/ -v`. The README guarantees the test suite
  is fully mocked, so CI does not need any external services.
- `RESEARCH_LOG.md` — this file (seeded for future runs).

**Why this was prioritized:**
- Highest resume score in the portfolio + zero CI signal. The repo
  already publishes a Dockerfile and a Helm chart, so reviewers expect
  to see a CI badge.
- Tests are fully mocked per the README's verification checklist, so
  the CI job is genuinely runnable without OpenAI / Weaviate / a
  Kubernetes cluster.
- Poetry-based install + Python 3.11 matches the repo's local-dev
  contract exactly.

**Evaluated and skipped this run:**
- Migrating the LangGraph agent from `langchain-openai` to
  `langchain-anthropic` + Claude. High impact (Claude/Anthropic-only
  is the constraint) but the existing tests mock `ChatOpenAI`, so the
  migration also requires re-keying tests and updating the Weaviate
  text2vec module. Tracked as the top next-run candidate.
- Docker image build CI — valuable but the multi-stage build is heavy
  for the free runner; defer until a registry push target is chosen.
- Helm chart lint workflow — nice to have but not the highest-leverage
  signal for a reviewer right now.

**Next-run candidates (ranked):**
1. Add an `langchain-anthropic` integration path gated on
   `ANTHROPIC_API_KEY`, keeping OpenAI as the fallback. Pairs with a
   Claude embedding option for the runbook store.
2. `docker-build.yml` workflow that builds + pushes the image to GHCR
   on tags.
3. `helm-lint.yml` workflow running `helm lint helm/` and `kubeconform`
   against the rendered templates.
4. README architecture diagram as an SVG (currently ASCII).
5. Convert `tests/` to `pytest-asyncio` style and exercise the
   `/api/v1/alerts` route end-to-end with an `httpx.AsyncClient` fixture.
