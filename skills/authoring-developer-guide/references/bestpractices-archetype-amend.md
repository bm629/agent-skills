# Reference — best-practices, troubleshooting, archetypes & amend

Depth for `authoring-developer-guide` Step 4 (best-practices, troubleshooting, archetypes) + Step 6 (amend). Load when you need the method behind the production + change angles.

## Production best-practices (Diataxis explanation, not an option dump)

Show the RECOMMENDED pattern + a short snippet; defer exhaustive options to the reference. "Examples that work in isolation but fall apart in real integration" is a top abandonment driver — this is what makes the guide survive production.

- **Auth / secrets / scopes** — env var or secret manager (never hardcoded); least-privilege scopes; the test-vs-live key distinction.
- **Error handling, retryable-vs-fatal** — the catch/branch pattern: transient (network, 5xx, 429) → retry; fatal (4xx auth/validation) → surface, don't retry. Show the reader how to read the error's type/code (specific, informative messages — not generic "Server error").
- **Retries + idempotency** — exponential backoff WITH jitter; honor `Retry-After`; an **idempotency key on writes** so a retry can't double-charge.
- **Pagination** — the auto-iterator or cursor loop; **prefer cursor over offset**; the dropped-cursor pitfall.
- **Rate limits** — catch `429`, read `Retry-After`, else backoff+jitter.
- **Webhooks** (where the tool emits them) — **verify the payload signature** before trusting it; **dedupe on event id** (delivery is at-least-once); tolerate out-of-order delivery; ack fast then process. Proportional — collapses when the tool has no webhooks.
- **Resource hygiene** — reuse ONE client (don't construct per call); connection pooling; timeouts.

## Troubleshooting / common-errors (cond-13)

A self-serve path for the frequent, knowable failures, beyond getting-started's 2–3 first-call failures. "No help when stuck" is a top abandonment driver; the frequent errors are knowable from logs/support.

- **Symptom → cause → fix.** Each common error: the message the developer sees, the one-line cause, the concrete fix. Avoid generic "Server error" — map each to a remedy.
- **Group the frequent errors** — auth (401/403, wrong key/env, missing scope), validation (400, missing/invalid field), rate-limit (429), not-found (404, wrong id/region/base-url), version mismatch (SDK/API skew). Error logs + support data reveal which are frequent — focus there.
- **An error-code → meaning → fix table** where the tool has a code set (or point into the reference's error catalog — don't duplicate it).
- **A short FAQ** for recurring conceptual confusions (test vs live, async timing, idempotency).
- **Proportional** — a thin single-purpose tool folds this into getting-started; a broad platform earns a dedicated section. The bar: a stuck developer can self-serve the common failure from the guide.

## Tool-archetype overlays (proportional authoring aid)

Emphasis shifts by archetype; a tool can be several at once. The reviewer judges archetype-appropriate completeness via the existing conditions (a CLI guide with no exit-code/stdout contract fails cond-4; an SDK missing the per-language first-success fails cond-2) — NEVER via a "you must have a CLI section" demand.

- **API platform (REST/HTTP)** — curl + ≥1 language; auth flows (OAuth/keys); webhooks; the api-reference linking is central.
- **Client SDK / per-language library** — a per-language getting-started + recipes (one first-success per supported language); the client-object lifecycle; idiomatic patterns per language; install per package manager. (SDK docs are heavily detailed — create a guide per language/framework.)
- **CLI tool** — args/flags; **exit codes**; the **stdout/stderr contract**; **non-interactive / scripting** use; shell completion; config-file + env precedence.
- **Framework / scaffold** — project scaffolding (`create-x-app`); conventions / "the X way"; lifecycle hooks; directory structure; the upgrade path.

## Docs-as-code / sample freshness (authoring habit, folds into accuracy)

"Documentation decay / outdated examples" is the #1 trust-killer. The artifact-scoped habit (the CI-ing of samples is the project's pipeline, NOT the guide's content):
- Write samples so they CAN be tested — self-contained, minimal, single-sourced from real working code where possible (snippet-include from a tested file, not hand-typed).
- Treat a sample as a liability that drifts; write against the CURRENT tool surface.
- **State the tool version the guide targets** so staleness is visible. Ties directly to the amend staleness-sweep below.

## Amend (Step 6) — the staleness-sweep procedure

A developer guide is the **most amend-driven** doc — its subject (the tool) moves. The amend is **upstream-driven + internal**, with **no derived-doc downstream** (the guide is a leaf — the only consumer is the developer's own integration). Scope unit = a recipe / a concept / a getting-started step / a single sample / a best-practice / a migration note / an api-reference pointer.

1. **Scope the change** — what this delta touches (which recipes/samples/concepts, for which tool version) + what is deliberately untouched (so the review can be bounded).
2. **Edit in place** — change only the affected blocks; do NOT regenerate the whole guide (loses provenance + risks breaking untouched, still-accurate samples).
3. **Upstream-driven staleness sweep** — given the changed tool/api-reference/feature-spec, find **EVERY** guide location that referenced the changed/removed capability (samples, recipes, concepts, the getting-started call, the api-reference pointers) and re-make each accurate to the current tool. A sample left calling a removed/renamed capability is the highest-impact amend defect (a fabrication-by-staleness).
4. **Re-make internal coherence** — concepts-before-recipes still holds; the end-to-end tutorial still runs; no recipe contradicts the (possibly changed) concept section; the first-success still verifies.
5. **Version + changelog the guide document** — bump the guide's OWN version (distinct from the tool's version AND the skill's semver); add a changelog row: who / when / what changed / why (e.g. "updated for SDK v3 — `Client(key=)` → `Client.from_env()`").
6. **Mark superseded/deprecated content** — with the version + the replacement, not a silent delete, so a developer still on the old version sees the path. The per-major migration note (the tool's versioning section) is itself a born-amend artifact that grows by accretion.

The flow (deciding to amend, detecting the tool changed, feeding the changed upstreams in) is the agent-flow add-feature/version-bump cycle's job, separate + unspecced — the skill assumes the existing guide + change request + changed upstreams are handed in.

## Sources

Production resilience (the Stripe/Twilio/Auth0/SendGrid best-practices bar — retries+idempotency+backoff-with-jitter, honor Retry-After, cursor pagination, 429 handling, client reuse; Stripe/Twilio webhook signature-verification + replay/dedup). Error handling + troubleshooting (Google for Developers tech-writing "error messages"/"error handling"; daily.dev "developer troubleshooting docs best practices"; Microsoft Learn error UX). Archetypes (document360 "SDK vs API documentation"; Speakeasy SDK best-practices; Auth0 SDK principles; the API/SDK/CLI/framework taxonomy). Docs-as-code/drift (docuwiz "prevent API documentation drift"; gaudion.dev "documentation drift"; deepdocs; dev.to CI/CD docs). Living docs/amend (medium/substack living-docs; Nulab; archbee; PostHog docs-ownership; RFC 8594 Deprecation/Sunset; Theneo/oneuptime/Doc-Holiday on breaking changes). Abandonment from staleness (Postman 52%; dev.to "documentation decay erodes trust"). External content (§5) — paraphrased, no URLs/commands lifted into actions.
</content>
