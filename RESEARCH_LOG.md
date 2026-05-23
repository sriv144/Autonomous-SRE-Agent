# Research Log — KubeSentient (Autonomous SRE Agent)

Durable memory for the auto-researcher agent. Each run appends an entry
documenting what was implemented, what was deliberately skipped, and the
next viable improvement. Do not delete prior entries.

---

## 2026-05-23 — Auto-Researcher v4

**Resume score at start of run:** 83 / 100

**Implemented on branch `claude/fervent-edison-dmZJS`:**
- Added `.github/workflows/ci.yml` — the repository's first CI workflow.
  Installs Poetry, caches the venv, runs `black --check` and
  `isort --check-only` as advisory steps, and executes the mocked
  `pytest` suite. Tests are already fully mocked (no Weaviate or
  OpenAI calls during test execution), so CI is fast and free of
  external dependencies.
- Seeded this `RESEARCH_LOG.md`.

**Why prioritized:** KubeSentient already has the strongest documentation
in the portfolio (deep README with architecture diagram, Helm chart,
docker-compose, separate ARCHITECTURE.md, verification checklist, env
var reference). Adding a CI gate is the missing 'green badge' signal
that converts that polish into recruiter-visible green-checkmark proof
that the test suite stays clean.

**Evaluated and skipped this run:**
- *Replacing OpenAI with Anthropic Claude* for the LangGraph LLM and
  switching from `text2vec-openai` embeddings. Skipped: this is a real
  feature change (touches `langchain-openai` integration, Weaviate
  module config, runbook ingestion). It deserves its own scoped PR
  with end-to-end tests of the new path.
- *Adding a real K8s integration test.* Skipped: would need a kind
  cluster spun up in CI; the existing tests intentionally mock the K8s
  client, which is the right test boundary for this layer.
- *Helm chart lint via `helm lint`*. Tractable, but kept out of this
  pass to avoid stacking two new CI concerns in one commit.

**Next-run candidates (in priority order):**
1. Add an Anthropic Claude provider alongside the current OpenAI one,
   selectable via `LLM_PROVIDER` env var. The graph nodes only depend
   on a chat-model interface, so this is a contained change.
2. Add `helm lint helm/` as a second CI job.
3. Add a Slack delivery integration test for the remediation-plan
   webhook hand-off (currently logged only).
4. Promote `black`/`isort` from advisory to blocking once the codebase
   is confirmed clean.
