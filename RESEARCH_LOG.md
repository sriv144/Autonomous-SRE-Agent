# Research Log

This file tracks autonomous research and improvement runs against this
repository.

## 2026-05-17 — Auto-Researcher v4

**Resume-worthiness score at start of run: 83 / 100** (rank 3 of 6).

| Signal | Score |
| --- | --- |
| Tech stack prestige (LangGraph + K8s + RAG + Weaviate + Helm) | 23 / 25 |
| Commit recency (updated 2026-05-11) | 22 / 25 |
| Feature completeness (alertmanager webhook, RAG ingest, helm chart, mocked tests) | 18 / 20 |
| Stars + visibility | 5 / 15 |
| README quality (clear, verbose, runnable end-to-end) | 15 / 15 |

### Implemented this run (branch: `claude/fervent-edison-Quaj7`)

- **refactor(tools): env-controlled K8s local mode.** Replaced the hard-coded
  `K8sService(local_mode=False)` in `src/agent_core/tools.py` with a
  `KUBESENTIENT_LOCAL_MODE` env var (accepts `1`, `true`, `yes`, `on` — case
  insensitive). Defaults to in-cluster mode so the deployed Helm pod keeps
  its current behaviour; flips to kubeconfig mode for local dev without
  source edits. Init failures now log a warning instead of swallowing the
  exception, but still leave `k8s = None` so the existing mocked tests pass.
- **docs(.env.example): document the new `KUBESENTIENT_LOCAL_MODE` knob**
  alongside the existing `KUBECONFIG` block so the toggle is discoverable
  from the standard onboarding flow.
- **ci(helm-lint): add `.github/workflows/helm-lint.yml`** that runs
  `helm lint helm/` and a `helm template ...` render check on every push or
  PR that touches `helm/`. Lives in its own workflow file so it composes
  cleanly with the pytest CI on prior branches without conflict.

### Why this was prioritized

Both changes were on the snPHW next-run list (`refactor local_mode`,
`helm lint`). They are the smallest, lowest-risk wins still open: the
refactor preserves default behaviour, and the helm workflow only runs when
the chart actually changes (path-filtered). Combined, they raise the
"production-grade" signal of the repo for resume reviewers without touching
the LangGraph agent code path.

### Evaluated and skipped

- **Pre-commit / ruff / mypy config in `pyproject.toml`.** The repo doesn't
  currently pin formatting tooling. Introducing it would either fail loudly
  on first run or silently no-op. Punted to a focused tooling-config PR.
- **`docker compose config` validation in CI.** Worth adding once the helm
  lint job has a green baseline; left out to keep this diff tight.
- **README demo screenshot / asciinema recording.** Higher impact but needs
  a live cluster to capture meaningfully; deferred until there's a real run.

### Next-run candidates

1. Wire `pre-commit` (ruff + black + mypy) once config is checked into
   `pyproject.toml`.
2. Add `docker compose config` validation to CI.
3. Capture an asciinema recording of an alert flowing through triage →
   investigator → planner → approval and embed it in the README.
4. Add a `KUBESENTIENT_LOCAL_MODE` smoke test that asserts the env-var
   parsing matches the documented truthy set.

### Prior research-log context

Previous runs (most recent first, none merged to `main`):

- `claude/fervent-edison-snPHW` (2026-04-27) — pytest CI (poetry, 3.11/3.12),
  Makefile with dev shortcuts, seeded research log.
