# Kubernetes Runbook

## Symptoms
- Pods stuck in CrashLoopBackOff or Pending
- OOMKilled errors
- Node NotReady status
- Deployments not rolling out

## Diagnosis

1. Check cluster health:
   ```bash
   kubectl get nodes
   kubectl top nodes
   ```

2. Check pod status:
   ```bash
   kubectl get pods -A | grep -v Running
   ```

3. Check recent events:
   ```bash
   kubectl get events --sort-by='.lastTimestamp' | tail -20
   ```

## Resolution

### CrashLoopBackOff

1. Check pod logs:
   ```bash
   kubectl logs <pod-name> --previous
   ```

2. Check pod description for events:
   ```bash
   kubectl describe pod <pod-name>
   ```

3. Common causes:
   - Missing config/secrets: Check if ConfigMap/Secret exists
   - Bad image: Verify image tag exists in registry
   - Failing health checks: Review readiness/liveness probes

### OOMKilled

1. Check memory usage:
   ```bash
   kubectl top pod <pod-name>
   ```

2. Check resource limits:
   ```bash
   kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].resources}'
   ```

3. Increase memory limit in deployment:
   ```yaml
   resources:
     limits:
       memory: "512Mi"  # Increase as needed
   ```

4. Apply and restart:
   ```bash
   kubectl apply -f deployment.yaml
   ```

### Node NotReady

1. Check node conditions:
   ```bash
   kubectl describe node <node-name> | grep -A5 Conditions
   ```

2. SSH to node and check kubelet:
   ```bash
   systemctl status kubelet
   journalctl -u kubelet --tail=50
   ```

3. If disk pressure, clean up:
   ```bash
   docker system prune -af
   ```

4. If unrecoverable, drain and replace:
   ```bash
   kubectl drain <node-name> --ignore-daemonsets
   kubectl delete node <node-name>
   ```

## Escalation

If cluster is degraded >10 minutes, page infrastructure team: @infra-oncall
