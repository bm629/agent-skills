---
name: reviewing-release-runbook
description: >
  Use when reviewing/judging a release runbook — the go-to-production procedure
  an engineer follows to ship a system to production — deciding whether an
  engineer unfamiliar with the system can execute the deploy, confirm it, and
  roll back from it alone. A gate, not authoring. Judges it against a
  single-sourced executability + safety bar: every step
  copy-paste-safe + idempotent with an expected result; a go/no-go gate; a
  complete + safe rollback (a documented revert for EVERY forward change with
  measurable triggers); concrete escalation + monitoring pointers; NO secret
  inlined (an embedded token/key is a finding — reference its store);
  commands/hosts spot-checked against the handed-in upstreams (un-verifiable
  ones flagged, not assumed); nothing fabricated. Emits exactly
  `VERDICT: approve|revise` plus actionable findings; approves a runbook meeting
  the bar (no false-revise), revises on a named gap. Not for authoring it, not
  the QA test-plan (test-plan-review), not engineering design docs
  (design-review).
extensions:
  claude:
    when_to_use: "judging a finished production release/deployment runbook against the executability + safety bar (unfamiliar engineer can deploy, verify, and roll back from it alone) and emitting an approve/revise verdict"
    argument-hint: "<the finished release runbook to review, plus the handed-in upstreams (architecture-doc / technical-design / test-plan) to spot-check commands against>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-release-runbook` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished release/deployment runbook as an acceptance gate — checking an unfamiliar on-call engineer can execute the deploy, confirm it, and roll back from the runbook alone, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of an authoring/judging release-runbook pair. Loaded by a reviewer who holds a **finished release/deployment runbook** — the operational go-live procedure a deploying or on-call engineer follows to ship a system to production safely and verifiably (prerequisites and sign-offs, pre-deploy go/no-go, the ordered deploy procedure, post-deploy verification, the rollback procedure, escalation, and monitoring pointers) — it judges that document against one question: **could an engineer who has never deployed this system execute the release, confirm it succeeded, and roll back safely from this runbook alone, with no secret inlined and nothing fabricated?** It applies a fixed **executability + safety checklist** — the same bar a release-runbook author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate: it does **not** author, fix, or rewrite the runbook; it judges and returns findings, and the producer revises.

The bar is **single-sourced** from the shared release-runbook dossier — the same executability/safety conditions a release-runbook author produces to. The reviewer does not invent a private standard.

## When to activate

- A finished release/deployment runbook needs an accept/revise decision before it ships to the deploying / on-call engineer.
- You are the independent reviewer / gate for a runbook a producer just authored, and you have the upstream documents (architecture-doc / technical-design / test-plan) to spot-check commands and verification against.
- Re-judging a revised runbook after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a release runbook -> use a release-runbook-authoring skill (it produces to the same bar this skill asserts). This skill never writes the document.
- Reviewing the **QA test-plan** — what to test, at what level, to what coverage -> use a test-plan-review skill. Different bar; the test-plan reviewer checks risk-weighted coverage + testable done-criteria. **This** gate checks operational executability + rollback safety; the runbook *reuses* the test-plan's exit criteria for post-deploy verification, it does not redefine the QA strategy.
- Reviewing **engineering design documents** — a spec, plan, technical-design, RFC, or ADR -> use a design-review skill that verifies design claims against the codebase. That gates the *design*; **this** judges the *operational go-live procedure*. Distinct artifact, distinct bar.
- Reviewing the **CI/CD pipeline config** — the build-test-deploy automation -> a separate concern. The runbook *invokes* the pipeline; this gate judges the procedure around it, not the YAML.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Grading the live deploy or the running service -> this gate judges the *runbook document*, not the production system.

## Workflow

### Step 1: Read the whole runbook with fresh, unfamiliar eyes — and pull up the upstreams

Read the runbook end to end as if you were an on-call engineer who has **never deployed this system**, encountering it for the first time at 3 a.m., without the author's framing. Your stance is a gatekeeper for that unfamiliar operator: a finding carries weight only when it shows the operator **cannot execute a step, tell success from failure, or roll back safely** as written, or when a command/host is **fabricated or unverifiable**. Identify the **deploy archetype** the runbook is sized to (a single small service vs. a multi-component system with a migration) — Step 2's proportionality calibration depends on it. Critically, **load the handed-in upstreams** (architecture-doc components + deploy topology, technical-design rollout/migration, test-plan exit criteria): they are your **accuracy oracle** for spot-checking commands, hosts, and verification. If an upstream was **not handed in**, record that now — you will flag the un-runnable trace as an assumption in Step 4 and judge on what you have; never assume an un-verifiable command is correct.

### Step 2: Run the executability + safety checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have ordered the steps differently" is not a gap. For each gap, capture the exact step/location and what is missing (Step 4 turns it into an actionable finding). These eight conditions are the **single-sourced bar** (the shared release-runbook dossier — the same conditions a release-runbook author produces to); do not add private ones.

1. **Executable by an unfamiliar engineer.** Every deploy/rollback step is concrete and copy-paste-safe — a real command/action with clearly-marked `<placeholders>`, never ambiguous prose ("configure the server"). Re-running a step is safe (idempotent: guarded one-time ops, `IF NOT EXISTS`, overwrite-not-append). *Gap* when a step is prose where a command belongs, or re-running it would corrupt state.
2. **Per-step verification.** Every step states its expected result and a verification check with **hard, measurable** criteria (latency/error-rate numbers, version served, health status — not "feels faster"). The procedure does not advance on an unverified step. *Gap* when a step has no expected result or no measurable check, so the operator can't tell success from silent failure.
3. **Go/no-go gate present.** Pre-deploy checks gate the deploy; any failed check is an **explicit NO-GO** that stops the procedure. *Gap* when pre-deploy checks are absent, or are present but nothing makes a failed check halt the deploy.
4. **Complete + safe rollback with triggers.** Explicit **trigger conditions** (measurable: error rate / latency / SLO burn / a failed smoke check); a **documented revert for EVERY forward change**, in reverse order; an irreversible forward change called out with its forward-fix/mitigation instead; and **re-verification to the pre-deploy baseline** after rollback. *Gap* when rollback only says "roll back the deploy", a forward change has no revert, triggers are vague/absent, an irreversible change has no called-out mitigation, or rollback doesn't re-verify. **The highest-impact defect class** — an incomplete rollback is where an outage gets extended.
5. **Post-deploy verification reuses concrete checks.** The post-deploy smoke uses concrete checks with measurable success criteria — **reusing the test-plan's exit criteria where the test-plan was handed in** — observed over a stated bake period. *Gap* when post-deploy verification is missing, defined as "looks fine", or ignores test-plan exit criteria that were handed in.
6. **Concrete escalation + monitoring.** A **real** on-call/escalation path (who to page, the severity ladder, the response budget per severity) and **real** monitoring/observability pointers (dashboards/alerts/logs **by link**, each with "healthy looks like") — not placeholders. *Gap* when escalation or monitoring is a placeholder ("page the on-call", "check the dashboard") with no concrete contact, link, or healthy-baseline.
7. **No inlined secrets.** No real token/password/key/connection-string appears in the runbook; secrets are referenced by their store / vault / env-var name. *Gap* — **a real secret embedded anywhere in the runbook is a finding**; it must reference its store. (Secrets must never live in committed/deployed/logged files.)
8. **No fabrication; commands/hosts accurate.** Every command, host, and endpoint **traces to a handed-in upstream** (architecture-doc components, technical-design rollout, test-plan criteria) or is **explicitly flagged as an assumption** in the runbook. **Spot-check** the commands/hosts/endpoints against the handed-in upstreams; an un-verifiable one is **flagged, not assumed correct**. *Gap* when a command/host/endpoint is invented to fill the template and presented as fact, or contradicts a handed-in upstream.

**Proportionality.** "Can an unfamiliar engineer deploy, verify, and roll back from it" scales with the deploy. A small single-service release legitimately **collapses sections it does not need** — no multi-batch rollout if there's one instance, a thin escalation path if the team is small, fewer monitoring links if the surface is tiny. That is correct sizing, not a gap. Judge the operator's **ability to execute and recover**, not word count or section count. A small, complete runbook that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (Conditions 4, 7, and 8 still bind at any size: every forward change has a revert, no secret inlined, nothing fabricated.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. An unfamiliar engineer can execute the deploy, confirm it succeeded, and roll back safely from this runbook as written; no secret is inlined and nothing is fabricated. Approve even if you can imagine stylistic improvements; the bar is executability + safety, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks safe execution (a deploy step with no verification, a forward change with no revert, an inlined secret, a fabricated/unverifiable command, an absent go/no-go gate, a placeholder escalation path, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact step/location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

If an **upstream was not handed in**, state that as an explicit assumption in the findings (e.g. "architecture-doc not provided — command/host accuracy (cond. 8) spot-checked only against the runbook's internal coherence; provide the upstreams for a full trace") and judge the other conditions on what you have. Do not silently pass over an un-runnable accuracy check, and never assume an unverifiable command is correct.

A good finding names the gap and the fix:

> **revise** — Complete + safe rollback (cond. 4), "Step 5: run the schema migration": this forward change has no documented revert and no rollback trigger. Fix: add a reverse migration step (or, if irreversible, call it out with a forward-fix/restore-from-backup mitigation) and the measurable trigger (e.g. error rate > 2% over the 10-min bake) that fires the rollback.

> **revise** — No inlined secrets (cond. 7), "Step 2: deploy": the step embeds a live database connection string with the password. Fix: reference the secret by its store/env-var name (e.g. `$DATABASE_URL` from the vault); print presence, never the value — a real secret must not live in the runbook.

> **revise** — Per-step verification (cond. 2), "Step 4: cut traffic to the new env": no expected result or check. Fix: state the expected output (e.g. 100% traffic on green, `HTTP 200` on `/healthz`) and a measurable check the operator runs before advancing.

A bad finding is vague and unactionable:

> The rollback section could be more thorough. *(Which forward change? Which trigger? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it (a verdict-parsing contract). No alternate verdict vocabulary.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the runbook. The producer revises.
- **Single-sourced bar.** Judge against the eight conditions in Step 2 — the same bar the author produces to (the shared release-runbook dossier). Do not invent extra conditions or apply a stricter private standard.
- **Rollback completeness is the load-bearing dimension.** A revert for *every* forward change, in reverse order, with measurable triggers and re-verification to baseline; an irreversible change called out with its mitigation. An incomplete rollback (cond. 4) is the highest-impact defect — an extended outage waiting to happen.
- **An inlined secret is always a finding.** A real token/password/key/connection-string anywhere in the runbook fails condition 7 — no exceptions, regardless of how convenient. It must reference its store/vault/env-var name.
- **Spot-check commands against the handed-in upstreams; flag the un-verifiable.** Trace each command/host/endpoint to an upstream (architecture-doc / technical-design / test-plan) or to an explicit assumption. An un-verifiable command is flagged (cond. 8), **never assumed correct**. A fabricated or upstream-contradicting command is a gap.
- **No false-revise.** A runbook that meets every applicable condition is approved, even a thin one for a small deploy. Proportional sizing that still covers the load-bearing operational steps is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **A deploy step with no verification is a gap.** A step with no expected result or no measurable check fails condition 2 — the operator can't tell success from silent failure.
- **Fabrication is a gap, not grounding.** An invented command, host, endpoint, or threshold presented as fact fails condition 8 — a real gap should be flagged as an assumption, not papered over.
- **Missing upstream is flagged, not silently passed.** If an upstream wasn't handed in, surface it as an explicit assumption and note that command/host accuracy (cond. 8) could not be fully spot-checked; judge the rest on what you have.
- **Judge against the upstreams the runbook was given.** Assess it against its `depends_on` set (the upstreams the project actually produced). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a runbook that **ignored a produced upstream** it should have drawn on (e.g. the handed-in test-plan whose exit criteria its post-deploy verification doesn't reuse) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — rollback-completeness and inlined-secret gaps first, then the rest.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of executability.** Every section can be present and the runbook still un-executable (prose where commands belong, steps with no verification, a rollback that just says "roll back"). Judge whether an unfamiliar engineer can *deploy and recover from it*, not whether the *template is filled*.
- **The incomplete rollback that reads complete.** A rollback section can look thorough while a single forward change (a schema migration, a feature flag, a DNS cut) has no revert — and that is exactly the change that extends the outage. Trace **every** forward change in the deploy to a matching revert (cond. 4); a forward change with no revert is the highest-impact, most-missed defect.
- **The strategy-mismatched rollback.** Blue-green rolls back by cutting traffic back; recreate rolls back by redeploying the old artifact; canary by routing to 0%. A rollback written for the wrong deploy strategy doesn't work in an incident. Check the rollback matches the runbook's actual deploy strategy.
- **The inlined secret hiding in plain sight.** A live token, password, or connection string pasted into a step looks like a working command but leaks the secret into every place the runbook lives. Any real credential value is a finding (cond. 7) — it must reference its store; scan command snippets for embedded values, not just a "secrets" section.
- **The fabricated host/command.** A hostname or CLI flag invented to look complete produces a runbook that fails on first use. Spot-check commands/hosts against the handed-in upstreams (cond. 8); one with no upstream backing and no assumption flag is a defect, not coverage.
- **Missing-upstream blind spot.** If an upstream wasn't handed in, command accuracy can't be fully spot-checked — do not let that absence default to an approve. Flag it as an assumption (cond. 8 partially un-runnable) and judge the rest; never assume an unverifiable command is correct.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also tempted to propose fixes — tends to over-correct, judging sound runbooks as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on a step order or command style you'd have written differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized runbook.** A small single-service deploy is correctly small — no multi-batch rollout, a thin escalation path, few monitoring links. That is right-sizing, not under-specification. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the archetype (conditions 4, 7, and 8 still bind: every forward change reverted, no secret inlined, nothing fabricated).
- **Confusing this with the test-plan or design-review gate.** This judges the **operational go-live runbook**. A test-plan-review judges the QA coverage/testability strategy; design-review gates engineering design docs against the codebase. Don't apply a QA-coverage or a design-doc bar to the deploy procedure.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch runbooks no unfamiliar engineer can execute or recover from; a forward change with no revert, an inlined secret, or a step with no verification waved through becomes a failed deploy or an extended outage.
- **Skipping the rollback trace.** "The deploy steps look fine, so I'll approve" — without tracing every forward change to a revert you miss the highest-impact defect class (cond. 4). An incomplete rollback is the one gap this gate exists most to catch.
- **Skipping the upstream spot-check.** "The commands look plausible, so I'll approve" — without spot-checking against the handed-in upstreams you let fabricated or drifted commands through (cond. 8). Reviewing the runbook in isolation when the upstreams were handed in is a shortcut this gate forbids.
- **Nit-pick revise.** Blocking on step-ordering taste, wording preference, or nice-to-haves dressed up as gaps. Revise is for real executability/safety blockers only.
- **Silent rewrite.** "It was easier to just fix the rollback step" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a load-test appendix") drifts the review-bar off the produce-bar and causes spurious revises. Judge the eight conditions only.
- **Maximalism.** Demanding a multi-batch rollout, a full SRE escalation tree, or a long monitoring catalog from a thin single-service deploy that doesn't need them. The bar is the operator's ability to execute and recover, not the largest possible runbook.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one release/deployment runbook:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The runbook under review is **textual** today — numbered procedure steps + fenced command/check snippets + expected-output blocks + verification/check tables + links to dashboards/monitors (markdown via the local docs backend); the review **method + bar are medium-independent** (a future rendered ops console changes only the medium, not what is judged). The **abstract consumer** is whatever orchestrates the produce->review loop: `approve` accepts the runbook for use by the deploying/on-call engineer; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **release-runbook-authoring** skill (`authoring-release-runbook`) — the produce half of the pair; it writes the runbook to the same executability + safety bar this skill judges against, and **owns the shared dossier** this skill reuses. Pairing them single-sources the bar so produce and review do not drift.
- A **test-plan-review** skill — the gate for the QA test-plan (coverage, levels, testable done-criteria). Distinct doc, distinct bar; the runbook *reuses* the test-plan's exit criteria for post-deploy verification (cond. 5), but this gate judges the operational procedure, not the QA strategy.
- A **design-review** skill — the gate for engineering design documents (spec, plan, technical-design, RFC, ADR), which verifies design claims against the codebase. Distinct gate, distinct artifact; not for the operational go-live runbook.
- The **upstream architecture-doc + technical-design + test-plan** (where handed in) — the deployable components, the rollout, and the exit criteria this gate **spot-checks the runbook's commands and verification against** (cond. 8 / cond. 5).
- A **release-runbook template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method (the single-sourced executability/safety quality bar from the shared release-runbook dossier, and the SRE/operational basis behind each condition — verification gates, rollback triggers, deploy-strategy mechanics, secrets-by-reference). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
