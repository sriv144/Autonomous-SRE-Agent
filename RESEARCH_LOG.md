# Research Log

Autonomous research-agent activity log for Autonomous-SRE-Agent /
KubeSentient. Each entry records (a) what was implemented, (b) why it
was prioritized, (c) what was evaluated but skipped, and (d) next-run
candidates. Do not delete prior entries.

---

## 2026-06-03 — Auto-Researcher v4

**Resume-worthiness score at start of run:** 78 / 100

- Stack prestige (25): 22 — LangGraph agent workflow, Weaviate +
  OpenAI embeddings RAG, K8s + Helm + AlertManager wiring.
- Commit recency (25): 18 — 23 days since last push.
- Feature completeness (20): 19 — docker-compose dev stack, Helm
  chart, fully-mocked pytest suite, ARCHITECTURE.md, ingest_runbooks
  CLI, env-var reference table, end-to-end curl walkthrough.
- Stars / visibility (15): 4 — 1 star, public topics.
- README quality (15): 15 — architecture diagram, prerequisites
  table, 6-step quickstart, K8s deployment section, verification
  checklist, env-var reference, project structure tree.

### Implemented on `claude/fervent-edison-oCTQH`

Log-only commit. **No source changes this run.**

### Why no implementation this run

This repo is already in the strongest shape on the slate:
- README is genuinely production-quality (diagram + verification
  checklist + Helm walkthrough).
- `.env.example`, Dockerfile, docker-compose, Helm chart, and a
  mocked pytest suite are all in place.
- `ARCHITECTURE.md` covers the LangGraph node topology.

The one notable gap is the lack of a CI workflow (`.github/workflows/`
does not exist), but adding it requires a careful choice of secrets
strategy because the agents instantiate at import time with an OpenAI
client. That deserves its own dedicated run rather than being
tacked on.

### Evaluated and skipped

- **Add `.github/workflows/ci.yml`.** Highest-value candidate but
  needs an OpenAI mock or test-env split first; otherwise the
  `agent_core` imports will hit the real API in CI. Deferred until
  there is time to introduce a real test-mode fixture.
- **Anthropic Claude backend for the LangGraph agent.** The hard
  constraint from auto-researcher is Claude-only for new AI work,
  but a full migration here means rewriting the planner / triage
  / investigator nodes and updating all mocked tests. Deferred to a
  dedicated run.
- **Real K8s tools instead of "K8s client not initialized" mocks.**
  Out of scope without a live cluster.
- **GitHub Actions integration test that spins up the docker-compose
  stack and POSTs a synthetic alert.** Valuable but heavy; defer.

### Next-run candidates

1. Build a CI workflow that runs `poetry install` + the existing
   mocked `pytest tests/` suite with a fake `OPENAI_API_KEY`. Verify
   the import-time graph build does not call out before adding.
2. Add an Anthropic Claude provider option to `agent_core/graph.py`
   selectable via `LLM_PROVIDER` env var.
3. Replace the OpenAI Weaviate `text2vec` module with a local
   embedding model (e.g. `sentence-transformers`) so the dev stack
   no longer requires an OpenAI key.
4. Add a status-/results-screenshot to the README so the agent
   workflow log is visible without running the stack.
5. Wire the `human_approval` node to a real Slack-button signal
   instead of the current mock.
