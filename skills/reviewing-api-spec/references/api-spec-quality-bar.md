# The api-spec quality bar — per-condition pass/gap signals (`reviewing-api-spec`)

The eleven conditions expanded with a **pass signal**, a **gap signal**, and a **worked finding**. Load when a borderline condition needs a sharper call. The bar is single-sourced with `authoring-api-spec`'s Step-7. Style-agnostic throughout (judge REST/GraphQL/gRPC in its own idiom — no OpenAPI reflex).

## cond-1 — Style, base & versioning
- **Pass:** style + base URL/endpoint + a versioning scheme stated; the breaking-vs-non-breaking rule + the deprecation→sunset policy present.
- **Gap:** no versioning scheme; or a versioning section that names a scheme but no breaking-change rule / no deprecation policy.
- **Finding:** *revise — Style, base & versioning (cond. 1), §1: the versioning scheme (`/v1`) is stated but there's no rule for what counts as a breaking change and no deprecation policy. Fix: state the additive-vs-breaking rule (additive = new optional field/operation; breaking = removal/rename/required-add) + the `Deprecation`→`Sunset` lifecycle.*

## cond-2 — Every operation listed & traced
- **Pass:** the op list is complete + scannable; each operation maps to a feature-spec behavior; method + success-status semantics correct.
- **Gap:** an operation with no trace (invented endpoint); a behavior with no operation; a mutating `GET`; `200` where `201` belongs. (GraphQL/gRPC: judge the root-type/method shape, not HTTP.)
- **Finding:** *revise — Every operation traced (cond. 2), §2: `DELETE /v1/audit-logs` appears in the operation list but no feature-spec behavior calls for deleting audit logs. Fix: remove the orphan operation, or trace it to a behavior (flag it back to the feature-spec author if intended).*

## cond-3 — Every operation fully typed on both sides *(signature spine)*
- **Pass:** request + response fully typed, each field required/optional + constraints, every response keyed to a status + typed body.
- **Gap:** an untyped/unconstrained field; a response with no status/body; **a happy-path-only operation (only its `2xx`)**.
- **Finding:** *revise — Typed both sides (cond. 3), §3 `POST /v1/invoices`: the `amount` field is "a number" with no type/units/constraint. Fix: type it `integer, minor units, required, >0` so a client/server agree on the shape.*

## cond-4 — Auth & per-operation authorization
- **Pass:** scheme + credential location named; OAuth flow per client type; every non-public operation names its scope/role; token lifecycle + HTTPS.
- **Gap:** an operation with no stated authorization (silently open / "logged-in" with no scope); unnamed scheme; a credential in a URL.
- **Finding:** *revise — Per-operation authorization (cond. 4), §3 `POST /v1/invoices`: the operation states "authenticated" but no required scope. Fix: name the scope (`invoices:write`) in the op + the §2 auth-scope column, so a client knows the grant a write needs.*

## cond-5 — Error model complete *(the signature condition)*
- **Pass:** one consistent error shape (machine code + message + request id) AND every failure case enumerated per operation with status + code + retryability.
- **Gap:** an operation showing only its `2xx`; an ad-hoc/different error body per endpoint; missing machine code/request id; no retryability.
- **Finding:** *revise — Error model complete (cond. 5), §3 `GET /v1/invoices/{id}`: only the `200` is documented. Fix: enumerate `401 unauthorized`, `403 forbidden` (if scoped), `404 not_found` in the shared Problem-Details shape with each status + machine code + retryability.*

## cond-6 — Shared types defined once + reference-not-redefine the data-model *(signature spine)*
- **Pass:** reusable DTOs defined once + referenced; wire DTOs reference the data-model + note deltas, never restate/contradict.
- **Gap:** the same shape re-typed inline across operations (drift); a DTO that re-types & contradicts a handed-in data-model. **Greenfield: no data-model → the DTO stands alone (not a gap).**
- **Finding:** *revise — Reference the data-model (cond. 6), §4 `Invoice`: the DTO re-types every stored column inline and exposes `internalLedgerId`, which the data-model marks internal. Fix: reference the `Invoice` entity + note only the wire deltas (computed/omitted); don't expose the internal field.*

## cond-7 — Pagination, filtering, sorting & rate-limits
- **Pass:** collection ops define pagination (strategy + envelope + default/max size); filterable/sortable fields + a stable tie-breaker; rate limits + `429`.
- **Gap:** an unbounded/unpaginated collection; a sorted-paginated collection with no tie-breaker; no max page size. **Collapse: a non-collection API has no pagination — don't false-revise.**
- **Finding:** *revise — Pagination (cond. 7), §3 `GET /v1/invoices`: returns all invoices with no pagination + no max page size. Fix: add cursor pagination (`limit` + `cursor`, `next_cursor`/`has_more`, default 20 / max 100) + a stable sort tie-breaker on `id`.*

## cond-8 — Examples present + consistent
- **Pass:** ≥1 request/response pair per primary operation, consistent with the schemas (field names/types/status/error shape).
- **Gap:** an example with a field the schema lacks, a wrong type, a wrong status, or a non-shared error body.
- **Finding:** *revise — Examples consistent (cond. 8), §8: the create-invoice example returns `"amount": "5000"` (string) but the `Invoice` schema declares `amount` an integer, and shows `200` where the schema says `201`. Fix: align the example to the schema (integer, `201`).*

## cond-9 — Naming + versioning consistent *(surface-uniformity only)*
- **Pass:** the naming convention + versioning scheme applied uniformly across the surface.
- **Gap:** mixed casing/pluralization across operations; the versioning scheme applied unevenly. **Do not re-litigate cond-1 (policy presence) or cond-2 (per-op correctness) here — cond-9 is only surface-wide uniformity.**
- **Finding:** *revise — Naming consistent (cond. 9): operations mix `/invoices` (plural) and `/payment` (singular) and `snake_case` vs `camelCase` fields. Fix: apply one convention across the surface.*

## cond-10 — Grounded, honest & consistent
- **Pass:** operations/shapes reflect the feature-spec + data-model; assumptions explicit; no fabrication; one-directional vs the api-reference; consistent with the shipped API (verified `file:line`) where one exists.
- **Gap:** an invented field/limit/status/code; an operation reverse-engineered from the published api-reference; a documented operation contradicting the deployed surface. **Greenfield: no shipped API → consistency N/A, never a false-revise.**
- **Finding:** *revise — One-directional (cond. 10), §3: the contract documents `expand[]` query params that exist only in the published api-reference's examples, with no feature-spec behavior — the contract was reverse-engineered from the reference. Fix: derive operations from the feature-spec; the api-reference is downstream, never an input.*

## cond-11 — (Amend only) delta well-scoped + classified + ripple-clean + versioned
- **Pass:** the changed operations meet 1–10 on what they touched; the change is classified additive/breaking; a breaking change carries a new version + deprecation→sunset + migration guide; compatibility analyzed; the ripple flagged; version+changelog; deprecated-not-deleted.
- **Gap:** an un-scoped delta; a breaking change mis-classified as additive (or edited in place under the same version); an un-flagged ripple; a silent deletion. **Greenfield first build → n/a (don't demand a changelog).**
- **Finding:** *revise — Amend (cond. 11): the change renames `amount`→`amountMinor` (breaking) but edits it in place under `/v1` with no deprecation. Fix: route the breaking change to `/v2`, deprecate `/v1` (`Deprecation`→`Sunset` + migration guide), and flag the api-reference re-sync + client impact.*
