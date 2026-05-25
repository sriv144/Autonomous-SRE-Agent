# Research Log

A running record of auto-researcher passes against this repo.

## 2026-05-25 -- Auto-Researcher v4

**Resume score at start:** 84/100. Excellent README, helm chart, docker
compose, fully mocked test suite, and a real LangGraph + Weaviate + K8s
architecture. Loses points on missing CI (the tests exist but nothing
runs them automatically), no Makefile to anchor the dev loop, and no
LICENSE.

**Implemented on branch `claude/fervent-edison-FVAfQ`:**

- `.github/workflows/ci.yml`: installs via Poetry, lints with ruff,
  runs the mocked pytest suite on every push and PR. Dummy
  `OPENAI_API_KEY` is set so the agent module's import doesn't fail.
- `Makefile`: documents the eight common dev loops (install / test /
  lint / up / down / logs / ingest / health) so newcomers can be
  productive with `make help`.
- MIT `LICENSE`.
- Seeded `RESEARCH_LOG.md`.

**Why this was prioritized:** The project is feature-complete and well
documented; the gap was operational signals (CI badge, license,
Makefile) that reviewers use as a quality proxy.

**Evaluated and skipped:**

- Adding Anthropic Claude as an alternative model provider: the
  LangGraph nodes are tightly coupled to `langchain_openai`. Worth
  doing as a dedicated provider-abstraction pass, not a drive-by.
- Helm chart hardening (resource limits, PodDisruptionBudget,
  NetworkPolicy): higher risk because it changes deployment shape and
  is harder to validate without a live cluster.
- Adding GitHub-hosted runbook ingestion (auto-pull from a Confluence
  export bucket): a real feature, but needs a credential model.

**Next-run candidates:**

- Provider abstraction so Claude / Gemini / local can be swapped via
  env var.
- Trace export to OpenTelemetry from the LangGraph nodes.
- Helm `values.yaml` hardening + chart-testing CI job.
- A small `examples/` folder with three pre-canned AlertManager payloads
  (CrashLoopBackOff, OOMKilled, HighErrorRate) and expected agent
  outputs as fixtures.
