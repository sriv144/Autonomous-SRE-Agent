# Security Policy

KubeSentient is designed to run inside a Kubernetes cluster with read access
to cluster state and outbound calls to OpenAI and Weaviate. Treat the K8s
tool surface and the credential handling paths as the security boundary.

## Supported versions

Only the latest commit on `main` receives security fixes.

## Reporting a vulnerability

**Do not** open a public GitHub issue for any of the following classes of
bug:

- A K8s tool that performs a write/mutation verb without going through the
  `human_approval` node (`scale`, `delete`, `patch`, `restart`, `exec`).
- A path that allows the agent to invoke remediation tools without an
  approval signal.
- Credential leakage: `OPENAI_API_KEY`, kubeconfig contents, Weaviate auth
  appearing in logs, prompts, or LLM context windows.
- Prompt injection from an alert payload that causes the planner to emit a
  plan invoking unsanctioned tools or to exfiltrate cluster state.
- SSRF or arbitrary URL fetch from any ingestion path.

Instead, email the maintainer privately with a reproduction, the affected
file path, and your suggested fix. You can expect an acknowledgement within
7 days and a coordinated disclosure plan before any public mention.

## Hardening checklist for self-hosted deployments

- Run the agent's ServiceAccount with read-only RBAC by default. Add a
  separate, narrower ServiceAccount for any approved write actions.
- Mount `.env` / OpenAI credentials as a read-only Kubernetes Secret; never
  bake them into the container image or Helm chart values.
- Pin the OpenAI model in `.env` so a model upgrade cannot silently change
  tool-calling behaviour.
- Restrict outbound egress to OpenAI and the in-cluster Weaviate service.
