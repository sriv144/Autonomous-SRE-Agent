# Research Log

This file tracks autonomous research and improvement runs against this
repository (KubeSentient — Autonomous SRE Agent). Each entry captures what was
evaluated, what was implemented, and what was skipped, so future runs do not
repeat the same work.

## Prior runs (on unmerged `claude/fervent-edison-*` branches)

- **2026-04-27** added `.github/workflows/ci.yml` (Poetry + mocked pytest on
  Python 3.11/3.12) and a top-level `Makefile`. That work has not been merged
  to `main`; this run does not duplicate it.

## 2026-05-28 — Auto-Researcher v4

**Resume score at start of run:** ~78 / 100 — top 3 of 6 across the portfolio
(distributed/infra + LangGraph agent + Weaviate RAG + FastAPI + Helm).

**Branch:** `claude/fervent-edison-0QUHr` (from `main`).

### Implemented

- **Env-controlled `K8S_LOCAL_MODE` toggle.** `src/agent_core/tools.py`
  previously hard-coded `K8sService(local_mode=False)`, and the README told
  users to manually edit the source to flip it. Replaced that with a
  `_resolve_local_mode()` helper that reads the `K8S_LOCAL_MODE` env var
  (truthy: `1/true/yes/on`), defaulting to `False` so in-cluster behavior is
  unchanged. The same container image can now run against a local kubeconfig
  (dev) or an in-cluster ServiceAccount (prod) purely via configuration.
- **Unit test** `tests/test_local_mode.py` covering default, truthy, and
  falsey parsing.
- **Documented** `K8S_LOCAL_MODE` in `.env.example`.
- **Seeded this `RESEARCH_LOG.md`.**

### Why this was prioritized

It is the highest-priority category (a real capability/usability fix) that is
still safe: it removes a documented "edit the code to deploy" footgun, is
backward-compatible (default preserves prior behavior), and is covered by a
test. Existing tests patch both kube config loaders and the `k8s` instance, so
they remain green.

### Evaluated and skipped

- **README env-table row for `K8S_LOCAL_MODE`.** Left for a focused docs pass
  to avoid a full rewrite of the large README in this commit; `.env.example`
  now documents it.
- **`helm lint helm/` + `docker compose config` CI validation.** Depends on a
  CI base that currently only lives on an unmerged branch; revisit once CI is
  merged to `main`.
- **pre-commit + ruff/mypy config.** Repo pins none of these; introducing them
  would surface pre-existing formatting drift as spurious failures. Defer to a
  config-pinning pass.

### Next-run candidates

1. Merge the unmerged CI workflow + Makefile to `main`, then add `helm lint`
   and `docker compose config` jobs.
2. Add the `K8S_LOCAL_MODE` row to the README environment-variable table.
3. Add a short demo screenshot or asciinema recording of the LangGraph
   workflow to the README.
4. CodeQL workflow — the agent handles OpenAI keys and cluster access, a good
   fit for security scanning.
