# Billing With Stripe Link CLI (Agent-first)

This project should use Stripe Link CLI as the primary payment-approval mechanism for agent-triggered compute.

## What Link CLI provides

- Agent can request spend credentials without storing user card details.
- User approves each purchase in Link (push/email flow).
- Approved request returns one-time-use credential data.
- Supports MPP (`HTTP 402`) merchants via `shared_payment_token`.

## Core Commands

Install:
```bash
npm i -g @stripe/link-cli
# or
npx @stripe/link-cli
```

Auth:
```bash
link-cli auth login --client-name "Agent EC2"
link-cli auth status --format json
```

List payment methods:
```bash
link-cli payment-methods list --format json
```

Create spend request (with approval):
```bash
link-cli spend-request create \
  --payment-method-id csmrpd_xxx \
  --merchant-name "Agent EC2 Compute" \
  --merchant-url "https://agent-ec2.example" \
  --context "Provisioning a 60-minute compute lease for requested agent job." \
  --amount 500 \
  --line-item "name:EC2 lease (60m),unit_amount:500,quantity:1" \
  --total "type:total,display_text:Total,amount:500" \
  --request-approval \
  --format json
```

Poll terminal state:
```bash
link-cli spend-request retrieve lsrq_001 \
  --interval 2 --max-attempts 150 --format json
```

## Integration Pattern for This Service

1. Orchestrator receives lease request.
2. Orchestrator creates Link spend request (`--request-approval`).
3. Service waits for terminal status (`approved` / `denied` / `expired`).
4. If approved, provision EC2 and start TTL lease.
5. If denied/expired, mark lease terminal and do not provision.

## MCP Option

Link CLI can run as local MCP server:
```json
{
  "mcpServers": {
    "link": {
      "command": "npx",
      "args": ["@stripe/link-cli", "--mcp"]
    }
  }
}
```

## Notes

- Keep raw card credential material out of logs.
- Treat spend requests as auditable objects tied to lease IDs.
- Include explicit human-readable context so user knows what they are approving.
