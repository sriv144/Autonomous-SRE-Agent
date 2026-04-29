# Research Log

A running log of autonomous research and improvement work performed against
this repository.

## 2026-04-29 — Auto-Researcher v4

**Resume score at start of run:** 80 / 100.

**Branch:** `claude/fervent-edison-dI8Uk`

### What was implemented
- Added `.github/workflows/ci.yml` that installs Poetry, runs the existing
  fully-mocked pytest suite on Python 3.11 and 3.12, and validates that the
  `Dockerfile` still builds. Mocked tests do not need OpenAI or a live
  Weaviate instance, so the workflow runs with dummy env vars.
- Added an MIT `LICENSE` so the project is unambiguously open-source.
- Seeded `RESEARCH_LOG.md` for cross-run memory.

### Why this was prioritized
The repository is technically strong (FastAPI + LangGraph + Weaviate RAG +
Kubernetes Helm chart) and the README is already excellent. The remaining
gaps that hurt resume credibility were:
1. No CI proof that the test suite passes.
2. No license file, which blocks reuse and makes reviewers wary.
3. No persistent log to coordinate future autonomous improvements.

All three additions are independent, reversible, and cannot regress runtime
behavior of the agent.

### Evaluated and skipped
- **Real K8s integration tests:** require a kind/k3d cluster. Would inflate
  CI time substantially. Worth a separate workflow on a schedule.
- **README rewrite:** README is already comprehensive and well-structured.
- **Switching from OpenAI to Anthropic Claude:** the Anthropic-only constraint
  applies to *this autonomous tool*, not to the user's project. Touching the
  agent's LLM provider would be a significant behavior change requiring code
  + test updates and is out of scope for a low-risk run.

### Next-run candidates
- Add a CI badge to the README once the workflow has run.
- Add a `helm lint` job to CI.
- Add a Trivy or Grype container-scan step to CI.
- Optional: add an Anthropic Claude provider alongside the existing OpenAI
  one, gated by env var, with parity tests.
