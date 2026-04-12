# Runbook: High CPU Throttling

## Overview

CPU throttling occurs when a container exceeds its CPU limit (`spec.resources.limits.cpu`). The Linux cgroup throttles the container's CPU time, causing request latency spikes even though the process appears healthy.

## Symptoms

- Elevated latency (p99 > SLO) without a corresponding error rate increase
- `container_cpu_cfs_throttled_seconds_total` metric increasing in Prometheus
- AlertManager alert: `KubeContainerCPUThrottlingHigh`
- CPU usage appears below limit in simple metrics but throttling is high

## Investigation Steps

### 1. Check current CPU usage vs limits

```bash
kubectl top pod <pod-name> -n <namespace> --containers
kubectl describe pod <pod-name> -n <namespace> | grep -A8 "Limits\|Requests"
```

### 2. Calculate throttling percentage in Prometheus

```promql
rate(container_cpu_cfs_throttled_periods_total{pod="<pod-name>"}[5m])
/
rate(container_cpu_cfs_periods_total{pod="<pod-name>"}[5m])
* 100
```

Throttling > 25% is considered high. Throttling > 50% will cause noticeable latency.

### 3. Identify which container is throttling

```bash
kubectl top pod <pod-name> -n <namespace> --containers
```

### 4. Check if it's a traffic spike or a steady-state issue

Review QPS / RPS in Grafana — a spike in traffic is expected to cause temporary throttling. Steady-state throttling indicates the limit is too low.

## Root Causes

1. **CPU limit set too low** — application is legitimately CPU-bound at normal traffic
2. **Burst traffic** — short traffic spikes hitting the limit
3. **Inefficient code / tight loops** — CPU-hungry code path triggered by specific requests
4. **Garbage collection pause (JVM/Python)** — GC can cause CPU spikes

## Remediation

### Increase CPU limit (immediate relief)

```bash
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/cpu","value":"2"},
    {"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"500m"}
  ]'
```

### Remove CPU limit entirely (controversial but valid for latency-sensitive services)

CPU limits in Kubernetes are implemented via CFS quotas, which can cause significant latency. For latency-sensitive workloads, removing the limit and relying only on requests + HPA is often better.

```bash
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[{"op":"remove","path":"/spec/template/spec/containers/0/resources/limits/cpu"}]'
```

### Scale horizontally to distribute load

```bash
kubectl scale deployment <deployment-name> --replicas=5 -n <namespace>
```

### Configure HPA on CPU utilization

```bash
kubectl autoscale deployment <deployment-name> \
  --cpu-percent=60 \
  --min=2 \
  --max=10 \
  -n <namespace>
```

## Long-term Actions

1. Profile the CPU-intensive code path (py-spy, async-profiler)
2. Add CPU throttling alert at 25% threshold for early warning
3. Review if the service should be split (microservice decomposition)

## Escalation

If throttling persists after doubling CPU limits, escalate to application team with:
- Prometheus throttling graph (last 2 hours)
- Profiler output identifying the hot code path
