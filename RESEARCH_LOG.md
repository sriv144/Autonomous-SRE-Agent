# Research Log

Persistent memory used by the auto-researcher agent. Each run appends a dated
section so future runs can see what was evaluated, what shipped, and what was
deliberately skipped.

## 2026-04-23 - Auto-Researcher v4

**Resume-worthiness score at start of run: 80 / 100**
- Tech stack prestige: 22/25 (LangGraph agents + Kubernetes + Weaviate RAG + FastAPI)
- Commit recency: 22/25 (last push 2026-04-14, within 30-day window)
- Feature completeness: 17/20 (end-to-end alert -> plan loop, Helm chart, Docker Compose, mocked tests)
- Stars / visibility: 5/15 (1 star)
- README quality: 14/15 (architecture diagram, prerequisites matrix, step-by-step Quick Start, verification checklist, env var table)

### Branch
`claude/fervent-edison-ONkrp`

### Implemented
- `.github/workflows/ci.yml` - GitHub Actions workflow that pins Python 3.11,
  installs Poetry 1.8.3, caches the project virtualenv, installs dependencies
  via `poetry install --no-interaction --no-root`, and runs `pytest tests/ -v`
  on pushes and PRs against `main`. Placeholder values are supplied for
  `OPENAI_API_KEY` and `WEAVIATE_URL` because the test suite is fully mocked
  per the README ("Run tests (all mocked, no external services needed)").

### Why this was prioritized
For an Autonomous SRE Agent project, the absence of CI is an immediate trust
signal to reviewers. Adding a green-badge-able workflow on every push makes
the repo's "production-grade" claims credible and protects future edits on
LangGraph nodes, ingestion, and the alert handler from silent regressions.
Everything else in the repo (Helm chart, Dockerfile, docker-compose, pytest
suite) was already in good shape, so CI was the single highest-impact
low-risk gap.

### Evaluated and skipped
- **Fix README inconsistency** (`cd "Autonomous SRE Agent"` -> `cd Autonomous-SRE-Agent`):
  cosmetic only, saved for a future docs pass.
- **Dependabot config**: `langgraph` and `weaviate-client` version pins
  interact non-trivially; safer to review updates manually than to have
  bots open PRs without a human gate.
- **Pre-commit hooks (ruff/black)**: safe but more intrusive. Defer until
  a CI green baseline is established here.
- **Expanding LangGraph node-level tests**: would require fixture scaffolding
  for mocked tool state; out of scope for a single-run CI bootstrap.
- **Observability doc (Prometheus scrape config + Grafana panels for the
  agent's own metrics)**: high resume value but requires more code context
  than a safe first pass warrants.

### Next-run candidates
1. Add Dependabot for pip + docker updates once CI is verified green.
2. Add `docs/OBSERVABILITY.md` with Prometheus scrape config and example
   Grafana panels for the agent's own metrics (strong SRE-role signal).
3. Expand `tests/` with LangGraph node-level coverage for
   `triage -> investigator -> planner` state transitions.
4. Add a second realistic runbook (e.g. `oom_kill.md`, `pvc_pending.md`)
   to the RAG index so the agent demonstrably handles more alert classes
   than the single `KubePodCrashLooping` demo in the README.
5. Small README fix: path casing in the Quick Start block.
