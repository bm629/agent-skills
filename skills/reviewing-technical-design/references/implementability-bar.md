# Implementability bar — the 11 conditions expanded

Per-condition pass/gap signals + a worked finding, for the SKILL.md Step-2
checklist. Load when a borderline condition needs a sharper call. Each
condition is single-sourced with `authoring-technical-design`'s Step-5.

## cond-1 — Requirement trace (bidirectional)

- **Pass:** the requirements are listed (an RTM-style trace) and every
  non-trivial design decision cites the requirement behind it; every
  requirement has a design element.
- **Gap:** an **orphan decision** (a component / interface / behavior with no
  requirement = scope creep), an **uncovered requirement** (a feature-spec
  criterion with no design = coverage gap), or traceability you cannot
  reconstruct.
- **Worked:** *revise — cond-1, §3: the design adds a `RetryScheduler` component
  but no requirement asks for retry; either trace it to a reliability
  requirement or cut it (scope creep).*

## cond-2 — Altitude / one-feature scope

- **Pass:** decisions are at feature/component scope; system-wide structure is
  referenced (architecture-doc), not redesigned.
- **Gap:** the TDD re-decides the datastore, the service boundaries, or a
  platform-wide choice — architecture work at the wrong altitude.
- **Worked:** *revise — cond-2, §3: the doc re-designs the message-bus topology;
  that is architecture-doc scope. Reference it and design only this feature's
  use of it.*

## cond-3 — Approach + decomposition implementable

- **Pass:** a short overview; single-responsibility components + collaborators
  concrete enough to build; the primary flow shown as a diagram **and** a
  numbered narration that agree.
- **Gap:** a god-component, a box labelled only with the feature name, no flow
  diagram, or a diagram that contradicts the prose (diagram/prose drift).
- **Worked:** *revise — cond-3, §4: the sequence diagram shows a cache lookup the
  narration never mentions; sync them or the reader can't tell which is right.*

## cond-4 — Reference-not-duplicate (SSOT)

- **Pass:** contracts an api-spec/data-model/architecture-doc owns are
  referenced with only the delta stated.
- **Gap:** an inlined endpoint list, table DDL, or topology that an owning doc
  holds — guaranteed future drift. (Load-bearing — a real gap, not a nit.)
- **Worked:** *revise — cond-4, §5: the full `users` table DDL is pasted from the
  data-model. Reference `data-model §Users` and state only the new
  `last_export_at` column this feature adds.*

## cond-5 — ≥1 real alternative + decision criterion

- **Pass:** a genuine alternative compared via trade-offs, with the criterion
  that settled the choice stated.
- **Gap:** a single un-weighed option, a strawman ("do nothing / rewrite
  everything"), or a choice settled by assertion with no criterion.
- **Worked:** *revise — cond-5, §9: only the chosen approach is described.
  Compare a real alternative (e.g. buffering vs streaming) and state the
  criterion that ruled it out (e.g. bounded memory under the 10k-row target).*

## cond-6 — Failure modes + cross-cutting robustness

- **Pass:** each significant failure carries detection + handling/recovery +
  user-visible effect; concurrency/idempotency stance named where relevant;
  security/scale/privacy addressed where the feature has a surface.
- **Gap:** a happy-path-only design, a failure listed with no handling, or an
  unaddressed security/data surface the feature clearly has.
- **Worked:** *revise — cond-6, §7: "dependency timeout" is listed with no
  handling. State the detection (the 5s timeout), the recovery (fail the job,
  discard the partial), and the user-visible effect (a retryable error).*

## cond-7 — Observability

- **Pass:** the health/failure signals are named (a success/error metric, the
  key log/trace, the alert on the dominant failure mode); they arm the
  rollback triggers.
- **Gap:** "we'll add logging later" on a production feature, or a cond-9
  rollback trigger with no signal behind it.
- **Worked:** *revise — cond-7, §8.2: no signals are named, yet §11 rolls back on
  "high error rate". Define the metric (e.g. `export_failures_total`) and the
  threshold that is both the alert and the rollback trigger.*

## cond-8 — Testing

- **Pass:** the strategy names the levels (unit/integration/e2e) the feature
  needs, covers the cond-6 failure cases, and states contract conformance for
  any exposed contract; references the feature-spec AC.
- **Gap:** "we'll test it", a strategy that omits the failure cases, or an
  exposed contract with no conformance check.
- **Worked:** *revise — cond-8, §10: only the happy path is tested. Add the
  timeout + partial-failure cases from §7 and a contract test for the new
  `format=csv` response.*

## cond-9 — Rollout / migration / rollback

- **Pass:** rollout phasing/flag named; migration + backward-compat where
  data/contract changes; rollback with **measurable** triggers (tied to cond-7).
- **Gap:** an implied big-bang for a risky change, a data/contract change with
  no migration, or a rollback with no measurable trigger ("roll back if it
  looks bad").
- **Worked:** *revise — cond-9, §11: a backfill is required but no migration path
  is given. State the expand-contract / dual-write plan and how old + new
  coexist during rollout.*

## cond-10 — Assumptions explicit + grounded, not fabricated

- **Pass:** unknowns surfaced as assumptions/open-questions; the design
  reflects the real system; nothing invented to look complete.
- **Gap:** the design reads as falsely complete, or asserts a limit/interface/
  approach with no upstream or research behind it (fabrication).
- **Worked:** *revise — cond-10, §6: the doc states "the queue holds 10k items"
  with no source. Trace it to a requirement/constraint or flag it as an
  assumption to validate.*

## cond-11 — (Amend only) delta well-scoped, ripple-clean, versioned

- **Active only** when handed a change request against an existing TDD
  (the input signal). On a greenfield first build it is n/a.
- **Pass:** the delta meets cond-1–10 on the changed decisions; still traced
  (or an upstream-amend flagged); the SSOT ripple handled (owning
  api-spec/data-model amend + downstream re-point named); version bumped +
  changelog; superseded decisions marked.
- **Gap:** an un-scoped delta, a broken trace, an un-flagged SSOT ripple,
  missing change history, or a silent deletion.
- **Worked:** *revise — cond-11: the amendment changes the `/export` response
  shape but doesn't flag that api-spec §Reports (the owner) needs its own
  amend, nor bump the doc version. Scope the delta, name the api-spec ripple,
  add the changelog entry.*

## Proportionality reminder

A thin feature collapses inapplicable conditions (no migration, no concurrency,
no separate observability, no exposed contract, no changelog). Judge
completeness-of-decisions, not section count. Non-collapsing baselines:
cond-1 (backward trace), cond-2 (altitude), cond-5 (real alternative),
cond-6 (failure-carries-handling), cond-10 (no fabrication).
