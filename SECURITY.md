# Security Policy

## Supported Versions

Only the latest commit on `main` is actively maintained.

## Reporting a Vulnerability

If you discover a security issue, please do not open a public GitHub issue.
Contact the maintainer directly so the fix can be coordinated before
disclosure.

When reporting, please include:

- A description of the issue and its impact
- A minimal reproduction (alert payload, kubectl context, or LangGraph state)
- Any logs, stack traces, or affected file paths
- Your suggested fix or mitigation, if you have one

## Webhook Surface

KubeSentient exposes `POST /api/v1/alerts` for AlertManager. In any
deployment beyond a local sandbox:

- Put the API behind an authenticated ingress — the FastAPI app itself
  does not currently authenticate AlertManager calls.
- Restrict the endpoint to the cluster’s AlertManager network identity
  via NetworkPolicy or service mesh policy.
- Never expose port 8000 directly to the public internet.

## Kubernetes Tooling

The agent ships read-only tools (logs, events, pod describe) and a
planner-only remediation flow with a mocked human-approval node. Treat
`human_approval` as a soft gate today — do **not** rewire it to apply
remediations without a real human in the loop.

When running inside a cluster:

- Run the pod with a service account scoped to `get/list/watch` on the
  resources you care about. Avoid `cluster-admin`.
- If you add write tools later, require explicit per-namespace RBAC and a
  dry-run path before any mutation.

## Secrets Hygiene

- The repository contract is `.env.example` only; never commit `.env`.
- `OPENAI_API_KEY` and any future `ANTHROPIC_API_KEY` must come from a
  Kubernetes Secret in production, not from the container image.
- Rotate any key that has been pushed to a public commit, even briefly.

## Dependencies

Dependencies are pinned in `pyproject.toml` / Poetry lock. Re-pin before
each release and run `pip-audit` (or Snyk / Dependabot equivalent)
periodically against the lockfile.
