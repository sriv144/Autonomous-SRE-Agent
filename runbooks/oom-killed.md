# Runbook: OOMKilled (Out of Memory)

## Overview

An `OOMKilled` event means the Linux kernel's OOM killer terminated a container because it exceeded its configured memory limit. The pod may or may not restart depending on the restart policy.

## Symptoms

- `kubectl describe pod` shows `Last State: OOMKilled` or `Exit Code: 137`
- Pod restart count incrementing
- AlertManager alerts: `KubePodOOMKilled`, `KubeContainerOOMKilledTotal`
- Application serving errors during the restart window

## Investigation Steps

### 1. Confirm OOMKill

```bash
kubectl describe pod <pod-name> -n <namespace> | grep -A5 "Last State"
# Look for: Reason: OOMKilled
```

### 2. Check current memory usage vs limits

```bash
kubectl top pod <pod-name> -n <namespace>
kubectl describe pod <pod-name> -n <namespace> | grep -A8 "Limits\|Requests"
```

### 3. Check memory trends in Grafana

Query Prometheus for memory usage trend before the kill:
```
container_memory_working_set_bytes{pod="<pod-name>", namespace="<namespace>"}
```

### 4. Identify the memory leak source

```bash
# Check logs just before OOMKill
kubectl logs <pod-name> -n <namespace> --previous --tail=200

# Check if this is a known memory-leaking dependency
kubectl exec <pod-name> -n <namespace> -- cat /proc/meminfo
```

## Root Causes

1. **Memory limit set too low** — application legitimately needs more memory under load
2. **Memory leak** — application is leaking memory and growing unbounded
3. **Large in-memory cache** — caching layer consuming too much RAM
4. **Heap dump on error** — JVM or Python process creating in-memory core dump

## Remediation

### Immediate: Increase memory limit (stops the restart loop)

```bash
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"1Gi"},
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"512Mi"}
  ]'
```

### Long-term: Fix memory leak

1. Profile the application (pyspy, jstack, pprof)
2. Review recent code changes that might have introduced unbounded data structures
3. Add memory limit alerts at 80% threshold for early warning

### Configure memory-aware autoscaling

```bash
kubectl autoscale deployment <deployment-name> \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n <namespace>
```

## Escalation

If OOMKills recur within 24 hours after increasing limits:
1. File ticket with application team to profile memory usage
2. Attach Grafana memory graph (last 7 days)
3. Note the exact workload pattern that triggers the kill
