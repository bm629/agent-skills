# Versioning & evolution — method depth (`authoring-api-spec`)

Worked depth for the versioning policy (stated day-one) and the Step-6 amend method. Load when filling the versioning section or amending an approved contract. Portable provenance in `sources.md`.

## Versioning scheme (state it up front)

Pick **one** and state it:

- **URL-path** (`/v1/...`) — least ambiguous, most cache/router-friendly. **Major-version only** (Google AIP-185: `v1`/`v2`, never `v1.1` — minor/patch changes are additive and don't bump the path). The default recommendation.
- **Header / media-type** (`Accept: application/vnd.example.v2+json` or an `API-Version` header) — keeps URLs stable; harder to test by hand.
- **Date-based** (Stripe: a `YYYY-MM-DD` version, an account **pinned** at signup, behavior frozen at the pin). Powerful but operationally heavy (version-shims).

## Breaking vs non-breaking (the classification rule)

State the rule so a reader knows what a minor revision may do. The **AIP-180** framing has three compatibility layers — *source* (client code still compiles), *wire* (bytes still parse), *semantic* (behavior still matches).

| Change | Class |
|---|---|
| Add an **optional** field / a new operation / a new enum value (clients tolerate unknown) / a new optional error case | **Additive (non-breaking)** — ships in-version |
| **Remove/rename** a field or operation · **narrow a type** / tighten validation · make an optional field **required** · change a default · change an operation's **semantics**/success status | **Breaking** — new version + deprecation |

The **tolerant-reader contract** is what makes additive changes safe: state that clients ignore unknown response fields. proto: never reuse/renumber a field number; reserve removed fields.

## Deprecation → sunset lifecycle (retirement, signposted)

A breaking removal is a **two-stage, signposted lifecycle**, never a silent removal:

1. **Deprecation** — still operational, no longer preferred. The **`Deprecation`** response header (RFC 9745; value = an RFC 9651 Date) and/or an OpenAPI `deprecated: true` flag; a published **migration path**.
2. **Sunset** — the point it may stop responding. The **`Sunset`** response header (RFC 8594; an HTTP-date). **`Sunset` MUST NOT be earlier than `Deprecation`** — a deprecation window precedes the sunset, giving clients time to migrate.

## The amend method (Step 6 — edit the delta, don't redraw)

Scope = the touched operations + their schemas + the shared types + the error cases on them (+ versioning, if breaking).

1. **Classify additive vs breaking** (above). A breaking change shipped as a minor in-version edit silently breaks every live client — the cardinal amend defect.
2. **A breaking change is a versioning event:** a new version (`/v2`, a new date-pin) + the deprecation→sunset lifecycle on the old surface + a migration guide. Never mutate/delete a live operation in place.
3. **Compatibility analysis:** backward (the unchanged version keeps working) + forward (new fields optional/defaulted, enum additions tolerated, no silent semantic change).
4. **Version + changelog:** bump the **document's own** revision (distinct from the API version) + a changelog entry (additive/breaking); mark retired operations **deprecated, not deleted**.
5. **Forward/downward ripple:** the downstream **api-reference** (re-synced/re-generated + the deprecation markers), the **impl/test-plan** building against the contract, the **live clients** (the sunset window), the **release-runbook**; the **upstream feature-spec is amended first** (§15 order). Name the ripple.

## Worked deltas

- **Additive (in-version):** add an optional `tags[]` to `POST /v1/invoices` request + the `Invoice` response. Class: additive. Version: none. Ripple: api-reference adds the field; impl validates it; no client breaks. Changelog: "added optional `tags` (additive)."
- **Breaking (new version):** rename `Invoice.amount`→`Invoice.amountMinor` + make `currency` required. Class: breaking. Route: `/v2/invoices` with the new shape; `/v1` deprecated (`Deprecation: <date>`) with a sunset (`Sunset: <date>`, e.g. +6 months); migration guide maps `amount`→`amountMinor`. Ripple: api-reference documents both + the deprecation; clients notified; runbook deploys v2 alongside v1. Changelog: "v2 — renamed amount→amountMinor, currency required (BREAKING); v1 deprecated, sunset <date>."
