# Agent Burst Compute Service

Temporary EC2 compute leasing for remote agents (e.g., Codex on Raspberry Pi).

## Idea

Agents run lightweight locally. When heavy compute is needed, they request a short-lived EC2 runtime (for example, 15-120 minutes). The end-user receives a payment/approval link. After payment, the job is executed on provisioned compute, logs/results are returned, and the instance is terminated automatically.

## Core Goals

- Fast provisioning of ephemeral compute
- Clear user approval and payment before cost is incurred
- Strict TTL auto-shutdown to cap spend
- Agent-friendly API (simple request/lease/execute lifecycle)

## Initial Scope (MVP)

- AWS EC2 only
- Stripe Link CLI spend-request + user approval activation
- One region, small fixed instance catalog
- Script/batch execution with stdout/stderr capture
- Hard runtime cap and kill switch

See `docs/` for architecture and API design.
