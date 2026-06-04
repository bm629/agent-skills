# reviewing-release-runbook

Judge a **finished release runbook** and decide whether an engineer unfamiliar with the system can execute the deploy, confirm it, and roll back from it alone — an acceptance gate, not authoring. The review half of the release-runbook pair; single-sources its bar from the same dossier as `authoring-release-runbook`.

## Purpose

The release runbook is the go-to-production procedure a deploying or on-call engineer follows to ship a system safely. This skill is the gate that decides whether it's good enough: it judges the runbook against an **executability + safety bar** and emits a machine-parseable verdict, so produce -> review -> accept can run as a loop.

## When to activate

- Judging a finished/draft release runbook before it's accepted.
- The review step of a produce->review->accept document loop.

### When NOT to activate

- **Authoring a release runbook** -> `authoring-release-runbook` (the producer revises on findings).
- **The QA test-plan** -> `reviewing-test-plan`.
- **The CI/CD pipeline config** -> a separate automation concern, not this.
- **Engineering design docs** (ADR/RFC) -> `design-review`.

## The executability + safety bar

Judges each, pass/gap: the runbook is **executable** by an engineer unfamiliar with the system (no ambiguous prose; steps copy-paste-safe + idempotent); **every step has an expected result/verification**; a **go/no-go gate** is present; the **rollback is complete + safe** (a documented revert for EVERY forward change, with measurable trigger conditions, and re-verification) — the load-bearing check; **post-deploy verification** reuses concrete checks (the test-plan exit criteria where handed in); **escalation + monitoring pointers are concrete**; **no secret/credential is inlined** (an embedded token/key is a finding — it must reference its store); commands/hosts are **accurate**, spot-checked against the handed-in upstreams (un-verifiable ones flagged, not assumed correct). Single-sourced from the shared dossier so the produce-bar and review-bar match.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + how to fix). **Approves** a runbook that meets the bar — no false-revise — and **revises** only on a real, named gap (e.g. a deploy step with no verification, a forward change with no revert, an inlined secret).

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the runbook.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Rollback-completeness is load-bearing** — a forward change without a documented revert is always a finding.
- **No inlined secret** — an embedded credential is always a finding.
- **No false-revise** — approves an executable, safely-rollback-able runbook even if stylistically improvable.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
