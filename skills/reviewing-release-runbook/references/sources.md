# Sources — reviewing-release-runbook

Research provenance for the **review method**. This is the *review* half of the release-runbook pair; its bar is **single-sourced** with the `authoring-release-runbook` skill — the **same eleven conditions** the producer writes to (its Step-6 + Step-7 self-check). The pair single-sources one bar so the produce-bar and the review-bar do not drift. The conditions and their SRE/operational basis are the same the author cites (method: `deep-research` primary + WebSearch corroboration, >=2 reputable sources per claim, Google SRE as the tier-1 anchor for verification + rollback).

## The single-sourced bar (the eleven review conditions)

- The same checklist the `authoring-release-runbook` producer writes to: (1) executable by an unfamiliar engineer; (2) per-step verification (a raw threshold or an SLO burn-rate); (3) go/no-go gate; (4) complete + safe rollback with measurable triggers + strategy-matched lever + roll-forward for an irreversible change; (5) post-deploy verification reusing the test-plan exit criteria; (6) concrete escalation + monitoring; (7) no inlined secrets; (8) no fabrication; (9) delta-scoped amend; (10) stateful-change safety (proportional); (11) comms/maintenance-window (proportional). Usable-under-release-pressure is the holistic lens, not a numbered condition.

## SRE/operational basis behind each condition (shared with the authoring twin)

- AWS Well-Architected, Reliability Pillar — REL08-BP01 "Use runbooks for standard activities such as deployment" (prerequisites, ordered steps, verification, rollback; every change-making runbook includes a rollback).
- Google SRE / Google Cloud SRE blog — "Reliable releases and rollbacks"; Google SRE workbook — "Canarying Releases" (measurable rollback criteria, automated rollback on SLO deviation, the post-deployment monitoring/bake window).
- OneUptime — "How to Create Effective Runbooks" (specific/executable/verifiable steps, expected results, copy-paste-ready commands with marked placeholders, rollback); "How to Write Idempotent Docker Entrypoint Scripts" (idempotency).
- Upstat — "Runbook Templates and Examples" (section set, rollback in reverse order, go/no-go decision points).
- Unleash — "Comparing deployment strategies: Canary, blue-green, and rolling"; Octopus Deploy — "Blue/green Versus Canary Deployments" (per-strategy deploy vs rollback shape, behind the strategy-mismatched-rollback gotcha).
- Azure Key Vault / Azure Automation runbook secret-management guidance; DEV Community — "Node.js Secret Management in Production" (secrets referenced by store/vault/env-var, never inlined into committed/deployed/logged files — the no-inlined-secrets condition).
- PagerDuty — escalation-policy + severity-level guidance; analytics-dashboard docs (the concrete escalation path + monitoring pointers condition).
- Pete Hodgson "expand/contract"; Tim Wellhausen "Expand and Contract"; PlanetScale "backward-compatible database changes"; Redgate Flyway "roll back or fix forward"; Hokstad "rollback vs rollforward" (cond. 10 stateful-change safety — expand-contract sequencing + the irreversible-change roll-forward/containment/restore recovery path).
- Google SRE workbook "Alerting on SLOs" (cond. 2/4 burn-rate basis); LaunchDarkly "why decouple deployments from releases"; Unleash "progressive delivery with feature flags" (cond. 4 flag-flip / canary rollback levers).
- Rootly / Cortex / incident.io (cond. 9 — runbook as a living, version-controlled, incident-hardened document); Octopus / Games24x7 (the dry-run/rehearsal + "Last validated" freshness signal — an aid, never a gate); Microsoft Learn / Datadog / OneUptime (cond. 11 — maintenance-window / status-page / stakeholder-comms).

## The reviewer-discipline basis

- The no-false-revise / no-false-approve calibration and the systematic-over-flagging gotcha follow the same reviewer-overcorrection discipline the document-skill library's other review gates apply (a reviewer asked to find problems tends to over-correct sound documents). Single-sourcing the bar with the authoring twin is the primary drift control.

> All upstream sources are secondary engineering references corroborated >=2 per claim across the pair's shared source set, with Google SRE as the tier-1 anchor for verification + rollback. This skill **judges**; it does not source project-specific commands/hosts/endpoints — the review requires those be traced to a handed-in upstream or flagged as an explicit assumption in the runbook, never assumed correct or fabricated.
