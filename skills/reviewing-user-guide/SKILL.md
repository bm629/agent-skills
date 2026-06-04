---
name: reviewing-user-guide
description: >
  Use when reviewing/judging an end-user guide — the consumer-facing help a
  (typically non-technical) product user reads to accomplish their goals
  (getting-started tutorial, task how-tos, explanation, a feature/config
  reference, troubleshooting) — deciding whether a real user can accomplish
  every supported goal from the guide alone. A gate, not authoring. Judges it
  against a single-sourced usability + accuracy bar: one how-to per user goal in
  the handed-in upstreams; the four Diataxis modes present and correctly typed
  (a how-to is steps, not a concept dump); the feature/config reference complete
  (NOT the HTTP API); every step accurate; no fabrication; troubleshooting
  covers known error states. Emits exactly
  `VERDICT: approve|revise` plus actionable findings; approves a guide meeting
  the bar (no false-revise), revises only on a named gap. Not for authoring it,
  not the developer adoption guide
  (developer-guide-review), not the endpoint catalog (api-reference-review),
  not engineering design docs (design-review).
extensions:
  claude:
    when_to_use: "judging a finished end-user guide against the usability + accuracy bar and emitting an approve/revise verdict"
    argument-hint: "<the finished end-user guide to review>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-user-guide` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished end-user guide as an acceptance gate — checking a real user can accomplish every supported goal from it, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging end-user-guide pair. Loaded by a reviewer who holds a **finished end-user guide** — the consumer-facing help the person *using* a product (typically non-technical) reads to accomplish their goals (a getting-started tutorial, task-oriented how-to guides, conceptual explanation, an end-user feature/configuration reference, and troubleshooting/FAQ) — it judges that guide against one question: **can a real user of the product accomplish every supported goal from this guide alone, without asking the author, with steps that match how the product actually behaves?** It applies a fixed **usability + accuracy checklist** — the same bar a user-guide author produces to, so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It judges the **textual markdown artifact** (prose, fenced snippets, screens described in words with wireframe links), not a rendered help site; the method and bar are medium-independent. It is an acceptance gate — it does **not** author, fix, or rewrite the guide; it judges and returns findings, and the producer revises.

## When to activate

- A finished end-user guide needs an accept/revise decision before it ships to its users.
- You are the independent reviewer / gate for an end-user guide a producer just authored.
- Re-judging a revised end-user guide after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing an end-user guide -> use a user-guide-authoring skill (it produces to the same bar this skill asserts). This skill never writes the guide.
- Reviewing a **developer adoption/integration guide** — the onboarding narrative for an SDK, library, CLI, framework, or API platform that a *developer* reads to integrate a tool -> use a developer-guide-review skill. That gate judges developer adoption; **this** gate judges the **end-user product** guide.
- Reviewing an **API reference** — the developer-facing HTTP/SDK endpoint catalog (endpoints, fields, errors, contract-consistency) -> use an api-reference-review skill. That gate judges contract-consistency, not end-user usability; the end-user reference here is the product surface (features, settings, CLI commands), NOT the HTTP API.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC -> use a design-review skill that verifies design claims against the codebase. Distinct gate, distinct bar.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole guide with fresh, independent eyes, and gather the upstreams

Read the guide end to end as if you were the target user encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *user*: a finding carries weight only when it shows a real user **cannot accomplish a supported goal from the guide as written**, or when a step would lead the user wrong because it does not match the product.

Then identify the **handed-in upstreams** the guide was produced from — its `depends_on` set (typically a feature-spec, user-flows, and/or wireframes; sometimes only a PRD). **Enumerate the user goals from the user-flows when user-flows is present** (each flow is a user goal/job); **when user-flows is absent, take the goals from the feature-spec / PRD.** Judge coverage against whatever upstream was *actually* handed in — never assume user-flows is always present. If an expected upstream is absent, note it as an assumption you are reviewing under; do not invent a goal the upstreams do not support, and do not fault the guide for a document the project never produced.

### Step 2: Run the usability + accuracy checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have worded this differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar; do not add private ones.

1. **Goal coverage — one how-to per goal, no orphans.** Every user goal enumerated from the handed-in upstreams (Step 1) has exactly **one** task-oriented how-to, and every how-to traces back to a goal. *Gap* when a goal has no how-to (a coverage hole), or a how-to exists for no upstream goal (an orphan that may signal an invented feature).
2. **Four Diataxis modes present AND correctly typed.** Tutorial, how-to, explanation, and reference are all present and **not conflated** — the **tutorial** is a single guaranteed happy path (no choices/failure branches, every step yields a visible result); a **how-to** is imperative numbered steps (NOT a concept dump); **explanation** has no steps; **reference** is neutral + complete. *Gap* when a mode is missing, or written as another mode — a how-to padded into a concept dump, an explanation that smuggles in steps, a tutorial branching into alternatives. (Mixing modes is the #1 cause of doc confusion.)
3. **End-user feature/config reference complete.** Every user-facing feature, setting, and CLI command/shortcut the product exposes is documented; the reference mirrors the product; it **describes, does not instruct**. *Gap* when a user-facing feature/setting/command is missing or stale. (It is the **end-user product surface**, NOT the HTTP API — do not fault it for omitting endpoints.)
4. **Steps accurate to the actual product behavior.** Every procedural step matches a behavior in the handed-in upstreams (spot-checked against the feature-spec / user-flows); no invented step, setting, screen, or menu. *Gap* on a step that contradicts the upstream behavior, or a fabricated feature/screen with no upstream basis. **Fabrication is a hard fail.**
5. **Procedure mechanics sound.** How-tos and the tutorial use **numbered steps, one action per step, second person, present tense, imperative voice, task-based headings** (bare infinitive, e.g. "Add an account"). *Gap* when procedures are unnumbered prose blobs, bundle several actions per step, or use noun-phrase/feature-named headings instead of task headings.
6. **Troubleshooting covers the known error states.** Every error/recovery path from the handed-in upstreams (the user-flows' error/recovery paths and the feature-spec's error handling) appears as a **symptom -> cause -> fix** entry, organized by user-visible symptom; recurring questions are in the FAQ; a "get more help" pointer exists. *Gap* when a known error state is left undocumented, or entries are organized by internal cause rather than user-visible symptom.
7. **Usable by the target audience.** A real user (typically non-technical) could accomplish **every** supported goal from the guide alone, without asking the author; language suits the audience (no unexplained jargon); screens are described in words and **wireframe-linked** rather than assumed visible. *Gap* when an ambiguity, missing prerequisite, or undefined term would block the user mid-task.
8. **Assumptions/gaps surfaced.** Where an upstream was absent or thin, the assumptions the guide made are **stated** (challengeable), not silently invented. *Gap* when a missing upstream answer was **fabricated** to look complete instead of flagged as an assumption.

**Proportionality.** "Usable to accomplish every goal" scales with the product. A thin product's guide legitimately collapses sections it does not need and carries a handful of how-tos — that is correct sizing, not a gap. Judge **coverage of the goals the upstreams actually carry + accuracy**, not section count or word count. A small, complete guide that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (The hard floor in condition 1 still holds at any size: a goal the upstreams carry must have a how-to.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A real user can accomplish every supported goal from the guide as written; the modes are correctly typed; the steps match the product. Approve even if you can imagine wording improvements; the bar is usability + accuracy, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks a user (a goal with no how-to, a conflated/mistyped Diataxis mode, an incomplete reference, a fabricated or inaccurate step, an undocumented known error state, jargon the audience can't follow, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Goal coverage (cond. 1): the user-flows carry a "Reset password" goal but the guide has no how-to for it. Fix: add a task-oriented "Reset your password" how-to (numbered steps from the flow's happy path).

> **revise** — Diataxis typing (cond. 2), "Export your data" how-to: the section is three paragraphs explaining *why* exports matter with no steps — it is an explanation, not a how-to. Fix: rewrite as numbered imperative steps (open Settings -> Export -> choose format -> confirm); move the "why" into the explanation section.

A bad finding is vague and unactionable:

> The guide could be clearer. *(Which goal? Which mode? Which step? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the guide. The producer revises.
- **Single-sourced bar.** Judge against the eight conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A guide that meets every applicable condition is approved, even a thin one for a small product. Proportional sizing that still covers the goals is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Enumerate goals from whatever upstream was handed in.** Take goals from the **user-flows when present, else the feature-spec/PRD** — never assume user-flows is always there. A **not-produced** upstream is **never** a revise trigger; flag its absence as an assumption. But a guide that **ignored a produced upstream** (a goal in the handed-in user-flows with no how-to, a step that contradicts the handed-in feature-spec) **is** a fair finding.
- **A goal with no how-to is a coverage gap.** Every goal the handed-in upstreams carry needs exactly one task-oriented how-to (cond. 1).
- **A mode written as another mode is a defect.** A how-to that is a concept dump, an explanation with steps, a tutorial that branches — each fails condition 2. Mixing Diataxis modes is the most common usability failure.
- **The reference is the end-user product surface, not the HTTP API.** Judge completeness over features/settings/CLI commands the product exposes (cond. 3); do not fault it for omitting endpoints — that is the api-reference's job.
- **Fabrication is a hard fail.** An invented step, setting, screen, or feature with no upstream basis fails condition 4 — a real gap should be flagged as an assumption (cond. 8), not papered over with an invented step.
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of usability.** Every section can be present and a user still stuck (a how-to that is really an explanation, a step that contradicts the product, a goal with no recipe). Judge whether a real user can *accomplish every goal*, not whether the *template is filled*.
- **The mistyped mode.** The single most common defect: a "how-to" that is three paragraphs of background with no steps (an explanation in disguise), or a tutorial that offers branching choices (a how-to/reference in disguise). Read each section for what it *is*, not what it is *titled* (cond. 2). Mixing modes reads complete but confuses the user.
- **The orphan how-to that signals a fabricated feature.** A how-to for a goal no handed-in upstream carries is not just an orphan — it often means an invented feature/screen leaked in (cond. 1 + cond. 4). Trace every how-to back to an upstream goal; an untraceable one is a fabrication flag, not a bonus.
- **Reference-as-API confusion.** Faulting the end-user reference for omitting HTTP endpoints, or accepting an endpoint catalog as the end-user reference — the end-user reference is the **product surface** (features, settings, CLI commands/shortcuts), not the API (cond. 3). Judge the surface the user touches.
- **Step accuracy without a running product.** You can't click through the live product — but you *can* spot-check each step against the handed-in feature-spec/user-flows (cond. 4). A step with no upstream basis is an un-verifiable claim; if the guide presents it as fact rather than flagging it as an assumption, that is the gap. Don't wave it through because "it sounds plausible".
- **Troubleshooting organized by cause, not symptom.** A troubleshooting section can list every internal error code yet still fail the user who only sees a *symptom* ("the page won't load"). Entries must be findable by the user-visible symptom -> cause -> fix (cond. 6); a cause-keyed list the user can't navigate is a gap.
- **Audience drift (unexplained jargon).** Steps that are accurate but assume technical knowledge the (typically non-technical) audience lacks fail condition 7 even when every other condition passes. The bar is usability *by the stated audience*, not by the author.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems — especially one also asked to propose fixes — tends to over-correct, judging sound guides as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on phrasing you'd have chosen differently. Plausible-sounding nits are the dominant reviewer error here.
- **False-revise on a proportionally-sized guide.** A thin product's guide is correctly small — a handful of how-tos, collapsed sections it doesn't need. That is right-sizing, not under-documentation. Manufacturing a gap from brevity drives avoidable revise loops; calibrate to the goals the upstreams actually carry.
- **Faulting markdown for not being a help site.** Expecting embedded screenshots or rendered pages — the artifact is **textual** (screens described in words + wireframe links). Judge the description and the link, not the absence of pixels.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch guides a user can't accomplish their goals from; a mistyped mode or a fabricated step waved through becomes a stuck or misled user.
- **Nit-pick revise.** Blocking on word choice, heading taste, or nice-to-haves dressed up as gaps. Revise is for real usability/accuracy blockers only.
- **Silent rewrite.** "It was easier to just fix the step" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a video / a marketing intro") drifts the review-bar off the produce-bar and causes spurious revises. Judge the eight conditions only.
- **Inventing an upstream expectation.** Faulting the guide for not covering a goal that lives only in a document the project never produced. Judge coverage against the handed-in upstreams; a missing upstream is an assumption, not a revise.
- **Maximalism.** Demanding the full broad section set from a thin product's guide. The bar is goal coverage + accuracy, not the largest possible guide.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one end-user guide:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce->review loop: `approve` accepts the guide as ready for its users; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **user-guide-authoring** skill — the produce half of the pair; it writes the guide to the same usability + accuracy bar this skill judges against. Pairing them single-sources the bar (a shared user-guide dossier) so produce and review do not drift.
- A **developer-guide-review** skill — the gate for the developer adoption/integration guide (SDK/library/CLI/framework/API-platform onboarding). Distinct doc, distinct audience; this skill judges the **end-user product** guide, not the developer onboarding narrative.
- An **api-reference-review** skill — the gate for the developer-facing HTTP/SDK endpoint catalog (contract-consistency). Distinct doc, distinct bar; the end-user reference judged here is the product surface, not the API.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not for an end-user guide.
- A **user-guide template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/sources.md` — research provenance for the review method (the single-sourced quality bar from the shared user-guide dossier: the Diataxis four-mode typing, the per-goal how-to coverage rule, the procedure-mechanics conventions, and the reviewer-overcorrection evidence behind the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
