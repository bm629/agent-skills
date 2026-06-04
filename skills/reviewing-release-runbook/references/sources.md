# Sources — reviewing-release-runbook

Research provenance for the **review method**. This is the *review* half of the release-runbook pair; its bar is **single-sourced** from the shared release-runbook dossier (`docs/superpowers/agent-flow/authoring-release-runbook/research/release-runbook-dossier.md`, section (b) — the standalone executability/safety quality bar), the **same eight conditions** the `authoring-release-runbook` producer writes to. The pair shares one dossier so the produce-bar and the review-bar do not drift. No new research was run for the reviewer; the conditions and their SRE/operational basis are reused from that dossier (method there: `deep-research` primary + WebSearch corroboration, >=2 reputable sources per claim, Google SRE as the tier-1 anchor for verification + rollback).

## The single-sourced bar (the eight review conditions)

- Shared release-runbook dossier, section (b) "Quality bar — standalone, reusable by `reviewing-release-runbook`" — the explicit pass/fail checklist this skill applies verbatim (executable by an unfamiliar engineer; per-step verification; go/no-go gate; complete + safe rollback with triggers; concrete escalation + monitoring; no inlined secrets; no fabrication; usable under release pressure).

## SRE/operational basis behind each condition (reused from the dossier)

- AWS Well-Architected, Reliability Pillar — REL08-BP01 "Use runbooks for standard activities such as deployment" (prerequisites, ordered steps, verification, rollback; every change-making runbook includes a rollback).
- Google SRE / Google Cloud SRE blog — "Reliable releases and rollbacks"; Google SRE workbook — "Canarying Releases" (measurable rollback criteria, automated rollback on SLO deviation, the post-deployment monitoring/bake window).
- OneUptime — "How to Create Effective Runbooks" (specific/executable/verifiable steps, expected results, copy-paste-ready commands with marked placeholders, rollback); "How to Write Idempotent Docker Entrypoint Scripts" (idempotency).
- Upstat — "Runbook Templates and Examples" (section set, rollback in reverse order, go/no-go decision points).
- Unleash — "Comparing deployment strategies: Canary, blue-green, and rolling"; Octopus Deploy — "Blue/green Versus Canary Deployments" (per-strategy deploy vs rollback shape, behind the strategy-mismatched-rollback gotcha).
- Azure Key Vault / Azure Automation runbook secret-management guidance; DEV Community — "Node.js Secret Management in Production" (secrets referenced by store/vault/env-var, never inlined into committed/deployed/logged files — the no-inlined-secrets condition).
- PagerDuty — escalation-policy + severity-level guidance; analytics-dashboard docs (the concrete escalation path + monitoring pointers condition).

## The reviewer-discipline basis

- The no-false-revise / no-false-approve calibration and the systematic-over-flagging gotcha follow the same reviewer-overcorrection discipline the document-skill library's other review gates apply (a reviewer asked to find problems tends to over-correct sound documents). Single-sourcing the bar from the dossier is the primary drift control.

> All upstream sources are secondary engineering references corroborated >=2 per claim in the shared dossier, with Google SRE as the tier-1 anchor for verification + rollback. This skill **judges**; it does not source project-specific commands/hosts/endpoints — the review requires those be traced to a handed-in upstream or flagged as an explicit assumption in the runbook, never assumed correct or fabricated.
