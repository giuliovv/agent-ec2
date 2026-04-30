# Billing Notes: "Link CLI" Clarification

## What "Link" likely refers to

Online check suggests this is most likely **Stripe Link** (one-click checkout method), used via Stripe Checkout/Payment Links.

- Link is a checkout capability, not a standalone separate CLI product.
- You can still use **Stripe CLI** for local webhook testing and event forwarding.

## Recommended MVP Billing Flow

1. Backend creates Stripe Payment Link (or Checkout Session).
2. Agent/user receives approval URL.
3. User pays.
4. Stripe webhook (`checkout.session.completed` or relevant payment event) marks lease as `PAID`.
5. Orchestrator provisions EC2 and starts lease timer.

## Why this works for agents

- Human-in-the-loop consent before spend.
- Familiar card/bank payment UX.
- Strong webhook model for activation.

## Follow-up to confirm

If you meant another "Link CLI" product, we should pin the exact vendor/tool name and swap this module.
