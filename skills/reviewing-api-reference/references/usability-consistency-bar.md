# Usability + contract-consistency bar — per-condition signals — `reviewing-api-reference`

Detailed pass/gap signals + worked findings for the 11-condition bar (SKILL.md Step 2). The bar is single-sourced with `authoring-api-reference`. Load when you need the detailed signal for a condition. Order findings by severity; cond. 5 drift / fabrication first of all.

## The load-bearing dimension — cond. 5 (consistency with the api-spec)

This is the check the gate exists to enforce; never skip it. Spot-check the documented endpoints, parameters, shapes, events, and errors against the **handed-in api-spec** one-to-one:

- **Orphan / fabricated endpoint** — the reference documents an operation the contract doesn't declare → gap. *Finding:* name the endpoint + "the handed-in api-spec declares no such operation; remove it or flag back to the api-spec author."
- **Contradiction** — a field type / required-flag / error code / auth scheme that disagrees with the contract → gap.
- **Missing operation/event** — a contract operation absent from the reference → gap (also cond. 2).
- **Hand-retyped generated catalog** — a manually-maintained duplicate of an OpenAPI-generated catalog → gap (a drift hazard); the generated catalog staying current is fine.
- If the **api-spec was not handed in**, flag cond. 5 as partially un-runnable (an assumption) and judge the rest — never default to approve.

## Deepened conditions — the added signals

### cond. 1 — first call reachable (auth-flow depth)
Pass: getting-started + auth reach one working call copy-paste; the auth section names the scheme/flow (API key / Authorization-Code / Client-Credentials / PKCE), where to get + how to send credentials, and shows the `401`/`403` failure. Gap: scheme/flow unnamed; no failure case; onboarding requires guessing.
*Worked finding:* "revise — cond. 1, Authentication: the section says 'authenticate with OAuth' but never names the flow, the token endpoint, or the scopes, and shows no `401`. A developer can't obtain or send a credential. Fix: name the flow (e.g. Client-Credentials), the token request, the scope, and the auth-failure response."

### cond. 3 — errors first-class (Problem Details)
Pass: one consistent error shape (RFC 9457 `application/problem+json` or the API's own) + a machine-readable `code` distinct from the HTTP status + a status-code table (cause+remedy) + per-endpoint error rows + semantically-correct statuses. Gap: only-2xx; generic errors with no per-endpoint rows; wrong status class (a 400 where 429/409/410 is correct).
*Worked finding:* "revise — cond. 3, `POST /v1/charges`: documents the `201` body but no failure responses. Fix: add the error rows the contract lists (`402 card_declined`, `409 idempotency_conflict`) + reference the shared error shape."

### cond. 4 — rate limits + idempotency
Pass (for an API that limits / accepts writes): the limit, `429`, `Retry-After`, `RateLimit-*` (noting they're replaced by `Retry-After` on a 429), backoff + jitter, idempotency keys. Gap: a limiting API leaves this undocumented. Proportional: a non-limiting read-only API omits it.

### cond. 7 — versioning + deprecation/sunset
Pass: how versions are expressed + pin/upgrade + breaking-change definition + a dated changelog; for any deprecated surface, the Deprecation/Sunset mechanics (`410 Gone` after sunset) + a migration path/guide. Gap: versioning silent for an API that versions; a deprecated endpoint with no migration path. Proportional: a v1-only API with nothing deprecated has a thin section.
*Worked finding:* "revise — cond. 7, `GET /v1/charges/legacy`: marked deprecated but no sunset date and no migration target. Fix: state the sunset date + link the replacement (`GET /v1/charges`)."

## New conditions

### cond. 10 — pagination / list-operation conventions (proportional)
Checked STRUCTURALLY for an API with **list operations**: the model (cursor/offset), standard param names, response metadata (`has_more`/`next_cursor`), a default + a documented **max** page size, the last-page signal, and a **stable tie-broken sort** (unique secondary key). Gap: a listing API leaves the model / max / tie-breaker undocumented. **n/a** for a non-listing API — do not manufacture it. Not a subjective "is the pagination elegant" judgment.
*Worked finding:* "revise — cond. 10, `GET /v1/widgets`: documents `limit` but no max page size and no stable-sort tie-breaker, so ordering is non-deterministic across pages. Fix: document the max + the secondary sort key (e.g. `created` then `id`)."

### cond. 11 — amend (delta-scoped; only on an amendment)
Active only when handed a change request / changed-contract delta (the input signal). Review the **delta**: changed blocks meet the bar; the delta re-syncs to the changed api-spec (cond. 5 on the delta); samples re-synced (cond. 6 — no stale sample); deprecation/migration documented where an endpoint changed/was removed (cond. 7); the doc's own version + amend-log updated (distinct from the API changelog). NOT a full re-review. **n/a on a greenfield first build.**
*Worked finding:* "revise — cond. 11, Charge object: the api-spec added `currency` and it's in the field table, but the worked response example and the Python sample omit it (stale samples). Fix: re-sync the Charge examples + samples (cond. 6); add the amend-log row."

## Proportionality + no-invented-conditions (the guard)

- A thin / proportionally-sized reference is **approved** when every *applicable* condition passes — pagination (cond. 10), rate-limits (cond. 4), webhooks, deprecation (cond. 7), amend (cond. 11) all legitimately collapse where they don't apply. Manufacturing a gap from brevity is the dominant reviewer error.
- The **API-style overlays** (REST/GraphQL/gRPC/webhooks/streaming) and the **webhook-documentation technique** are authoring AIDS — judged via cond. 2 (every operation/event documented), cond. 3 (signature/failure first-class), cond. 5 (traces to the contract), never a demand for a named section.
- The **rendered-docs-site features** (full-text/AI search, an interactive try-it / API explorer / Postman collection, accessibility/i18n) are **out of scope** for the markdown reference — never a revise trigger.
- Conditions 2 and 5 bind at **any** size: every contract operation/event present, everything traced to the contract.
