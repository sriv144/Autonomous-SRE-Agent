# Research Log

A running log of autonomous research-and-development cycles on KubeSentient.
Each entry summarizes the resume-impact score at the start of the run, what
was shipped on the listed branch, what was evaluated and skipped, and the
candidate ideas left for the next pass.

---

## 2026-05-18 — Auto-Researcher v4

**Resume score at start of run:** 70/100
**Branch:** `claude/fervent-edison-9dHiZ`

### Implemented
- **feat: migrate reasoning LLM from OpenAI `gpt-4-turbo-preview` to Anthropic `claude-sonnet-4-6`.**
  - `src/agent_core/nodes.py`: `ChatOpenAI` -> `ChatAnthropic`, `ANTHROPIC_MODEL` env override.
  - `pyproject.toml`: add `anthropic` + `langchain-anthropic` deps; bumped to `0.2.0`.
  - `.env.example`: `ANTHROPIC_API_KEY` becomes the required reasoning key; `OPENAI_API_KEY` is
    now scoped to Weaviate `text2vec-openai` embeddings only.
  - `README.md`: model + env table updated, secret-creation snippet expanded for Kubernetes.
  - `tests/test_agent_flow.py`: mock target switched from `ChatOpenAI` to `ChatAnthropic`.

### Why this was prioritized
- Project standard is Claude/Anthropic models only.
- Sonnet 4.6 has stronger tool-use reasoning and lower latency than `gpt-4-turbo-preview` for the
  4-node investigation loop (triage -> investigator -> tools -> planner).
- Separating the reasoning LLM (Claude) from the embedding provider (OpenAI via Weaviate) keeps
  the architecture clean and lets either side swap independently.
- The change is contained: one source file, one test, plus configuration. The existing graph
  topology, tool bindings, and FastAPI surface are untouched, so blast radius is small.

### Evaluated and skipped (with reasons)
- **Switch Weaviate from `text2vec-openai` to `text2vec-transformers`** — would fully remove the
  OpenAI dependency but requires bringing up a local embedding model container and re-ingesting
  runbooks. High blast radius for a follow-up cycle.
- **Replace mocked `human_approval` with a real interrupt + REST resume endpoint** — needs new
  routes, request models, and persistence wiring. Worth doing but a multi-file change with real
  state migration risk; deferred.
- **Add LangGraph checkpointer for resumable runs** — non-trivial, requires a database (SQLite
  for dev, Postgres for prod) and migrations.
- **Slack delivery of plans** — README already references Slack; the wiring isn't there. Would
  add `httpx` Slack webhook posting in a follow-up.

### Next-run candidates
1. Real human-in-the-loop approval endpoint with LangGraph `interrupt_before`.
2. Slack webhook delivery of remediation plans (with diff vs. last plan for the same alert).
3. Prometheus metrics for the agent itself: plan latency, tool-call counts, token usage.
4. Drop OpenAI by switching Weaviate to `text2vec-transformers` or local embeddings.
5. End-to-end pytest with a recorded LangGraph trace (no real LLM calls).
