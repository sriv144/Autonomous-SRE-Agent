# Runbook: CrashLoopBackOff

## Overview

A pod in `CrashLoopBackOff` state means the container is repeatedly starting, crashing, and being restarted by Kubernetes. The backoff timer grows exponentially (10s, 20s, 40s… up to 5 min) between restarts.

## Symptoms

- `kubectl get pods` shows `CrashLoopBackOff` in the STATUS column
- High restart count in the RESTARTS column
- AlertManager alert: `KubePodCrashLooping`

## Common Root Causes

1. **Application error on startup** — misconfiguration, missing env var, bad entrypoint
2. **OOMKilled** — container exceeds its memory limit
3. **Liveness probe too aggressive** — probe kills the container before app finishes initializing
4. **Missing ConfigMap or Secret** — app fails because a mounted volume doesn't exist
5. **Image pull issue resolved but old crashloop persists** — stale pod state

## Investigation Steps

### 1. Check pod status and restart count

```bash
kubectl get pod <pod-name> -n <namespace>
kubectl describe pod <pod-name> -n <namespace>
```

Look at:
- `Last State.Exit Code` — exit code 1 = app error, exit code 137 = OOMKilled, exit code 143 = SIGTERM
- `Events` section at the bottom

### 2. Read the crash logs

```bash
# Current logs
kubectl logs <pod-name> -n <namespace>

# Logs from the previous crashed container (most useful)
kubectl logs <pod-name> -n <namespace> --previous
```

### 3. Check resource limits

```bash
kubectl describe pod <pod-name> -n <namespace> | grep -A5 Limits
```

If `Exit Code: 137` appears, the container was OOMKilled — increase memory limits.

### 4. Check mounted volumes

```bash
kubectl describe pod <pod-name> -n <namespace> | grep -A10 Volumes
kubectl get configmap -n <namespace>
kubectl get secret -n <namespace>
```

## Remediation

### OOMKilled
```bash
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"512Mi"}]'
```

### Bad liveness probe
```bash
# Edit the deployment to increase initialDelaySeconds
kubectl edit deployment <deployment-name> -n <namespace>
# Increase livenessProbe.initialDelaySeconds to 60+
```

### Application misconfiguration
```bash
# Check env vars
kubectl exec <pod-name> -n <namespace> -- env | grep -i config

# Check if secret/configmap exists
kubectl get secret <secret-name> -n <namespace>
```

### Force restart (clear backoff timer)
```bash
kubectl rollout restart deployment/<deployment-name> -n <namespace>
```

## Escalation

If the crash loop persists after 3+ remediation attempts with different root causes, escalate to the owning team with:
- Full `kubectl describe pod` output
- `kubectl logs --previous` output
- Resource metrics from Grafana dashboard
