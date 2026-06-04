---
name: reviewing-wireframes
description: >
  Use when reviewing or judging a finished wireframes document to decide whether
  downstream visual design and UI engineering can build the screen structure from it
  — an acceptance gate, not authoring. Judges a TEXTUAL markdown wireframe
  (layout description + ASCII/markdown box sketch + per-element annotations), not
  binary/Figma assets, against a single-sourced buildability + coverage bar: every
  flow-named screen and state has a wireframe, all four per-screen states
  (empty/loading/populated/error) are documented, layout and hierarchy are
  unambiguous, components are identified and design-system-consistent, affordances
  are annotated, responsive and a11y are considered, gaps are surfaced, and it
  stays structural not hi-fi. Emits exactly `VERDICT:
  approve|revise` plus actionable findings; approves a doc meeting the bar (no
  false-revise), revises only on a real, named gap. Not for authoring the doc, not
  for the navigation graph (user-flows review) or the visual tokens (design-system
  review), nor other document types.
extensions:
  claude:
    when_to_use: "judging a finished wireframes document against the buildability + coverage bar and emitting an approve/revise verdict"
    argument-hint: "<the finished wireframes doc; plus the upstream user-flows and design-system if available>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `reviewing-wireframes` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished wireframes document as an acceptance gate — checking it is buildable and complete vs the upstream flows, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging wireframes pair. Loaded by a reviewer who has a **finished wireframes document** in hand, it judges that document against one question: **can downstream visual design and UI engineering build the screen structure from it, with every flow-named screen and state covered?** It applies a fixed **buildability + coverage checklist** (the same bar the wireframes author produces to, so the produce-bar and review-bar do not drift), then emits a single machine-parseable verdict plus findings the producer can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or redraw the wireframes; it judges and returns findings, and the producer revises.

A wireframe here is **low-to-mid fidelity and structural**, expressed in text as a **structured layout description + an ASCII/markdown box sketch + per-element annotations** — not a pixel mockup and not a binary design file. The method is **medium-independent**: the artifact today is markdown, and a future design-tool backend changes only the medium, not the checklist below.

The reviewer is given the wireframes doc and, **when available**, two cross-check inputs: the **upstream user-flows** (to verify screen coverage — every flow-named screen and state-transition has a wireframe) and the **design-system** (to verify components are real and consistent, not invented). When a cross-check input is absent, judge coverage and consistency from the wireframes doc's own stated screen inventory and component references, and note the missing input rather than inventing the comparison.

## When to activate

- A finished wireframes document needs an accept/revise decision before downstream visual design / UI engineering begins.
- You are the independent reviewer / gate for a wireframes doc a producer just authored.
- Re-judging a revised wireframes doc after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a wireframes doc → use a wireframes-authoring skill. This skill never writes or redraws the wireframes.
- Judging the **navigation graph / the paths a user takes** between screens → that is the upstream **user-flows** concern; use a user-flows-review skill. This skill judges per-screen layout and coverage, not the flow graph itself.
- Judging the **visual token system or the component catalog** (color/type/spacing tokens, component anatomy/variants) → that is the **design-system** concern; use a design-system-review skill. This skill checks that wireframe components *reference* the design-system consistently, not whether the design-system itself is sound.
- Judging high-fidelity visual design / final pixels, color, or type → that is downstream visual design, out of a structural wireframe's scope.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole wireframes doc with fresh, independent eyes

Read the document end to end as if encountering it for the first time, without the author's framing. Your stance is a gatekeeper for the *next* step (visual design + UI engineering build): findings carry weight only when they show the screen structure cannot be built as written, or a flow-named screen/state is missing. If the upstream user-flows and/or the design-system were provided, skim them now so Step 2 can cross-check coverage and component consistency against them.

### Step 2: Run the buildability + coverage checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have laid it out differently" is not a gap. For each gap, capture the exact location (which screen / which state) and what is missing (Step 4 turns it into an actionable finding).

1. **Full screen coverage.** Every screen the upstream user-flows name — and every state-transition they imply — has a wireframe. No orphan screens, no coverage gaps vs the flows. *Gap* when a flow-named screen or an implied transition state has no wireframe (cross-check against the provided user-flows; if absent, check the doc's own screen inventory for internal completeness and note the missing input).
2. **All four per-screen states.** Each screen documents **empty, loading, populated, and error** — not just the happy/populated view. *Gap* when a screen shows only the populated view and omits one or more of empty / loading / error (the single most common wireframe gap).
3. **Unambiguous layout + content hierarchy.** Layout regions and content priority are clear enough to build the structure without guessing. *Gap* when a region's arrangement or the content ordering is ambiguous enough that two engineers would build two different structures.
4. **Components identified + consistent.** Each notable element names its component (the **design-system** component where one exists), reused components are consistent across screens, and **no components or visual tokens are invented**. *Gap* when an element is an unidentified blob, the same element is named inconsistently across screens, or a component/token is invented that the design-system does not define (cross-check against the provided design-system; if absent, check internal consistency and flag invented-looking names).
5. **Affordances annotated.** Every interactive element's behavior and destination is annotated — what it does on interaction (tap/hover/validation/conditional visibility), where it leads, and relevant edge cases (truncation, overflow, sorting, pagination, dropdown contents). *Gap* when the sketch is a static picture with elements a developer must guess the behavior of.
6. **Responsive considered.** For screens where it matters, the reflow across the target breakpoints is stated — what stacks, collapses, hides, or reorders. *Gap* when a screen that clearly reflows says nothing about how. A screen with no meaningful reflow need not belabor it; do not manufacture a gap.
7. **Accessibility considered.** Focus/reading order, labels/landmarks, and contrast / non-color-only intent are annotated. *Gap* when a screen with interactive controls has no a11y annotation at all.
8. **Gaps surfaced, not invented.** Undefined screens/content and missing design-system components are explicit **assumptions/open-questions**, not silently filled. *Gap* (and a notable one) when the doc papers over an undefined screen or a missing component by inventing a plausible one and presenting it as decided. An honestly-labelled assumption is **not** a gap.
9. **Structural, not hi-fi.** The doc stays low-to-mid fidelity — layout + annotation — with no final pixels, color, or type. *Gap* when it overshoots into hi-fi visual design (specifying exact colors, type, pixel spacing) and steps on the design-system's scope.

**Proportionality.** "Buildable enough" scales with the screen and the project. A trivial screen legitimately collapses conditions it does not need (a static info screen may have no meaningful loading/error state or reflow) — judge completeness-of-decisions for *that* screen, not a fixed word count. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. The screen structure can be built from this doc as written, and every flow-named screen + state is covered. Approve it even if you can imagine layout improvements; the bar is buildability + coverage, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks the build or leaves a flow-named screen/state uncovered (a missing per-screen state, an unidentified or invented component, an ambiguous layout, no a11y annotation, a flow-named screen with no wireframe, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location (which screen / which state), and **how to fix it** — so the producer can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Per-screen states (cond. 2): the Dashboard screen documents only the populated view; empty, loading, and error states are missing. Fix: add the three missing states — empty (zero-items message + the create CTA), loading (skeleton mirroring the populated layout), error (message placement + the retry affordance, inline vs blocking).

A bad finding is vague and unactionable:

> The Dashboard could use more states. *(Which states? Why does it fail? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, redraw, or fill in the wireframes. The producer revises.
- **Single-sourced bar.** Judge against the nine buildability + coverage conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or a stricter private standard.
- **No false-revise.** A doc that meets every applicable condition is approved, even a thin one with proportionally collapsed screens. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A missing state, an invented component, or an uncovered flow-named screen is a `revise`.
- **Coverage is keyed to the flows.** A screen or state-transition the upstream user-flows name with no wireframe is a coverage gap and a `revise`. Where the flows were not provided, judge the doc's own screen inventory and note the missing cross-check input.
- **Invented components/tokens are blocking.** A component or visual token the design-system does not define, presented as decided rather than flagged as an assumption, is a `revise` until referenced to a real component or surfaced as an open question.
- **Judge against the upstreams the document was given.** Assess the document against its `depends_on` set (the upstream documents the project actually produced). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a document that **ignored a produced upstream** it should have drawn on (e.g. a `depends_on` feature-spec whose behaviors the flows don't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location (screen/state) + concrete fix. No vague notes.
- **Stay in lane.** Don't grade the navigation graph (user-flows' job) or the visual token system / component catalog (design-system's job); judge per-screen layout, coverage, and consistency.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (missing screen/state, invented component, ambiguous layout), then minor ones (a thin a11y note).
- Reference the condition number/name in each finding so the producer maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.
- When a cross-check input (user-flows or design-system) is absent, say so once in the findings rather than silently assuming coverage/consistency.

## Gotchas

- **Approving for completeness instead of buildability.** Every per-screen section can be present and the doc still un-buildable (ambiguous regions, un-annotated affordances, a screen named by a flow but never drawn). Judge whether the *screen structure can be built and every flow-named screen is covered*, not whether the *template is filled*.
- **Missing the happy-path-only gap.** A screen that documents only the populated view and silently omits empty/loading/error is the most common defect — the states are where real UX lives. Check all four per screen (cond. 2), don't let a polished populated view distract you.
- **Missing the flow-coverage gap.** A flow names a screen (or implies a transition state) that never gets a wireframe. Trace the provided user-flows → screens before claiming done; the doc's screen inventory table is where this surfaces (cond. 1).
- **Letting an invented component pass.** A confident component name the design-system does not define is drift, not rigor — it breaks handoff. Cross-check against the design-system; flag invented-looking names as a gap, not a detail (cond. 4).
- **False-revise on a proportionally thin screen.** A static info screen legitimately has no meaningful loading/error state or reflow; collapsed conditions it doesn't need are not gaps. Manufacturing a gap from brevity is the most common reviewer error — calibrate to the screen.
- **Drifting into hi-fi review.** Grading exact colors, type, or pixel spacing both overshoots the structural scope and steps on the design-system's job. Judge structure + annotation; the visual tokens are the design-system's (cond. 9).
- **Drifting the bar.** Reviewing against your personal layout preferences instead of the nine conditions silently raises the bar above what the author produced to, causing avoidable revise loops. Stick to the shared checklist.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — the gate exists to catch un-buildable or incomplete wireframes; a screen missing its error state waved through poisons the downstream build.
- **Nit-pick revise.** Blocking on layout taste, sketch aesthetics, or nice-to-haves dressed up as gaps. Revise is for real buildability/coverage blockers only.
- **Silent redraw.** "It was easier to just fix the sketch" — authoring inside a review collapses the produce/judge separation and removes the producer's chance to learn the gap.
- **Inventing conditions.** "It should also pick final colors / a full component spec" when that isn't in the bar — that drifts the review-bar into hi-fi visual design and the design-system's scope.
- **Grading the wrong artifact.** Judging the navigation graph (user-flows) or the design tokens/component catalog (design-system) instead of the per-screen wireframes — stay in lane.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one wireframes document:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location (screen/state) + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the wireframes doc for the next phase (downstream visual design + UI engineering build); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **wireframes-authoring** skill — the produce half of the pair; it writes the wireframes to the same buildability + coverage bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **user-flows-review** skill — the sibling gate for the upstream navigation graph / paths. Distinct gate, distinct bar; the user-flows are a *cross-check input* here (for screen coverage), not what this skill grades.
- A **design-system-review** skill — the sibling gate for the visual token system + component catalog. Distinct gate, distinct bar; the design-system is a *cross-check input* here (for component consistency), not what this skill grades.
- A **wireframes template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/buildability-bar.md` — the nine checklist conditions expanded with per-condition pass/gap signals and worked finding examples. Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the method + the single-sourced bar (shared with the wireframes-authoring sibling).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
