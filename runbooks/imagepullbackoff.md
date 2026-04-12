# Runbook: ImagePullBackOff / ErrImagePull

## Overview

`ImagePullBackOff` means Kubernetes cannot pull the container image from the registry. The node's container runtime (containerd/docker) tried to fetch the image and failed. The backoff timer grows with each retry.

## Symptoms

- `kubectl get pods` shows `ImagePullBackOff` or `ErrImagePull` status
- AlertManager alert: `KubePodImagePullError`
- No container has started; restarts may be 0

## Investigation Steps

### 1. Read the pull error

```bash
kubectl describe pod <pod-name> -n <namespace>
# Read the Events section — it shows the exact pull error message
```

Common error messages:
- `Failed to pull image "myrepo/myapp:latest": rpc error: ... 401 Unauthorized` → Auth failure
- `Failed to pull image "myrepo/myapp:v1.2.3": not found` → Tag doesn't exist
- `Failed to pull image "myrepo/myapp:latest": ... connection refused` → Registry unreachable
- `pull access denied` → Repository is private and credentials are missing

### 2. Verify the image tag exists

```bash
# For Docker Hub
docker manifest inspect <image>:<tag>

# For ECR
aws ecr describe-images --repository-name <repo> --image-ids imageTag=<tag>

# For GCR
gcloud container images list-tags gcr.io/<project>/<image>
```

### 3. Check if an imagePullSecret exists

```bash
kubectl get secret -n <namespace> | grep registry
kubectl describe pod <pod-name> -n <namespace> | grep imagePullSecret
```

## Root Causes and Remediation

### Wrong image tag (typo or deleted tag)

```bash
# Fix the tag in the deployment
kubectl set image deployment/<deployment-name> \
  <container-name>=<registry>/<image>:<correct-tag> \
  -n <namespace>
```

### Missing imagePullSecret (private registry)

```bash
# Create registry secret
kubectl create secret docker-registry registry-credentials \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n <namespace>

# Patch deployment to use it
kubectl patch deployment <deployment-name> -n <namespace> \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/imagePullSecrets","value":[{"name":"registry-credentials"}]}]'
```

### ECR token expired (12-hour TTL)

AWS ECR tokens expire. Use the ECR credential helper or rotate the pull secret:

```bash
# Regenerate ECR token and update secret
aws ecr get-login-password --region <region> | \
  kubectl create secret docker-registry ecr-secret \
    --docker-server=<account>.dkr.ecr.<region>.amazonaws.com \
    --docker-username=AWS \
    --docker-password-stdin \
    --namespace <namespace> \
    --dry-run=client -o yaml | kubectl apply -f -
```

### Registry network issue (node cannot reach registry)

```bash
# Test from inside the cluster
kubectl run debug --image=busybox --rm -it --restart=Never -- \
  wget -qO- <registry-url>/v2/

# Check network policies
kubectl get networkpolicy -n <namespace>
```

## Escalation

If the image exists and credentials are correct but pull still fails, the issue is likely a node-level network or disk pressure problem. Check node events:

```bash
kubectl describe node <node-name> | grep -A20 Events
```

Escalate to platform/infra team if node-level issues are suspected.
