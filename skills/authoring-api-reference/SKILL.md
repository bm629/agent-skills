---
name: authoring-api-reference
description: >
  Use when authoring (or amending) a published, consumer-facing API reference —
  the docs an integrating client developer reads to call an API. Guides the
  producer through the METHOD, not the outline: deriving every endpoint, field,
  and error from the upstream api-spec contract (never fabricating one),
  grounding onboarding + examples in established public-API-docs practice,
  authoring prose-first yet adapting to OpenAPI-generated catalogs,
  documenting auth flows, errors, rate-limits, pagination + deprecation, and
  keeping the reference consistent with the contract — so a developer can
  authenticate and integrate every operation from the reference alone. Amends
  an existing reference as an
  upstream-driven re-sync when the contract changes, with a doc version + amend
  log. Composes with an api-reference template tool + deep-research. Assumes the
  upstream api-spec — never a blank page. Not the engineering wire contract
  (api-spec), not the end-user guide, not reviewing one.
extensions:
  claude:
    when_to_use: "authoring or amending the published, consumer-facing API reference a client developer integrates against — derived from and consistent with the upstream api-spec contract"
    argument-hint: "<the api-spec (+ feature-spec/architecture-doc) to turn into a consumer-facing API reference, or the existing reference + the changed contract to re-sync>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-14
---

# `authoring-api-reference` — SKILL.md

> **Variant:** standard · **When to use:** authoring (or amending) the published, consumer-facing API reference — to a bar where a client developer can authenticate, make a first successful call, and integrate every operation from the reference alone, with every endpoint, field, and error consistent with the upstream api-spec contract (no drift, nothing fabricated).

## Overview

This skill is the *how-to* of writing a strong **published, consumer-facing API reference** — the documentation an integrating client developer reads to call an API. It carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: an **api-reference template tool** that supplies the section *structure*, and a **deep-research capability** to ground the onboarding narrative, examples, and conventions in established public-API-docs practice. The producer is handed the **upstream api-spec** (the engineering wire contract every endpoint, field, and error is derived from) and, where present, the **feature-spec** (the usage context — what each operation is for) and the **architecture-doc** (auth/versioning context) — never a blank page. The bar to clear: a developer can **authenticate, make a first successful call, and correctly use every operation from the reference alone**, and **every documented endpoint, shape, and error traces to the api-spec contract** — no drift, nothing fabricated.

The reference is the **narrative + onboarding + worked-example layer on top of** the api-spec contract. It adds the getting-started walkthrough, the auth walkthrough, the worked examples, the pagination/error/rate-limit/deprecation guidance, and the troubleshooting the contract omits — it does **not** redefine, replace, or contradict the contract.

## When to activate

- Authoring a published, consumer-facing API reference from an upstream api-spec that defines the operations a client integrates against.
- Documenting per-endpoint usage (purpose, typed parameters, worked request + response examples, error responses) plus getting-started + authentication, events/webhooks where the API emits them, pagination, an errors + rate-limits guide, code samples, and versioning + deprecation.
- Filling an api-reference template with researched, contract-consistent, runnable per-endpoint content.
- Adding the human-authored narrative + examples + drift check on top of a reference whose endpoint catalog is auto-generated from OpenAPI.
- **Amending** an existing reference when the upstream contract changes (a new/changed/deprecated endpoint) — re-syncing the affected blocks (see Step 7).

**Do NOT activate when:**

- Authoring the engineering **wire contract** itself (operations, exhaustive schemas, the internal error model) — that is the *upstream* `authoring-api-spec`. The api-reference is the published consumer doc **downstream of** and consistent with it; it references the contract, it does not re-derive it.
- Writing the **end-user product guide** / **developer adoption guide** (task help for the product's end user, or an SDK/CLI/platform how-to) — that is `authoring-user-guide` / `authoring-developer-guide`, a different audience.
- Writing the **persistence data-model** or the **system architecture** — separate upstream concerns (`authoring-data-model` / `authoring-architecture-doc`).
- Reviewing or grading a finished api-reference — that is the runtime gate `reviewing-api-reference`; this skill is produce-side only.
- Writing project-specific endpoints, an SDK tutorial, or any other document type.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them.

- **Consume the handed-in set; do not hardcode one input.** The **primary** upstream is the **api-spec** (the engineering wire contract; OpenAPI for REST, AsyncAPI / OpenAPI-3.1 `webhooks` for events, SDL for GraphQL, proto for RPC); also read the **feature-spec** where present (usage context) and the **architecture-doc** where present (auth/versioning context). The typical upstreams named here are method guidance, not a cap on what you receive.
- **On an amendment, you are also handed the existing reference + the change** (the changed contract / change request). See Step 7.
- **Derive every endpoint from the api-spec.** Every endpoint, parameter, field type, required/optional flag, error code, event, and auth scheme in the reference comes from the handed-in contract. The contract supplies the *facts*; research supplies the *conventions* (onboarding/error-doc/rate-limit/pagination/sample shape) — not the endpoints.
- **Self-contained + graceful.** Produce the reference from *whatever* context you actually receive. When an expected informing document is absent (e.g. no separate feature-spec), proceed on the api-spec alone and surface the gap as an **explicit assumption — never fabricate** an endpoint, parameter, field, error, or event to look complete.
- **Use a research capability where one is available** (deep-research) to ground the reference in established public-API-docs practice, not merely to fill the template. If no research capability is available, state conventions as explicitly-flagged assumptions — never fabricate.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your api-reference template tool (`content-template-gateway`, comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive api-reference structure (request/forge one, or fall back to the canonical set: overview, getting-started, authentication, base URL + versioning + deprecation, per-endpoint reference, events/webhooks, core objects, pagination/filtering/sorting, errors, rate limits, code samples + SDKs, API versioning + changelog, the doc's own revision history), then proceed.

### Step 2: Load the upstream docs; drive coverage off the api-spec

Read the upstream **api-spec** and any handed-in context (feature-spec, architecture-doc) — this is your **input, not a blank page**. The api-spec's operations are your **endpoint-coverage checklist**: every operation (and every contract-declared event/webhook) in the contract must appear in the reference, and every documented endpoint/event must exist in the contract (no orphan/invented endpoints, none missing). Pull each operation's parameters, field types, error responses, and auth scheme **from the contract** — do not re-type or contradict them. Where the upstream is thin (e.g. the contract names an operation but not its usage context), make the gap an **explicit assumption**, never a silently-invented shape.

### Step 3: Choose the mode — prose-first by default, generation-adaptive

Detect how the project renders the endpoint catalog:

- **Hand-authored (default).** Author the consumer reference by hand from the api-spec: the getting-started/auth narrative, the worked request/response examples, the per-endpoint prose, and the contract-consistency check.
- **Generated from OpenAPI.** Where the project auto-generates the endpoint catalog (Swagger UI, Redocly, Stoplight, Mintlify, Fern, Scalar), the catalog stays current because it is generated — do **not** re-type it (a hand-retyped duplicate drifts immediately). Your value **shifts** to (i) the surrounding **getting-started / authentication narrative** the generator does not write, (ii) **example quality** (runnable worked request/response pairs + code samples), and (iii) the **drift / consistency check** over the generated output. The deeper discipline is **docs-as-code single-source-of-truth**: the OpenAPI description is the SSoT, the catalog is generated from it, and **contract testing** (validating live responses against the spec) is the automated drift guard — your human drift-check complements it over the narrative + examples + hand-written sections.

One skill, two surfaces of the same job. **The quality bar (Step 6) is identical in both modes** — generation changes who types the endpoint table, not whether the reference is usable and contract-consistent.

### Step 4: Research to ground the narrative and conventions

Use a deep-research pass to ground the reference in established public-API-docs practice (the Stripe/Twilio-style bar) — the shape of a getting-started quickstart, the auth walkthrough, the error-doc conventions, the rate-limit/retry conventions, the pagination conventions, the deprecation/sunset conventions, and the code-sample conventions — for *this* product's surface, not "API docs in general." Research the **conventions**; the **endpoints come from the contract**. If no research capability is available, do **not** fabricate conventions, status codes, or limits — state them as explicitly-flagged assumptions to validate.

### Step 5: Apply the per-section method

Fill the template's sections to this method. Collapse a section a thin API doesn't need; size proportionally. (Depth for each convention lives in `references/conventions-and-styles.md`.)

- **Overview + getting-started — the first successful call.** The getting-started section must run end to end to a single success (get a key, make one request, recognize the response) **before** advanced features. The highest-leverage section for adoption.
- **Authentication walkthrough — name the FLOW, show success + failure.** Name the scheme/flow the contract uses — static **API key**, or which **OAuth 2.0** flow (Authorization-Code / Client-Credentials / PKCE) — the **scopes** (least-privilege, requested incrementally), where to get credentials, exactly how to send them (worked example), the **token lifecycle** (expiry + refresh), and **both** the success case and the auth-failure (`401`/`403`) response. (Holding a token is delegated *authorization*, not proof of identity.)
- **Base URL + versioning + deprecation + conventions.** The base URL, how versions are expressed, how a developer pins/upgrades, what counts as a breaking change, the **deprecation/sunset policy** (see below), and the up-front conventions (content type, date format, id format, idempotency keys, request-id header).
- **Per-endpoint reference — every operation, fully worked.** For **each** operation in the contract: method+path, a purpose line, typed parameters (path/query/body, each required/optional with constraints), a **worked request example** with real values, a **worked response example** (success — and at least one **failure**), the **error/status codes** it returns with cause + fix, and a **deprecation marker** (since/sunset/migrate-to) where the operation is deprecated. A block that shows only the `200` body is **not done**. (For GraphQL, document operations against the schema; for gRPC, the service methods — same per-operation bar.)
- **Events / webhooks — where the API emits them.** Document the **event catalog** (every event type — operations in reverse), a **payload schema + example per event**, **signature verification** (HMAC over the raw body + a timestamp to block replay), and **delivery semantics** (at-least-once → a delivery-id idempotency key; retries with backoff; the 2xx-within-N-seconds ack). Proportional — omit for a request/response-only API.
- **Core objects / shared data types — define once.** Define each reusable object shape **once** in a core-objects section and reference it from the per-endpoint/event blocks; never redefine a resource inside every endpoint.
- **Pagination / filtering / sorting — document the model once.** For an API with list operations: the **model** (cursor for large/changing sets, offset for small/stable), **standard parameter names** (`limit`, `after`/`before`, `page`/`per_page`), **response metadata** (`has_more`, `next_cursor`, `total_count` where feasible), a **default + a documented max** page size, the **last-page signal**, and a **stable, tie-broken sort** (a unique secondary key so ordering is deterministic across pages). Proportional — omit if nothing lists.
- **Errors guide — first-class, the named standard.** Document **one consistent error-response shape** once (prefer **RFC 9457 Problem Details**, `application/problem+json`, successor to 7807), a status-code table (cause + remedy), the **machine-readable error `code`** distinct from the HTTP status, and the **semantically-correct status** (429 for rate-limit, 409 conflict, 410 for sunset). Docs that cover only 2xx force developers to learn failure modes by trial and error.
- **Rate limits.** State the limit, the `429` signal, `Retry-After` (and `RateLimit-*`/`X-RateLimit-*` where present — noting they are replaced by `Retry-After` on a 429), **exponential backoff + jitter**, and **idempotency keys** for safe retries.
- **Code samples + SDKs.** Show **curl + at least one language** per primary operation, with values matching the schemas exactly; add more languages **only** where an official SDK exists. Don't pad with languages you don't ship a client for.
- **API versioning + changelog.** The versioning/deprecation policy and a dated, newest-first **API changelog** (what changed in the API surface) — distinct from the doc's own revision history (Step 7 / the amend log).

### Step 6: Self-check against the usability + contract-consistency bar before handing off

Confirm all hold (this is the bar the runtime review gate asserts — author and gate share it, single-sourced, so they don't drift). cond-5 is the **load-bearing** check.

1. **First call is reachable** — getting-started + authentication (scheme/flow named, credentials obtainable + sendable, the auth-failure shown) let a developer authenticate and make a **first successful call** end to end, copy-paste.
2. **Every operation documented** — every api-spec operation (**including contract-declared events/webhooks**) appears with purpose + typed parameters + a worked request + a worked response + its error responses. No contract operation missing; no documented operation absent from the contract.
3. **Errors are first-class** — one consistent error shape (Problem-Details-shaped) + a machine-readable code + a status-code table + per-endpoint error rows + semantically-correct statuses. A reference covering only 2xx fails.
4. **Rate limits documented** — the limit, `429`, `Retry-After`, `RateLimit-*`, backoff + jitter, idempotency keys (proportional — absent if the API doesn't limit).
5. **Consistent with the contract** — every endpoint, field type, required/optional flag, error code, event, and auth scheme traces to the api-spec; no drift, nothing fabricated; no hand-retyped duplicate of a generated catalog. **This is the load-bearing check.**
6. **Samples runnable + consistent** — curl + >=1 language with realistic values that match the schemas exactly. An example that contradicts its schema is a defect.
7. **Versioning + deprecation stated** — the versioning/deprecation policy (Sunset/Deprecation mechanics, a migration path for a deprecated surface) + a dated API changelog (proportional — thin for a v1-only API).
8. **Shared types defined once + referenced** — reusable objects defined once in a core-objects section and referenced, not redefined per endpoint.
9. **Grounded, not fabricated** — endpoints/events reflect the api-spec; conventions reflect researched practice; gaps surfaced as assumptions, not invented.
10. **Pagination/list conventions** (proportional) — for an API with list operations, the model + standard params + metadata + default/max + the stable tie-broken sort are documented once. A non-listing API has none.
11. **Amend (on an amendment)** — the delta re-syncs to the changed contract, samples re-checked, deprecation/migration documented, the doc version + amend log updated (Step 7). N/A on a greenfield first build.

**Thin-input gate:** if an operation the contract names cannot be documented to the bar (e.g. its usage context or error responses are absent and cannot be researched or credibly assumed), surface it as a **blocker** ("operation under-documented — needs the api-spec author / product decision") rather than inventing a shape. A reference whose endpoints, errors, *or* examples are guesses is not safe to integrate against.

### Step 7: Amend an existing reference — the upstream-driven re-sync

When handed an existing reference + a change (most often **the upstream api-spec contract changed**), edit the delta — do not rewrite. (Depth + a worked example in `references/amend.md`.)

1. **Scope the change** to the affected endpoints/fields/errors/events/auth; edit those blocks, preserve the unchanged catalog.
2. **Re-sync against the changed contract** — re-run the cond-5 consistency check on **only** the changed blocks: every changed/new endpoint/field/error now traces to the changed api-spec; a removed contract operation is removed (or marked deprecated). If editing reveals a contract gap (the docs need an operation the contract doesn't declare), **flag it back to the api-spec author** — never fabricate it in.
3. **Propagate the internal ripple** — the shared-object entry + every referencing endpoint, the **worked examples + code samples re-checked against the new schema** (a stale sample is a defect), the per-endpoint error rows.
4. **Handle the deprecation→sunset lifecycle** — a removed/changed endpoint is **marked deprecated** (Deprecation/Sunset, a sunset date, a **migration guide/replacement link**), kept through the window, removed only after sunset — not silently dropped.
5. **Version + amend log** — bump the **reference document's own** version + add a who/when/what/why amend-log row, and mark superseded content. This is distinct from the **API changelog** (what changed in the API) and from the skill's version.

### API-style overlays (authoring aids — proportional, judged by outcome)

A reference's shape shifts by **API style**: REST (the default — resources + the per-endpoint table), **GraphQL** (one endpoint + a typed schema; document types + queries/mutations/subscriptions, not a path table), **gRPC/RPC** (proto + methods + streaming), **webhooks/event-driven** (the event catalog above), **streaming/WebSocket/SSE** (connection lifecycle + message schema). These are aids keyed to the API's nature, applied proportionally — the bar adapts, it does not bloat. (Detail in `references/conventions-and-styles.md`.) **Out of scope (the rendered docs site owns them, not this markdown artifact):** full-text/AI search, an interactive try-it / API explorer / Postman collection, and the docs site's accessibility/i18n — the method is medium-independent; do not over-claim them here.

## Rules

**Hard rules (never violate):**

- **Derive every endpoint from the contract.** Every endpoint, parameter, field type, error code, event, and auth scheme comes from the handed-in api-spec. No orphan/invented endpoint, no contract operation missing.
- **Never fabricate.** Don't invent an endpoint, parameter, field, status code, error, event, or limit to look complete. With no source, state it as an explicitly-flagged assumption to validate.
- **Consistent with the api-spec — no drift.** Field types, required/optional flags, error codes, events, and auth must match the contract. The reference adds narrative + onboarding + worked examples; it does not redefine or contradict the contract. A documented endpoint the contract doesn't declare, or a field the contract doesn't carry, is a defect.
- **Document the errors, not just the happy path.** One consistent error shape + a status-code table + per-endpoint error rows. A reference listing only 2xx is incomplete.
- **First successful call is reachable.** Getting-started + authentication run end to end to one success before advanced features.
- **Examples match the schemas.** Every worked request/response and code sample uses the exact field names, types, and status codes the contract declares. An example contradicting its schema is a defect — re-check examples after any contract change.
- **Curl + >=1 language, no padding.** Samples show curl plus at least one language; more only where an official SDK exists.
- **Define shapes once.** Shared object types live in one core-objects section and are referenced; never redefine a resource inside every endpoint.
- **Amend by re-sync, not rewrite.** On a contract change, edit the affected blocks, re-run consistency on the delta, re-check samples, document deprecation/migration, bump the doc version + amend log. Don't silently delete a removed endpoint — deprecate it with a migration path.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Consumer reference, not the wire contract, not the end-user guide.** Write the published developer reference — not the engineering api-spec (upstream), not the end-user product guide (different audience), not the implementation.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — a thin API collapses sections it doesn't need (pagination disappears if nothing lists; the SDK table waits until SDKs exist; webhooks/rate-limits/deprecation are absent until they apply; the changelog starts with one row). The bar is a developer's ability to integrate, not word count.
- Prefer the order a developer encounters operations (create -> retrieve -> list -> update -> delete) within a resource group.
- Mirror the curl example with the language sample so a developer sees the same call both ways.

## Gotchas

- **Drift from the contract.** The reference silently diverging from the api-spec — a documented endpoint the contract dropped, a field the reference shows that the contract never declared, an error the reference omits — is the single most damaging defect. Same failure mode hand-authored or generated; the drift check (Step 6.5) guards it in both modes.
- **Happy-path-only endpoints.** Showing the `200` body and stopping is the most common reference defect. Each endpoint must show at least one failure case and the error/status codes it returns.
- **Re-typing the generated catalog.** Where the catalog is generated, manually re-typing it duplicates the generator and immediately drifts. Let generation own the catalog; spend your effort on the narrative, the examples, and the drift check.
- **Stale samples after a contract change.** On an amendment, a worked example or code sample left unchanged after the schema changed reads as runnable but won't run. Re-check every sample the change touches (Step 7.3).
- **Conflating the three changelogs.** The **API changelog** (what changed in the API surface), the **doc's own amend log** (how this document changed), and the skill's version are three different things. The amend log + doc version are the document's; the API changelog is the API's.
- **Silently dropping a removed endpoint.** A removed/changed operation is *deprecated with a migration path* (Sunset/Deprecation, 410 after sunset), not deleted out from under integrators.
- **Confusing the reference with the wire contract or the end-user guide.** The api-spec is the engineering contract (upstream, exhaustive); the api-reference is the published consumer doc on top of it. The user-guide/developer-guide is a different audience. Keep this the developer integration reference.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

**Worked contrast — looks-complete vs integrable** (use it to self-detect):

| Aspect | Looks complete (reject) | Integrable (ship) |
|---|---|---|
| First call | "Authenticate, then call the API." | A copy-paste curl quickstart: get a key from the dashboard, `GET /v1/widgets` with the `Authorization` header, the exact `200` body to expect. |
| Auth | "Uses OAuth." | "Client-Credentials flow; request scope `widgets:read`; `POST /oauth/token` → a 1h Bearer token; on `401` refresh." — the flow + scope + lifecycle + failure. |
| Endpoint coverage | "The main endpoints are documented." | Every operation (and event) in the api-spec has a block; the index matches the contract one-to-one. |
| Parameters | "Takes the widget fields." | "`name` (string, required, max 255), `status` (string, optional, one of `active`/`archived`, default `active`)." — from the contract. |
| Pagination | "Returns a list." | "Cursor pagination: `limit` (max 100, default 20) + `starting_after`; `has_more` + `next_cursor`; ordered by `created` then `id` (tie-breaker)." |
| Errors | "Errors are returned on failure." | Problem-Details shape + a machine `code` + per-endpoint rows (`400 invalid_request`, `404 not_found`, `409 conflict`) + a status-code table — every code from the contract. |
| Deprecation | (endpoint silently removed) | "`GET /v1/charges/legacy` — deprecated 2026-06-14, sunset 2026-09-12, migrate to `GET /v1/charges`." |
| Consistency | (untraced) | Every endpoint/field/error/event traces to the api-spec; nothing shown that the contract doesn't declare. |

If your fill reads like the left column — true of any API, no worked examples, no error cases, no trace to the contract — it isn't done.

## Anti-patterns

- **"The api-spec is thin, I'll fill in plausible endpoints/params."** Never fabricate. Derive from the contract; surface gaps as assumptions or a blocker.
- **"I'll spec the happy path; the errors are obvious."** They aren't — document each endpoint's failure responses and status codes.
- **"The catalog is generated, so I'm done."** Generation gives you the catalog, not the onboarding narrative, the example quality, or the drift check — that is the human-authored value.
- **"This is also the wire contract, so I'll write exhaustive internal schema rigor."** The contract is upstream; the reference is the consumer doc on top of it. Reference it, don't re-derive it.
- **"This is also the end-user / developer-adoption guide."** Different audience — this is the developer integration reference.
- **"I'll add a GraphQL/webhook section because best-practice says so."** Overlays are proportional aids — add them only where the API has that surface; don't bloat a REST reference.
- **"The endpoint was removed, I'll just delete its block."** Deprecate with a migration path; don't drop it out from under integrators.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know what good API docs look like."** The research grounds *this product's* onboarding, error-doc, pagination, and sample conventions — not API-docs theory.

## Output

A **comprehensive, published API reference** (or a re-synced amendment of one) that meets the **Step 6 usability + contract-consistency bar** (first call reachable; every api-spec operation/event documented with purpose + typed params + a worked request + a worked response + its errors; errors first-class with one Problem-Details-shaped error + a status-code table; rate limits documented; **consistent with the contract — every endpoint/field/error/event traced, no drift, nothing fabricated**; samples runnable + matching the schemas; pagination conventions where applicable; versioning + deprecation stated; shared types defined once; proportional; on an amendment, re-synced + doc-versioned). The artifact is **textual** — endpoint sections + fenced request/response examples + fenced code samples; the method + bar are **medium-independent** (markdown today via the local docs backend; a future rendered docs site changes only the medium — and owns search/try-it/a11y/i18n — not the skill). The **abstract consumer** is the client developer who integrates against the API from the reference alone, and a runtime review gate (which asserts the same bar). The api-reference **depends on** the api-spec (and references the feature-spec/architecture-doc where present) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- An **api-reference template tool** (`content-template-gateway`) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** (`deep-research`) — grounds the onboarding narrative, examples, and conventions in established public-API-docs practice.
- An **api-spec-authoring skill** (`authoring-api-spec`) — produces the *upstream* engineering wire contract every endpoint, field, event, and error in this reference derives from and stays consistent with.
- A **feature-spec** and an **architecture-doc** (where present) — upstream context: the usage context for each operation, and the auth/versioning context.
- A **review gate** (`reviewing-api-reference`) — asserts the same usability + contract-consistency bar on the finished reference at runtime; author and gate share one bar (single-sourced) so they don't drift.
- An **end-user product-guide / developer-adoption-guide skill** (`authoring-user-guide` / `authoring-developer-guide`) — a *different* document/audience (the product's end user, or the SDK/CLI adoption narrative that *points into* this reference).

## Progressive disclosure

- `references/conventions-and-styles.md` — the auth-flow specifics (API key / OAuth2 flows / scopes / token lifecycle), the RFC 9457 Problem-Details error model, the rate-limit / `RateLimit-*` / idempotency mechanics, the pagination conventions (cursor/offset, standard params, metadata, tie-broken sort), and the API-style overlays incl. the webhook/event documentation method. Load when filling those sections.
- `references/amend.md` — the upstream-driven re-sync amend procedure, the deprecation→sunset lifecycle (RFC 8594/9745), the three-changelog distinction, and a worked amend example. Load when amending.
- `references/sources.md` — research provenance for the method + quality bar. Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.

## Changelog

- **1.1.0** (2026-06-14) — production-grade restructure (additive; single-sourced with `reviewing-api-reference`'s 11-condition bar). Added the **iteration/amend method** (Step 7 — the upstream-driven re-sync) + `references/amend.md`; deepened authentication-flow depth, the RFC 9457 Problem-Details error model, RateLimit-*/jitter/idempotency, and deprecation/sunset (RFC 8594/9745) mechanics; added **pagination/list-operation conventions** + the **API-style overlays** incl. webhook/event documentation as authoring aids + `references/conventions-and-styles.md`. Step-6 self-check 9 → 11. Input contract + medium unchanged.
- **1.0.0** (2026-06-05) — initial reviewed release.
