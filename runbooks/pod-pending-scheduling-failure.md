# Runbook: Pod Stuck in Pending (Scheduling Failure)

## Overview

A pod in `Pending` state means Kubernetes has accepted the pod spec but cannot schedule it onto any node. This is a scheduler-level issue, not an application issue.

## Symptoms

- `kubectl get pods` shows `Pending` for more than 2-3 minutes
- AlertManager alert: `KubePodNotScheduled`
- No node assigned in `kubectl describe pod` output

## Investigation Steps

### 1. Describe the pod to read scheduler events

```bash
kubectl describe pod <pod-name> -n <namespace>
# Read the Events section at the bottom — the scheduler explains why it failed
```

Common failure messages:
- `0/5 nodes are available: 5 Insufficient memory` → Not enough memory on any node
- `0/5 nodes are available: 5 node(s) had taint that the pod didn't tolerate` → Node taint mismatch
- `0/5 nodes are available: 5 node(s) didn't match Pod's node affinity/selector` → Affinity rules too strict
- `persistentvolumeclaim "<pvc-name>" not found` → Missing PVC

### 2. Check cluster node capacity

```bash
kubectl describe nodes | grep -A5 "Allocated resources"
kubectl top nodes
```

### 3. Check node taints

```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

### 4. Check PVC status (if volume-related)

```bash
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name> -n <namespace>
```

## Root Causes and Remediation

### Insufficient cluster capacity

```bash
# Scale up the node group (cloud-specific)
# AWS EKS:
eksctl scale nodegroup --cluster=<cluster> --name=<nodegroup> --nodes=5

# GKE:
gcloud container clusters resize <cluster> --node-pool=<pool> --num-nodes=5 --region=<region>

# Or reduce the pod's resource requests temporarily
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"256Mi"}]'
```

### Node affinity / selector too restrictive

```bash
# Check what selectors are on the pod
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.nodeSelector}'

# Check available node labels
kubectl get nodes --show-labels

# Edit deployment to relax affinity rules
kubectl edit deployment <deployment-name> -n <namespace>
```

### Missing PVC / PersistentVolume

```bash
# Check if PVC is bound
kubectl get pvc <pvc-name> -n <namespace>

# If status is Pending, check StorageClass
kubectl get storageclass
kubectl describe pvc <pvc-name> -n <namespace>

# Manually provision PV or fix StorageClass configuration
```

### Node taint issue

```bash
# Add toleration to the deployment
kubectl patch deployment <deployment-name> -n <namespace> --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/tolerations","value":[
    {"key":"<taint-key>","operator":"Equal","value":"<taint-value>","effect":"NoSchedule"}
  ]}
]'
```

## Escalation

If pending > 15 minutes and node capacity looks adequate, escalate to infra/platform team to investigate the scheduler and cluster autoscaler logs.
