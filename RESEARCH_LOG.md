# Research Log

This log tracks autonomous-agent improvements (auto-researcher runs).
Each entry records what was implemented, why, what was skipped, and
candidates for future runs.

## 2026-05-26 — Auto-Researcher v4

**Resume score at run start:** 75/100
(K8s + LangGraph + RAG stack, polished README, mocked test suite,
Helm chart present, recent activity, 1 GitHub star)

### Implemented (branch: `claude/fervent-edison-DU4LA`)
- **CI workflow** (`.github/workflows/ci.yml`): Python 3.11 +
  Poetry install + compileall syntax check + full pytest suite.
  Tests are mocked per README so no external services are required
  in CI.

### Why prioritised
- README's verification checklist explicitly lists
  `poetry run pytest tests/ -v` as a success criterion, but nothing
  enforced it on push.
- Tests are mocked → they will pass reliably in CI without secrets.
- An SRE repo without CI is an obvious gap to a recruiter; with CI
  it signals practitioner credibility.

### Evaluated and skipped
- **Dependabot config** — useful but needs careful tuning for
  Poetry + Helm; deferred to a follow-up.
- **Helm chart lint in CI** — adds toolchain (`helm` action) for
  little marginal value this run; chart already lints clean locally.
- **Pre-commit hooks** — duplicative with CI; deferred.
- **Black / isort formatting checks** — current source is not
  guaranteed pre-formatted; enabling now could block PRs on
  cosmetic-only issues.

### Next-run candidates
- Dependabot for `pyproject.toml` and the Helm chart.
- README CI status badge once the workflow has a run history.
- Integration job that runs `docker compose up` and curls
  `/health` + `/api/v1/alerts` end-to-end.
- Helm chart lint + `kubeval` validation job.
