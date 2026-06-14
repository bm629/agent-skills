---
name: reviewing-wireframes
description: >
  Use when reviewing/judging a finished (or amended) wireframes document — an
  acceptance gate: can the downstream hi-fi + UI engineering build the screen
  structure from it. Judges a TEXTUAL markdown wireframe against a single-sourced
  buildability + coverage + composition bar: every flow-named screen/state covered
  with quality states; layout
  unambiguous on a grid + shared app-shell meeting an objective layout-quality
  bar; real + consistent components; affordances + data-display annotated;
  microcopy intent (no data-model leak in labels); screen-composition a11y
  (landmarks/focus-order/target-size) — pixel contrast/focus-appearance are the
  design-system's, not judged here; responsive; gaps surfaced; structural not
  hi-fi; an amend reviewed as a scoped versioned delta. Emits `VERDICT:
  approve|revise` + actionable findings; approves a doc meeting the bar (no
  false-revise on a thin screen), revises only on a named gap. Not for authoring,
  the navigation graph (user-flows), the visual tokens (design-system), or hi-fi.
extensions:
  claude:
    when_to_use: "judging a finished (or amended) wireframes document against the buildability + composition bar and emitting an approve/revise verdict"
    argument-hint: "<the finished wireframes doc; plus the upstream user-flows and design-system if available>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-14
---

# `reviewing-wireframes` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) wireframes document as an acceptance gate — checking it is buildable, covered, and well-composed vs the upstream flows, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging wireframes pair. Loaded by a reviewer who has a **finished wireframes document** in hand, it judges that document against one question: **can the downstream hi-fi pass + UI engineering build the screen structure from it, with every flow-named screen and state covered and each screen well-composed?** It applies a fixed **buildability + coverage + composition checklist** — the same bar `authoring-wireframes` produces to, single-sourced so produce-bar and review-bar don't drift — then emits a single machine-parseable verdict plus findings the producer can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or redraw; it judges and returns findings.

A wireframe here is **low-to-mid fidelity and structural**, expressed in text as a **structured layout description + an ASCII/markdown box sketch + per-element annotations** — not a pixel mockup and not a binary design file. The method is **medium-independent**: the artifact today is markdown, and a future design-tool backend changes only the medium, not the checklist below.

The reviewer is given the wireframes doc and, **when available**, two cross-check inputs: the **upstream user-flows** (to verify screen coverage) and the **design-system** (to verify components are real + consistent and that the doc didn't re-judge the per-component a11y contract). When a cross-check input is absent, judge from the doc's own screen inventory + component references and note the missing input rather than inventing the comparison.

## When to activate

- A finished wireframes document needs an accept/revise decision before the downstream hi-fi pass / UI engineering begins.
- You are the independent reviewer / gate for a wireframes doc a producer just authored.
- Re-judging a revised wireframes doc after a prior `revise`, or reviewing an **amended** doc as a scoped delta (see cond. 13).

**Do NOT activate when:**

- Authoring or repairing a wireframes doc → use `authoring-wireframes`. This skill never writes or redraws.
- Judging the **navigation graph / paths between screens** → that is the upstream **user-flows** concern (`reviewing-user-flows`). This skill judges per-screen layout + coverage.
- Judging the **visual token system / component catalog** or the **per-component a11y contract** (contrast, focus-appearance, the component's own target-size/keyboard) → that is the **design-system** concern. This skill checks that wireframe components *reference* the DS consistently and that the doc *reserves* screen-composition a11y — not whether the DS itself is sound.
- Judging high-fidelity visual design / final pixels, color, type, motion → that is the downstream **hi-fi** pass, out of a structural wireframe's scope.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole wireframes doc with fresh, independent eyes

Read it end to end without the author's framing. Your stance is a gatekeeper for the *next* step (hi-fi + UI engineering build): a finding carries weight only when it shows the screen structure cannot be built as written, a flow-named screen/state is missing, or the composition fails the objective bar. If the upstream user-flows and/or the design-system were provided, skim them now so Step 2 can cross-check coverage + component consistency.

### Step 2: Run the checklist — judge each condition

For each condition below decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have laid it out differently" is **not** a gap (the bar is objective). Capture the exact location (which screen / which state) for each gap (Step 4 turns it into a finding). Each condition is **proportional to the screen's archetype** — a thin/static screen legitimately collapses conditions it doesn't need; do not manufacture a gap from brevity.

1. **Full screen coverage.** Every flow-named screen + implied state-transition has a wireframe. *Gap* when one has none (cross-check the user-flows; if absent, check the doc's own inventory + note the missing input). *Non-collapsing baseline.*
2. **All applicable per-screen states + quality.** empty/loading/populated/error + success where a state-change occurs (+ partial where relevant). *Quality*, not just presence: loading = a skeleton mirroring the layout (not a bare spinner) where known; empty = reason + guide-to-action; error = plain-language cause + recovery. *Gap* when an applicable state is missing or a present state is empty-shell. *Collapse:* a static screen has only populated.
3. **Layout & composition unambiguous.** Regions + content priority clear enough to build without guessing; on a grid; in the **one shared app-shell** (no per-screen re-invention). *Gap* when two engineers would build two different structures, or a screen re-invents/drops the shell. *Collapse:* a one-element screen needs no grid discussion.
4. **Layout quality (objective).** Primary action on the scan path, related elements grouped, no gratuitous region/element, consistency with sibling screens. *Gap* only on an **objective** failure (primary action buried, unrelated items jammed together, a redundant region, a sibling screen laid out inconsistently). Subjective taste ("a nicer layout exists") is **NOT** a gap. *Collapse:* a trivial screen trivially holds.
5. **Components identified + consistent + real.** Each notable element names its DS component (where one exists); reused components consistent; **none invented**; anatomy used. *Gap* on an unidentified blob, inconsistent naming, or an invented component/token presented as decided. *Non-collapsing baseline (no-invention).*
6. **Affordances + data-display annotated.** Every interactive element's behavior + destination + edge cases annotated; data-dense screens specify their table/list/card choice + controls (sort/filter/paginate/density/expansion) + progressive disclosure; forms use structured inputs (no serialized-string fields). *Gap* when a control's behavior must be guessed, or a data table is an unstructured "a table goes here". *Collapse:* a static screen has no data/forms.
7. **Content & microcopy intent.** Load-bearing text slots state their intent; **no raw data-model identifier as a label** (human label + description); persistent labels (placeholder ≠ label); terminology consistent across screens; i18n expansion room where localized. *Gap* on a data-model leak in a label, a placeholder-as-label, or terminology drift. *Baseline:* the no-data-model-leak label rule + terminology consistency are non-collapsing; i18n collapses for single-locale (with a stated reason).
8. **Responsive considered.** For screens where form-factor matters, the reflow mechanism (stack/collapse/hide/reorder) + mobile content-priority + adaptive nav + touch-target reservation are stated. *Gap* when a screen that clearly reflows says nothing about how. *Collapse:* a single-form-factor surface (stated reason) or a screen with no meaningful reflow.
9. **Screen-composition accessibility.** Landmarks, one-h1 heading order, reading/focus order, accessible names (incl. icon-only), keyboard-operability, ≥24px target-size **reservation**, focus-not-obscured (where sticky), non-color-only intent. **Pixel contrast + focus-appearance + the per-component target-size/keyboard are NOT judged here — they are the design-system's contract; grading them is out-of-lane.** *Gap* when a screen with interactive controls has no composition-a11y annotation, an icon-only control has no accessible name, or a required action is mouse-only. *Baseline:* landmarks + one h1 + names + keyboard apply at any size; the rest where present.
10. **Annotation, handoff & sketch-sync.** Notation legend defined; every load-bearing element annotated (how-it-works, not just drawn); elements map to DS components (the design-to-code handoff); **sketch ⇄ annotations in sync** (no orphan annotation, no un-annotated element). *Gap* on a static un-annotated sketch or a sketch/annotation mismatch. *Baseline:* sketch⇄annotation sync + buildable handoff are non-collapsing.
11. **Gaps surfaced, not invented.** Undefined screens/content, missing DS components, and deferred component-contract a11y (no DS/hi-fi) are explicit assumptions/open-questions, not silently filled/dropped. *Gap* when the doc papers over an undefined screen/component by inventing one as decided. An honestly-labelled assumption is **not** a gap.
12. **Structural, not hi-fi.** Lo-to-mid fidelity — layout + annotation; no final pixels, color, or type. *Gap* when it overshoots into hi-fi (exact colors/type/pixel spacing) and steps on the hi-fi/design-system scope. *Non-collapsing baseline.*
13. **Delta-scoped review (amended docs only).** When reviewing an amendment, review the **diff**, not the whole doc: scope-confined (untouched screens unchanged); ripple-clean (a shared-region change reached **all** reusing screens; no inventory row orphaned; no flow-named screen newly uncovered; no component-name drift; sketch⇄annotations still in sync; referenced DS components still real/non-deprecated); the doc's own version bump correct for the change class; a breaking removal carries deprecation; changelog matches the diff. *Gap* on any of these. *N/A* for a greenfield first build.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. The structure can be built as written, every flow-named screen + state is covered, and the composition meets the objective bar. Approve even if you can imagine layout improvements; the bar is buildability + coverage + objective composition, not perfection.
- **revise** — one or more conditions have a real, named gap (a missing/empty state, an invented component, an ambiguous layout, a buried primary action, a data-model-leak label, no composition-a11y, a hi-fi overshoot, an uncovered flow-named screen, a bad delta).

Do not revise to signal effort or request nice-to-haves; do not revise on subjective layout taste (cond. 4) or on pixel-contrast the design-system owns (cond. 9). A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location (which screen / which state), and **how to fix it** — so the producer resolves it in one pass. On `approve`, findings are optional non-blocking notes.

A good finding names the gap and the fix:

> **revise** — Per-screen states (cond. 2): the Dashboard screen documents only the populated view; empty, loading, and error are missing. Fix: add empty (zero-items message + create CTA), loading (skeleton mirroring the populated layout), error (message placement + retry, inline vs blocking).

A bad finding is vague: *"The Dashboard could use more states."*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, redraw, or fill in. The producer revises.
- **Single-sourced bar.** Judge against the conditions in Step 2 — the same bar the author produces to. No private stricter standard, no invented extra condition.
- **No false-revise.** A doc meeting every applicable condition is approved, even a thin one with proportionally collapsed screens. Revise only on a real, named gap. Subjective layout taste (cond. 4) is never a gap.
- **No false-approve.** A missing state, invented component, uncovered flow-named screen, data-model-leak label, or hi-fi overshoot is a `revise`.
- **Coverage is keyed to the flows.** A flow-named screen/state with no wireframe is a `revise`. Where the flows weren't provided, judge the doc's own inventory + note the missing cross-check.
- **Invented components/tokens are blocking.** A component/token the design-system doesn't define, presented as decided rather than flagged, is a `revise`.
- **Stay in lane on a11y.** Judge **screen-composition** a11y (cond. 9); do **not** grade pixel contrast, focus-appearance, or the per-component target-size/keyboard — those are the design-system's contract. Grading them is out-of-lane (drift), not rigor.
- **Judge against the upstreams the document was given.** A *not-produced* upstream is never a revise trigger. A *produced-but-ignored* upstream (a flow whose screens the wireframes don't cover; a DS whose components they invent past) **is** a fair finding.
- **Amend = delta review.** On an amendment, review the diff + ripple (cond. 13), not the whole doc; don't re-litigate untouched screens.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (missing screen/state, invented component, ambiguous layout, buried primary action), then minor (a thin microcopy note).
- Reference the condition number/name in each finding.
- Keep approve-notes few and clearly non-blocking.
- When a cross-check input (user-flows or design-system) is absent, say so once rather than silently assuming.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the doc still un-buildable (ambiguous regions, un-annotated affordances, a flow-named screen never drawn). Judge whether the *structure can be built + every flow-named screen is covered*, not whether the *template is filled*.
- **Missing the happy-path-only gap.** A screen with only the populated view silently omitting empty/loading/error/success is the most common defect.
- **Missing the flow-coverage gap.** A flow names a screen that never gets a wireframe — trace the flows → screens; the inventory table is where this surfaces (cond. 1).
- **Letting an invented component pass.** A confident component name the design-system doesn't define is drift — flag it (cond. 5).
- **Grading pixel contrast.** Revising because a contrast ratio isn't stated is out-of-lane — that's the design-system's contract; judge the *reserved non-color intent + composition*, not the pixel value (cond. 9).
- **Revising on layout taste.** "I'd have used cards" is subjective — cond. 4 is objective only (scan-path/grouping/no-gratuitous/consistency). Manufacturing a taste gap is a false-revise.
- **False-revise on a proportionally thin screen.** A static info screen legitimately has no loading/error, no grid discussion, no reflow. Calibrate to the archetype.
- **Drifting into hi-fi review.** Grading exact colors, type, or pixel spacing overshoots structural scope (cond. 12).
- **Re-reviewing the whole doc on an amend.** Review the diff + ripple (cond. 13); re-litigating untouched screens is noise.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph won't parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving — the gate exists to catch un-buildable/incomplete wireframes; a screen missing its error state waved through poisons the downstream build.
- **Nit-pick revise.** Blocking on layout taste, sketch aesthetics, pixel contrast, or nice-to-haves dressed as gaps. Revise is for real buildability/coverage/composition blockers only.
- **Silent redraw.** "Easier to just fix the sketch" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** "It should also pick final colors / a full component spec / a contrast ratio" — that drifts the bar into hi-fi + the design-system's lane.
- **Grading the wrong artifact.** Judging the navigation graph (user-flows) or the token catalog / component a11y contract (design-system) instead of the per-screen wireframes — stay in lane.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, one token.

## Output

A single review result for one wireframes document:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the wireframes doc for the next phase (downstream hi-fi + UI engineering); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- **`authoring-wireframes`** — the produce half; writes to the same buildability + coverage + composition bar this skill judges. Pairing single-sources the bar so produce + review don't drift.
- **`reviewing-user-flows`** — the sibling gate for the upstream navigation graph; the user-flows are a *cross-check input* here (screen coverage), not what this skill grades.
- **`reviewing-design-system`** — the sibling gate for the visual token system + component catalog + the **per-component a11y contract** (contrast, focus-appearance); the design-system is a *cross-check input* here (component consistency), not what this skill grades.
- A downstream **hi-fi** review — judges final visuals/pixels; this skill stops at structure.
- A **wireframes template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/buildability-bar.md` — the checklist conditions expanded with per-condition pass/gap signals + worked findings (incl. the a11y boundary + the layout-quality objective subset + the delta-review). Load when a borderline condition needs a sharper call.
- `references/sources.md` — research provenance for the method + the single-sourced bar (shared with the `authoring-wireframes` sibling).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
