# Failure modes, cross-cutting, testing, rollout, amend — sections 7–12

Depth for the SKILL.md Step-4 method (sections 7–11) and Step-6 (amend). Load
when filling a TDD's failure/observability/testing/rollout/changelog sections
or amending an approved TDD.

## Error handling + failure modes (FMEA-style)

A flow that never fails isn't designed — this is where implementation bugs
hide. Enumerate each significant failure and, for **each**, give three things:

- **Detection** — how the system notices it (a timeout, a validation failure,
  a non-200, a checksum mismatch).
- **Handling / recovery** — the designed response (retry with backoff, fail the
  job + discard the partial, fall back, surface a retryable error).
- **User-visible effect** — what the caller/user sees.

Cover at least: invalid/malformed input, dependency failure or **timeout**, and
**partial failure** mid-operation. State the **retry / timeout / idempotency**
stance explicitly. A failure listed without its handling is not done. A table
(`Failure mode | Detection | Handling/recovery | User-visible effect`) keeps it
auditable.

## Cross-cutting concerns

### Security & privacy

- Security surface: new authn/authz, secrets handling (**reference the secret
  store — never inline a secret/token/key in the doc**), external calls,
  destructive actions, untrusted input.
- Privacy surface: PII the feature touches, retention, data classification,
  regional constraints.
- State the mitigation where there is a surface; mark **N/A** where there isn't
  (proportional).

### Observability (first-class — not "add logging later")

A production-grade feature is observable, not merely functional. Name the
concrete signals across the three pillars, scaled to the feature:

- **Metrics** — a success/throughput metric + an error/failure metric (with a
  reason label), and a latency/lag metric where load-bearing.
- **Logs / traces** — the key log line or trace span for the dominant path and
  the dominant failure.
- **Alerts** — the alert on the dominant failure mode (a threshold, e.g.
  "failure rate > 5% over 5m").
- These signals **arm the rollback triggers** (section 11) — the alert
  threshold and the rollback trigger are the same number. "We'll add metrics
  later" leaves a feature you can't operate or safely roll back.

## Testing approach

- State the verification in testable terms across the levels the feature needs:
  **unit** (the core logic + edge cases), **integration** (the real
  collaborators / the port boundary), **end-to-end** (the user-visible path).
- **Cover the failure cases from section 7**, not just the happy path.
- **Contract conformance** — for any contract the feature exposes (an API, an
  event, a schema delta), state how conformance is checked (contract tests,
  schema validation).
- **Reference** the feature-spec's acceptance criteria as the coverage
  checklist rather than restating them (same SSOT discipline as interfaces).

## Rollout, migration, rollback

- **Rollout** — how it ships: phasing / feature-flag / canary / dark-launch;
  name the enablement mechanism. A risky change gets a phased or flagged path,
  not an implied big-bang.
- **Migration + backward-compat** — where the feature changes persisted data or
  a contract: the migration path (dual-write / backfill / expand-contract) and
  how old + new coexist during rollout. N/A for a purely additive feature.
- **Rollback** — a documented **revert** plus the **measurable triggers** that
  fire it (an error-rate or latency threshold tied to the observability
  signals — not "roll back if it looks bad"). The feature flag is usually the
  fastest rollback lever.
- Close with residual risks + open questions.

## Amend — the versioned delta procedure (Step 6 depth)

An approved TDD is a living document; its most common operation is a **delta**,
not a rewrite. Procedure:

1. **Scope** the change to the affected design **decision(s)** — a component
   responsibility / an interface-contract delta / a failure-mode + handling / a
   rollout step / an alternative+criterion. Edit those in place; leave the rest
   (preserves the review history and stable decision IDs).
2. **Re-make the internal chain** for what you touched: the changed decision
   still traces to a requirement; its failure-modes / observability / testing /
   rollout still hold; the alternatives-criterion still settles the choice.
3. **Analyze the bidirectional + SSOT ripple:**
   - **Upstream** — if a changed requirement drove the change, the
     **PRD/feature-spec is amended first** (doc-before-downstream order). A
     decision with no upstream requirement after the change is newly orphaned.
   - **Internal** — the re-made chain in step 2.
   - **Downstream + SSOT** — if the change touches a contract, the **api-spec /
     data-model that OWNS it needs its own amendment** (the TDD only states the
     delta — the source of truth lives there), and the impl / test-plan /
     release-runbook built from the TDD are re-pointed.
4. **Version + changelog** — bump the produced doc's own version (distinct from
   any code/skill version) and add a changelog entry: who / when / what / why.
5. **Mark superseded** decisions (status: superseded-by … + a reciprocal note),
   don't silently delete them — a reader can see what changed and why.
