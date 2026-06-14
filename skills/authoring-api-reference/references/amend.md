# Amending a reference — the upstream-driven re-sync — `authoring-api-reference`

Depth for SKILL.md Step 7. Load when amending an existing reference. The api-reference is the most living document in the doc corpus, and its amend has a signature shape that differs from other document types.

## Why the api-reference amend is distinctive — RE-SYNC, not redraft

The dominant amend trigger is the **upstream api-spec contract changing** — a new endpoint, a changed parameter/field/type, a new error code, a removed/deprecated operation, a new event. Unlike a doc whose amend is internally motivated, the api-reference's amend is overwhelmingly a **re-sync**: the contract moved, so the reference must move with it or it **drifts** (the highest-impact defect — the cond-5 failure). The amend operation is "re-derive the affected blocks and re-run the consistency check on the delta," plus the API's own **deprecation→sunset lifecycle**.

**Scope unit:** an endpoint / parameter / field / error code / auth scheme / shared object type / event / version entry.

## The amend procedure

1. **Scope the change.** Identify exactly which endpoints/fields/errors/events/auth the contract change touches. Edit **those blocks**; preserve the unchanged catalog (edit-not-redraw).
2. **Re-sync against the changed contract.** Re-run the consistency check (cond-5) on ONLY the changed blocks: every changed/new endpoint/field/error now traces to the changed api-spec; a removed contract operation is removed (or marked deprecated — step 4). If editing reveals a contract GAP (the docs need an operation the contract doesn't declare), **flag it back to the api-spec author** — never fabricate the endpoint into the reference.
3. **Propagate the internal ripple:**
   - **Shared objects** — a changed field shape → update the core-objects entry AND every endpoint/event that references it.
   - **Samples + worked examples** — re-check every worked request/response + code sample touched by the change against the new schema. A sample left stale after a schema change is a defect (it looks runnable but won't run).
   - **Per-endpoint error rows + the index/navigation.**
4. **Handle the deprecation→sunset lifecycle.** A removed/changed endpoint is marked **deprecated** (not silently deleted): the `Deprecation` header (RFC 9745 — boolean or the announce timestamp) + the `Sunset` header (RFC 8594 — when it stops responding) + a **sunset date** + a **migration guide / replacement link** (`Link` header). Keep it documented through the deprecation window; remove only after sunset (the contract may then return `410 Gone`). A breaking change with no migration path is a gap.
5. **Version + amend log.** Bump the **reference document's own** version header + add a who/when/what/why amend-log row; mark superseded/removed content.

## Three distinct version lines (do not conflate)

| Line | What it tracks | Who reads it |
|---|---|---|
| **API changelog** (a reference section) | what changed in the **API surface** (endpoints added, params changed, deprecations + sunset dates) | the integrating developer, to plan upgrades |
| **Doc amend log** (the reference's own revision history) | how this **document** changed (who/when/what/why) | the doc maintainer |
| **Skill / tooling version** | the authoring/reviewing skill's semver | the skill maintainer |

An amendment bumps the **doc version + amend log** and (if the API changed) adds an **API changelog** row. They are not the same field.

## Worked amend example

*Contract change:* the api-spec adds an optional field `currency` (string, ISO-4217, default `USD`) to the `Charge` object and deprecates `GET /v1/charges/legacy` (sunset in 90 days, replaced by `GET /v1/charges`).

*Correct amend:*
1. Scope = the `Charge` core-object + every endpoint returning a Charge + the legacy endpoint block.
2. Add `currency` to the core-objects `Charge` entry (typed, default), confirm it traces to the changed contract.
3. Update the worked response examples that show a Charge to include `currency`; re-check the code samples.
4. Mark `GET /v1/charges/legacy` **deprecated** with `Sunset: <date>` + a migration note/link to `GET /v1/charges`; keep it documented through the window.
5. Bump the doc version + amend-log row ("2026-06-14 — added `Charge.currency`; deprecated `GET /v1/charges/legacy`, sunset 2026-09-12, migrate to `GET /v1/charges`"); add the API changelog row.

*Wrong amend (would be a revise):* the field added to the docs but the response examples/samples left without `currency` (stale samples); or the legacy endpoint silently deleted with no migration note; or a brand-new field invented that the changed contract doesn't actually declare (fabrication).

## What the reviewer checks on an amendment (cond-11, delta-scoped)

The reviewer, handed the change request / changed-contract delta, reviews the **delta only**: the changed blocks meet the bar; the delta re-syncs to the changed api-spec (cond-5 on the delta); samples re-synced (cond-6); deprecation/migration documented where an endpoint changed/was removed (cond-7); the doc-amend metadata present (doc version bumped + amend-log row); ripple-clean. NOT a full re-review of the unchanged catalog. On a greenfield first build no change request is handed in, so cond-11 is n/a.
