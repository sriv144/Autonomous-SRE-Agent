# Research Log

Rolling log of autonomous research + improvement passes against this repo.

## 2026-06-07 — Auto-Researcher v4

**Resume score at start of run:** 88 / 100

Breakdown:
- Tech stack prestige: 25 / 25 (LangGraph + RAG + Weaviate + K8s + Helm + AlertManager hooks — cleanly hits SRE/AI infra storytelling)
- Commit recency: 22 / 25
- Feature completeness: 18 / 20 (full graph: triage → investigator → planner → approval, with read-only K8s tools and Weaviate RAG)
- Stars + visibility: 3 / 15
- README quality: 20 / 20-ish — capped (architecture ASCII diagram, prereqs, quick start, helm install, AlertManager wiring, env var table, verification checklist, project tree)

**Why prioritized:** highest base score of the cohort, but the only missing surface-level item is a license file. Without `LICENSE`, a recruiter or contributor cannot tell whether they can reuse the code, and GitHub does not show a license badge. Adding it is zero-risk.

**What was implemented (branch `claude/fervent-edison-5OlEN`):**
- `LICENSE` — MIT, so the repo is unambiguously reusable.
- `RESEARCH_LOG.md` — this file.

**What was evaluated and skipped, with reasons:**
- *Migrate the agent + embedding stack from OpenAI to Anthropic Claude.* This is the single highest-impact change available: README and `docker-compose.yaml` both reference `OPENAI_API_KEY` + `gpt-4-turbo-preview` + Weaviate `text2vec-openai`. Swapping to Claude Sonnet 4 for the LangGraph nodes and a separate embedding provider (or keeping OpenAI just for embeddings) is real work — must update `pyproject.toml`, the LangGraph node modules, the Weaviate schema, and every test. Deferred to a dedicated pass so the change can be benchmarked and tested properly.
- *CI workflow (lint + test).* No `.github/workflows/` directory exists. Worth adding, but the test suite uses `poetry` and pulls in `weaviate-client`, `langgraph`, `langchain-openai`; getting a clean hermetic green run in CI without live OpenAI calls means writing mock fixtures first. Deferred so the first CI commit is actually green.
- *CONTRIBUTING.md.* Low impact in isolation; will fold into the CI / Claude-migration pass.
- *Update `gpt-4-turbo-preview` reference to a current model.* Tightly coupled with the Claude-migration work; skipped this pass.

**Next-run candidates:**
1. Anthropic Claude migration: replace `langchain-openai` calls with `langchain-anthropic` + `claude-sonnet-4-6` for triage/investigator/planner nodes; keep embedding provider behind an env var so Weaviate can stay on OpenAI embeddings or move to Voyage / local sentence-transformers.
2. `.github/workflows/ci.yml` running `poetry install` + `pytest -q` with mocked LangChain LLM clients.
3. CONTRIBUTING.md describing how to add new agent nodes / new runbooks.
4. `helm/values.yaml` doc block + a screenshot or asciinema of the live agent flow embedded in README.
