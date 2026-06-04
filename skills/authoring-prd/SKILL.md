---
name: authoring-prd
description: >
  Use when authoring a PRD (product requirements document) for a software or
  product project — turning a product idea into a comprehensive, plannable
  requirements doc. Guides the producer through the METHOD, not the outline:
  grounding the problem in evidence, defining measurable success metrics,
  drawing a defensible MVP boundary, writing testable requirements + acceptance
  criteria, and surfacing risks and open questions — to a bar an engineer can
  plan milestones from. Composes with a separate PRD template tool (which
  supplies the section structure) and a deep-research capability (to ground each
  section in the given idea). Not for reviewing a finished PRD and not for
  authoring other document types.
extensions:
  claude:
    when_to_use: "authoring or expanding a PRD from a product idea"
    argument-hint: "<the product idea / context to turn into a PRD>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-prd` — SKILL.md

> **Variant:** standard · **When to use:** producing a comprehensive PRD from a product idea, to a quality bar the downstream build can be planned from.

## Overview

This skill is the *how-to* of writing a strong, comprehensive Product Requirements Document — the judgment a producer applies, not the section list. It assumes two collaborators: a **PRD template tool** that supplies the section *structure*, and a **deep-research capability** to ground each section in evidence. The producer is handed a **product idea (and any upstream context documents)** and must **elaborate** it into a PRD — never emit generic boilerplate. The bar to clear: the finished PRD is *plannable* — an engineer can derive milestones and tasks from it.

## When to activate

- Authoring a new PRD from a product idea or brief.
- Expanding a thin idea into a comprehensive requirements doc (product or substantial feature).
- Filling a PRD template with researched, decision-complete content.

**Do NOT activate when:**

- Reviewing or grading a finished PRD → use a PRD-review skill.
- Authoring a different document type (architecture doc, runbook, wireframes) → use that type's skill.
- A one-line note or a trivial change that needs no requirements doc.

## Inputs

Read the **project idea** plus **every document the plan hands you** — your `depends_on` set (any analysis documents discovery placed upstream, e.g. a problem-statement, market/competitor scan, business case, or user research) — and ground the PRD in them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your PRD template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive PRD structure (request/forge one, or fall back to the canonical PRD section set), then proceed.

### Step 2: Load the idea + context; discover gaps; commit to elaborating it

Read the product idea and any upstream context. **Before drafting, fill knowledge gaps** — identify what's unknown about the core problem, success metrics, users, and constraints, and resolve it (ask, or research, or state an explicit assumption). Every section's content must trace back to *this* idea and its users — not a generic template fill. Where the idea is thin, make assumptions **explicit** (an Open Question or stated Assumption), never silently generic. If the core problem can't even be credibly assumed, stop and raise the Step 5 thin-idea blocker rather than drafting.

### Step 3: Research to ground each section

Use a deep-research pass to ground the problem, users, market/competitive context, and metric baselines in evidence. Cite where it matters. Research the specific domain of the idea, not "PRDs in general." **If no research capability is available, do NOT fabricate evidence or citations** — state the problem/users/metrics as explicitly-flagged assumptions and list them under "validate before build."

### Step 4: Apply the per-section method

Fill the template's sections to this method:

- **Problem** — lead with **evidence** of the pain (data, research, signals); name who has it and what it costs today. An asserted, unevidenced problem is the most common PRD failure.
- **Goals & success metrics** — 2–4 **measurable** outcomes; for each, a target **and** the measurement method / tracking instrumentation, defined **before** building. User-outcome-focused, tied to user *and* business value. A few crisp bullets, not a metric dump.
- **Users & personas** — concrete personas with real needs and scenarios; user stories ("As a … I want … so that …").
- **Scope: MVP & non-goals** — split must-have-for-first-launch from later; state **non-goals** and **release criteria** explicitly. This is the primary scope-creep guard.
- **Requirements** — functional (testable, from the user's view) and non-functional (performance, reliability, security, privacy, scalability, accessibility) with targets.
- **User stories & acceptance criteria** — each story carries **acceptance criteria** that make "done" checkable.
- **Risks** — likelihood/impact + mitigation; a short **pre-mortem** ("if this failed in 6 months, why?") sharpens it.
- **Cross-cutting (applies across all sections, not a section itself)** — precise, jargon-free, unambiguous language for a cross-functional audience.

### Step 5: Self-check against the plannability bar before handing off

Confirm all hold (this is the bar a reviewer will assert):

1. **Evidenced problem** — backed by evidence, not asserted.
2. **Defined users** — at least the primary persona(s) with concrete needs.
3. **Measurable success** — 2–4 metrics, each with a target + measurement method.
4. **Defensible MVP boundary** — clear in-scope vs out-of-scope/non-goals + release criteria.
5. **Concrete features** — features + acceptance criteria specific enough to derive milestones/tasks.
6. **Risks + open questions surfaced** — not hidden.
7. **Clear + unambiguous** — jargon-free, consistent terminology; no vague adjectives standing in for requirements.
8. **Grounded, not assumed** — the problem and success metrics rest on evidence, not unvalidated assumptions. If key parts *are* assumptions (a thin idea), the PRD says so prominently and lists what must be validated before build. Feasibility/sign-off needs (eng/design) are flagged.

**Thin-idea gate:** if the core problem cannot be evidenced or even credibly assumed, surface that as a **blocker** ("idea too thin to specify — needs discovery") rather than papering it with assumptions. A PRD whose problem, users, *and* metrics are all unvalidated assumptions is not plannable.

## Rules

**Hard rules (never violate):**

- **Evidence the problem.** Never assert the problem without evidence or a stated, flagged assumption.
- **Metrics must be measurable.** Every success metric has a target and a measurement method; reject vanity/unmeasurable goals.
- **No vague language.** Replace subjective words ("fast", "intuitive", "easy", "scalable") with **quantifiable benchmarks** (e.g. "p95 < 200ms", "task done in ≤ 3 clicks"). Vague adjectives are not requirements.
- **Never fabricate evidence.** Do not invent statistics, survey figures, or citations to make a section look grounded. If you have no research capability and no real source, state the claim as an **explicitly-flagged assumption** and add it to "validate before build." An invented number is worse than an honest assumption.
- **Draw the MVP boundary.** Always state what is in the MVP, what is deferred, and the non-goals. No "MVP = everything."
- **Acceptance criteria on stories.** A user story without checkable acceptance criteria is not done.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Elaborate the given idea.** The PRD's specifics come from the idea + research, never generic boilerplate.
- **Plannable or not done.** Do not hand off a PRD an engineer cannot derive milestones from.

**Preferences (override-able):**

- "Comprehensive" sets the output *ambition*, but stay **proportional** — completeness of decisions, not word count. A thin idea legitimately collapses sections it doesn't need.
- Keep goals/metrics to 2–4 bullets.
- Prefer a short pre-mortem over a long risk table.

## Gotchas

- **Asserted problem.** "Users struggle with X" with no evidence reads authoritative but is the weakest part of most PRDs — ground it or flag the assumption.
- **Vanity metrics.** "Users will love it" / "more engagement" are not metrics. A metric names *what* is measured, its *target*, and *how* it's tracked.
- **Fuzzy MVP boundary.** Without an explicit in/out split + release criteria, scope creeps indefinitely. Name the exclusions.
- **Restating the outline.** Re-deriving the section list inside the PRD content (or in this skill) instead of filling the template's sections with judgment — duplicates the template tool and drifts from it.
- **Generic fill.** Content that would be true of any product means you elaborated the *template*, not the *idea*. Tie every section to the specific idea.

**Worked contrast — generic (compliant on the surface) vs grounded** (use it to self-detect):

| Section | Generic / un-grounded (reject) | Grounded (ship) |
|---|---|---|
| Problem | "Freelancers struggle to track invoices." | "[from real research] X% of freelancers reported ≥1 late payment/quarter; the pain is chasing payment, not data entry." *(the number must come from a real source — never invent it; if unresearched, write it as a flagged assumption + 'validate')* |
| Metric | "Reduce late payments." | "Cut median days-to-payment from 21→14 within 90 days, tracked via invoice-paid timestamps." |
| Requirement | "Payments should be fast." | "Payment-status webhook reflects within 60s (p95)." |
| Acceptance criterion | "Login works." | "Given a registered user with valid credentials, when they submit the login form, they reach the dashboard in < 2s; invalid credentials show an inline error." |

If your fill reads like the left column — true of any product, no number, no source — it isn't done.

## Anti-patterns

- **"The success metric is that it works."** Unmeasurable — forbidden; define metric + target + method.
- **"MVP = the full feature set."** No boundary — forbidden; split must-have vs later + non-goals.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.
- **"The idea is thin, so I'll write a generic PRD."** Surface assumptions/open questions instead; never boilerplate.
- **"Skip the research, I know PRDs."** The research grounds *this idea's* problem/users/market — not PRD theory.
- **"It should be fast and intuitive."** Vague adjectives masquerading as requirements — replace with quantifiable benchmarks or cut them.

## Output

A **comprehensive PRD** that meets the **Step 5 plannability bar** (evidenced problem, defined users, measurable metrics, defensible MVP boundary with non-goals, concrete features with acceptance criteria, surfaced risks/open questions, grounded-not-assumed, clear unambiguous language). The **abstract consumer** is the downstream planning phase (which derives milestones/tasks from it) and a reviewer (which asserts the same bar). The PRD's *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **PRD template tool** (e.g. a content/template gateway) — supplies the comprehensive PRD section structure this skill fills.
- A **deep-research capability** — grounds each section's content in evidence about the given idea.
- A **PRD-review skill** — asserts the same plannability bar on the finished PRD; author and reviewer share one bar so they don't drift.

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
