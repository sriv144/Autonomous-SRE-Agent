# Research Log

This log tracks autonomous research-and-development passes over the
Autonomous-SRE-Agent (KubeSentient) repository. Each run records the
resume-impact score, what was implemented (and why), what was
evaluated and skipped, and candidates for the next pass.

---

## 2026-05-27 — Auto-Researcher v4

**Resume-worthiness score at start of run:** 72 / 100

**Branch:** `claude/fervent-edison-HM9gk`

### What was implemented

- **Pluggable LLM provider** — `src/agent_core/nodes.py` now selects
  the chat model via a new `LLM_PROVIDER` env var (`openai` or
  `anthropic`). Anthropic Claude (default `claude-sonnet-4-6`) is now
  a first-class backend alongside the original
  `gpt-4-turbo-preview`. The factory imports `langchain_anthropic`
  lazily so the dependency is only required when the operator opts
  in. The existing test (`tests/test_agent_flow.py`) keeps working
  because `ChatOpenAI` is still imported at module level.
- **`pyproject.toml`** — added `langchain-anthropic ^0.1.15` as a
  regular dependency.
- **`.env.example`** — documents `LLM_PROVIDER`, `ANTHROPIC_API_KEY`,
  `ANTHROPIC_MODEL`, and the caveat that `OPENAI_API_KEY` is still
  required for Weaviate's `text2vec-openai` embeddings.
- **README** — added a "LLM Provider Selection" section, a Claude
  model menu, updated env-var reference and verification checklist.
- **CI workflow** (`.github/workflows/ci.yml`) — runs Poetry +
  pytest on every push and PR. Repo had no CI before this run.

### Why this was prioritized

This is the highest-impact resume signal in the entire portfolio:
showing the same SRE agent running on either an OpenAI or an
Anthropic backend demonstrates vendor-agnostic AI engineering, model
selection literacy, and the ability to refactor a hard-coded
dependency into a clean provider boundary. The change is also low
risk — default behavior is preserved (provider defaults to
`openai`), and existing tests continue to pass with the same mocks.

### Evaluated and skipped

- **Replacing Weaviate `text2vec-openai` with Anthropic embeddings**
  — Anthropic does not yet expose a public embeddings API, so the
  RAG vectorizer must stay on OpenAI for now. Switching to a
  fully open-source embedder (`text2vec-transformers`, `voyage-ai`,
  etc.) is a multi-file Helm + docker-compose change and would risk
  re-indexing the runbook store. Deferred.
- **Memory checkpointer** — `graph.py` already comments that
  "Memory checkpointer would go here." Adding LangGraph's
  `MemorySaver` would be valuable but requires test updates and
  state-serialization design.
- **Real K8s client wiring in CI** — Out of scope (would need a
  kind / k3d cluster in Actions).
- **Reorganizing nodes into per-role files** — Cosmetic.

### Next-run candidates

1. Add a LangGraph `MemorySaver` checkpointer so investigations
   survive process restarts; wire `interrupt_before=["approval"]`
   for genuine human-in-the-loop.
2. Add an evaluation harness that replays a fixture set of
   AlertManager payloads against both providers and diffs the
   remediation plans (model-agnostic regression testing).
3. Replace `text2vec-openai` with an open-source embedder option in
   `docker-compose.yaml` and `helm/` so the RAG path also becomes
   provider-agnostic.
4. Add Anthropic prompt caching for the long SystemMessage + tool
   prompt to cut cost on repeated alerts of the same group.
5. Wire structured outputs (Pydantic-validated remediation plan)
   instead of free-form markdown so downstream automation can
   consume `plan.steps[]`.
