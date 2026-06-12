# RESEARCH_LOG.md

Persistent memory for the auto-researcher agent. Read top-to-bottom before deciding what to ship on the next pass.

---

## 2026-06-12 — Auto-Researcher v4

**Resume score at start of run:** 80 / 100 (top-3 of the 6-repo portfolio)

**Score breakdown:**
- Tech stack prestige: 23/25 — LangGraph + RAG (Weaviate) + K8s + Helm + FastAPI = elite agentic-SRE.
- Commit recency: 22/25 — updated 2026-05-11.
- Feature completeness: 17/20 — full Docker Compose stack, Helm chart, mocked pytest suite, runbook ingestion, AlertManager webhook all ship.
- Stars / visibility: 4/15 — 1 star.
- README quality: 14/15 — sequence diagram, env table, verification checklist. Strongest README in the cohort.

### What was implemented this pass (branch `claude/fervent-edison-qiarsa`)

Pure additive scaffolding — zero source-code, CI, agent graph, or Helm value touched:

- `.github/ISSUE_TEMPLATE/bug_report.yml` with **deployment-mode** dropdown (Docker / poetry / Helm) and **surface** dropdown covering all four LangGraph nodes, K8s tools, Weaviate RAG, ingestion, Helm, and Docker.
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/PULL_REQUEST_TEMPLATE.md` with an SRE safety checklist (no K8s write tool bypasses the human-approval gate; AlertManager v4 payload validation; no live cluster identifiers; least-privilege RBAC).
- `CHANGELOG.md`.

### Why these and not something bigger?

Open-PR inventory (PRs #2–#17) already covers Poetry-based CI, MIT LICENSE, Makefile, Anthropic Claude provider migration (PR #7), pluggable LLM factory (PR #6), `K8S_LOCAL_MODE` env toggle (PR #5), and SECURITY.md. Adding another CI variant duplicates. Issue templates with a deployment-mode dropdown are uniquely useful for a repo whose README documents three different ways to run it, and the safety checklist in the PR template protects the human-approval gate that's central to the agent's design.

### Evaluated and skipped

- **`/metrics` Prometheus endpoint** — high value, but needs to read the FastAPI app factory and add a dep. Queued.
- **Slack-based human-approval channel** — flagged in the README's roadmap; needs a real Slack app config. Queued.
- **Promoting Anthropic Claude PR #7 to ready-for-review** — maintainer decision, not auto-researcher decision.
- **Adding a real runbook to `runbooks/`** — touches the RAG corpus and could change retrieval behavior.

### Next-run candidates (priority order)

1. **`/metrics` Prometheus endpoint** — register `prometheus-fastapi-instrumentator` and expose `http_requests_total`, `langgraph_node_duration_seconds`. SRE repo without `/metrics` is ironic.
2. **`runbooks/INDEX.md`** — auto-generated catalog of the runbooks in `runbooks/`, so reviewers can see RAG corpus coverage at a glance.
3. **Merge the lowest-risk of the open scaffolding PRs** (issue templates + LICENSE + Makefile) into one clean PR.
4. **`docs/RUNBOOK_AUTHORING.md`** — extract the "adding more runbooks" section from README into a focused doc.
5. **OpenTelemetry trace spans around each LangGraph node** — wires into the `/metrics` work above.
