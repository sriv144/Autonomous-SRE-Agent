# Research Log

A running ledger of autonomous-improvement passes against this repository.
Each entry records the resume-worthiness score at the start of the run,
what was implemented, what was evaluated and skipped, and what the next
pass should look at.

## 2026-05-19 — Auto-Researcher v4

**Resume-worthiness score at start of run: 80 / 100** (rank 3 of 6).

| Signal | Score |
| --- | --- |
| Tech stack prestige (LangGraph + Weaviate RAG + K8s + Helm + FastAPI) | 22 / 25 |
| Commit recency (updated 2026-05-11) | 22 / 25 |
| Feature completeness (working stack, multi-stage Docker, Helm chart) | 17 / 20 |
| Stars + visibility (1 star) | 5 / 15 |
| README quality (architecture diagram, full quick-start, env table, checklist) | 14 / 15 |

### Implemented this run (branch: `claude/fervent-edison-lpd1a`)

- **`.github/workflows/helm-and-compose-validate.yml`.** Adds two
  validation-only jobs:
  - `helm-lint`: installs Helm via `azure/setup-helm@v4` and runs
    `helm lint helm/` against the chart at the repo root. Catches
    `values.yaml` schema typos and templating issues before someone
    discovers them at `helm install` time.
  - `docker-compose-config`: runs `docker compose config -q` against
    `docker-compose.yaml`, with stub env vars for `OPENAI_API_KEY` /
    `OPENAI_MODEL` / `LOG_LEVEL` so the interpolation succeeds in CI.
    Catches malformed YAML, broken `${VAR}` interpolation, and missing
    services / volumes.
  Both jobs are scoped via `paths:` filters so they only run when the
  chart or compose file changes, and they cancel-in-progress on the same
  ref. No runtime code is touched.
- **Seeded this `RESEARCH_LOG.md`.**

### Why this was prioritized

The prior `claude/fervent-edison-T7V0c` (2026-04-26) run already shipped
LICENSE, CITATION.cff, CONTRIBUTING.md, SECURITY.md, and the mocked
pytest CI workflow (`.github/workflows/ci.yml`). The remaining
low-risk, high-signal gap was infrastructure validation: the repo ships
a Helm chart and a docker-compose stack as first-class deploy paths,
but neither was gated by CI. A broken chart only fails at `helm install`
time, often inside someone's eval cluster — a poor reviewer experience
for a repo whose pitch is "production K8s SRE agent". Helm lint and
compose config validation are the cheapest possible defence; both jobs
finish in under a minute, both are scoped to the relevant paths, and
neither alters any runtime behaviour.

The `T7V0c` log explicitly listed "Add `helm lint helm/` and
`docker compose config` validation to CI" as the #1 next-run candidate.

### Evaluated and skipped

- **kind / k3d e2e test that posts a synthetic AlertManager webhook and
  asserts the agent reaches `human_approval` without invoking any mutating
  tool.** Highest-impact follow-up but needs a kind cluster + a Weaviate
  test fixture + the agent's ServiceAccount in CI. Deserves its own PR.
- **Helm `values.schema.json`.** Strong value (`helm install` then
  validates values before apply), but requires exhaustively cataloguing
  every existing chart value and the upgrade path; not a one-shot.
- **Replace `gpt-4-turbo-preview` default with the latest Claude model via
  the Anthropic SDK.** Aligns with the portfolio direction, but touches
  the LangGraph agent + LLM client construction; deferred to its own
  focused branch alongside parity tests.
- **Pre-commit + ruff/black/mypy config.** `pyproject.toml` does not
  currently declare any of these tools; introducing them risks blocking
  the Poetry dev loop described in CONTRIBUTING.md.
- **README badges row.** The existing CI workflow lives on the sibling
  unmerged `T7V0c` branch, so badges added now would point at a workflow
  that does not yet run on `main`. Defer until that branch lands.

### Next-run candidates

1. Replace the `gpt-4-turbo-preview` default with `claude-sonnet-4-6` via
   an Anthropic adapter behind an `LLM_PROVIDER` env var (mirrors the
   pattern shipped on `claude/admiring-davinci-lpd1a` for FinLens).
2. Add `helm/values.schema.json` so user values are validated at
   `helm install` time, not at apply time.
3. Add a kind-based e2e test in CI that posts a synthetic AlertManager
   webhook and asserts the agent reaches `human_approval` without
   invoking any mutating tool.
4. Add a `pre-commit` config (ruff + black + mypy strict) once the
   pyproject.toml gains the matching tool sections.
5. Add badges (CI, helm-and-compose-validate, license, Python) to the
   README once the sibling CI branch is on `main`.

### Prior research-log context

Previous runs on unmerged `claude/fervent-edison-*` branches (most
recent first, none merged to `main`):

- `T7V0c` (2026-04-26) — LICENSE + CITATION + CONTRIBUTING + SECURITY +
  `.github/workflows/ci.yml` mocked pytest gate.
- `snPHW` (2026-04-27) — `.github/workflows/ci.yml` + top-level
  `Makefile` shortcuts mirroring README commands.
