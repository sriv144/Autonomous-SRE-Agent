# Runbook: Deployment Rollout Stuck / Not Progressing

## Overview

A Kubernetes Deployment rollout is "stuck" when new ReplicaSet pods are not becoming Ready within the `progressDeadlineSeconds` (default 600s / 10 minutes). This blocks automated deployment pipelines and leaves the service in a partially-updated state.

## Symptoms

- `kubectl rollout status deployment/<name>` hangs or reports timeout
- AlertManager alert: `KubeDeploymentRolloutStuck` or `KubeDeploymentReplicasMismatch`
- CI/CD pipeline waiting on rollout confirmation
- Some pods running old image, some running new image (mixed traffic)

## Investigation Steps

### 1. Check rollout status

```bash
kubectl rollout status deployment/<deployment-name> -n <namespace> --timeout=60s
kubectl get replicaset -n <namespace> | grep <deployment-name>
```

### 2. Check new pods' status

```bash
kubectl get pods -n <namespace> -l app=<app-label> --sort-by=.metadata.creationTimestamp
```

Look for pods in `CrashLoopBackOff`, `Pending`, `ImagePullBackOff`, or stuck in `ContainerCreating`.

### 3. Describe the newest pods

```bash
# Find the newest ReplicaSet
kubectl get rs -n <namespace> --sort-by=.metadata.creationTimestamp

# Describe the pods from the newest RS
kubectl describe pod <new-pod-name> -n <namespace>
```

### 4. Check readiness probe

```bash
kubectl describe pod <new-pod-name> -n <namespace> | grep -A10 "Readiness"
```

If readiness probe is failing, the pod never becomes Ready and the rollout blocks.

### 5. Check deployment conditions

```bash
kubectl describe deployment <deployment-name> -n <namespace> | grep -A5 Conditions
```

Look for `Progressing` condition status and reason.

## Root Causes and Remediation

### New pods are crashing (bad image/config)

Follow the [CrashLoopBackOff runbook](pod-crashloopbackoff.md) for the new pods, then roll back:

```bash
kubectl rollout undo deployment/<deployment-name> -n <namespace>
kubectl rollout status deployment/<deployment-name> -n <namespace>
```

### Readiness probe too strict for new version

The new version may take longer to initialize:

```bash
kubectl patch deployment <deployment-name> -n <namespace> --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/initialDelaySeconds","value":30},
  {"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/failureThreshold","value":10}
]'
```

### Insufficient cluster capacity for rolling update

If `maxSurge` creates extra pods but there's no room:

```bash
# Check if new pods are Pending
kubectl get pods -n <namespace> | grep Pending

# Temporarily reduce maxUnavailable/maxSurge to roll slower
kubectl patch deployment <deployment-name> -n <namespace> --type='json' -p='[
  {"op":"replace","path":"/spec/strategy/rollingUpdate/maxSurge","value":1},
  {"op":"replace","path":"/spec/strategy/rollingUpdate/maxUnavailable","value":0}
]'
```

### PodDisruptionBudget blocking evictions

```bash
kubectl get pdb -n <namespace>
kubectl describe pdb <pdb-name> -n <namespace>
# Check if minAvailable is too high for the current replica count
```

## Emergency Rollback

```bash
# Rollback to previous version immediately
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Rollback to specific revision
kubectl rollout history deployment/<deployment-name> -n <namespace>
kubectl rollout undo deployment/<deployment-name> -n <namespace> --to-revision=<N>
```

## Escalation

If rollback also gets stuck, the cluster state is compromised. Escalate immediately to the platform team with full `kubectl describe deployment` and `kubectl get events -n <namespace>` output.
