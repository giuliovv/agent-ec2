# Agent Burst Compute Service (MVP)

Temporary EC2 compute leasing for remote agents (e.g., Codex on Raspberry Pi), with payment-gated activation.

## MVP Scope

- FastAPI backend with lease state machine
- HTTP `402 Payment Required` on unpaid lease creation
- Stripe Link CLI / MPP-compatible payment contract (`shared_payment_token`)
- Simulated payment endpoint for local development
- Static frontend (cheap hosting via S3 + CloudFront)

## Project Layout

- `services/api/` backend API
- `frontend/` static demo UI
- `infra/cloudfront/` simple deploy helper
- `docs/` architecture + payment/API docs

## Run Backend Locally

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Health check:
```bash
curl http://localhost:8080/healthz
```

## Try the Flow

1. Open `frontend/index.html` in browser.
2. Set API base URL (default `http://localhost:8080`).
3. Create lease -> observe `402` + payment metadata.
4. Simulate payment (`POST /v1/pay/{lease_id}`).
5. Submit job.

## Cheap Frontend Hosting (S3 + CloudFront)

Sync static files to S3:
```bash
infra/cloudfront/deploy_frontend.sh <bucket-name> us-east-1
```

Then create a CloudFront distribution with the S3 bucket as origin.

## Next Steps

- Replace `/v1/pay/{lease_id}` stub with real Link CLI + MPP handler
- Add persistent DB (DynamoDB/Postgres)
- Add real EC2 provisioning + TTL terminator
- Add auth, quotas, and spend limits
