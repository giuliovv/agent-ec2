# API Sketch (HTTP 402-first)

## Lease Lifecycle

`REQUESTED -> PAYMENT_REQUIRED (402) -> PAID -> PROVISIONING -> READY -> RUNNING -> COMPLETED`

Failure states:
- `PAYMENT_DENIED`
- `PAYMENT_EXPIRED`
- `PROVISION_FAILED`
- `RUN_FAILED`
- `TIMEOUT_TERMINATED`

## 1) Request Lease

`POST /v1/leases`

Request:
```json
{
  "agent_id": "codex-rpi-01",
  "profile": "cpu-small",
  "max_minutes": 60,
  "job_summary": "Run integration tests for repo X"
}
```

### Response A: Payment Required (`402`)

```json
{
  "error": "PAYMENT_REQUIRED",
  "lease_id": "lease_123",
  "status": "PAYMENT_REQUIRED",
  "payment": {
    "provider": "stripe_link_cli",
    "mode": "mpp_http_402",
    "spend_request_id": "lsrq_001",
    "credential_type": "shared_payment_token",
    "mpp_endpoint": "https://api.agent-ec2.example/v1/pay/lease_123",
    "poll_url": "/v1/leases/lease_123"
  },
  "expires_at": "2026-05-01T12:00:00Z"
}
```

### Response B: Already Paid/Authorized (`201`)

```json
{
  "lease_id": "lease_123",
  "status": "PAID"
}
```

## 2) Poll Lease Status

`GET /v1/leases/{lease_id}`

- Returns `402` while unpaid.
- Returns `200` once in `PAID/PROVISIONING/READY/RUNNING/COMPLETED`.

## 3) Submit Job

`POST /v1/leases/{lease_id}/jobs`

Request:
```json
{
  "command": "bash run_heavy.sh",
  "env": {"MODE": "ci"},
  "artifacts": ["results/*.json", "logs/*.txt"]
}
```

## 4) Job Status / Logs

`GET /v1/jobs/{job_id}`
`GET /v1/jobs/{job_id}/logs`

## 5) Terminate Early

`POST /v1/leases/{lease_id}/terminate`
