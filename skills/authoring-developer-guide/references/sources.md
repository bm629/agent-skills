# Sources — `authoring-developer-guide`

Research provenance for the method + quality bar. Primary research via `deep-research` (2026-06-05); **WebFetch was sandbox-denied, so research fell back to WebSearch with >=2 independent sources per load-bearing claim** (noted per the standing deep-research-primary norm). External content was passed through `external-content-sanitizer` before folding in (clean — descriptive summaries, no commands/URLs/tool-refs lifted into actions). The shared dossier distilling these sources lives at `docs/superpowers/agent-flow/authoring-developer-guide/research/developer-guide-dossier.md` (reused by `reviewing-developer-guide`).

## Diataxis framework (the four modes, kept separated)

- diataxis.fr/start-here, diataxis.fr/ — the four documentation types (tutorial / how-to / explanation / reference), their distinct reader needs, the reader progression, and the keep-them-separated principle.
- github.com/evildmp/diataxis-documentation-framework — the canonical source text for the four types.
- idratherbewriting (what-is-diataxis), sequinstream (we-fixed-our-documentation-with-the-diataxis-framework), coderslingo (diataxis-framework-documentation) — adoption write-ups: mixing modes as the most common cause of confusing docs; reference works best in isolation.

## Developer-experience (DX) docs practice + information architecture

- Fern (buildwithfern.com) — API-documentation-best-practices, API-design-best-practices, SDK-generation-tools: organize around developer workflows not API structure; quickstart auth + one working call; standardized errors; resilience defaults (retries/timeouts/idempotency); pagination abstraction; versioning + changelog + migration.
- Mintlify (how-to-write-technical-documentation) — quickstart to meaningful value (not hello-world); concepts before reference; task-oriented how-to guides.
- GitBook (documentation-structure), Document360 (write-developer-documentation, SDK-vs-API) — logical ordering: introductory concepts (Getting Started, Installation) before specifics (API Reference, Guides).
- Archbee (API-documentation-examples, SDK-documentation), Pragmatic Engineer (building-great-SDKs) — goal-named guides, multi-language code examples, SDK guide vs API reference split.
- Pluralsight (tech-documentation-best-practices), business.daily.dev (Stripe/Twilio/GitHub dev-trust), APIMatic (quickstart-guide-design), Voiden (developer-focused-API-docs) — docs-as-a-product; frame docs around the developer's problem, not the endpoint list.

## Getting-started credential convention (runnable, env-var, not hardcoded)

- Square / Plaid / Google / Coinbase / AWS SDK quickstarts — credentials read from an env var / `.env` to avoid hardcoded credentials in source.

## Production best-practices (errors, retries, idempotency, pagination, rate limits, versioning)

- AWS SDK retry-behavior, Google Vertex retry-strategy, BoldSign API-retry — exponential backoff with jitter + timeouts; retry only the retryable failures, fail fast on the rest.
- API7 + commercetools error-handling — distinguish retryable vs fatal; idempotency keys for create/charge so retried writes don't duplicate.
- getknit (API-rate-limiting), aimadetools (how-to-handle-API-errors) — catch 429, read `Retry-After`, else backoff+jitter, queue non-urgent.
- Fern (API-design), getknit, deepdocs (API-documentation-best-practices) — cursor-based pagination; SemVer + clear deprecation timelines (6-12 months standard) + migration guides with before/after for each breaking change.

## Notes / caveats

- A few vendor specifics (e.g. one vendor's exact env-var name) are single-source and used only as illustrative examples, not load-bearing claims; every load-bearing claim has >=2 independent sources.
- WebFetch denied -> WebSearch summaries only; claims verified by cross-source agreement, not primary-page quotes.
