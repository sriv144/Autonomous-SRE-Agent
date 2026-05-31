# Research Log

Automated improvement log maintained by the auto-researcher agent.

---

## 2026-05-31 — Auto-Researcher v4

**Resume score at start of run:** 76 / 100 (3rd of 6 target repos)

### Implemented (branch: `claude/fervent-edison-D2Gmr`)

- **Migrated agent reasoning from OpenAI gpt-4-turbo to Anthropic Claude.**
  - `src/agent_core/nodes.py`: swapped `ChatOpenAI` for `ChatAnthropic` with
    `claude-sonnet-4-6` as the default model (override via `ANTHROPIC_MODEL`).
  - `pyproject.toml`: removed `openai` + `langchain-openai`, added `anthropic`
    and `langchain-anthropic`. Bumped project version to `0.2.0`.
  - `.env.example`: added `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`; clarified
    that the OpenAI key is now scoped only to Weaviate's text2vec embeddings.
  - `docker-compose.yaml`: pass `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` into
    the `api` service.
  - `tests/test_agent_flow.py`: updated the patch path so the existing
    graph-compilation test still runs offline against the new LLM import.
  - `README.md`: rewrote prerequisites, env-var table, quick-start, and helm
    sections to reflect Claude as the reasoning model.

### Why this was prioritized

- **Alignment with the auto-researcher "Claude/Anthropic models only" rule.**
  The repo was the only one of the six still calling OpenAI for reasoning.
- **Resume value:** "Built an autonomous SRE agent powered by Anthropic Claude
  using LangGraph + Weaviate RAG" reads stronger than the generic OpenAI version
  and matches the current job-market focus on Anthropic.
- **Clean, low-risk swap:** the Python code never imported `openai` directly
  (only `langchain_openai`), so the diff is mechanical and tightly scoped.
  Weaviate's `text2vec-openai` module is unaffected because it runs inside the
  Weaviate container against its own env var.

### Evaluated and skipped

- **Adding a CI workflow (pytest).** Skipped this run to keep the commit
  focused on the LLM migration; tracked as the next candidate.
- **Adding prompt caching on the system message + tool definitions.** The
  system prompt and tool count are small enough today that caching would not
  materially reduce cost. Worth revisiting once runbook chunks are injected
  into the system context.
- **Switching Weaviate to a non-OpenAI vectorizer (`text2vec-cohere` or local
  `text2vec-transformers`).** Higher risk — changes the embedding space and
  invalidates existing ingested data. Deferred.
- **Wiring real human approval (instead of the mocked node).** Requires API
  design for the approval endpoint and likely a persistence layer; out of scope
  for a single auto-researcher run.

### Next-run candidates

1. CI workflow: `.github/workflows/ci.yml` running `poetry install && pytest`.
2. Add prompt caching once runbook context is moved into the system message.
3. Implement a real `/api/v1/approve` endpoint backed by a checkpointer.
4. Stream the planner's response via FastAPI SSE so operators see partial plans.
5. Replace the mocked `human_approval` node with a LangGraph interrupt.
