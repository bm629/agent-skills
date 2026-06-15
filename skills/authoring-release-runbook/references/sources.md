# Sources — authoring-release-runbook

Research provenance for the SRE/operational method and the executability/safety bar this skill prescribes. Method: `deep-research` primary + WebSearch corroboration; ≥2 reputable sources per structural/operational claim; Google SRE is the tier-1 anchor for verification + rollback. This bar is single-sourced across the authoring + reviewing pair (the reviewer's 11-condition checklist asserts the same bar this skill produces to).

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

## Stateful-change safety — expand-contract + roll-forward (cond-10)

- Pete Hodgson — "expand/contract: making a breaking change without a big bang" (parallel-change, backward-compatible, independently rollbackable steps).
- Tim Wellhausen — "Expand and Contract" (zero-downtime breaking changes to persistent data).
- PlanetScale — "backward-compatible database changes" (backward-compatible-first; rollback without data loss).
- Redgate Flyway — "failed deployments: roll back or fix forward?"; Hokstad — "rollback vs rollforward"; SQLServerCentral — "rollback vs roll forward" (irreversible change → roll-forward / containment / restore-from-backup).

## SLO burn-rate triggers + progressive-delivery rollback levers (cond-2/cond-4)

- Google SRE workbook — "Alerting on SLOs" (multi-window, multi-burn-rate); OneUptime — "burn-rate alerts".
- LaunchDarkly — "why decouple deployments from releases"; Unleash — "progressive delivery with feature flags"; AB Tasty — "dark launch" (the flag-flip as a near-instant localized rollback lever).

## Living document — amend + rehearsal + comms (cond-9/cond-11)

- Rootly — "incident-response runbooks"; Cortex — "what is a runbook"; incident.io — "automated runbooks" (version-controlled, post-incident-hardened living document).
- Octopus — "deployment checklist"; Games24x7 — "the importance of a production dry run"; getDX — "production readiness checklist" (rehearse in staging; inject failures; "Last validated").
- Microsoft Learn — "planned maintenance window FAQ"; Datadog — "status pages"; OneUptime — "scheduled maintenance" (notify ahead / status-page the window / restored-notification, per-channel owners).

> All sources are secondary engineering references corroborated ≥2 per claim, with Google SRE as the tier-1 anchor for verification + rollback. Project-specific commands, hosts, and endpoints are NOT sourced here — the skill requires those be traced to a handed-in upstream or flagged as an explicit assumption, never fabricated.
