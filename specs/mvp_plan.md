# MVP Plan

## Milestone 1: Lease + Payment

- Implement `POST /v1/leases`
- Create Stripe Payment Link
- Persist lease in `AWAITING_PAYMENT`
- Handle webhook to transition to `PAID`

## Milestone 2: Provision + TTL

- Launch EC2 from template
- Attach minimal IAM role
- Register lease as `READY`
- Enforce auto-terminate at TTL

## Milestone 3: Job Execution

- Submit command payload
- Execute under non-root runtime user
- Stream logs to S3 + API
- Mark terminal job state

## Milestone 4: Safety + Quotas

- Per-user quota and spend caps
- Lease cancellation path
- Dead-letter queue for failed transitions
