# Billing With Stripe Link CLI + HTTP 402 (Agentic Pattern)

## Verified capabilities (from `stripe/link-cli`)

- One-time-use payment credentials from Link wallet.
- Optional human approval via `--request-approval`.
- MPP/HTTP-402 support via `shared_payment_token`.
- Direct MPP payment helper: `link-cli mpp pay ...`.
- Works via `npx` (minimal install footprint).

## Minimal-install client pattern

No global install required:
```bash
npx @stripe/link-cli auth login --client-name "Agent EC2"
npx @stripe/link-cli payment-methods list --format json
```

For MPP/402 merchants:
```bash
npx @stripe/link-cli spend-request create \
  --payment-method-id csmrpd_xxx \
  --merchant-name "Agent EC2 Compute" \
  --merchant-url "https://agent-ec2.example" \
  --context "Lease compute for agent job" \
  --amount 500 \
  --line-item "name:EC2 lease (60m),unit_amount:500,quantity:1" \
  --total "type:total,display_text:Total,amount:500" \
  --credential-type "shared_payment_token" \
  --format json
```

Then pay the HTTP-402 endpoint:
```bash
npx @stripe/link-cli mpp pay https://api.agent-ec2.example/v1/pay/lease_123 \
  --spend-request-id lsrq_001 \
  --method POST \
  --data '{}' \
  --format json
```

## Two operating modes

1. Interactive approval mode (safer default)
- Include `--request-approval`.
- User approves each spend request via Link app/email.

2. Unattended mode (your requested UX)
- Do not require per-request approval.
- Agent uses pre-authenticated Link account and policy-scoped payment method.
- Still enforce server-side spend controls (caps, quotas, lease TTL).

## Important product constraint

Link CLI still requires an initial Link account authentication/binding step.
"No user involvement" can mean no per-transaction prompts after setup, but not zero trust/bootstrap setup.

## MCP option

If agent runtime already supports MCP:
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

## Recommendation for this project

- Use HTTP 402 as canonical server response when lease is unpaid.
- Prefer MPP (`shared_payment_token`) for API-native flow.
- Support both modes:
  - `approval_required=true` for human-in-loop customers
  - `approval_required=false` for pre-authorized autonomous agents
