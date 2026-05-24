# Research Log

A running log of automated research + improvement passes on this repo.
Each entry records what was implemented, why, what was evaluated but
skipped, and candidate work for the next pass.

## 2026-05-24 — Auto-Researcher v4

**Resume score at start of run:** 76 / 100
*(LangGraph + FastAPI + Weaviate + Helm + K8s + RAG — production-shape
repo with thorough README, an ARCHITECTURE.md, Helm chart, Docker
Compose stack, and four mocked test files. The most visible gap was
the absence of CI.)*

**Branch:** `claude/fervent-edison-lJSR8`

**What was implemented**

- `.github/workflows/ci.yml`: single `lint-and-test` job that
  installs Poetry, restores cached dependencies, runs
  `poetry install` (both `--no-root` then root install for the
  package itself), and runs `poetry run pytest tests/ -v`. Tests
  are kept as a required gate because the README explicitly
  guarantees they're fully mocked with no external services
  needed. Provides placeholder values for `OPENAI_API_KEY` and
  `WEAVIATE_URL` so module-level config reads don't crash before
  the mocks engage.

No source code was touched. Only CI configuration and this log were
added.

**Why this was prioritised**

The project already presents extremely well: ARCHITECTURE.md with
diagram, multi-stage Dockerfile, Compose stack, Helm chart, mocked
test suite, AlertManager integration docs, env-var reference table.
The single low-hanging visible gap was running those mocked tests
automatically on push. Risk is low because the test author already
guarantees no-network execution.

**Evaluated and skipped**

- Adding black / isort / mypy steps: dev deps are declared in
  `pyproject.toml`, but running them against the current code
  without first confirming clean state could surface a long list
  of formatting / typing errors and produce a noisy first CI run.
  Worth a focused PR that does the formatting pass and the CI
  hookup together.
- Live Kubernetes integration tests: README acknowledges the K8s
  client returns "K8s client not initialized" in local dev. Real
  K8s tests would need a kind / k3d cluster in CI — valuable but
  is its own larger workstream.
- Helm chart lint: `helm lint helm/` would add a useful guard but
  requires `azure/setup-helm` and a check that the chart values
  validate. Logged as next-run.
- Touching agent code, prompts, or runbooks: out of scope, would
  need behavioural verification.

**Next-run candidates**

- Add a `lint` job that runs `poetry run black --check`,
  `poetry run isort --check`, and `poetry run mypy src`. Land
  any formatting fixes in the same PR.
- Add `helm lint helm/` as a chart-validation step.
- Add Dockerfile build verification (`docker build .`) so the
  multi-stage image is exercised on every PR.
- Pre-commit hook config wiring the same lint stack so
  contributors get parity locally.
- Coverage reporting via `pytest --cov` and a Codecov upload.
- Add an end-to-end Compose smoke test: `docker compose up -d`,
  curl `/health`, tear down. Catches regressions in the API
  wiring without needing real K8s.
