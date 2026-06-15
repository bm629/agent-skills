---
name: authoring-release-runbook
description: >
  Use when authoring or amending a release/deployment runbook: the
  go-to-production procedure for shipping a system to production safely.
  Guides the METHOD, not the outline: grounding it in SRE/operational
  practice, deriving deploy steps from the
  architecture-doc + technical-design rollout and verification from the test-plan
  exit criteria, writing idempotent copy-paste-safe steps each with an expected
  result, defaulting the deploy strategy to blue-green, sequencing a stateful
  change as a backward-compatible expand-contract migration (roll-forward if
  irreversible), giving every forward change a documented revert with
  measurable triggers, naming the comms window for a user-impacting deploy, and
  amending the living runbook as a versioned re-validated delta — to a bar where
  an unfamiliar engineer can deploy, confirm, and roll back from it alone, no
  secret inlined and nothing fabricated. Composes with a template tool +
  deep-research. Not the CI/CD pipeline config (cicd-plan), not a post-mortem,
  not reviewing one.
extensions:
  claude:
    when_to_use: "authoring or amending the production go-live runbook (deploy + verify + rollback + escalation) for a release"
    argument-hint: "<the release/version to ship (+ architecture-doc / technical-design / test-plan context)>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `authoring-release-runbook` — SKILL.md

> **Variant:** standard · **When to use:** authoring the go-to-production operational runbook for a release — to a bar an unfamiliar on-call engineer can execute the deploy, confirm it, and roll back from the runbook alone.

## Overview

This skill is the *how-to* of writing a strong release runbook — the operational procedure a deploying or on-call engineer follows to ship a system to production safely and verifiably. It is the broad operational go-live document: prerequisites and sign-offs, pre-deploy go/no-go checks, the ordered deploy procedure, post-deploy verification, the rollback procedure, and the on-call/escalation + monitoring pointers. This skill carries the producer's judgment — an **SRE/operational research method** and an **executability/safety bar** — **not** the section list. It assumes two collaborators: a **release-runbook template tool** that supplies the section *structure*, and a **deep-research capability** to ground the procedure in established practice. The producer is handed the upstream documents the plan determined inform this runbook (typically the **architecture-doc + technical-design + test-plan**) and must **derive a real, executable procedure** from them — never emit a generic skeleton. The bar to clear: an engineer who has never deployed this system can execute the release, confirm it succeeded, and roll back safely from the runbook alone, every step has an expected result and every forward change has a documented revert, no secret is inlined, and nothing is fabricated. A runbook is also a **living document** — re-run every release and hardened by every incident — so this skill covers **amending** it as a versioned, end-to-end-re-validated delta (Step 7), not only the first authoring.

## When to activate

- Authoring a production release/deployment/go-live runbook for a system or service.
- Documenting the manual + verification + rollback procedure *around* a deploy: prerequisites, go/no-go, ordered deploy steps, post-deploy smoke, rollback, escalation, and monitoring pointers.
- Filling a release-runbook template with researched, executable, upstream-derived content.
- **Amending** an existing runbook after an upstream change (a changed deploy topology / rollout / exit criteria) OR a post-incident learning (an outage exposed a missing rollback step / failure mode) — Step 7.

**Do NOT activate when:**

- Authoring the CI/CD pipeline automation itself (the build-test-deploy YAML/config) — that is a **cicd-plan**. The runbook *invokes* the pipeline and documents the procedure around it; it does not author the pipeline config.
- Writing an after-the-fact incident retrospective or post-mortem — the runbook is the **pre-planned** procedure (including rollback); the retrospective is written after an incident.
- Defining the QA scope, levels, coverage, or test-case catalog — that is a **test-plan**. The runbook *reuses* the test-plan's exit criteria for its post-deploy verification; it does not redefine the QA strategy.
- Authoring the architecture-doc / technical-design the runbook references — those are *upstream input* here.
- Reviewing or grading a finished runbook — use `reviewing-release-runbook` (the runtime gate, which asserts the same bar).

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this runbook's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive.

- **Derive the deploy steps** from the architecture-doc's deployable components/services + the deploy topology, and the technical-design's rollout/migration specifics.
- **Derive the verification** from the test-plan's exit/done criteria — the post-deploy smoke reuses them.
- Be **self-contained and graceful** — produce the runbook from *whatever* context you actually receive; when an expected upstream (e.g. an observability/monitoring pointer, or the test-plan) is absent, proceed on what you have and surface the gap as an **explicit assumption** — never fabricate a command, host, or endpoint to fill it.
- **Use a research capability where one is available** (deep-research) to ground the runbook in established SRE/operational practice, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your release-runbook template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. The genre's load-bearing sections — prerequisites/sign-offs, pre-deploy go/no-go, the deploy procedure, post-deploy verification, rollback, escalation, and monitoring pointers — come from the template; your job is the *content quality* that fills them.

### Step 2: Load the upstreams; drive the procedure off them

Read the handed-in documents — this is your **input, not a blank page**. From the architecture-doc, identify every deployable component/service and the deploy topology. From the technical-design, take the rollout/migration plan, the order changes must land in, and any backward-compatibility constraint. From the test-plan, take the exit criteria that the post-deploy verification will assert. Where an upstream is thin or absent, make the gap an **explicit stated assumption**, never a silent default or an invented command.

### Step 3: Research to ground the procedure in SRE/operational practice

Use a deep-research pass to ground the runbook in established practice — not to invent. Confirm the operational conventions (idempotency, per-step verification, rollback triggers, secrets-by-reference) and the deploy-strategy mechanics against reputable sources. Design *with* the grain of what the upstreams describe. **If no research capability is available, do NOT fabricate** commands, thresholds, or hosts — state them as explicitly-flagged assumptions to validate before the release.

### Step 4: Choose the deploy strategy

**Default to blue-green** — deploy to an idle environment, smoke-test it, cut traffic over; rollback = cut traffic back. **Override** to the strategy best-suited to the project when the architecture-doc / technical-design implies one, or a user/system/agent pins one. The deploy steps **and** the rollback steps differ per strategy:

| Strategy | Deploy shape | Rollback shape |
|---|---|---|
| Blue-green (default) | Deploy to idle env, smoke-test, cut traffic over | Cut traffic back to the old env (instant) |
| Rolling | Update a subset of instances at a time, verify each batch | Scale the new down / old up (gradual) |
| Canary | Route a small % (1–10%), bake on metrics, ramp | Route 0% / scale the new down (localized) |
| Recreate | Stop old, deploy, start new (incurs downtime) | Redeploy the previous artifact |

Write the deploy and rollback procedures for the strategy you chose — not a generic one.

### Step 5: Write each step to the executability + safety method

Fill the template's sections to this method. Collapse a section a small release does not need; never pad.

- **Prerequisites & sign-offs** — the access/tooling required, the immutable artifact to ship (by id/tag, traced to the build), and the required approvals (QA/test sign-off, change approval, on-call ack). Record who approves, not just that approval is needed.
- **Pre-deploy checks (go/no-go)** — environment/config preconditions verified immediately before deploy, each with an **expected result**; an explicit GO/NO-GO gate where any failed check is a NO-GO that stops the procedure. Include identifying the current live version as the rollback target.
- **Deploy procedure** — **ordered, idempotent, copy-paste-safe** steps. Each step is a real command/action with clearly-marked `<placeholders>`, never ambiguous prose ("configure the server"). Re-running a step must be safe (guard one-time ops; `IF NOT EXISTS`; overwrite, don't append). **Every step states its expected output and a verification check** with hard, measurable criteria (status, version served, a health value) — the procedure does not advance on an unverified step.
- **Stateful-change / migration safety** (when the release changes a schema or data) — prefer a **backward-compatible, expand-and-contract (parallel-change)** sequence so a rollback is always safe: **expand** (add the new column/table alongside the old — never drop/rename in place), **migrate** (deploy code using the new structure; both coexist; backfill if needed), **contract** (remove the obsolete element in a *later, separate* release). Decouple the schema migration from the code deploy where possible. For an **irreversible** change (a `DROP`, a destructive transform, a committed data mutation) there is no clean down-migration — name its recovery path in the rollback (see below), don't write a phantom revert.
- **Post-deploy verification / smoke** — concrete checks with measurable success criteria, **reusing the test-plan's exit criteria**; observe (bake) for a stated period. Define success in numbers (error rate < threshold, p99 latency < threshold, **or an SLO error-budget burn-rate within bounds**), never "feels fine".
- **Rollback procedure** — explicit **trigger conditions** (measurable: error rate / latency / **SLO error-budget burn-rate** / a failed smoke check); a **documented revert for EVERY forward change**, in reverse order; the revert lever matches the strategy (blue-green = cut traffic back; canary/rolling = route 0% / scale down; recreate = redeploy the old artifact; **feature-flagged = flip the flag off — a near-instant localized lever**). For an **irreversible** forward change, **roll forward, not back** — name the fix-forward / containment / compensating-transaction / restore-from-backup path instead of a phantom down-migration that loses data. End with **re-verification to the pre-deploy baseline** after rollback.
- **On-call / escalation** — a real path: who to page, the severity ladder, the response budget per severity, the escalation policy.
- **Monitoring / observability pointers** — the dashboards/alerts/logs to watch, **by link**, each with "healthy looks like". Link the monitors; never embed live panels.
- **Maintenance window / comms** (when the deploy is **user-impacting**) — the comms plan: notify stakeholders ahead, post the maintenance window on the **status page**, send a restored-notification after; assign a per-channel owner (email / status page / in-app banner). **Proportional** — an internal / zero-user deploy needs none (leave it empty; that is correct, not a gap).

**Dry-run / rehearsal (aid, not a gate).** Before the real run, execute the whole procedure in a production-like staging environment, **inject a failure to prove the rollback actually works**, and have an engineer outside the team follow it (the "unfamiliar engineer" bar, empirically). Record the date in the template's **Last validated** field — the freshness signal that the runbook still matches the system. A first-ever runbook has not been rehearsed; this is a quality signal, never a precondition.

### Step 6: Self-check against the executability + safety bar before handing off

Confirm all hold (this is the bar the runtime `reviewing-release-runbook` gate asserts — **author and reviewer produce/judge the same 11-condition bar so they do not drift**; the numbering matches the reviewer's conditions). Each *proportional* item collapses to n/a where it does not apply — that is correct sizing, not a gap.

1. **Executable by an unfamiliar engineer** — every deploy/rollback step is concrete and copy-paste-safe with marked placeholders; no ambiguous prose; re-running a step is safe (idempotent).
2. **Per-step verification** — every step states its expected result and a measurable verification check (a raw threshold or an SLO burn-rate); the procedure does not advance unverified.
3. **Go/no-go gate present** — pre-deploy checks gate the deploy; any failed check is an explicit NO-GO that stops the procedure.
4. **Complete + safe rollback with triggers** — measurable trigger conditions (incl. a burn-rate); a revert for every forward change in reverse order with a **strategy-matched lever** (incl. a flag-flip where flagged); an irreversible change rolled **forward** with a stated recovery path; re-verification to baseline.
5. **Post-deploy verification reuses concrete checks** — the smoke uses measurable success criteria, **reusing the test-plan's exit criteria** where handed in, over a stated bake period.
6. **Concrete escalation + monitoring** — a real on-call/escalation path and real monitoring pointers (by link, with "healthy looks like") — not placeholders.
7. **No inlined secrets** — no real token/password/key in the runbook; secrets referenced by their store / vault / env-var name.
8. **No fabrication** — every command, host, and endpoint traces to a handed-in upstream or is explicitly flagged as an assumption.
10. **Stateful-change safety** *(proportional — n/a when there is no schema/data change)* — a schema/data forward change is reversible/backward-compatible (expand-contract-sequenced) OR names a roll-forward/containment/restore recovery path.
11. **Comms / maintenance-window** *(proportional — n/a when the deploy is not user-impacting)* — a user-impacting deploy names its comms/maintenance-window plan.

(Condition **9** — delta-scoped amend — applies only when you are *amending* an existing runbook; its self-check is **Step 7**. **Usable under release pressure** — reads top-to-bottom as a procedure an on-call engineer can follow at 3 a.m. without asking the author — is the **holistic lens** over the whole runbook, not a numbered item.)

**Thin-input gate:** if the deploy can't be credibly described from what's given or even reasonably assumed, surface it as a **blocker** ("runbook under-specified — needs the deploy topology / rollout decision") rather than papering it with invented commands.

### Step 7: Amend an existing runbook (the living-document path)

A release runbook is re-run every release and hardened by every incident. When you are handed an existing runbook + a change request, **amend it — do not regenerate it**:

1. **Scope** the change to the affected unit — a deploy step / a rollback step+trigger / a go-no-go check / a post-deploy check / the deploy strategy / a stateful-change step / an escalation or monitoring pointer / the comms plan.
2. **Detect the trigger** (twin): an **upstream change** (the architecture-doc topology, the technical-design rollout, or the test-plan exit criteria changed → re-derive the affected steps) OR a **post-incident learning** (an outage exposed a missing rollback step, an un-verified failure mode, or a too-slow/missing trigger → add the rollback trigger / verification gate / corrected step the incident demanded).
3. **Edit, don't rewrite** — amend only the affected steps.
4. **Re-validate end-to-end** — a runbook is an order-dependent procedure, so a changed step can silently break a *later* step's precondition (a renamed env, a reordered migration, a changed health endpoint). Walk the whole procedure for a broken downstream precondition; re-dry-run where feasible and **refresh the "Last validated" date, or explicitly flag re-validation as pending** (re-rehearsal is an aid, never forced).
5. **Confirm the bar on the delta** — the changed/added step meets the applicable binding conditions: executable + verified (cond-1/2); any new forward change has a revert + measurable trigger, and an irreversible one a roll-forward path (cond-4/cond-10); no secret inlined (cond-7); nothing fabricated (cond-8).
6. **Version + changelog + supersede** — bump the runbook's own **document version** (distinct from the deployed release version), add a changelog entry naming the trigger, mark the prior version superseded.

This is the bar the reviewer's **cond-9** (delta-scoped amend) asserts; on a greenfield first build cond-9 is n/a.

## Rules

**Hard rules (never violate):**

- **Idempotent, copy-paste-safe steps.** A step that can't be pasted and re-run safely is not a step. No ambiguous prose where a command belongs.
- **Every step has an expected result.** A step without a verification gate is not done — the next step must not start on an unverified one.
- **A documented revert for every forward change, with triggers.** Rollback names *when* (measurable triggers) and *how* (a revert per change, reverse order, a strategy-matched lever), re-verifies to baseline, and calls out any irreversible change with its mitigation.
- **A stateful change is backward-compatible or explicitly irreversible.** Sequence a schema/data change as expand-contract so a rollback is clean; an irreversible change names a roll-forward/containment/restore path, never a phantom down-migration that loses data.
- **Amend, don't regenerate.** On a change request to an existing runbook, edit the affected steps, re-validate the whole procedure end-to-end, and version+changelog the runbook — never silently rewrite it (Step 7).
- **Never inline a secret.** Reference the secret store / vault / env-var name. A real token/password/key in the runbook is a defect — secrets must never live in committed/deployed/logged files.
- **Never fabricate a command, host, or endpoint.** Trace each to an upstream; if you can't, flag it as an explicit assumption to validate before the release.
- **Compose, don't duplicate the outline.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Reuse the test-plan's exit criteria for verification.** Don't redefine the QA strategy; assert the criteria it already owns.
- **Document the procedure around the pipeline, not the pipeline.** The runbook invokes the CI/CD automation and documents the manual + verification + rollback steps; it does not author the pipeline config (that is a cicd-plan).
- **Executable + safe + complete, or not done.** Don't hand off a runbook an unfamiliar engineer couldn't deploy and roll back from.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — completeness of the load-bearing operational steps, not word count. A small service collapses sections it doesn't need.
- Default the deploy strategy to blue-green; override to rolling/canary/recreate when the upstream design implies one or it is pinned.
- Express each step as a fenced command snippet + an expected-output block; express verification as a check table with measurable pass criteria.
- The **comms/maintenance-window** plan is proportional to user-impact (an internal deploy needs none); the **dry-run/rehearsal** + "Last validated" is a freshness aid, never a precondition for a first runbook.

## Gotchas

- **Ambiguous prose where a command belongs.** "Configure the server and restart it" is not executable at 3 a.m. — give the exact command with marked placeholders and the expected output.
- **A step with no expected result.** Without a verification gate the operator can't tell success from silent failure; the next step proceeds on a broken state. State the expected output and the check.
- **Rollback that only says "roll back".** A revert for *every* forward change in reverse order, with the measurable trigger that fires it — and the irreversible-change call-out — is the safety net; "roll back the deploy" is not.
- **Inlined secrets.** Pasting a real token/connection string into a step leaks it into every place the runbook lives. Reference the store/vault/env-var name; print presence, never the value.
- **Strategy-blind rollback.** Blue-green rolls back by cutting traffic; recreate rolls back by redeploying the old artifact. A rollback written for the wrong strategy doesn't work — match the rollback to the chosen strategy.
- **Fabricated hosts/commands.** Inventing a hostname or a CLI flag to look complete produces a runbook that fails on first use. Trace to an upstream or flag as an assumption.
- **Big-bang schema change with no clean rollback.** Dropping/renaming a column in the same release that ships the code that stops using it leaves no safe revert. Sequence expand-contract (add new alongside old; migrate; contract later) so each step is independently rollbackable.
- **A phantom down-migration for an irreversible change.** Writing "rollback: run the down-migration" for a `DROP` that already destroyed data is a false safety net — it loses data. Name roll-forward / containment / restore-from-backup instead.
- **Regenerating the whole runbook on a small change.** A one-line topology fix does not need a rewrite — amend the affected step, re-validate end-to-end (a changed step can break a later precondition), and version+changelog it (Step 7).
- **A comms plan bolted onto an internal deploy.** Comms is proportional to user-impact; an internal/zero-user deploy needs none — forcing a status-page section there is padding, not safety.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

## Anti-patterns

- **"The deployer knows the commands, I'll keep it high-level."** The bar is an *unfamiliar* engineer under pressure — every step is concrete and copy-paste-safe, or the runbook fails when it's needed most.
- **"Rollback is just reverse the deploy."** Each forward change needs its own revert and a measurable trigger; an irreversible change needs a stated mitigation. Hand-waving rollback is where outages get extended.
- **"I'll inline the token so the step just works."** That leaks the secret. Reference its store; the runbook names the secret, never its value.
- **"No monitoring pointer was handed to me, I'll write a plausible dashboard URL."** Fabricating an endpoint produces a dead link in an incident. Surface the missing pointer as an assumption instead.
- **"I'll write the pipeline YAML here too."** That is a cicd-plan. The runbook documents the procedure around the pipeline, not the automation config.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"The migration's a one-liner, I'll just drop the column."** A breaking schema change with no backward-compatible step is the most common un-rollbackable deploy — expand-contract it, or call it irreversible and roll forward.
- **"It's a small change, I'll just rewrite the runbook."** Amend the affected step + re-validate end-to-end; a silent rewrite loses the change history and risks a broken downstream precondition.
- **"Skip the research, I know how to deploy."** The research grounds *this* runbook in proven SRE conventions (idempotency, verification gates, rollback triggers, strategy mechanics) — not deploy folklore.

## Output

A **comprehensive release runbook** that meets the **Step 6 executability + safety bar** (the 11-condition bar: executable by an unfamiliar engineer, a per-step verification gate, a go/no-go gate, a complete + safe rollback with triggers + roll-forward for an irreversible change, post-deploy verification reusing the test-plan exit criteria, concrete escalation + monitoring pointers, no inlined secret, nothing fabricated, stateful-change safety and a comms plan where applicable, usable under release pressure) — or, on an amendment, a versioned end-to-end-re-validated **delta** (Step 7). Expressed **textually** in the markdown medium — numbered procedure steps + fenced command/check snippets + expected-output blocks + verification/check tables + links to dashboards/monitors (not embedded live panels); the method and bar are medium-independent. The **abstract consumer** is the deploying/on-call engineer who executes the release, and the runtime `reviewing-release-runbook` gate (which asserts the same bar). The runbook **depends on** the handed-in upstreams (typically architecture-doc + technical-design + test-plan) as input. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **release-runbook template tool** (e.g. a content/template gateway) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the runbook in established SRE/operational practice (idempotency, verification gates, rollback triggers, deploy-strategy mechanics, secrets-by-reference).
- The **upstream architecture-doc + technical-design + test-plan** (where present) — the deployable components, the rollout, and the exit criteria the runbook derives from (input, never re-authored here).
- `reviewing-release-runbook` — the runtime gate that asserts the same executability + safety bar on the finished runbook; author and reviewer share one bar so they don't drift.
- A **cicd-plan** (separate, not in this composition) — the pipeline automation the runbook *invokes*; the runbook documents the procedure around it, not the config.

## Progressive disclosure

- `references/stateful-and-rollback.md` — depth on stateful-change safety + rollback levers: expand-and-contract / parallel-change migration phasing, the roll-forward-vs-rollback decision + containment for an irreversible change, the SLO error-budget burn-rate basis, and the feature-flag / automated-canary rollback levers. Load when the release changes a schema/data or uses progressive delivery.
- `references/amend-and-rehearsal.md` — depth on the Step-7 amend procedure (the twin trigger + the end-to-end re-validation ripple), the pre-prod dry-run/rehearsal practice, and the maintenance-window / stakeholder-comms plan. Load when amending an existing runbook or planning a user-impacting deploy.
- `references/sources.md` — research provenance for the SRE/operational method + the executability/safety bar (AWS Well-Architected runbook guidance, Google SRE canarying/reliable-releases + alerting-on-SLOs, OneUptime/Upstat runbook practice, expand-contract migration + roll-forward sources, deploy-strategy comparisons, feature-flag/dark-launch, secret-management guidance). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the skill listing.
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
