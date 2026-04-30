# Architecture (MVP)

## Components

1. `api-gateway` (public HTTPS)
- Receives agent lease requests and execution requests.
- Returns payment/approval URL.

2. `orchestrator` service
- Creates payment intents/links.
- Provisions EC2 after successful payment webhook.
- Tracks lease state machine.

3. `billing` integration
- Stripe Payment Links or Checkout Session.
- Webhook confirmation drives state transition to `PAID`.

4. `runner` on EC2
- Bootstraps via user-data.
- Pulls one signed job payload.
- Executes in sandboxed runtime user.
- Uploads logs/artifacts.

5. `state store`
- Postgres or DynamoDB for leases/jobs/events.

6. `artifact store`
- S3 for logs, outputs, metadata.

## State Machine

`REQUESTED -> AWAITING_PAYMENT -> PAID -> PROVISIONING -> READY -> RUNNING -> COMPLETED`

Error paths:
- `PAYMENT_EXPIRED`
- `PROVISION_FAILED`
- `RUN_FAILED`
- `TIMEOUT_TERMINATED`

## Security Baseline

- Signed agent tokens (short-lived JWT)
- Per-lease scoped credentials
- No inbound SSH; use SSM/agent pull model
- Encrypted artifacts (S3 SSE)
- Mandatory TTL termination watchdog

## Cost Controls

- Max lease duration (default 60m)
- Instance allowlist (e.g., `c7i.large`, `g6.xlarge`)
- Region allowlist
- Daily spend cap and per-user quota
