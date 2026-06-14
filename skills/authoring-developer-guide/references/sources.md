# Sources — `authoring-developer-guide`

Research provenance for the method + quality bar. Originally researched via `deep-research` (2026-06-05); **revised 2026-06-14** (skill v1.1.0 production-grade IMPROVE) adding the sources behind the new/deepened angles — information architecture / findability, the developer-docs quality rubric, troubleshooting/common-errors, tool-archetype overlays, docs-as-code/freshness, and the iteration/amend method (see the per-angle sections below + the two depth references `structure-onboarding.md` and `bestpractices-archetype-amend.md`). External content was passed through `external-content-sanitizer` before folding in (clean — descriptive summaries, no commands/URLs/tool-refs lifted into actions). This skill is self-contained: the distilled depth lives in this skill's own `references/`; the adoptability + accuracy bar is single-sourced with `reviewing-developer-guide` (the two halves share one bar).

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

## New/deepened angles (v1.1.0 IMPROVE — 2026-06-14)

- **Developer-docs quality rubric.** idratherbewriting "measuring documentation quality — a rubric for developer docs" (Findability/Accuracy/Relevance/Clarity/Completeness/Readability, ~80 characteristics) + "quality checklist for API documentation"; the Good Docs Project — the named grounding the bar instantiates.
- **Information architecture / start-here findability + scannability.** Fern (information-architecture best-practices), GitBook (documentation-structure), idratherbewriting (doc-navigation design principles), Docsie (IA), LogRocket + IxDF (progressive disclosure) — a signposted start-here, reader-journey order, scannable headings, reveal-gradually.
- **Time-to-first-call (TTFC).** Postman / TechCrunch / Nordic APIs "the most important API metric is time to first call"; Stripe/Vercel TTFC <90s; first call within ~10 min → 3–4× conversion; sandbox/test-mode sign-up (BILL/Paddle/Authorize.net/Amazon SP-API).
- **Troubleshooting / common-errors.** daily.dev "developer troubleshooting docs best practices" (group frequent errors, map each to a fix); Google for Developers tech-writing "error messages"/"error handling" (specific informative messages, numeric codes); Microsoft Learn error UX.
- **Tool-archetype overlays.** document360 "SDK vs API documentation"; Speakeasy "SDK best practices"; Auth0 SDK principles; the API/SDK/CLI/framework taxonomy.
- **Docs accessibility (light).** document360 WCAG for docs; W3C WAI alt-text; WCAG 2.2 SC 1.1.1/2.4.4; Google tech-writing (link text, define acronyms).
- **Iteration/amend + docs-as-code/freshness.** docuwiz "prevent API documentation drift"; gaudion.dev "documentation drift"; deepdocs; medium/substack living-docs; Nulab; archbee; PostHog docs-ownership; RFC 8594 Deprecation/Sunset; Theneo/oneuptime/Doc-Holiday on breaking changes. Abandonment from staleness: Postman (52% poor docs); dev.to "documentation decay erodes trust".

## Notes / caveats

- A few vendor specifics (e.g. one vendor's exact env-var name) are single-source and used only as illustrative examples, not load-bearing claims; every load-bearing claim has >=2 independent sources.
- WebFetch denied -> WebSearch summaries only; claims verified by cross-source agreement, not primary-page quotes.
