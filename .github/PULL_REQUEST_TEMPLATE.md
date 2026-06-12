## Summary

<!-- One or two sentences on what changed and why. -->

## Surface

- [ ] FastAPI route or schema
- [ ] LangGraph node / state / graph
- [ ] K8s tool (read-only)
- [ ] K8s tool (write / remediation) — **requires extra review**
- [ ] RAG / runbook ingestion
- [ ] Helm chart / Dockerfile / docker-compose
- [ ] Docs / CI / scaffolding only

## Test plan

- [ ] `poetry run pytest tests/ -v` is green (suite is fully mocked per README)
- [ ] `docker compose up --build` brings `api` to `Application startup complete`
- [ ] `curl http://localhost:8000/health` returns `{"status":"ok",...}`
- [ ] `curl -X POST .../api/v1/alerts` with the README's sample payload returns `202 Accepted` and produces a plan in api logs

## Safety checklist (skip if N/A)

- [ ] No new K8s write tool can run without the human-approval gate
- [ ] Webhook payload validation rejects malformed AlertManager v4 messages
- [ ] No secrets, kubeconfigs, or live cluster identifiers in the diff
- [ ] RBAC additions in the Helm chart follow least-privilege
