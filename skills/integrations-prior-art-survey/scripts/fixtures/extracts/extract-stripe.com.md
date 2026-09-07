# stripe.com

## Integration surface

The API products this domain actually uses, top-N with evidence:

1. **Payment Intents** — create and confirm a charge. Used by every checkout flow in scope.
2. **Customers** — the identity the subscription and invoice objects hang off.
3. **Webhooks** — `payment_intent.*` and `invoice.*` events drive the downstream ledger.

Operations outside this list exist and were not surveyed; the scope's capabilities did not reach
them.

## Evidence

> "Stripe uses conventional HTTP response codes to indicate the success or failure of an API
> request." — the vendor's own API reference, read 2026-08-22.

> The reference documents a per-account request ceiling and the headers that report remaining
> quota, which is what `rate_limit_documented: documented` records.

## Cost to integrate

- **Auth** — an API key over HTTP Bearer. The cheapest band: no token exchange, no per-tenant
  configuration.
- **Events** — webhooks are emitted and signed, but the event envelope is proprietary rather than
  a published convention, so a receiver cannot be reused across vendors.
- **Normalisation** — the object model is close to the domain's own, so little mapping is owed.
- **Sandbox** — a test mode exists, so integration work does not need live credentials.
