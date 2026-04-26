# Research Log

A running ledger of autonomous-improvement passes against this repository.
Each entry records the resume-worthiness score at the start of the run,
what was implemented, what was evaluated and skipped, and what the next
pass should look at.

## 2026-04-26 — Auto-Researcher v4

- Branch: `claude/fervent-edison-T7V0c`
- Resume score at start of run: **80 / 100**
  - Tech stack prestige: 22 (LangGraph + Weaviate RAG + K8s + Helm + FastAPI)
  - Commit recency: 22 (last commit 2026-04-12)
  - Feature completeness: 17 (working stack, multi-stage Docker, Helm chart)
  - Stars + visibility: 5
  - README quality: 14 (architecture diagram, end-to-end quickstart, table
    of env vars, verification checklist)

### Implemented this run
- `LICENSE` (MIT) — was missing entirely; this is a public repo and the
  absence of a license meaningfully blocks reuse.
- `CITATION.cff` so KubeSentient is machine-citable from incident-management
  research and GitHub's "Cite this repository" widget.
- `CONTRIBUTING.md` codifying the two safety invariants the agent depends on
  (read-only by default, plan-only without approval) and the Conventional
  Commits workflow.
- `SECURITY.md` describing the K8s-tool / credential / prompt-injection
  threat model and a private-disclosure path.
- `.github/workflows/ci.yml` running `poetry install` + the existing fully
  mocked `pytest` suite on every push and PR to `main`. Uses a dummy
  `OPENAI_API_KEY` because the test suite never makes real LLM calls.

### Why this was prioritized
No prior auto-researcher branch had landed any work on this repo (the
existing `claude/fervent-edison-*` branches matched `main` exactly), so the
highest-leverage gap was the missing LICENSE and the missing CI gate around
the already-thorough mocked test suite. README polish was deliberately out
of scope this run because the README is already strong (architecture
diagram, full Docker / Helm walkthrough, env var table, verification
checklist).

### Evaluated and skipped
- **Adding kind / k3d e2e tests in CI** — would meaningfully improve
  coverage but requires a real K8s cluster and a fixture for the agent's
  ServiceAccount. Belongs in a dedicated PR.
- **Pre-commit hooks** — `pyproject.toml` does not declare lint config and
  adding hooks without aligning ruff/black settings risks blocking the
  Poetry workflow described in `CONTRIBUTING.md`.
- **README badges row (CI / license / Python)** — natural follow-up once
  this CI workflow is on `main` and the badges actually link to something.
- **Adding a Helm chart values schema (`values.schema.json`)** — high value
  for cluster operators but requires extracting and validating every
  existing chart value; not a one-shot.

### Next-run candidates
1. Add a Helm `values.schema.json` so `helm install` validates user values
   instead of failing late at apply time.
2. Add a kind-based e2e test in CI that posts a synthetic AlertManager
   webhook and asserts the agent reaches the `human_approval` node without
   invoking any mutating tool.
3. Replace the `gpt-4-turbo-preview` default with the latest Claude model
   via the Anthropic SDK (the project already accepts an OpenAI-compatible
   provider; a small adapter would generalise this).
4. Add a `pre-commit` config (ruff + black + mypy strict) and a CI lint job.
5. Add badges (CI, license, Python, Helm chart version) to the README.
