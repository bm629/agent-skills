---
name: authoring-prd
description: >
  Use when authoring a PRD (product requirements document) for a software or
  product project — turning a product idea into a comprehensive, plannable
  requirements doc. Guides the producer through the METHOD, not the outline:
  grounding the problem in evidence (jobs-to-be-done), defining measurable
  success metrics with guardrails, drawing a defensible MVP boundary, specifying
  functional + a non-functional taxonomy with numeric targets, writing testable
  acceptance criteria, keeping the problem→goal→metric→feature→AC chain
  traceable, naming dependencies, and surfacing risks + open questions — to a bar
  an engineer can plan milestones from. Also amends an existing PRD as a
  versioned, changelogged delta. Composes with a separate PRD template tool (the
  section structure) and a deep-research capability. Not for reviewing a finished
  PRD and not for authoring other document types.
extensions:
  claude:
    when_to_use: "authoring or amending a PRD from a product idea or a change request"
    argument-hint: "<the product idea / context to turn into a PRD, or the existing PRD + change>"
version: "1.2.0"
forge:
  status: unreviewed
  forged: 2026-06-04
  reviewed: null
---

# `authoring-prd` — SKILL.md

> **Variant:** standard · **When to use:** producing (or amending) a comprehensive PRD from a product idea, to a quality bar the downstream build can be planned from.

## Overview

This skill is the *how-to* of writing a strong, comprehensive Product Requirements Document — the judgment a producer applies, not the section list. It assumes two collaborators: a **PRD template tool** that supplies the section *structure*, and a **deep-research capability** to ground each section in evidence. The producer is handed a **product idea (and any upstream context documents)** and must **elaborate** it into a PRD — never emit generic boilerplate. The bar to clear: the finished PRD is *plannable* — an engineer can derive milestones and tasks from it. The skill is single-sourced with `reviewing-prd`: the Step-5 self-check IS the reviewer's 12-condition bar, so author and reviewer do not drift.

## When to activate

- Authoring a new PRD from a product idea or brief.
- Expanding a thin idea into a comprehensive requirements doc (product or substantial feature).
- **Amending an existing PRD** as a versioned delta (a new/changed requirement, a scope shift) — see Step 6.
- Filling a PRD template with researched, decision-complete content.

**Do NOT activate when:**

- Reviewing or grading a finished PRD → use `reviewing-prd`.
- Authoring a different document type (feature-spec, technical-design, runbook, wireframes) → use that type's skill. The PRD states WHAT + WHY; the HOW lives downstream in the feature-spec (per-feature behavior) and the technical-design (engineering design).
- A one-line note or a trivial change that needs no requirements doc.

## Inputs

Read the **project idea** plus **every document the plan hands you** — your `depends_on` set (any analysis documents discovery placed upstream, e.g. a problem-statement, market/competitor scan, business case, or user research) — and ground the PRD in them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. **Use a research capability where available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template. When **amending**, the existing PRD + the change request are also inputs (Step 6).

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your PRD template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive PRD structure (request/forge one, or fall back to the canonical PRD section set), then proceed.

### Step 2: Load the idea + context; name the archetype; discover gaps

Read the product idea and any upstream context. **Name the product archetype** — consumer / B2B-enterprise / internal tool / platform-API / data-ML / regulated — because it sets which sections carry weight (see `references/archetype-and-amend.md`). **Before drafting, fill knowledge gaps** — identify what's unknown about the core problem, success metrics, users, and constraints, and resolve it (ask, or research, or state an explicit assumption). Every section's content must trace back to *this* idea and its users — not a generic template fill. Where the idea is thin, make assumptions **explicit**, never silently generic. If the core problem can't even be credibly assumed, stop and raise the Step-5 thin-idea blocker rather than drafting.

### Step 3: Research to ground each section

Use a deep-research pass to ground the problem, users, market/competitive context, and metric baselines in evidence. Cite where it matters. Research the specific domain of the idea, not "PRDs in general." **If no research capability is available, do NOT fabricate evidence or citations** — state the problem/users/metrics as explicitly-flagged assumptions and list them under "validate before build."

### Step 4: Apply the per-section method

Fill the template's sections to this method:

- **Problem** — lead with **evidence** of the pain (data, research, signals); name who has it and what it costs today. Frame it as the **job-to-be-done** ("When [situation], I want [motivation], so I can [outcome]") so the problem rests on a real job, not a presupposed feature. An asserted, unevidenced problem is the most common PRD failure.
- **Goals & success metrics** — 2–4 **measurable** outcomes; for each, a target **and** the measurement method / tracking instrumentation, defined **before** building. Pair leading (input) with lagging (outcome) metrics, and where a headline metric is **gameable or could harm another axis**, name a **guardrail/counter-metric**. Use a framework (North Star / OKR / HEART / AARRR) to pick the *right* few — the framework is a tool, not a deliverable. A few crisp bullets, not a metric dump. (Depth: `references/nfr-and-metrics.md`.)
- **Users & personas** — concrete personas with real needs and scenarios; user stories ("As a … I want … so that …").
- **Scope: MVP & non-goals** — split must-have-for-first-launch from later; state **non-goals** and **release criteria** explicitly. The out-of-scope/Won't-have list is the primary scope-creep guard (+ feature budget / time-box where useful). Prioritize defensibly (RICE / MoSCoW / Kano as aids).
- **Requirements** — functional (testable, from the user's view) and **non-functional**, treated as a **named category taxonomy**, each load-bearing category carrying a **numeric/checkable target**: performance (p95 latency, throughput), availability/reliability (an SLO), security, privacy/data-handling, accessibility (**WCAG 2.2 AA** floor), scalability, maintainability, compatibility, localization/i18n, compliance — proportional to the archetype (a deliberately best-effort NFR may say so). (Taxonomy + numeric bars: `references/nfr-and-metrics.md`.)
- **User stories & acceptance criteria** — each story carries **acceptance criteria** (Given/When/Then or rule-based) that make "done" independently testable.
- **Traceability** — keep the chain whole: every feature traces up to a goal, every goal has ≥1 feature, every metric ties to a goal, every story has AC. Agile-light (a small matrix) — no heavy RTM tool. No orphan feature, no goal without a feature.
- **Dependencies** — name cross-team and external dependencies (services, data, third parties, required sign-offs) as their own concern; they gate sequencing downstream.
- **Risks** — likelihood/impact + mitigation; a short **pre-mortem** ("if this failed in 6 months, why?") sharpens it.
- **Assumptions, open questions, decision log** — surface unknowns explicitly; for a living PRD, log key decisions (what/when/why).
- **Cross-functional readiness (proportional aid, NOT a required section)** — prompt for feasibility sign-off and, *by archetype*, GTM/launch/support/analytics. Include only what the archetype needs — do not bolt a GTM section onto every PRD.
- **Cross-cutting** — precise, jargon-free, unambiguous language for a cross-functional audience; one name per entity.

### Step 5: Self-check against the plannability bar before handing off

Confirm all that apply hold (this is the same 12-condition bar `reviewing-prd` asserts):

1. **Evidenced problem** — backed by evidence (or a flagged assumption), framed as a job; not asserted.
2. **Defined users** — at least the primary persona(s) with concrete needs.
3. **Measurable success** — 2–4 metrics, each with target + method; a guardrail where the headline metric is obviously gameable in a way that harms a stated goal.
4. **Defensible MVP boundary** — in-scope vs out-of-scope/non-goals + release criteria.
5. **Concrete features** — features + acceptance criteria specific enough to derive milestones/tasks.
6. **Grounded, not assumed (no fabrication)** — problem and metrics rest on evidence; assumptions flagged + listed for "validate before build"; no fabricated numbers.
7. **Risks, dependencies-context + open questions surfaced** — not hidden.
8. **Clear + unambiguous** — jargon-free, consistent terminology; no vague adjectives standing in for requirements.
9. **NFR taxonomy** — the archetype's load-bearing NFR categories present, each with a numeric/checkable target (or stated best-effort).
10. **Traceable** — no orphan feature; every goal has a feature; metrics tie to goals; stories have AC.
11. **Dependencies named** — cross-team/external dependencies + sign-offs surfaced (or "none").
12. **Amend integrity** (when amending) — see Step 6.

**Thin-idea gate:** if the core problem cannot be evidenced or even credibly assumed, surface that as a **blocker** ("idea too thin to specify — needs discovery") rather than papering it with assumptions.

### Step 6: Amend an existing PRD as a versioned delta (when iterating)

When the input is an existing PRD + a change (not a greenfield idea):

- **Scope the change** — state what this amendment touches and what is deliberately untouched.
- **Edit in place, don't rewrite** — change only the affected requirements/goals/metrics/scope lines; do not regenerate the whole PRD (regeneration loses provenance and risks silent drift).
- **Version + changelog** — bump the PRD's own doc version; add a change-history entry: who / when / **what changed / why** (and who requested it).
- **Mark superseded content** — outdated requirements/metrics are explicitly marked superseded (with the reason), not silently deleted.
- **Analyze ripple** — trace the change's blast radius: which acceptance criteria, metrics, other requirements, and downstream docs (feature-spec, technical-design) are now stale. Surface the affected set (or "no downstream impact" with reason) so the traceability chain isn't left broken.

(Full amend procedure: `references/archetype-and-amend.md`.)

## Rules

**Hard rules (never violate):**

- **Evidence the problem.** Never assert the problem without evidence or a stated, flagged assumption.
- **Metrics must be measurable.** Every success metric has a target and a measurement method; reject vanity/unmeasurable goals. Add a guardrail where the headline metric is gameable.
- **NFRs get numeric targets.** A load-bearing non-functional requirement names a quantifiable target; "should be fast/secure" is not a requirement.
- **No vague language.** Replace subjective words ("fast", "intuitive", "easy", "scalable") with **quantifiable benchmarks** (e.g. "p95 < 200ms", "task done in ≤ 3 clicks").
- **Never fabricate evidence.** Do not invent statistics, survey figures, or citations. State unsourced claims as **explicitly-flagged assumptions** + "validate before build." An invented number is worse than an honest assumption.
- **Draw the MVP boundary.** Always state in-scope, deferred, and non-goals. No "MVP = everything."
- **Acceptance criteria on stories.** A user story without checkable acceptance criteria is not done.
- **Keep the chain traceable.** No orphan feature; every goal has at least one feature.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it.
- **Elaborate the given idea.** The PRD's specifics come from the idea + research, never generic boilerplate.
- **Amend, don't rewrite.** When changing an existing PRD, edit in place + version + changelog; never silently regenerate.
- **Plannable or not done.** Do not hand off a PRD an engineer cannot derive milestones from.

**Preferences (override-able):**

- "Comprehensive" sets the output *ambition*, but stay **proportional** — completeness of decisions, not word count. A thin idea legitimately collapses sections it doesn't need (no NFR matrix on a trivial tool, no dependencies when there are none).
- Keep goals/metrics to 2–4 bullets; prefer a short pre-mortem over a long risk table.
- Frameworks (North Star/OKR/HEART; RICE/MoSCoW/Kano) are aids to choose the right metrics/priorities — pick what fits the archetype; don't force one.

## Gotchas

- **Asserted problem.** "Users struggle with X" with no evidence reads authoritative but is the weakest part of most PRDs — ground it or flag the assumption.
- **Vanity metrics.** "Users will love it" / "more engagement" are not metrics. A metric names *what* is measured, its *target*, and *how* it's tracked.
- **Metric with no guardrail.** A gameable headline metric (e.g. "messages sent") with nothing guarding against the harm it could cause (spam) invites gaming — name the counter-metric.
- **NFRs as adjectives.** "Should be fast and secure" — replace with the category's numeric target (p95, SLO, WCAG 2.2 AA), proportional to the archetype.
- **Orphan feature / dangling goal.** A feature serving no stated goal (or a goal with no feature) breaks the chain a planner relies on — trace it or cut it.
- **Fuzzy MVP boundary.** Without an explicit in/out split + release criteria, scope creeps indefinitely. Name the exclusions.
- **Restating the outline.** Re-deriving the section list inside the PRD content instead of filling the template's sections with judgment.
- **Generic fill.** Content that would be true of any product means you elaborated the *template*, not the *idea*.
- **GTM-by-reflex.** Bolting a GTM/launch section onto a PRD whose archetype (e.g. an internal tool) doesn't need it. Readiness prompts are proportional aids, not universal sections.
- **Silent rewrite on amend.** Regenerating the whole PRD for a one-requirement change — loses the changelog and risks drift. Edit in place.

**Worked contrast — generic (compliant on the surface) vs grounded** (use it to self-detect):

| Section | Generic / un-grounded (reject) | Grounded (ship) |
|---|---|---|
| Problem | "Freelancers struggle to track invoices." | "[from real research] X% of freelancers reported ≥1 late payment/quarter; the pain is chasing payment, not data entry." *(number must come from a real source — never invent it; if unresearched, write it as a flagged assumption + 'validate')* |
| Metric | "Reduce late payments." | "Cut median days-to-payment from 21→14 within 90 days, tracked via invoice-paid timestamps; guardrail: support tickets/user ≤ baseline." |
| NFR | "Payments should be fast and reliable." | "Payment-status webhook reflects within 60s (p95); 99.9% delivery over a rolling 30-day window." |
| Acceptance criterion | "Login works." | "Given a registered user with valid credentials, when they submit the login form, they reach the dashboard in < 2s; invalid credentials show an inline error." |

If your fill reads like the left column — true of any product, no number, no source — it isn't done.

## Anti-patterns

- **"The success metric is that it works."** Unmeasurable — define metric + target + method.
- **"MVP = the full feature set."** No boundary — split must-have vs later + non-goals.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"The idea is thin, so I'll write a generic PRD."** Surface assumptions/open questions instead; never boilerplate.
- **"Skip the research, I know PRDs."** The research grounds *this idea's* problem/users/market — not PRD theory.
- **"It should be fast and intuitive."** Vague adjectives masquerading as requirements — replace with quantifiable benchmarks.
- **"NFRs are an implementation detail."** Missed-early NFRs cause expensive rewrites — name them with targets at PRD time.
- **"I'll regenerate the whole PRD for this change."** Amend in place + version + changelog instead.

## Output

A **comprehensive (or amended) PRD** that meets the **Step-5 plannability bar**. The **abstract consumer** is the downstream planning phase (which derives milestones/tasks from it), the downstream feature-spec/technical-design (which elaborate the HOW), and a reviewer (`reviewing-prd`, which asserts the same 12-condition bar). The PRD's *structure* comes from the template tool; this skill supplies the *content quality*. Medium: a textual markdown document (the method is medium-independent).

## Related

- A **PRD template tool** (e.g. `content-template-gateway`) — supplies the comprehensive PRD section structure this skill fills.
- A **deep-research capability** — grounds each section's content in evidence about the given idea.
- **`reviewing-prd`** — asserts the same 12-condition plannability bar on the finished PRD; author and reviewer share one bar so they don't drift.
- A **`design-review`** skill — the sibling gate for the PRD's engineering *downstream* docs (feature-spec/technical-design/ADR/RFC); distinct gate, not used on the PRD itself.
- Typical upstream `depends_on`: a problem-statement / market scan / business case / user research (guidance, not a precondition — stay self-contained).

## Progressive disclosure

- `references/nfr-and-metrics.md` — the NFR category taxonomy + numeric-target bars, and the metric frameworks (North Star/OKR/HEART/AARRR) + guardrail/counter-metric guidance. Load when filling Requirements or Goals & Metrics.
- `references/archetype-and-amend.md` — the per-archetype section-emphasis overlays (consumer/B2B/internal/platform-API/data-ML/regulated) and the full amend (edit-in-place + version + ripple) procedure. Load when naming the archetype or amending.
- `references/sources.md` — research provenance for the method + quality bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
