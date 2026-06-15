---
name: reviewing-user-guide
description: >
  Use when reviewing/judging an end-user product guide — the consumer-facing help a
  typically non-technical person reads to accomplish product goals (tutorial, how-tos,
  explanation, a product feature/settings reference, troubleshooting, glossary) — deciding
  whether a real user can accomplish every supported goal from the guide alone. A
  gate, not authoring. Judges a single-sourced 12-condition usability + accuracy bar: one
  how-to per goal; the four Diataxis modes correctly typed (not conflated); a complete
  product reference (NOT the HTTP API); accurate steps named by their
  exact UI label; symptom-keyed troubleshooting; plain language a non-technical reader can
  follow; accessibility + findability; surfaced assumptions, no fabrication; a delta-scoped
  amend. Emits exactly `VERDICT: approve|revise` plus actionable findings; approves a guide
  meeting the bar (no false-revise), revises only on a named gap. Not authoring it, the
  developer adoption guide, the endpoint catalog, or engineering design docs (design-review).
extensions:
  claude:
    when_to_use: "judging a finished end-user guide against the usability + accuracy bar and emitting an approve/revise verdict"
    argument-hint: "<the finished end-user guide to review>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `reviewing-user-guide` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished end-user guide as an acceptance gate — checking a real user can accomplish every supported goal from it against a single-sourced 12-condition bar, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging end-user-guide pair. Loaded by a reviewer who holds a **finished end-user guide** — the consumer-facing help the person *using* a product (typically non-technical) reads to accomplish their goals (a getting-started tutorial, task-oriented how-to guides, conceptual explanation, an end-user feature/configuration reference, troubleshooting/FAQ, and a glossary) — it judges that guide against one question: **can a real user of the product accomplish every supported goal from this guide alone, without asking the author, with steps that match how the product actually behaves and language a non-technical reader can follow?** It applies a fixed **12-condition usability + accuracy checklist** — the same bar a user-guide author produces to, single-sourced and numbered identically so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It judges the **textual markdown artifact** (prose, fenced snippets, screens described in words with wireframe links), not a rendered help site; the method and bar are medium-independent. It is an acceptance gate — it does **not** author, fix, or rewrite the guide; it judges and returns findings, and the producer revises.

## When to activate

- A finished end-user guide needs an accept/revise decision before it ships to its users.
- You are the independent reviewer / gate for an end-user guide a producer just authored.
- Re-judging a revised end-user guide after a prior `revise` verdict.
- Reviewing an **amend** — a versioned delta on a published guide after an upstream change (judged delta-scoped, cond-9).

**Do NOT activate when:**

- Authoring or repairing an end-user guide -> use a user-guide-authoring skill (it produces to the same bar this skill asserts). This skill never writes the guide.
- Reviewing a **developer adoption/integration guide** — the onboarding narrative for an SDK, library, CLI, framework, or API platform that a *developer* reads to integrate a tool -> use a developer-guide-review skill. That gate judges developer adoption; **this** gate judges the **end-user product** guide.
- Reviewing an **API reference** — the developer-facing HTTP/SDK endpoint catalog (endpoints, fields, errors, contract-consistency) -> use an api-reference-review skill. That gate judges contract-consistency, not end-user usability; the end-user reference here is the product surface (features, settings, CLI commands), NOT the HTTP API.
- Reviewing an **engineering design document** — an architecture spec, design doc, ADR, or RFC -> use a design-review skill that verifies design claims against the codebase. Distinct gate, distinct bar.
- Checking template/section conformance -> that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole guide with fresh, independent eyes, and gather the upstreams

Read the guide end to end as if you were the target (typically non-technical) user encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *user*: a finding carries weight only when it shows a real user **cannot accomplish a supported goal from the guide as written**, or when a step would lead the user wrong because it does not match the product.

Then identify the **handed-in upstreams** the guide was produced from — its `depends_on` set (typically a feature-spec, user-flows, and/or wireframes; sometimes only a PRD; sometimes a design-system for UI terms). **Enumerate the user goals from the user-flows when user-flows is present** (each flow is a user goal/job); **when user-flows is absent, take the goals from the feature-spec / PRD.** Judge coverage against whatever upstream was *actually* handed in — never assume user-flows is always present. If an expected upstream is absent, note it as an assumption you are reviewing under; do not invent a goal the upstreams do not support, and do not fault the guide for a document the project never produced.

**Amend mode (detected by input signal):** if you are handed an **existing guide + a change request + the changed upstreams**, judge the **delta** under cond-9 — not a full re-review.

### Step 2: Run the 12-condition usability + accuracy checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have worded this differently" is not a gap. For each gap, capture the exact location and what is missing (Step 4 turns it into an actionable finding). The conditions are the single-sourced bar (identical to the author's Step-10 self-check, numbered the same); do not add private ones.

1. **Goal coverage — one how-to per goal, no orphans.** Every user goal enumerated from the handed-in upstreams (Step 1) has exactly **one** task-oriented how-to, and every how-to traces back to a goal. *Gap* when a goal has no how-to (a coverage hole), or a how-to exists for no upstream goal (an orphan that may signal an invented feature).
2. **Four Diataxis modes present AND correctly typed.** Tutorial, how-to, explanation, and reference are all present and **not conflated** — the **tutorial** is a single guaranteed happy path (no choices/failure branches, every step yields a visible result); a **how-to** is imperative numbered steps (NOT a concept dump); **explanation** has no steps; **reference** is neutral + complete. *Gap* when a mode is missing, or written as another mode — a how-to padded into a concept dump, an explanation that smuggles in steps, a tutorial branching into alternatives. (Mixing modes is the #1 cause of doc confusion.)
3. **End-user feature/config reference complete.** Every user-facing feature, setting, and CLI command/shortcut the product exposes is documented; the reference mirrors the product; it **describes, does not instruct**. *Gap* when a user-facing feature/setting/command is missing or stale. (It is the **end-user product surface**, NOT the HTTP API — do not fault it for omitting endpoints.)
4. **Steps accurate to the actual product behavior — incl. UI terminology.** Every procedural step matches a behavior in the handed-in upstreams (spot-checked against the feature-spec / user-flows); no invented step, setting, screen, or menu; and each control is named by its **exact product/design-system label** (a step that names a control the product doesn't have, or by the wrong label, is an accuracy gap). *Gap* on a step that contradicts the upstream behavior, a fabricated feature/screen with no upstream basis, or a label that doesn't match the product. **Fabrication is a hard fail.**
5. **Procedure mechanics sound.** How-tos and the tutorial use **numbered steps, one action per step, second person, present tense, imperative voice, task-based headings** (bare infinitive, e.g. "Add an account"), naming controls by their exact labels. *Gap* when procedures are unnumbered prose blobs, bundle several actions per step, or use noun-phrase/feature-named headings instead of task headings.
6. **Troubleshooting covers the known error states.** Every error/recovery path from the handed-in upstreams (the user-flows' error/recovery paths and the feature-spec's error handling) appears as a **symptom -> cause -> fix** entry, organized by user-visible symptom; recurring questions are in the FAQ; a "get more help" pointer exists. *Gap* when a known error state is left undocumented, or entries are organized by internal cause rather than user-visible symptom.
7. **Usable by the target audience.** A real user (typically non-technical) could accomplish **every** supported goal from the guide alone, without asking the author; prerequisites are stated; screens are described in words and **wireframe-linked** rather than assumed visible. *Gap* when an ambiguity, missing prerequisite, or undefined step would block the user mid-task. *(Language comprehensibility — jargon/readability — is cond-10; do not double-judge it here. This condition is the accomplish-the-goal / prerequisite / screen-description outcome.)*
8. **Assumptions/gaps surfaced.** Where an upstream was absent or thin, the assumptions the guide made are **stated** (challengeable), not silently invented. *Gap* when a missing upstream answer was **fabricated** to look complete instead of flagged as an assumption.
9. **Amend is a scoped, swept, versioned delta** (n/a on a greenfield first build). On an iteration: the delta meets the bar on what it touched; the **upstream staleness sweep is complete** — no changed/removed/renamed capability is still referenced by a stale step / reference entry / screen link / troubleshooting entry / glossary term (a structural "find every reference" check); internal coherence holds (the tutorial still runs, the modes stay typed, the reference still mirrors the product); the revision-history is updated; superseded/removed items are marked. *Gap* on an incomplete sweep (a stale reference survives), broken coherence, missing change-history, or an unmarked removal. Detected by the input signal (an existing guide + change request + changed upstreams).
10. **Plain language / readability.** A non-technical reader can follow the guide: purpose-first; reasonable sentence length; **every product-specific term and acronym defined on first use** (and collected in the glossary); no unexplained acronym; an audience-fit reading level. Judged by **outcome** (a real user can follow it), NOT a readability score. *Gap* when unexplained jargon or a bare acronym would block the non-technical reader mid-step. *(Overlap guard: a jargon/readability defect is cond-10; an unfollowable-flow / missing-prerequisite defect is cond-7 — do not double-penalize the same defect under both.)*
11. **Accessibility (proportional).** In the textual artifact: link text is **meaningful** (no bare "click here"); headings **nest** correctly (no skipped levels); no step relies on **color alone** ("click the green button") or **location alone** ("the button on the right") — controls are named by label; described screens carry alt-text intent. *Gap* on a bare-link / color-only / location-only instruction that would block a reader who can't perceive the cue. *(Proportional — n/a where there are no links/images/color cues. Pixel contrast and focus appearance are the rendered-site / design-system's concern, NOT judged here.)*
12. **Findability / start-here.** A first-time reader can **locate** the start-here (the tutorial) and their goal's section across the doc set without already knowing the product (a §1 signpost / navigable structure). *Gap* when there is no start-here orientation and a reader can't tell which document answers their question. *(Overlap guard: worded distinct from cond-1 "organized by goal — coverage" and cond-2 "modes typed"; trivially holds for a one-page guide; do NOT revise under cond-12 a defect already caught by cond-1/cond-2.)*

**Proportionality.** "Usable to accomplish every goal" scales with the product. A thin product's guide legitimately collapses sections it does not need and carries a handful of how-tos — that is correct sizing, not a gap. A thin guide also legitimately has nothing to amend (cond-9 n/a on first build), no jargon to define (cond-10 trivially passes), no images/color cues (cond-11 n/a), and is trivially findable (cond-12). Judge **coverage of the goals the upstreams actually carry + accuracy + a non-technical reader can follow it**, not section count or word count. A small, complete guide that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity. (The hard floor in condition 1 still holds at any size: a goal the upstreams carry must have a how-to.)

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A real (non-technical) user can accomplish every supported goal from the guide as written; the modes are correctly typed; the steps match the product and name controls correctly; the language is followable. Approve even if you can imagine wording improvements; the bar is usability + accuracy, not perfection — and not maximalism.
- **revise** — one or more conditions have a real, named gap that blocks a user (a goal with no how-to, a conflated/mistyped Diataxis mode, an incomplete reference, a fabricated/inaccurate/mislabeled step, an undocumented known error state, an incomplete amend staleness-sweep, unexplained jargon, a color-/location-only instruction, no start-here a reader can navigate from, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition (by number), the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Goal coverage (cond. 1): the user-flows carry a "Reset password" goal but the guide has no how-to for it. Fix: add a task-oriented "Reset your password" how-to (numbered steps from the flow's happy path).

> **revise** — Plain language (cond. 10), "Configure SSO" how-to: step 2 says "provision the IdP via SAML metadata" with no definition of IdP/SAML for the non-technical reader. Fix: define IdP and SAML on first use (and in the glossary), or restate the step in plain language.

A bad finding is vague and unactionable:

> The guide could be clearer. *(Which goal? Which mode? Which step? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the guide. The producer revises.
- **Single-sourced bar.** Judge against the twelve conditions in Step 2 — the same bar the author produces to, numbered identically. Do not invent extra conditions or apply a stricter private standard.
- **No false-revise.** A guide that meets every applicable condition is approved, even a thin one for a small product. Proportional sizing that still covers the goals is not a defect. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Honor the two overlap guards.** Do not double-penalize: a jargon/readability defect is cond-10 (not also cond-7); a navigation/findability defect is cond-12 (not also cond-1/cond-2). A single defect yields a single finding under the condition that owns it.
- **Enumerate goals from whatever upstream was handed in.** Take goals from the **user-flows when present, else the feature-spec/PRD** — never assume user-flows is always there. A **not-produced** upstream is **never** a revise trigger; flag its absence as an assumption. But a guide that **ignored a produced upstream** (a goal in the handed-in user-flows with no how-to, a step that contradicts the handed-in feature-spec) **is** a fair finding.
- **The reference is the end-user product surface, not the HTTP API.** Judge completeness over features/settings/CLI commands the product exposes (cond. 3); do not fault it for omitting endpoints.
- **Fabrication is a hard fail.** An invented step, setting, screen, or feature with no upstream basis fails condition 4 — a real gap should be flagged as an assumption (cond. 8), not papered over with an invented step. A step left describing a removed/renamed capability after an amend is fabrication-by-staleness (cond. 9).
- **Every revise finding is actionable** — failed condition + location + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of usability.** Every section can be present and a user still stuck (a how-to that is really an explanation, a step that contradicts the product, a goal with no recipe, jargon the audience can't follow). Judge whether a real user can *accomplish every goal*, not whether the *template is filled*.
- **The mistyped mode.** The single most common defect: a "how-to" that is three paragraphs of background with no steps (an explanation in disguise), or a tutorial that offers branching choices (a how-to/reference in disguise). Read each section for what it *is*, not what it is *titled* (cond. 2).
- **The orphan how-to that signals a fabricated feature.** A how-to for a goal no handed-in upstream carries often means an invented feature/screen leaked in (cond. 1 + cond. 4). Trace every how-to back to an upstream goal.
- **A step that names the wrong control.** "Click Save" when the product's button reads "Apply" blocks a non-technical user — a label mismatch is a cond-4 accuracy gap, not a nitpick.
- **Reference-as-API confusion.** Faulting the end-user reference for omitting HTTP endpoints, or accepting an endpoint catalog as the end-user reference — the end-user reference is the **product surface** (cond. 3).
- **Step accuracy without a running product.** You can't click through the live product — but you *can* spot-check each step against the handed-in feature-spec/user-flows (cond. 4). A step with no upstream basis presented as fact (rather than flagged as an assumption) is the gap.
- **Troubleshooting organized by cause, not symptom.** A troubleshooting section can list every internal error code yet still fail the user who only sees a *symptom* ("the page won't load"). Entries must be findable by the user-visible symptom -> cause -> fix (cond. 6).
- **Double-penalizing across the overlap guards.** Flagging one unexplained acronym under BOTH cond-10 and cond-7, or a missing start-here under BOTH cond-12 and cond-1 — one defect, one condition. The guards exist precisely to stop this.
- **Readability-score gating.** Demanding a specific Flesch-Kincaid / grade-level number — cond-10 is judged by whether a non-technical reader can follow it, not a score (a score is an authoring aid).
- **Over-strict accessibility on a thin guide.** A guide with two links and no images trivially passes cond-11; faulting it for "no alt text" when it has no images is a false-revise. Cond-11 is proportional and excludes pixel-contrast (the design-system's job).
- **Incomplete amend sweep waved through.** On an amend, one updated screen is not the sweep — a stale reference surviving in another mode (a glossary term, a troubleshooting entry) fails cond. 9. Check every mode.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct, judging sound guides as defective. Calibrate to the bar: a condition is a gap only on a *named, real* deficiency, not on phrasing you'd have chosen differently.
- **False-revise on a proportionally-sized guide.** A thin product's guide is correctly small — a handful of how-tos, collapsed sections, no changelog on a first draft. That is right-sizing, not under-documentation.
- **Faulting markdown for not being a help site.** The artifact is **textual** (screens described in words + wireframe links). Judge the description and the link, not the absence of pixels.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — a mistyped mode, a fabricated step, an unswept amend, or unexplained jargon waved through becomes a stuck or misled user.
- **Nit-pick revise.** Blocking on word choice, heading taste, or nice-to-haves dressed up as gaps. Revise is for real usability/accuracy blockers only.
- **Silent rewrite.** "It was easier to just fix the step" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** Adding a private requirement the bar does not carry ("it should also include a video / a marketing intro / a specific reading-grade score"). Judge the twelve conditions only; minimalism, navigation-category quality, alt-text technique, and the section-set are aids judged by outcome, never demanded.
- **Inventing an upstream expectation.** Faulting the guide for not covering a goal that lives only in a document the project never produced. A missing upstream is an assumption, not a revise.
- **Maximalism.** Demanding the full broad section set (or a changelog, or a glossary) from a thin product's guide. The bar is goal coverage + accuracy + followability, not the largest possible guide.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one end-user guide:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition number + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce->review loop: `approve` accepts the guide as ready for its users; `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **user-guide-authoring** skill — the produce half of the pair; it writes the guide to the same 12-condition usability + accuracy bar this skill judges against. Produce-side and review-side are **single-sourced**: this skill writes the bar out in `references/usability-bar.md`, and the author produces to the same bar — numbered identically — in its Step-10 self-check, so they do not drift.
- A **developer-guide-review** skill — the gate for the developer adoption/integration guide (SDK/library/CLI/framework/API-platform onboarding). Distinct doc, distinct audience; this skill judges the **end-user product** guide, not the developer onboarding narrative.
- An **api-reference-review** skill — the gate for the developer-facing HTTP/SDK endpoint catalog (contract-consistency). Distinct doc, distinct bar; the end-user reference judged here is the product surface, not the API.
- A **design-review** skill — the gate for engineering design documents (architecture specs, design docs, ADRs, RFCs), which verifies claims against the codebase. Distinct gate, distinct bar; not for an end-user guide.
- A **user-guide template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/usability-bar.md` — the single-sourced 12-condition bar in depth: each condition's pass/gap signals + worked findings (the new cond-9 amend staleness-sweep, cond-10 plain-language, cond-11 accessibility, cond-12 findability, and the deepened cond-4/5 UI-terminology), and the two overlap guards. Load when judging a borderline condition.
- `references/sources.md` — research provenance for the review method (the single-sourced quality bar: Diataxis four-mode typing, the per-goal how-to coverage rule, the procedure-mechanics conventions, plain-language + WCAG-for-docs grounding, and the reviewer-overcorrection evidence behind the no-false-revise discipline). Load only to audit where the guidance came from.

## Body budget

- `description` <= 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body <= ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.

## Changelog

- **1.1.0** (2026-06-15) — production-grade restructure: single-sourced 12-condition bar (8 → 12; added cond-9 amend, cond-10 plain-language, cond-11 accessibility, cond-12 findability; deepened cond-4/5 with UI-terminology; migrated the jargon clause from cond-7 to cond-10) with two explicit overlap guards (cond-10↔cond-7, cond-12↔cond-1/cond-2) and per-condition proportionality; added `references/usability-bar.md`; re-grounded the bar onto the per-pair provenance. Additive — `VERDICT` output + input contract unchanged. (1.0.0 → 1.1.0.)
</content>
