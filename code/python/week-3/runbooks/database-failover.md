# Database Failover Runbook

## Symptoms
- Application errors: "connection refused" or "too many connections"
- High replication lag (>30 seconds)
- Primary database unresponsive

## Diagnosis

1. Check database status:
   ```bash
   pg_isready -h primary.db.internal
   ```

2. Check connection pool:
   ```bash
   SELECT count(*) FROM pg_stat_activity;
   ```
   Normal: <100 connections. Critical: >400 connections.

3. Check replication lag:
   ```bash
   SELECT extract(epoch FROM now() - pg_last_xact_replay_timestamp());
   ```

## Resolution

### Connection Pool Exhaustion

1. Identify long-running queries:
   ```sql
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY duration DESC;
   ```

2. Kill long-running queries (>5 minutes):
   ```sql
   SELECT pg_terminate_backend(pid);
   ```

3. If pool still exhausted, restart application pods:
   ```bash
   kubectl rollout restart deployment/api-server
   ```

### Primary Failure

1. Verify primary is down:
   ```bash
   pg_isready -h primary.db.internal
   ```

2. Promote replica to primary:
   ```bash
   pg_ctl promote -D /var/lib/postgresql/data
   ```

3. Update DNS to point to new primary:
   ```bash
   aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://failover.json
   ```

4. Notify team in #incidents channel.

## Escalation

If resolution takes >15 minutes, page the database on-call: @db-oncall
