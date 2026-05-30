# Research Log

This log records what the Auto-Researcher agent has shipped on Autonomous-SRE-Agent (KubeSentient), why it picked those changes, and which candidates it skipped. Future runs read this file first so they avoid duplicating prior work.

## 2026-05-30 — Auto-Researcher v4

### Resume-worthiness score at start of run
**~70 / 100** (top three repos).
- Tech stack prestige: 22/25 (LangGraph + Kubernetes + RAG + Weaviate + Helm is a strong agentic-SRE stack).
- Commit recency: 20/25 (active ~19 days ago).
- Feature completeness: 14/20 (FastAPI webhook + LangGraph workflow + Helm chart, but single-vendor LLM).
- Stars + visibility: 2/15.
- README quality: 11/15 — detailed quick-start but no CI badge and a single-provider story.

### Branch
`claude/fervent-edison-zus2A`

### What shipped (single atomic commit)
- **New file `src/agent_core/llm_provider.py`** — small factory that returns `ChatOpenAI` or `ChatAnthropic` based on the `LLM_PROVIDER` env var. Selection is validated up-front so misconfiguration surfaces at startup, not inside the first tool call.
- **Modified `src/agent_core/nodes.py`** — replaces the hard-coded `ChatOpenAI(...)` with `build_llm()`. Behaviour is byte-identical when `LLM_PROVIDER` is unset because the factory defaults to OpenAI + `gpt-4-turbo-preview`.
- **Updated `pyproject.toml`** — adds `langchain-anthropic`, `anthropic`, and `ruff` (dev) so the new provider works under Poetry.
- **Updated `.env.example`** — documents `LLM_PROVIDER`, `ANTHROPIC_API_KEY`, and `ANTHROPIC_MODEL`. Notes that Weaviate's `text2vec-openai` module still needs `OPENAI_API_KEY` even when the agent runs on Claude.
- **Updated `README.md`** — adds CI / Python / LangGraph / multi-LLM badges, a new "LLM provider (multi-backend)" section, and refreshed deployment notes for both provider paths.
- **New file `.github/workflows/ci.yml`** — ruff lint, full pytest run with mocked services, plus a dedicated job that imports the LLM factory on both provider paths.
- **New file `RESEARCH_LOG.md`** — this file.

### Why these changes were prioritised
1. **New feature beats polish in priority order.** Multi-LLM support is a real capability: an SRE platform that can route between OpenAI and Claude based on cost / latency / reliability is a top-of-stack agentic engineering signal for resumes and interviews.
2. **Backwards-compatible by construction.** OpenAI remains the default; existing `OPENAI_API_KEY`-only deployments behave identically.
3. **Risk surface is contained.** The factory lives in its own module, raises early on missing keys or packages, and is exercised by a CI job on both paths.

### Evaluated and skipped
- **Switching the agent default to Anthropic Claude.** Skipped — it would silently break every existing deployment that only has `OPENAI_API_KEY`. The factory documents the switch as a one-line env change instead.
- **Adding a third provider (Bedrock / Azure OpenAI).** Defer; would inflate the dependency set with limited resume signal. Logged as a follow-up.
- **Wiring per-node provider selection (planner vs investigator on different models).** Genuinely interesting but the planner / investigator share the bound-tools client today; refactoring that contract risks the LangGraph wiring and deserves its own PR with tests.
- **Replacing the OpenAI Weaviate embedding module with a local model.** Out of scope this run; it touches the ingestion path, the Helm chart, and the runbook fixtures. Next-run candidate.
- **Adding `SECURITY.md` / `CONTRIBUTING.md`.** Logged for the next run; this commit already lands a meaningful feature and we want the diff to stay reviewable.

### Next-run candidates
1. Add a `Bedrock` provider branch to `llm_provider.py` and document the IAM setup.
2. Replace `text2vec-openai` with a local embedding backend (e.g. `text2vec-transformers`) so the Claude path is OpenAI-free end-to-end.
3. Land `SECURITY.md`, `CONTRIBUTING.md`, and a `LICENSE` to match the README badges.
4. Add a tiny e2e test that boots Weaviate via `testcontainers`, ingests one runbook, and asserts a remediation plan comes back — currently everything is mocked.
5. Surface a `/v1/diagnostics` endpoint that returns the active provider + model so operators can confirm the routing decision without reading logs.
