# API Gateway Runbook

## Symptoms
- 502/503 errors from the gateway
- High latency (>2s response times)
- Rate limiting errors (429s)

## Diagnosis

1. Check gateway health:
   ```bash
   curl -s https://api.example.com/health | jq .
   ```

2. Check upstream services:
   ```bash
   kubectl get pods -n api | grep -v Running
   ```

3. Check rate limit status:
   ```bash
   redis-cli GET "ratelimit:global"
   ```

## Resolution

### 502 Bad Gateway

1. Identify failing upstream:
   ```bash
   kubectl logs -n gateway deploy/api-gateway --tail=100 | grep 502
   ```

2. Check if upstream pods are healthy:
   ```bash
   kubectl describe pod <pod-name> -n api
   ```

3. Restart unhealthy upstream:
   ```bash
   kubectl rollout restart deployment/<service-name> -n api
   ```

### Rate Limiting Issues

1. Check current limits:
   ```bash
   redis-cli HGETALL "ratelimit:config"
   ```

2. Temporarily increase limit (emergency only):
   ```bash
   redis-cli HSET "ratelimit:config" "requests_per_minute" "1000"
   ```

3. Identify source of traffic spike:
   ```bash
   kubectl logs -n gateway deploy/api-gateway | awk '{print $1}' | sort | uniq -c | sort -rn | head
   ```

### SSL Certificate Issues

1. Check certificate expiry:
   ```bash
   echo | openssl s_client -connect api.example.com:443 2>/dev/null | openssl x509 -noout -dates
   ```

2. Renew certificate:
   ```bash
   certbot renew --nginx
   ```

3. Reload gateway:
   ```bash
   kubectl rollout restart deployment/api-gateway -n gateway
   ```

## Escalation

If API is down >5 minutes, page platform team: @platform-oncall
