# Research Log

Maintained by the Auto-Researcher passes. Each entry records what was looked
at, what was implemented, and what was deferred so future runs do not redo
the same work.

## 2026-06-08 — Auto-Researcher v4

**Resume-worthiness score (start of run):** ~70 / 100
- Tech stack prestige (25): 23 — Kubernetes + AlertManager + LangGraph
  + Weaviate RAG hits a lot of senior-infra-engineer signals.
- Commit recency (25): 22 — last push 2026-05-11, inside the 30-day
  window.
- Feature completeness (20): 17 — webhook-to-plan flow, runbook ingest,
  Helm chart, Dockerfile, mocked human approval node all wired up.
- Stars + visibility (15): 3 — 1 star.
- README quality (15): 14 — already excellent: architecture ASCII
  diagram, quickstart, env reference, verification checklist, K8s deploy
  path. Hard to improve without rewriting.

**Implemented on branch `claude/fervent-edison-fX5uP`:**
- `.github/workflows/ci.yml` — ruff (advisory) + py_compile of tracked
  `.py` files. Doesn’t spin up Weaviate or pull OpenAI credentials, so it
  stays cheap and credential-free.
- `SECURITY.md` — vulnerability reporting policy plus surface-specific
  notes for the AlertManager webhook, K8s tooling RBAC, and human-approval
  gate.
- `RESEARCH_LOG.md` — this file.

**Why prioritized:** the README already carries most of the recruiter-facing
weight. The missing pieces were CI badge + a security policy that explains
the deployment surface. Both are zero-risk additions.

**Evaluated and skipped this run:**
- Adding optional Anthropic Claude provider alongside OpenAI in
  `src/agent_core/`. High resume value (provider-agnostic agent) but it
  requires reading the LangGraph node graph carefully to keep tool-calling
  contracts intact. Queued for a focused pass.
- Wiring `pytest` into CI. The suite is mocked-only per README, so it should
  run cleanly, but a Poetry-install step needs to be vetted first.
- Adding a `/metrics` Prometheus endpoint to the FastAPI app for the agent
  loop. Solid resume value; needs code touch, queued.

**Next-run candidates:**
- Add an Anthropic Claude provider option (`ANTHROPIC_API_KEY`) behind a
  `LLM_PROVIDER` env switch.
- Add a `/metrics` Prometheus endpoint with counters for alerts received,
  plans generated, and tool calls per node.
- Wire `pytest -q tests/` into CI behind a Poetry install step once the
  lockfile is confirmed healthy on a clean runner.
- Replace the mocked `human_approval` node with a Slack interactive-message
  flow (this is the kind of feature that reads well in interviews).
