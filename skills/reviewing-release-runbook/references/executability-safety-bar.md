# The 11-condition executability + safety bar (depth)

Per-condition pass/gap signals + worked findings for the conditions where calibration is hardest — the deepened (2, 4) and the new conditional (9, 10, 11) ones. Conditions 1, 3, 5, 6, 7, 8 are judged as in the SKILL.md Step-2 list. Single-sourced with `authoring-release-runbook`.

## cond. 2 — Per-step verification (deepened: burn-rate basis)

- **Pass:** every step states an expected result + a measurable check — a raw threshold (`HTTP 200`, version served, error rate < 0.5%, p99 < 200ms) **or** an SLO error-budget burn-rate within bounds.
- **Gap:** a step has no expected result, or the check is non-measurable ("looks fine", "feels healthy").
- **Not a gap:** using a raw threshold instead of a burn-rate (or vice versa) — both are accepted measurable forms. Never demand a burn-rate.

## cond. 4 — Complete + safe rollback (deepened: levers + strategy-match + burn-rate trigger)

- **Pass:** a documented revert for EVERY forward change, reverse order, with a measurable trigger; the revert **lever matches the strategy** (blue-green = cut traffic back; canary/rolling = route 0% / scale down; recreate = redeploy old; feature-flagged = flip off); re-verify to baseline.
- **Gap:** "roll back the deploy" with no per-change revert; a forward change with no revert; a vague/absent trigger; **a lever that doesn't match the strategy** (e.g. "redeploy the old artifact" for a blue-green deploy whose actual rollback is a traffic cut); no re-verify.
- **Accepted (not a gap):** a flag-flip or an automated canary-rollback as the lever; a burn-rate as the trigger. The completeness bar is unchanged — only the accepted vocabulary widens.

## cond. 9 — Delta-scoped amend (new; conditional on an amend input)

Applies ONLY when reviewing a change/delta against an existing runbook. On a greenfield first build → **n/a**.

- **Pass:** the delta is in-scope (edit-not-rewrite); it addresses its trigger (an upstream change re-derived OR a post-incident learning turned into a rollback trigger / verification gate / corrected step); the changed steps meet the applicable binding conditions (1/2/4 + 7/8); the amend **addresses re-validation** — the procedure is re-checked end-to-end for a broken downstream precondition AND "Last validated" is refreshed OR re-validation is flagged pending; the change history is present (runbook-version bump + changelog + superseded).
- **Gap:** the amend regenerates the whole runbook; an edit broke a later step's precondition (a renamed env / reordered migration / changed endpoint a downstream step still assumes); a new forward change has no revert; re-validation is ignored entirely; no change history.
- **NOT a gap (the dominant amend error to avoid):** re-litigating the unchanged runbook; revising because the dry-run wasn't re-run or "Last validated" wasn't freshly dated when re-validation is explicitly flagged pending. Rehearsal is an aid, never a gate.
- *Worked finding:* "**revise** — cond. 9: the amend renamed the target env in Step 3.1 but Step 4.2 still curls the old host (broken downstream precondition). Fix: re-validate end-to-end, update Step 4.2, bump the runbook version + changelog the trigger."

## cond. 10 — Stateful-change safety (new; proportional)

Applies ONLY when the release changes a schema or data. No schema/data change → **n/a, no gap**.

- **Pass:** a schema/data forward change is reversible/backward-compatible (an expand-and-contract / parallel-change sequence — add-alongside, migrate, contract-later) OR names a stated recovery path for an irreversible change (roll-forward / containment / restore-from-backup).
- **Gap:** a breaking schema change ships with no backward-compatible sequencing AND no stated recovery path — most often a `DROP`/destructive transform whose "rollback" is a down-migration that cannot recover the dropped data (a phantom revert).
- **Judged by outcome:** the expand-contract *pattern name* is never demanded — a single additive backward-compatible migration passes with no phasing.
- **Overlap with cond. 4 is intentional:** a catastrophic migration defect may surface under both cond. 4 (a forward change with no revert) and cond. 10 (an irreversible stateful change with no recovery path) — cite both if you like, but it is one fix.
- *Worked finding:* "**revise** — cond. 10: Step 3.2 `DROP COLUMN legacy_total` is irreversible but the rollback runs a down-migration that can't restore the data. Fix: sequence expand-contract (stop writing it now, drop later) or name the recovery path (restore-from-backup `<location>`)."

## cond. 11 — Comms / maintenance-window (new; proportional)

Applies ONLY when the deploy is user-impacting. Internal / zero-user deploy → **n/a, no gap, say nothing**.

- **Pass:** a user-impacting deploy names its comms/maintenance-window plan (notify ahead / status-page the window / restored-notification, with a per-channel owner).
- **Gap:** a clearly user-impacting deploy (downtime / a customer-facing change) carries no comms plan at all.
- **NOT a gap:** an internal cron-job/back-office deploy with no users and no comms plan — that is correct sizing. Flagging it is a false-revise.

## The proportional-collapse discipline (the load-bearing guard)

Conditions 9, 10, 11 are **conditional** — each collapses to n/a where it doesn't apply. The dominant reviewer error on this pair is now **false-revising a thin runbook** for a conditional condition it never triggered (a migration-safety section on a stateless deploy, a comms plan on an internal tool, a re-dry-run on an amend). Calibrate: a gap is only a *named, real* deficiency in an *applicable* condition.
</content>
