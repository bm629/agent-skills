# Amend procedure, pre-prod rehearsal & comms (depth)

Depth for the SKILL.md Step-7 amend method + the dry-run and comms aids. Load when amending an existing runbook or planning a user-impacting deploy.

## The amend procedure (Step 7 depth)

A release runbook is a **living, re-run, incident-hardened** document. It is amended whenever the system it deploys changes OR an incident teaches it something.

### Property 1 — the TWIN trigger

1. **An upstream change** — the architecture-doc deploy topology, the technical-design rollout/migration, or the test-plan exit criteria changed → re-derive the affected deploy/verification steps.
2. **A post-incident learning** — an outage exposed a gap in the *runbook itself*: a missing rollback step, an un-verified failure mode, a too-slow/missing trigger, an ambiguous step → the runbook is hardened (it gains a rollback trigger, a verification gate, or a corrected step). "Document every 'uh, what do I do now?' moment as a runbook update."

### Property 2 — the END-TO-END re-validation ripple (the signature)

A runbook is an **order-dependent executable procedure**. A changed step can silently invalidate a *later* step's precondition:

- a renamed/relocated environment breaks every later command that targets it;
- a reordered migration breaks a later verification that assumed the old order;
- a changed health endpoint breaks the post-deploy smoke and the rollback re-verify.

So the ripple is NOT "insert the new step and ship". It is: **re-check the whole procedure end-to-end** for a broken downstream precondition; **re-dry-run** where feasible; **refresh the "Last validated" date OR explicitly flag re-validation as pending** (re-rehearsal is an aid, never forced).

### The steps

1. **Scope** the change to the affected unit.
2. **Detect the trigger** (upstream change OR post-incident learning).
3. **Edit, don't rewrite** — amend only the affected steps.
4. **Re-validate end-to-end** — walk the whole procedure for a broken downstream precondition; re-dry-run where feasible (an aid, never forced); refresh the "Last validated" date OR flag re-validation pending.
5. **Confirm the bar on the delta** — the changed step meets the applicable binding conditions (executable + verified; any new forward change has a revert + trigger, an irreversible one a roll-forward path; no secret inlined; nothing fabricated).
6. **Version + changelog + supersede** — bump the runbook's own document version, add a changelog entry naming the trigger, mark the prior version superseded.

This is the bar the reviewer's cond-9 (delta-scoped amend) asserts; on a greenfield first build cond-9 is n/a.

## Pre-production rehearsal / dry-run (aid, never a gate)

"A runbook is only as good as its last rehearsal." Before the real run:

- Execute the entire runbook in a production-like staging environment (some teams 48–72h before, same time of day, real owners, no proxies).
- **Deliberately inject failures** ("simulation mode" / fire drill) to prove the *rollback* actually works — not just the happy-path deploy.
- Have an engineer outside the dev team follow the runbook to surface hidden assumptions — exactly the "unfamiliar engineer" bar, empirically.
- Record a **"Last validated"** date — the freshness signal that the runbook still matches the system.

Why an aid, not a gate: a first-ever runbook has never been rehearsed; gating on a rehearsal/last-validated date would false-revise a brand-new (correct) runbook. The reviewer judges the *executability the dry-run is meant to prove* (cond-1/2/4), not whether a dry-run happened.

## Maintenance-window / stakeholder comms (proportional)

A **user-impacting** production deploy carries a comms plan:

- Notify stakeholders ahead of the window (lead time varies — days for customer-facing).
- Post the maintenance window on the **status page** (planned-maintenance, distinct from an unplanned-incident degradation).
- Send a **restored** notification after.
- Assign **per-channel owners** (email / status page / in-app banner) for a complex window.

**Proportional** — a customer-facing service needs it; an internal tool or a zero-user service needs none (and the reviewer's cond-11 is n/a there, not a gap).

## Sources

- Living-document / version-controlled / post-incident hardening: Rootly "incident-response runbooks"; Cortex "what is a runbook"; incident.io "automated runbooks".
- Dry-run / rehearsal / inject-failures: Octopus "deployment checklist"; Games24x7 "the importance of a production dry run"; getDX "production readiness checklist".
- Maintenance window / status page / stakeholder comms: Microsoft Learn "planned maintenance window FAQ"; Datadog "status pages"; OneUptime "scheduled maintenance".
</content>
