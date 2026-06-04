# Sources — authoring-release-runbook

Research provenance for the SRE/operational method and the executability/safety bar this skill prescribes. Method: `deep-research` primary + WebSearch corroboration; ≥2 reputable sources per structural/operational claim; Google SRE is the tier-1 anchor for verification + rollback. The shared dossier (`release-runbook-dossier.md`, persisted alongside the design records) carries the full evidence and is single-sourced across the authoring + reviewing pair.

## Canonical section set + verification gates

- AWS Well-Architected, Reliability Pillar — REL08-BP01 "Use runbooks for standard activities such as deployment" (runbooks for deployment: prerequisites, ordered steps, verification, rollback).
- OneUptime — "How to Create Effective Runbooks" / "How to Build Effective Runbooks" (metadata + pre-deploy checklist + specific/executable/verifiable steps + expected results + rollback).
- Upstat — "Runbook Templates and Examples" / "Complete Guide to Runbooks and Operational Procedures" (section set; rollback in reverse order; go/no-go decision points).

## Idempotency + copy-paste-safe steps

- OneUptime — copy-paste-ready commands with marked placeholders; "if you can't paste it, it's not production-ready".
- OneUptime — "How to Write Idempotent Docker Entrypoint Scripts" (guard one-time ops, IF NOT EXISTS, overwrite-not-append).
- Ansible Community Documentation — playbooks idempotency model.

## Rollback triggers + revert-per-change + re-verify

- Google SRE / Google Cloud SRE blog — "Reliable releases and rollbacks"; Google SRE workbook — "Canarying Releases" (measurable rollback criteria; automated rollback on SLO deviation; post-deployment monitoring window).
- AWS Well-Architected REL08-BP01 — every change-making runbook includes a rollback.

## Deploy strategies (deploy vs rollback per strategy)

- Unleash — "Comparing deployment strategies: Canary, blue-green, and rolling".
- Octopus Deploy — "Blue/green Versus Canary Deployments".
- Google SRE workbook — "Canarying Releases" (canary % traffic, bake, ramp, localized rollback).

## Secrets by reference

- Azure Key Vault / Azure Automation runbook secret-management guidance (reference the vault/secret name, never inline; SecureString; managed identity).
- DEV Community — "Node.js Secret Management in Production: Vault, AWS Secrets Manager, and Zero-Leakage Patterns" (secrets never in committed/deployed/logged files; reference names, not values).

## On-call / escalation + monitoring pointers

- PagerDuty — escalation-policy + severity-level guidance; analytics-dashboard docs (severity ladder, response budget, dashboards linking runbooks).

> All sources are secondary engineering references corroborated ≥2 per claim, with Google SRE as the tier-1 anchor for verification + rollback. Project-specific commands, hosts, and endpoints are NOT sourced here — the skill requires those be traced to a handed-in upstream or flagged as an explicit assumption, never fabricated.
