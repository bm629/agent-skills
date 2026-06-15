---
name: authoring-api-spec
description: >
  Use when authoring an API specification — the engineering wire contract of an
  API surface: operations/endpoints, request + response schemas (fields, types,
  required/optional, constraints), auth, a complete error model,
  pagination/rate-limits, versioning, and worked examples. Guides the producer
  through the METHOD, not the outline: rendering the contract in the project's
  style (OpenAPI for REST, SDL for GraphQL, proto for RPC), typing every field,
  enumerating the ERROR CASES (not just the happy path),
  tracing each operation to a feature-spec behavior, and referencing the
  data-model rather than redefining it — to a bar where a client can call every
  operation and a server can implement it from the contract alone. Composes with a
  separate api-spec template tool and a deep-research capability. Assumes the
  upstream feature-spec (+ architecture-doc + data-model where present) — never a
  blank page. Not the persistence data-model, the consumer-facing API reference,
  the implementation, or reviewing a finished api-spec.
extensions:
  claude:
    when_to_use: "authoring or amending the engineering wire contract (operations, schemas, auth, errors) of an API surface"
    argument-hint: "<the feature-spec (+ architecture-doc/data-model) to turn into an API contract>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-15
---

# `authoring-api-spec` — SKILL.md

> **Variant:** standard · **When to use:** authoring the engineering wire contract of an API surface — to a bar where a client integrates and a server implements from the contract alone, with no ambiguity about shapes, errors, or auth.

## Overview

This skill is the *how-to* of writing a strong **API specification** — the engineering **wire contract** of an API surface. It says what each operation looks like over the wire: the request and response shapes (fields, types, required/optional, constraints), the auth model, the error model, and worked examples. This skill carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: an **api-spec template tool** that supplies the section *structure*, and a **deep-research capability** to ground the contract in established API-design practice. The producer is handed the **upstream feature-spec** (the behaviors the API must expose) and, where present, the **architecture-doc** (service boundaries) and the **data-model** (the entities resources map to) — never a blank page. The bar to clear: the contract is *implementable and callable* — a client engineer can call every operation correctly and a server engineer can implement it without asking the author, with no ambiguity about shapes, errors, or auth.

## When to activate

- Authoring an API specification from an approved feature-spec that names the behaviors an API must expose.
- Specifying the operations, request/response schemas, auth, error model, and examples of an API surface (REST, GraphQL, or RPC/gRPC).
- Filling an api-spec template with researched, decision-complete, fully-typed per-operation content.
- **Amending** an approved api-spec as a versioned delta (a new/changed operation, a field added/removed, a parameter made required, an operation retired) — see Step 6.

**Do NOT activate when:**

- Designing the **persistence data-model** (stored entities + relationships) → that is a separate concern and is *upstream* here. The api-spec describes wire DTOs and **references** the data-model; a DTO is not a stored row.
- Writing the **published, consumer-facing API reference** (the prose docs end-users read, often generated *from* this contract) → that is a separate downstream document with a different audience.
- Writing the **implementation / architecture** (how the service behind the endpoints is built) → that is the design layer, not the interface.
- Reviewing or grading a finished api-spec → use `reviewing-api-spec` (the dedicated gate, single-sourced with this skill's Step-7 bar); this skill is produce-side only.
- Authoring the **feature-spec** itself (the behaviors) → that is *upstream input* here.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your api-spec template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive api-spec structure (request/forge one, or fall back to the canonical set: API overview, operation list, per-operation request+response, shared data types, auth+authorization, error model, pagination/filtering/rate-limits, examples, open questions), then proceed.

### Step 2: Pick the API style first — then apply the same rigor in that style's notation

A project uses **one** API style. Choose it, then render the contract in that style's notation — but the *rigor* (typed schemas, complete errors, auth, examples) is identical across all three:

- **REST** → OpenAPI/JSON-Schema conventions: endpoint tables (method + path), typed parameters and request bodies, responses keyed by HTTP status, reusable schemas, declared security schemes.
- **GraphQL** → SDL: typed object/scalar/enum/input types, `Query`/`Mutation`/`Subscription` root fields, errors in the top-level `errors` array.
- **RPC / gRPC** → proto `service`/`rpc` method signatures with typed request and response messages and status codes.

Do **not** mandate OpenAPI for a non-REST project — OpenAPI is the REST flavor, not the only format. The skill teaches contract rigor for whichever style the project uses.

### Step 3: Load the upstream docs; drive coverage off the feature-spec

Read the approved **feature-spec** and any upstream context (architecture-doc, data-model) — this is your **input, not a blank page**. The feature-spec's behaviors are your operation-coverage checklist: every behavior the API must expose becomes one or more operations; every operation traces back to a behavior (no orphan/invented endpoints). Map each resource onto the **data-model's entities by reference** — note where the wire DTO differs from the stored entity (computed, derived, or omitted fields); do not duplicate or contradict the data-model. Where the upstream is thin, make the gap an **explicit open question or stated assumption**, never a silently-invented shape.

### Step 4: Research to ground the contract

Use a deep-research pass to ground the contract in established API-design practice — REST/HTTP semantics and status codes, JSON-Schema/OpenAPI rigor, GraphQL SDL, RPC/gRPC, consistent naming, error modeling (e.g. RFC 9457 Problem Details for REST), versioning, and auth patterns — for *this* product's surface, not "API specs in general." **If no research capability is available, do NOT fabricate field names, limits, status codes, or error codes** — state them as explicitly-flagged assumptions to validate before build.

### Step 5: Apply the per-section method

Fill the template's sections to this method. Collapse a section a thin API doesn't need; size proportionally.

- **API overview** — state the **style + transport**, the **base URL/endpoint**, and a concrete **versioning** scheme (URL path `/v1` is least ambiguous and most common — major-version only per AIP-185; plan versioning from the start). State naming + date/time conventions once, here.
- **Versioning policy — classify changes + plan retirement (state it day-one).** State **what counts as a breaking change**: *additive* = a new **optional** field/operation/enum-value the tolerant-reader client ignores (clients must ignore unknown response fields); *breaking* = removal/rename/type-narrowing/required-add/default-change/semantic-shift (AIP-180 source/wire/semantic). And state the **deprecation → sunset lifecycle** for a removal: `Deprecation` (RFC 9745, the date it became deprecated) → a migration window → `Sunset` (RFC 8594, the date it may stop responding; `Sunset` ≥ `Deprecation`) + a published migration path. The *policy* is stated here; the *act* of deprecating a specific operation during a change is Step 6 (amend).
- **Resource / operation list** — one row per operation up front (method+path / root field / `Service.Method`) so the surface is scannable before the per-operation detail.
- **Per-operation request + response — fully typed on both sides.** Every parameter/argument/field carries a **type, a required/optional flag, and constraints** (length, enum, format, range). Every response is keyed to a **status code** (or gRPC status / GraphQL data-vs-errors) with its body schema. **Choose the status deliberately** — `201`+`Location` for a create, `204` for a no-body success, `401` (unauthenticated) vs `403` (forbidden/insufficient-scope) not conflated, `409` for a conflict, `422`/`400` for validation; not `200` for everything. An operation specified only on the happy path is **not done**.
- **Shared data types** — define each reusable DTO **once** and reference it by name (`$ref` / SDL type / proto message); never inline-redefine the same shape across operations. These are **wire** types — where a DTO projects a stored entity, reference the data-model, do not restate it.
- **Auth + authorization** — name the scheme(s) (API key / OAuth 2.0 + **which flow** — auth-code+PKCE for user-facing/public clients, client-credentials for service-to-service / JWT / mTLS), where the credential goes, and the **authorization** model: **every non-public operation names its required scope/role**, mapped to the operation list's auth-scope column ("authenticated" without a per-operation scope is under-specified). State token lifecycle + HTTPS + no secret in a URL.
- **Error model — the catalog, not just the happy path.** Define **one consistent error shape** for the whole API (e.g. RFC 9457 Problem Details for REST; an `errors` array for GraphQL; `google.rpc.Status` for gRPC) carrying a **machine-readable code** (the client branches on it — the HTTP status is too coarse), a **human message** (for logs, not end-user display), and a **request/trace id**. Then **enumerate every named failure case** per operation (validation, auth, forbidden, not-found, conflict, rate-limited, server) with its status code **and its retryability** (`429`/`5xx` retryable after `Retry-After` with backoff; `4xx` not — retrying won't help). This is the single most-skipped part of an api-spec — do it deliberately.
- **Pagination / filtering / sorting / rate-limits** — for collection operations, pick a pagination strategy (cursor-based for large/dynamic/user-facing; offset for small/static), define the request params + the response envelope (next-cursor / has-more / `Link` header) + default/max page size; list filterable + sortable fields with a stable tie-breaker; state rate limits + the headers + the `429` behavior.
- **Worked examples** — at least one full request/response pair per primary operation, **consistent with the schemas** (same field names, types, status codes). An example that contradicts its schema is a defect.

### Step 6: Amending an approved contract (the delta case)

When the contract already exists and a change is requested — **edit the delta, don't redraw**. Scope = the touched operations + their request/response schemas + the shared types + the error cases on them (+ the versioning section if the change is breaking). Then:

1. **Classify the change — additive vs breaking.** *Additive* (a new optional field, a new operation, a new optional response field a tolerant-reader ignores, a new optional error case) ships **in-version**. *Breaking* (a removed/renamed field or operation, a type narrowing, an optional field made required, a default/semantic change, a removed enum value) does **not** edit in place under the same version. A breaking change shipped as a minor in-version edit silently breaks every live client — the cardinal amend defect.
2. **A breaking change is a versioning event, not an edit.** Route it to a **new version** (`/v2`, a new date-pin) and put the old surface through the **deprecation → sunset lifecycle** (`Deprecation` → a migration window → `Sunset`, `Sunset` ≥ `Deprecation`) with a **migration guide** (old→new mapping). Never silently mutate or delete the old operation.
3. **Analyze backward/forward compatibility** — backward: the existing version keeps working; forward: new fields optional/defaulted, enum additions tolerated, an operation never silently changing meaning.
4. **Version + changelog the delta** — bump the **document's own** version (the §10 revision history, distinct from the API version) + a changelog entry (additive/breaking); mark retired operations **deprecated, not silently deleted**.
5. **Flag the forward/downward ripple** — the change ripples to the **downstream api-reference** (re-synced/re-generated from the changed contract + the deprecation markers), the implementation + test-plan building against it, the **live clients** (the reason for the sunset window), and the release-runbook; the **upstream feature-spec is amended first** (a new behavior drives the new operation). Name the ripple; don't leave it for a downstream reader to discover.

A greenfield first contract skips Step 6 (no prior version to amend).

### Step 7: Self-check against the no-ambiguity bar before handing off

Confirm all hold (this is the bar a runtime review gate — `reviewing-api-spec` — asserts; author and gate share it so they don't drift):

1. **Style + base + versioning stated** — the API style, base URL/endpoint, and a concrete versioning scheme are present; the **breaking-vs-non-breaking change rule + the deprecation→sunset policy** are stated.
2. **Every operation listed + traced** — the operation list is complete; each operation maps to an upstream feature-spec behavior (no orphan/invented endpoints, none missing).
3. **Every operation fully typed on both sides** — request and response fully typed, each field required/optional with constraints, every response keyed to a status code. A happy-path-only operation fails.
4. **Auth + per-operation authorization** — authentication scheme(s) (+ OAuth flow per client type) stated; **every non-public operation names its required scope/role**; token lifecycle + HTTPS; nothing implicitly open.
5. **Error model complete** — one consistent error shape (machine code + message + request id) **and** every named failure case enumerated per operation **with its retryability**. A spec listing only 2xx responses fails.
6. **Shared types defined once + referenced** — reusable DTOs defined once and referenced; wire types reference the data-model rather than restating/contradicting it.
7. **Pagination/rate-limits specified** — collection operations define pagination; rate limits + headers stated.
8. **Examples present + consistent** — at least one request/response pair per primary operation, matching the schemas exactly.
9. **Naming + versioning consistent** — applied uniformly across the surface.
10. **Grounded, honest & one-directional** — operations/shapes reflect the feature-spec + data-model (not fabricated; gaps surfaced as assumptions/open-questions, not invented); **one-directional vs the api-reference** (this contract is the published reference's source of truth — never reverse-engineered from it); where a live API exists, claims about current operations/shapes are **consistent with the shipped surface** (greenfield: N/A).
11. **(Amend only) delta well-scoped + classified + versioned** — on a change request: the changed operations meet 1–10 on what they touched; the change is **classified additive/breaking**; a breaking change carries a **new version + the deprecation→sunset plan + a migration guide**; backward/forward compatibility analyzed; the forward/downward ripple flagged; the document version bumped + a changelog; retired operations marked deprecated, not deleted. On a greenfield first build, n/a.

**Thin-input gate:** if a behavior the API must expose cannot be researched or even credibly assumed into a contract, surface it as a **blocker** ("operation under-defined — needs product/engineering decision") rather than inventing a shape. An api-spec whose shapes, errors, *and* auth are all guesses is not callable.

## Rules

**Hard rules (never violate):**

- **Type both sides of every operation.** Request and response fully typed, each field required/optional with constraints, every response keyed to a status code. An untyped field or an unstated status is not done.
- **Enumerate the error cases.** Every operation names its failure cases (validation, auth, not-found, conflict, rate-limit, server) with status codes — not just the happy path. A happy-path-only operation is incomplete.
- **One consistent error shape.** The whole API shares a single error response shape (machine code + message + request id); don't invent a different error body per endpoint.
- **Reference the data-model, don't redefine it.** Wire DTOs map onto the upstream data-model's entities by reference; note the deltas. Never restate or contradict the stored schema. A DTO is not a stored row.
- **One-directional vs the api-reference.** The published consumer-facing **api-reference** is the *downstream* consumer of this contract — often generated from it. This contract is the reference's source of truth; never reverse-engineer the contract from the published docs (that inverts the dependency). The data-model is *upstream*, the api-reference is *downstream*.
- **A breaking change is a new version, not an in-place edit.** When amending, classify additive vs breaking; route a breaking change to a new version + a `Deprecation`→`Sunset` lifecycle with a migration path; never silently mutate or delete a live operation under the same version (Step 6).
- **Trace every operation to a feature-spec behavior.** No orphan/invented operation, no missing behavior. Coverage runs off the feature-spec.
- **Style-agnostic rigor, not OpenAPI-only.** Render in the project's one style's notation (OpenAPI for REST, SDL for GraphQL, proto for RPC); apply the same rigor regardless. Don't force OpenAPI onto a non-REST API.
- **Examples match the schemas.** Every example uses the exact field names, types, and status codes the schemas declare. An example contradicting its schema is a defect.
- **Never fabricate.** Don't invent field names, limits, status codes, or error codes to look complete. With no source, state them as explicitly-flagged assumptions to validate before build.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Contract, not implementation, not published reference.** Specify the *interface* (the wire shapes), not how the service is built and not the prose end-user reference.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of the *contract* (every operation typed, errors enumerated, auth stated), not word count. A thin API collapses sections it doesn't need.
- Prefer RFC 9457 Problem Details for REST error bodies; prefer cursor-based pagination for large/dynamic collections.
- Prefer URL-path versioning (`/v1`) unless the project already standardizes on header/date-based.

## Gotchas

- **Happy-path-only operations.** Specifying the `200` body and stopping is the most common api-spec defect. Each operation must enumerate its `4xx`/`5xx` failure cases with status codes — the error catalog is part of the contract, not an afterthought.
- **Redefining the data-model as DTOs.** Re-typing the stored entity inline drifts from (and contradicts) the upstream data-model. Reference it; note only where the wire shape differs (computed/derived/omitted fields).
- **Confusing the contract with the published reference.** This is the engineering contract the build implements against; the consumer-facing reference (often generated from it) is a separate downstream document with a different audience. Don't write prose end-user docs here.
- **OpenAPI tunnel vision.** Reaching for OpenAPI on a GraphQL or gRPC API misfits the style. Pick the project's one style; render in *its* notation (SDL / proto).
- **Examples that drift from the schema.** An example with a field the schema doesn't declare (or a wrong type/status) breaks the contract silently. Keep examples consistent with the declared shapes.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

**Worked contrast — under-specified (compliant on the surface) vs callable** (use it to self-detect):

| Aspect | Under-specified (reject) | Callable (ship) |
|---|---|---|
| Operation trace | "There's an endpoint for invoices." | "`POST /v1/invoices` implements feature-spec §3.2 *Create invoice*; projects the `Invoice` data-model entity (omits `internalLedgerId`)." |
| Request | "Takes invoice fields." | "Body: `amount` (integer, required, >0, minor units), `currency` (string, required, ISO-4217), `dueDate` (string, optional, RFC-3339)." |
| Response | "Returns the invoice." | "`201` → `Invoice` schema (section 4); `Location` header set to the new resource." |
| Error model | "Errors are returned." | "`400 validation_error` (bad field), `401 unauthorized`, `403 forbidden` (missing `invoices:write`), `409 conflict` (duplicate idempotency-key) — all in the shared Problem-Details shape." |
| Auth | "Authenticated." | "OAuth 2.0 bearer; requires scope `invoices:write`." |
| Example | "See the docs." | "Request/response pair using `amount: 5000`, `currency: \"USD\"`; `201` body matches the `Invoice` schema exactly." |

If your fill reads like the left column — true of any API, no types, no status codes, no error cases — it isn't done.

## Anti-patterns

- **"I'll spec the happy path; the errors are obvious."** They aren't — name each failure case with its status code, or a client can't handle it.
- **"I'll redefine the entities as request/response shapes."** Reference the data-model; restating it drifts and contradicts. Note only the wire deltas.
- **"OpenAPI is the standard, I'll use it for everything."** OpenAPI is the REST flavor; a GraphQL API needs SDL, a gRPC API needs proto. Match the project's style.
- **"This is also the API reference, so I'll write end-user prose."** The contract and the published reference are different documents/audiences; keep this the engineering contract.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"Skip the research, I know REST."** The research grounds *this product's* surface, naming, and error model — not API theory.
- **"It's a small change, I'll edit the field in place."** A breaking change (rename/remove/type-narrow/required-add) under the same version silently breaks every live client — classify it, route it to a new version + a `Deprecation`→`Sunset` lifecycle with a migration guide (Step 6).

## Output

A **comprehensive API specification** that meets the **Step 7 no-ambiguity bar** (style+base+versioning [+ breaking-change rule + deprecation/sunset policy] stated; every operation listed, traced, and fully typed on both sides with status codes; auth + per-operation authorization specified; a complete error model with every failure case named + retryability; shared types defined once and referencing the data-model; pagination/rate-limits specified; examples present and consistent; naming/versioning consistent; grounded + one-directional vs the api-reference; nothing fabricated) — and, on a change, **amended as a versioned delta** (Step 6: classified additive/breaking, a breaking change routed to a new version + deprecation→sunset, the ripple flagged). The artifact is **textual** — endpoint tables + fenced schema blocks (JSON / OpenAPI fragment / SDL / proto) + example request/response pairs; the method + bar are medium-independent. The **abstract consumer** is the client engineers who integrate against the contract, the server engineers who implement it, the downstream published api-reference often generated from it, and the **`reviewing-api-spec`** gate (which asserts the same bar). The api-spec **depends on** the feature-spec (and references the data-model) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- An **api-spec template tool** (e.g. a content/template gateway) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the contract in established API-design practice (REST/HTTP, OpenAPI/JSON-Schema, GraphQL SDL, gRPC, error modeling, versioning, auth).
- A **feature-spec-authoring skill** — produces the *upstream* feature-spec whose behaviors this contract exposes.
- An **architecture-doc** and a **data-model** (where present) — upstream context: the service boundaries, and the entities the wire DTOs reference.
- **`reviewing-api-spec`** — the dedicated review gate for the finished api-spec; asserts the same no-ambiguity bar (its conditions are single-sourced 1:1 with this skill's Step-7 self-check) so author and gate don't drift. (The generic `design-review` carves the api-spec artifact out to this twin.)
- A **consumer-facing API-reference skill** — the *downstream* published reference, a distinct document often generated from this contract.

## Progressive disclosure

- `references/contract-method.md` — depth on the contract spine: style choice + operations/method-semantics (RFC 9110) + status-code selection + type-both-sides + the complete error model (RFC 9457 + machine code + retryability) + auth/per-operation-authorization + pagination/tie-breaker. Load when filling a section needs the worked detail.
- `references/versioning-and-amend.md` — depth on versioning + evolution: the scheme (URL-path/header/date-based, AIP-185), the breaking-vs-non-breaking classification (AIP-180), the deprecation→sunset lifecycle (RFC 9745/8594), and the Step-6 amend method + the forward/downward ripple. Load when versioning or amending.
- `references/sources.md` — research provenance for the method + quality bar (OpenAPI, JSON Schema, GraphQL SDL, gRPC/protobuf, RFC 9110/9457, RFC 8594/9745, AIP-180/185, REST design + error/pagination guides). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.

## Changelog

- **1.2.0** (2026-06-15) — restructure for the production-grade pair (single-sourced with the net-new `reviewing-api-spec` twin). Added the **amend method** (Step 6: classify additive/breaking → a breaking change is a new version + a `Deprecation`→`Sunset` lifecycle → compatibility → version+changelog → the forward/downward ripple to the api-reference/impl/clients). Deepened **versioning** (breaking-vs-non-breaking classification + the deprecation→sunset policy, AIP-180/185 + RFC 8594/9745), **per-operation authorization** (every non-public operation names its scope + the OAuth flow per client type), the **error model** (machine code + request id + retryability), **status-code selection**, and the **one-directional-vs-the-api-reference** rule. Extended the self-check to Step 7 (cond-1/4/5/10 deepened + a new cond-11 amend) — single-sourced 1:1 with the twin's 11 conditions. Re-pointed the gate references at `reviewing-api-spec`. Added `references/contract-method.md` + `references/versioning-and-amend.md`. No prior coverage dropped.
- **1.1.0** (2026-06-04) — initial reviewed release.
