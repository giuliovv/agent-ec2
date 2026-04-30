# API Sketch

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

Response:
```json
{
  "lease_id": "lease_123",
  "status": "AWAITING_PAYMENT",
  "approval_url": "https://pay.example/...",
  "expires_at": "2026-05-01T12:00:00Z"
}
```

## 2) Poll Lease Status

`GET /v1/leases/{lease_id}`

Returns current state + compute endpoint when ready.

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
