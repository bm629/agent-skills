# authoring-api-spec

Author an **API specification** — the engineering **wire contract** of an API surface: the operations/endpoints, request + response schemas (fields, types, required/optional, constraints), the auth + authorization model, a complete error model, pagination/filtering/rate-limits, versioning, and worked request/response examples. The how-to (a contract-design method + a no-ambiguity bar), composed with a separate api-spec template tool and a deep-research capability; targets a textual markdown artifact (endpoint tables + fenced schema blocks — JSON / OpenAPI fragment / SDL / proto — + example request/response pairs).

## Purpose

An api-spec is the agreement between the service that implements an API and the clients that consume it. This skill carries the producer's judgment — not the section list — guiding a producer to render the contract in the project's API style (OpenAPI/JSON-Schema for REST, SDL for GraphQL, proto/method-signatures for RPC) with the same rigor across all three, type every field, enumerate the error cases (not just the happy path), trace each operation to a feature-spec behavior, and reference the data-model's entities rather than redefining them. The bar to clear: a client engineer can call every operation correctly and a server engineer can implement it from the contract alone, with no ambiguity about shapes, errors, or auth.

## When to activate

- Authoring an API specification from an approved feature-spec that names the behaviors an API must expose.
- Specifying the operations, request/response schemas, auth, error model, and examples of an API surface (REST, GraphQL, or RPC/gRPC).
- **Amending** an approved api-spec as a versioned delta (a new/changed operation, a field added/removed, a parameter made required, an operation retired).
- Filling an api-spec template with researched, decision-complete, fully-typed per-operation content.

### When NOT to activate

- **The persistence data-model** (stored entities + relationships) → `authoring-data-model` (it is *upstream*; the api-spec describes wire DTOs and references it — a DTO is not a stored row).
- **The published, consumer-facing API reference** (prose end-user docs, often generated *from* this contract) → a separate downstream document with a different audience.
- **The implementation / architecture** behind the endpoints → the design layer, not the interface.
- **Reviewing a finished api-spec** → `reviewing-api-spec` (its dedicated gate; the generic `design-review` carves the api-spec artifact out to this twin).

## Workflow

Take the section structure from the api-spec template tool (don't invent an outline). Pick the API style first (REST / GraphQL / RPC), then apply identical rigor in that style's notation — do not force OpenAPI onto a non-REST API. Load the feature-spec and any upstream context; its behaviors are the operation-coverage checklist (every operation traces to a behavior; resources map onto the data-model's entities by reference). Research to ground the contract in established API-design practice (HTTP semantics + status codes, JSON-Schema/OpenAPI rigor, SDL, gRPC, RFC 9457 error modeling, versioning, auth). Then fill each section to method: API overview (style + base + versioning, with the breaking-change rule + the deprecation→sunset policy stated day-one); a scannable operation list; per-operation request + response fully typed on both sides with deliberately-chosen status codes; shared types defined once and referenced; the auth + per-operation authorization model (the OAuth flow per client type, a scope/role per non-public operation); a single consistent error shape (machine code + request id) **plus every named failure case enumerated per operation with its retryability** (the most-skipped part); pagination/filtering/rate-limits for collections; and worked examples consistent with the schemas. Self-check against the 12-point no-ambiguity bar before handoff. On an **amend**, edit the delta — classify additive vs breaking; a breaking change is a **new version + a `Deprecation`→`Sunset` lifecycle with a migration guide**, never an in-place edit; analyze backward/forward compatibility; version + changelog; flag the forward/downward ripple to the api-reference/impl/clients.

## Output

A comprehensive API specification meeting the **no-ambiguity bar** (style+base+versioning [+ breaking-change rule + deprecation/sunset policy] stated; every operation listed, traced, and fully typed on both sides with status codes; auth + per-operation authorization specified; a complete error model with every failure case named + retryability; shared types defined once and referencing the data-model; pagination/rate-limits specified; examples present and consistent; naming/versioning consistent; grounded + one-directional vs the api-reference; nothing fabricated) — and, on a change, amended as a versioned delta. Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same 12-condition bar the `reviewing-api-spec` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Style-agnostic rigor, not OpenAPI-only** — renders in the project's one style's notation; the typed-schemas/complete-errors/auth/examples rigor is identical across REST, GraphQL, and RPC.
- **Complete error model** — every operation names its failure cases with status codes + retryability, in one consistent error shape; not just the happy path.
- **References the data-model, doesn't redefine it** — wire DTOs map onto the upstream entities by reference, noting only the deltas; a DTO is not a stored row.
- **Amends by versioning** — on a change, classifies additive/breaking; a breaking change is a new version + a deprecation→sunset lifecycle + a migration guide, never an in-place edit; flags the forward/downward ripple.
- **Single-sourced bar** — shared with the dedicated `reviewing-api-spec` twin (the 12-condition gate), so produce and review don't drift.
- **capability-record-aware** — when a `capability_record` is injected by the caller, scope boundaries for `entry_points`, `publishes`, `consumes`, and `refs` are drawn from it; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
