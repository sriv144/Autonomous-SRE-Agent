# KubeSentient — Autonomous SRE Agent

An autonomous site reliability agent for Kubernetes. It receives Prometheus AlertManager webhooks, investigates the affected cluster resources using read-only Kubernetes tools, queries a runbook knowledge base via RAG (Weaviate + OpenAI embeddings), and produces a structured remediation plan.

The reasoning loop runs on **Anthropic Claude Sonnet 4.6** via `langchain-anthropic`. OpenAI is used **only** to embed runbook chunks for the Weaviate vector store — it never sees the agent's reasoning traffic.

## Architecture

```
Prometheus -> AlertManager -> POST /api/v1/alerts
                                    |
                           FastAPI (port 8000)
                                    |
                         LangGraph Agent Workflow (Claude Sonnet 4.6)
                        +-----------------------+
                        |  triage -> investigator|
                        |      | (tools)         |
                        |  K8s: logs/events/pods |
                        |  RAG: runbook search   |
                        |      |                 |
                        |  planner -> approval   |
                        +-----------------------+
                                    |
                       Remediation plan (logs/Slack)
                                    ^
                          Weaviate (port 8080)
                          runbook knowledge base
```

## Prerequisites

| Tool | Version |
|------|---------|
| Docker + Docker Compose | 24+ |
| Python | 3.11+ (for local dev) |
| Poetry | 1.7+ (for local dev) |
| Anthropic API key | for reasoning |
| OpenAI API key | for runbook embeddings (Weaviate text2vec-openai) |
| kubectl + kubeconfig | optional (for live K8s tools) |

## Quick Start (Docker — Recommended)

### 1. Clone and configure

```bash
cd "Autonomous SRE Agent"
cp .env.example .env
```

Open `.env` and set:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### 2. Build and start all services

```bash
docker compose up --build
```

This starts:
- `weaviate` — vector database on port 8080 (with `text2vec-openai` module)
- `api` — KubeSentient FastAPI on port 8000

Wait until you see `Application startup complete` in the api logs.

### 3. Ingest runbooks into Weaviate

```bash
docker compose exec api python -m scripts.ingest_runbooks
```

Expected output:
```
Weaviate is ready.
Found 18 chunks to ingest...
Ingestion complete - 18 chunk(s) written to Weaviate.
```

### 4. Verify the stack

```bash
# Health check
curl http://localhost:8000/health
# -> {"status": "ok", "version": "0.1.0"}

# Weaviate ready
curl http://localhost:8080/v1/.well-known/ready
# -> {}
```

### 5. Send a test alert

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "version": "4",
    "groupKey": "test-crash-loop",
    "status": "firing",
    "receiver": "kubesentient",
    "groupLabels": {"alertname": "KubePodCrashLooping"},
    "commonLabels": {
      "alertname": "KubePodCrashLooping",
      "namespace": "production",
      "pod": "payment-service-7d8f9b-xkp2j"
    },
    "commonAnnotations": {
      "summary": "Pod payment-service-7d8f9b-xkp2j is crash looping"
    },
    "externalURL": "http://alertmanager:9093",
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "KubePodCrashLooping",
        "namespace": "production",
        "pod": "payment-service-7d8f9b-xkp2j"
      },
      "annotations": {
        "summary": "Pod crash looping in production namespace"
      },
      "startsAt": "2024-01-15T10:00:00Z"
    }]
  }'
```

Expected response: `{"status": "accepted", "message": "Alerts queued for processing"}`

### 6. Watch the agent work

```bash
docker compose logs -f api
```

You'll see the LangGraph workflow execute:
```
[INFO] kubesentient.routes   - Received webhook from kubesentient with 1 alerts
[INFO] kubesentient.agent    - Node: initial_triage
[INFO] kubesentient.agent    - Node: investigator
[INFO] kubesentient.agent    - Node: planner
[INFO] kubesentient.agent    - Node: human_approval - Waiting for user signal (Mocked)
[INFO] kubesentient.routes   - Agent finished. Remediation Plan:
                               ## Root Cause Analysis ...
```

> **Note:** K8s tools (logs, events, pod describe) will return "K8s client not initialized" in local dev because there's no real cluster. The agent will still invoke the RAG runbook search and produce a plan based on the alert context. For full K8s tool functionality, run inside a cluster or set `KUBECONFIG` and change `local_mode=True` in `src/agent_core/tools.py:8`.

---

## Local Development (without Docker)

```bash
# Install dependencies
pip install poetry
poetry install

# Set env vars
export ANTHROPIC_API_KEY=sk-ant-your-key-here
export OPENAI_API_KEY=sk-your-openai-key-here     # embeddings only
export WEAVIATE_URL=http://localhost:8080         # must have Weaviate running separately

# Run the API
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests (all mocked, no external services needed)
poetry run pytest tests/ -v
```

---

## Kubernetes Deployment (Production)

### 1. Build and push the image

```bash
docker build -t your-registry/kubesentient:v1.0.0 .
docker push your-registry/kubesentient:v1.0.0
```

### 2. Create the secrets

```bash
kubectl create secret generic kubesentient-secrets \
  --from-literal=anthropic-api-key=sk-ant-your-key-here \
  --from-literal=openai-api-key=sk-your-openai-key-here \
  -n kubesentient
```

### 3. Install via Helm

```bash
helm install kubesentient ./helm \
  --namespace kubesentient \
  --create-namespace \
  --set image.repository=your-registry/kubesentient \
  --set image.tag=v1.0.0
```

### 4. Ingest runbooks into the cluster's Weaviate

```bash
# Port-forward Weaviate
kubectl port-forward svc/kubesentient-weaviate 8080:8080 -n kubesentient &

# Run ingestion locally against the cluster's Weaviate
WEAVIATE_URL=http://localhost:8080 poetry run python -m scripts.ingest_runbooks
```

### 5. Configure AlertManager

Add to your AlertManager config:
```yaml
receivers:
  - name: kubesentient
    webhook_configs:
      - url: http://kubesentient-api.kubesentient.svc.cluster.local/api/v1/alerts
        send_resolved: false
```

---

## Adding More Runbooks

Drop any `.md` file into the `runbooks/` directory and re-run ingestion:

```bash
# Local
python -m scripts.ingest_runbooks

# Docker
docker compose exec api python -m scripts.ingest_runbooks

# Kubernetes
kubectl exec -n kubesentient deployment/kubesentient-api -- \
  python -m scripts.ingest_runbooks --runbooks-dir /app/runbooks
```

**Real runbook sources:**
- [AWS Operational Runbooks](https://docs.aws.amazon.com/systems-manager/latest/userguide/runbooks.html)
- [Kubernetes SIG Runbooks](https://runbooks.prometheus-operator.dev/) — excellent per-alert runbooks
- Your own team's Confluence/Notion pages (export to markdown)

---

## Verification Checklist

After a fresh deploy, verify in order:

- [ ] `curl localhost:8000/health` -> `{"status":"ok","version":"0.1.0"}`
- [ ] `curl localhost:8080/v1/.well-known/ready` -> `{}`
- [ ] Runbook ingestion completes without errors
- [ ] POST to `/api/v1/alerts` returns `202 Accepted`
- [ ] API logs show all 4 agent nodes executing (triage, investigator, planner, approval)
- [ ] A remediation plan appears in logs
- [ ] `poetry run pytest tests/ -v` — all tests pass

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | **Yes** | — | Anthropic API key powering the reasoning loop (Claude Sonnet 4.6) |
| `ANTHROPIC_MODEL` | No | `claude-sonnet-4-6` | Override the Claude model id |
| `OPENAI_API_KEY` | **Yes** | — | OpenAI key used solely for Weaviate `text2vec-openai` embeddings |
| `WEAVIATE_URL` | No | `http://localhost:8080` | Weaviate HTTP URL |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `KUBECONFIG` | No | `~/.kube/config` | Path to kubeconfig for local K8s access |

---

## Project Structure

```
.
├── src/
│   ├── api/              # FastAPI: routes, models, app factory
│   ├── agent_core/       # LangGraph workflow: graph, nodes (Claude), tools, state
│   └── ingestion/        # Weaviate client + document chunker
├── runbooks/             # Markdown runbooks for RAG knowledge base
├── scripts/
│   └── ingest_runbooks.py  # CLI: load runbooks into Weaviate
├── tests/                # pytest test suite (fully mocked)
├── helm/                 # Kubernetes Helm chart
├── Dockerfile            # Multi-stage container build
├── docker-compose.yaml   # Local dev stack
├── pyproject.toml        # Python dependencies (Poetry)
└── .env.example          # Environment variable template
```
