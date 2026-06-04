---
name: authoring-api-reference
description: >
  Use when authoring a published, consumer-facing API reference — the
  documentation an integrating client developer reads to call an API
  (getting-started, authentication, a per-endpoint reference, shared object
  types, errors + rate-limits, code samples, a changelog). Guides the
  producer through the METHOD, not the
  outline: deriving every endpoint, field, and error from the upstream
  api-spec contract (never fabricating one), grounding the onboarding
  narrative + examples in established public-API-docs practice, authoring
  prose-first yet adapting where the catalog is generated from OpenAPI, and
  keeping the reference consistent with the contract — so a developer can
  authenticate, make a first call, and integrate every operation from the
  reference alone. Composes with a separate api-reference template tool and
  deep-research. Assumes the upstream api-spec (+ feature-spec /
  architecture-doc where present) — never a blank page. Not the engineering
  wire contract (api-spec), not the end-user guide, not reviewing one.
extensions:
  claude:
    when_to_use: "authoring the published, consumer-facing API reference a client developer integrates against — derived from and consistent with the upstream api-spec contract"
    argument-hint: "<the api-spec (+ feature-spec/architecture-doc) to turn into a consumer-facing API reference>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `authoring-api-reference` — SKILL.md

> **Variant:** standard · **When to use:** authoring the published, consumer-facing API reference — to a bar where a client developer can authenticate, make a first successful call, and integrate every operation from the reference alone, with every endpoint, field, and error consistent with the upstream api-spec contract (no drift, nothing fabricated).

## Overview

This skill is the *how-to* of writing a strong **published, consumer-facing API reference** — the documentation an integrating client developer reads to call an API. It carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: an **api-reference template tool** that supplies the section *structure*, and a **deep-research capability** to ground the onboarding narrative, examples, and conventions in established public-API-docs practice. The producer is handed the **upstream api-spec** (the engineering wire contract every endpoint, field, and error is derived from) and, where present, the **feature-spec** (the usage context — what each operation is for) and the **architecture-doc** (auth/versioning context) — never a blank page. The bar to clear: a developer can **authenticate, make a first successful call, and correctly use every operation from the reference alone**, and **every documented endpoint, shape, and error traces to the api-spec contract** — no drift, nothing fabricated.

The reference is the **narrative + onboarding + worked-example layer on top of** the api-spec contract. It adds the getting-started walkthrough, the auth walkthrough, the worked examples, and the troubleshooting the contract omits — it does **not** redefine, replace, or contradict the contract.

## When to activate

- Authoring a published, consumer-facing API reference from an upstream api-spec that defines the operations a client integrates against.
- Documenting per-endpoint usage (purpose, typed parameters, worked request + response examples, error responses) plus a getting-started + authentication walkthrough, an errors + rate-limits guide, code samples, and versioning.
- Filling an api-reference template with researched, contract-consistent, runnable per-endpoint content.
- Adding the human-authored narrative + examples + drift check on top of a reference whose endpoint catalog is auto-generated from OpenAPI.

**Do NOT activate when:**

- Authoring the engineering **wire contract** itself (operations, exhaustive schemas, the internal error model) — that is the *upstream* `authoring-api-spec`. The api-reference is the published consumer doc **downstream of** and consistent with it; it references the contract, it does not re-derive it.
- Writing the **end-user product guide** (task help for the product's end user, not the developer integrating the API) — that is `authoring-user-guide` / `authoring-developer-guide`, a different audience.
- Writing the **persistence data-model** or the **system architecture** — separate upstream concerns (`authoring-data-model` / `authoring-architecture-doc`).
- Reviewing or grading a finished api-reference — that is the runtime gate `reviewing-api-reference`; this skill is produce-side only.
- Writing project-specific endpoints, an SDK tutorial, or any other document type.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them.

- **Consume the handed-in set; do not hardcode one input.** The **primary** upstream is the **api-spec** (the engineering wire contract); also read the **feature-spec** where present (usage context — what each operation is for) and the **architecture-doc** where present (auth/versioning context). The typical upstreams named here are method guidance, not a cap on what you receive.
- **Derive every endpoint from the api-spec.** Every endpoint, parameter, field type, required/optional flag, error code, and auth scheme in the reference comes from the handed-in contract. The contract supplies the *facts*; research supplies the *conventions* (onboarding/error-doc/rate-limit/sample shape) — not the endpoints.
- **Self-contained + graceful.** Produce the reference from *whatever* context you actually receive. When an expected informing document is absent (e.g. no separate feature-spec), proceed on the api-spec alone and surface the gap as an **explicit assumption — never fabricate** an endpoint, parameter, field, or error to look complete.
- **Use a research capability where one is available** (deep-research) to ground the reference in established public-API-docs practice, not merely to fill the template. If no research capability is available, state conventions as explicitly-flagged assumptions — never fabricate.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your api-reference template tool (`content-template-gateway`, comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive api-reference structure (request/forge one, or fall back to the canonical set: overview, getting-started, authentication, base URL + versioning, per-endpoint reference, core objects, pagination/filtering/sorting, errors, rate limits, code samples + SDKs, versioning + changelog), then proceed.

### Step 2: Load the upstream docs; drive coverage off the api-spec

Read the upstream **api-spec** and any handed-in context (feature-spec, architecture-doc) — this is your **input, not a blank page**. The api-spec's operations are your **endpoint-coverage checklist**: every operation in the contract must appear in the reference, and every documented endpoint must exist in the contract (no orphan/invented endpoints, none missing). Pull each operation's parameters, field types, error responses, and auth scheme **from the contract** — do not re-type or contradict them. Where the upstream is thin (e.g. the contract names an operation but not its usage context), make the gap an **explicit assumption**, never a silently-invented shape.

### Step 3: Choose the mode — prose-first by default, generation-adaptive

Detect how the project renders the endpoint catalog:

- **Hand-authored (default).** Author the consumer reference by hand from the api-spec: the getting-started/auth narrative, the worked request/response examples, the per-endpoint prose, and the contract-consistency check.
- **Generated from OpenAPI.** Where the project auto-generates the endpoint catalog (Swagger UI, Redocly, Stoplight, Mintlify, Fern, Scalar), the catalog stays current because it is generated — do **not** re-type it. Your value **shifts** to (i) the surrounding **getting-started / authentication narrative** the generator does not write, (ii) **example quality** (runnable worked request/response pairs + code samples), and (iii) the **drift / consistency check** over the generated output — confirm the narrative, examples, and any hand-written sections still match the current contract.

One skill, two surfaces of the same job. **The quality bar (Step 6) is identical in both modes** — generation changes who types the endpoint table, not whether the reference is usable and contract-consistent.

### Step 4: Research to ground the narrative and conventions

Use a deep-research pass to ground the reference in established public-API-docs practice (the Stripe/Twilio-style bar) — the shape of a getting-started quickstart, the auth walkthrough, the error-doc conventions, the rate-limit/retry conventions, and the code-sample conventions — for *this* product's surface, not "API docs in general." Research the **conventions**; the **endpoints come from the contract**. If no research capability is available, do **not** fabricate conventions, status codes, or limits — state them as explicitly-flagged assumptions to validate.

### Step 5: Apply the per-section method

Fill the template's sections to this method. Collapse a section a thin API doesn't need; size proportionally.

- **Overview + getting-started — the first successful call.** The getting-started section must run end to end to a single success (get a key, make one request, recognize the response) **before** advanced features. This is the highest-leverage section for adoption.
- **Authentication walkthrough.** Name the scheme the contract uses, where to get credentials, exactly how to send them (worked example), the token lifecycle, and the auth-failure responses. Show the success case **and** the failure case.
- **Base URL + versioning + conventions.** State the base URL, how versions are expressed, how a developer pins/upgrades, what counts as a breaking change, and the up-front conventions (content type, date format, id format, idempotency keys, request-id header).
- **Per-endpoint reference — every operation, fully worked.** For **each** operation in the contract: method+path, a purpose line, typed parameters (path/query/body, each required/optional with constraints), a **worked request example** with real values, a **worked response example** (success — and at least one **failure**), and the **error/status codes** the operation returns with cause + fix. A block that shows only the `200` body is **not done**.
- **Core objects / shared data types — define once.** Define each reusable object shape **once** in a core-objects section and reference it from the per-endpoint blocks; never redefine a resource inside every endpoint.
- **Errors guide — first-class, not just the happy path.** Document **one consistent error-response shape** once, a status-code table (cause + remedy), and the machine-readable error codes. Docs that cover only 2xx force developers to learn failure modes by trial and error.
- **Rate limits.** State the limit, the `429` signal, the `Retry-After` header (and `RateLimit-*`/`X-RateLimit-*` where present), exponential backoff, and idempotency keys for safe retries.
- **Code samples + SDKs.** Show **curl + at least one language** per primary operation; add more languages **only** where an official SDK exists. Do not pad with languages you don't ship a client for — sample the languages your SDKs cover.
- **Versioning + changelog.** State the versioning/deprecation policy and a dated, newest-first changelog.

### Step 6: Self-check against the usability + contract-consistency bar before handing off

Confirm all hold (this is the bar the runtime review gate asserts — author and gate share it, single-sourced, so they don't drift):

1. **First call is reachable** — getting-started + authentication together let a developer authenticate and make a **first successful call** end to end, copy-paste.
2. **Every operation documented** — every api-spec operation appears with purpose + typed parameters (required/optional + constraints) + a worked request example + a worked response example + its error responses. No contract operation missing; no documented operation absent from the contract.
3. **Errors are first-class** — one consistent error shape + a status-code table (cause + remedy) + per-endpoint error rows. A reference covering only 2xx fails.
4. **Rate limits documented** — the limit, `429`, `Retry-After`, backoff, idempotency keys.
5. **Consistent with the contract** — every endpoint, field type, required/optional flag, error code, and auth scheme traces to the api-spec; no drift, nothing fabricated. **This is the load-bearing check.**
6. **Samples runnable + consistent** — curl + >=1 language with realistic values that match the schemas exactly. An example that contradicts its schema is a defect.
7. **Versioning stated** — versioning/deprecation policy + a dated changelog.
8. **Shared types defined once + referenced** — reusable objects defined once in a core-objects section and referenced, not redefined per endpoint.
9. **Grounded, not fabricated** — endpoints reflect the api-spec; conventions reflect researched practice; gaps surfaced as assumptions, not invented.

**Thin-input gate:** if an operation the contract names cannot be documented to the bar (e.g. its usage context or error responses are absent and cannot be researched or credibly assumed), surface it as a **blocker** ("operation under-documented — needs the api-spec author / product decision") rather than inventing a shape. A reference whose endpoints, errors, *or* examples are guesses is not safe to integrate against.

## Rules

**Hard rules (never violate):**

- **Derive every endpoint from the contract.** Every endpoint, parameter, field type, error code, and auth scheme comes from the handed-in api-spec. No orphan/invented endpoint, no contract operation missing.
- **Never fabricate.** Don't invent an endpoint, parameter, field, status code, error, or limit to look complete. With no source, state it as an explicitly-flagged assumption to validate.
- **Consistent with the api-spec — no drift.** Field types, required/optional flags, error codes, and auth must match the contract. The reference adds narrative + onboarding + worked examples; it does not redefine or contradict the contract. A documented endpoint the contract doesn't declare, or a field the contract doesn't carry, is a defect.
- **Document the errors, not just the happy path.** One consistent error shape + a status-code table + per-endpoint error rows. A reference listing only 2xx is incomplete.
- **First successful call is reachable.** Getting-started + authentication run end to end to one success before advanced features.
- **Examples match the schemas.** Every worked request/response and code sample uses the exact field names, types, and status codes the contract declares. An example contradicting its schema is a defect.
- **Curl + >=1 language, no padding.** Samples show curl plus at least one language; more only where an official SDK exists. Don't pad with languages you don't maintain a client for.
- **Define shapes once.** Shared object types live in one core-objects section and are referenced; never redefine a resource inside every endpoint.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Consumer reference, not the wire contract, not the end-user guide.** Write the published developer reference — not the engineering api-spec (upstream), not the end-user product guide (different audience), not the implementation.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — a thin API collapses sections it doesn't need (pagination disappears if nothing lists; the SDK table waits until SDKs exist; the changelog starts with one row). The bar is a developer's ability to integrate, not word count.
- Prefer the order a developer encounters operations (create -> retrieve -> list -> update -> delete) within a resource group.
- Mirror the curl example with the language sample so a developer sees the same call both ways.

## Gotchas

- **Drift from the contract.** The reference silently diverging from the api-spec — a documented endpoint the contract dropped, a field the reference shows that the contract never declared, an error the reference omits — is the single most damaging defect. It is the same failure mode whether the catalog is hand-authored or generated; the drift check (Step 6.5) guards it in both modes.
- **Happy-path-only endpoints.** Showing the `200` body and stopping is the most common reference defect. Each endpoint must show at least one failure case and the error/status codes it returns — the failure modes are part of the reference, not an appendix.
- **Re-typing the generated catalog.** Where the endpoint catalog is generated from OpenAPI, manually re-typing it duplicates the generator and immediately drifts. Let generation own the catalog; spend your effort on the narrative, the examples, and the drift check.
- **Confusing the reference with the wire contract.** The api-spec is the engineering contract the build implements against (upstream, exhaustive, internal); the api-reference is the published consumer doc downstream of and consistent with it, adding onboarding + examples. Don't re-derive the contract here.
- **Confusing the reference with the end-user guide.** The developer API reference and the end-user product guide are different audiences/documents. Keep this the developer integration doc.
- **Examples that drift from the schema.** A worked example or code sample with a field the contract doesn't declare (or a wrong type/status) breaks the reference silently. Keep examples consistent with the contract's shapes.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

**Worked contrast — looks-complete vs integrable** (use it to self-detect):

| Aspect | Looks complete (reject) | Integrable (ship) |
|---|---|---|
| First call | "Authenticate, then call the API." | A copy-paste curl quickstart: get a key from the dashboard, `GET /v1/widgets` with the `Authorization` header, the exact `200` body to expect. |
| Endpoint coverage | "The main endpoints are documented." | Every operation in the api-spec has a block; the endpoint index matches the contract one-to-one. |
| Parameters | "Takes the widget fields." | "`name` (string, required, max 255), `status` (string, optional, one of `active`/`archived`, default `active`)." — from the contract. |
| Errors | "Errors are returned on failure." | Per-endpoint rows (`400 invalid_request`, `404 not_found`, `409 conflict`) + one shared error shape + a status-code table — every code from the contract. |
| Samples | "See the SDK docs." | curl + a Python sample with realistic values matching the schema, mirroring each other. |
| Consistency | (untraced) | Every endpoint/field/error traces to the api-spec; nothing shown that the contract doesn't declare. |

If your fill reads like the left column — true of any API, no worked examples, no error cases, no trace to the contract — it isn't done.

## Anti-patterns

- **"The api-spec is thin, I'll fill in plausible endpoints/params."** Never fabricate. Derive from the contract; surface gaps as assumptions or a blocker.
- **"I'll spec the happy path; the errors are obvious."** They aren't — document each endpoint's failure responses and status codes, or a developer can't handle them.
- **"The catalog is generated, so I'm done."** Generation gives you the catalog, not the onboarding narrative, the example quality, or the drift check — that is the human-authored value.
- **"This is also the wire contract, so I'll write exhaustive internal schema rigor."** The contract is upstream; the reference is the consumer doc on top of it. Reference it, don't re-derive it.
- **"This is also the end-user guide, so I'll write product task help."** Different audience — this is the developer integration reference.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know what good API docs look like."** The research grounds *this product's* onboarding, error-doc, and sample conventions — not API-docs theory.

## Output

A **comprehensive, published API reference** that meets the **Step 6 usability + contract-consistency bar** (first call reachable; every api-spec operation documented with purpose + typed params + a worked request + a worked response + its errors; errors first-class with one shape + a status-code table; rate limits documented; consistent with the contract — every endpoint/field/error traced, no drift, nothing fabricated; samples runnable + matching the schemas; versioning stated; shared types defined once; proportional). The artifact is **textual** — endpoint sections + fenced request/response examples + fenced code samples (curl + >=1 language); the method + bar are **medium-independent** (markdown today via the local docs backend; a future rendered docs site or design-tool backend changes only the medium, not the skill). The **abstract consumer** is the client developer who integrates against the API from the reference alone, and a runtime review gate (which asserts the same bar). The api-reference **depends on** the api-spec (and references the feature-spec/architecture-doc where present) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- An **api-reference template tool** (`content-template-gateway`) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** (`deep-research`) — grounds the onboarding narrative, examples, and conventions in established public-API-docs practice.
- An **api-spec-authoring skill** (`authoring-api-spec`) — produces the *upstream* engineering wire contract every endpoint, field, and error in this reference derives from and stays consistent with.
- A **feature-spec** and an **architecture-doc** (where present) — upstream context: the usage context for each operation, and the auth/versioning context.
- A **review gate** (`reviewing-api-reference`) — asserts the same usability + contract-consistency bar on the finished reference at runtime; author and gate share one bar (single-sourced) so they don't drift.
- An **end-user product-guide skill** (`authoring-user-guide` / `authoring-developer-guide`) — a *different* document/audience (the product's end user, not the developer integrating the API).

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (public-API-docs best-practice guides, Stripe/Twilio conventions, OpenAPI generation tooling, HTTP error/rate-limit semantics). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
