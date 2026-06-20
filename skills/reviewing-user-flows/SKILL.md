---
name: reviewing-user-flows
description: >
  Use when reviewing/judging a finished user-flows document to decide whether a
  downstream wireframing pass can enumerate every screen and whether each path is
  complete, walkable, resilient, accessible, and sound — an acceptance gate, not
  authoring. A user-flows doc is the navigation/interaction graph: entries + IA frame,
  happy path, branches, error/recovery + edge states, resilience, flow-level
  accessibility, screens traversed. Judges it against a single-sourced bar: goals map
  to flows (no orphans), entries+exits defined, branches resolve, no dead ends, states
  (incl. loading+success) covered, irreversible actions guarded, every path keyboard/
  AT-completable, the flow objectively sound, notations synced, screens enumerable;
  plus a delta-scoped review when amending. Emits exactly `VERDICT: approve|revise` with
  actionable findings. Approves a doc meeting the bar (no false-revise on a thin one),
  revises only on a named gap. Not for authoring, not for wireframes, not for the PRD.
extensions:
  claude:
    when_to_use: "judging a finished user-flows document against the completeness + walkability + structure + resilience + accessibility + quality + amend bar and emitting an approve/revise verdict"
    argument-hint: "<the finished user-flows document to review (+ the prior version, when judging an amendment)>"
version: "1.3.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-13
---

# `reviewing-user-flows` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished user-flows document as an acceptance gate — checking it is complete, walkable, structured, resilient, accessible, and sound, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging user-flows pair. Loaded by a
reviewer who has a **finished user-flows document** in hand, it judges that document
against one question: **can a downstream wireframing pass enumerate every screen, and
can every path be walked, recovered, completed (incl. by an AT user), and is it a good
flow?** A user-flows doc maps the navigation/interaction graph — entry points + the IA
frame, the happy path, decision branches, error/recovery + edge states, interaction
resilience, flow-level accessibility, and the screens/states traversed. This skill
applies a fixed **checklist** (the same bar a user-flows author produces to, so the
produce-bar and review-bar do not drift), then emits a single machine-parseable verdict
plus findings the author can act on in one revision pass. It is an acceptance gate — it
does **not** author, fix, or redraw the flows; it judges and returns findings.

## When to activate

- A finished user-flows document needs an accept/revise decision before downstream
  wireframing begins.
- You are the independent reviewer / gate for a user-flows doc a producer just authored.
- Re-judging a revised user-flows doc after a prior `revise` verdict.
- **Judging an amendment** — a versioned delta against a prior user-flows doc (the
  delta-scoped review, condition 13).

**Do NOT activate when:**

- Authoring or repairing a user-flows doc → use `authoring-user-flows`. This skill never
  writes the flows.
- Reviewing **screen layout / structure** (region layout, content hierarchy, components
  per screen) or **per-screen pixel accessibility** (contrast, target size, focus
  appearance) → that is a wireframes-review skill. This gate judges how the screens
  *connect* and whether each path can be *completed*, not what a screen looks like.
- Reviewing the **upstream PRD** (goals, personas, metrics) → use a PRD-review skill.
- Checking template/section conformance → a template concern; this skill judges *quality
  against the bar*, not whether every heading is present.
- Judging a **user journey** (emotion/channel/over-time) — a different artifact.

## Workflow

### Step 1: Read the whole document with fresh, independent eyes

Read the user-flows doc end to end as if encountering it for the first time. Hold the
upstream PRD (goals + personas) alongside it — coverage is judged against those goals;
hold the design system (if one was given) for the nav/component references; on an
amendment, hold the **prior version** for the delta. Your stance is a gatekeeper for the
*next* step (wireframing) and for the user who must actually walk these paths: a finding
carries weight when it shows the screens cannot be enumerated, a path cannot be walked /
recovered / completed, an irreversible action is unguarded, or the flow is objectively
worse than the job needs. Note where a flow, branch, exit, or hand-off is load-bearing.

### Step 2: Run the checklist — judge each condition pass/gap

For each condition below, decide **pass** or **gap**. A condition fails only on a *real,
named* deficiency — "I'd have drawn it differently" is **not** a gap (the quality
conditions are objective only; see condition 12). For each gap, capture the exact
location (which flow, step, branch, node, hand-off) and what is missing (Step 4 turns it
into an actionable finding). Conditions scale with the product (see Proportionality).

The capability-boundary checklist item (below) applies ONLY when a `capability_record` was injected into the authoring invocation and is available as review context. When absent, treat it as n/a — do not penalise a document for lacking capability-boundary markers when no boundary was defined.

**Kept core (completeness + walkability):**

1. **Goal/persona coverage — no orphans.** Every PRD goal (framed as the job the persona
   is getting done) maps to a flow; every flow traces back to a goal/persona; standard
   flows are grounded in their established pattern (or the deviation is stated). A
   coverage map is present. *Gap* when a goal has no flow, a flow serves no goal, no
   coverage map, or a solved-problem flow is reinvented with no rationale.
2. **Defined entry + exit.** Every flow names all entry points (homepage, deep link,
   email, notification — each may start a different state) and a **concrete success/
   confirmation state** (not just an abstract "success"); alternate exits (cancel/
   abandon/hand-off) are clean. *Gap* when a flow begins in mid-air or ends with no
   concrete end state. *(Non-collapsing baseline: every flow has a success state.)*
3. **Every decision branch resolved.** Each decision lists **all** outgoing branches;
   each resolves to a step, another flow, or an exit. *Gap* on a dangling side or a
   branch that points nowhere.
4. **Every error/edge state has a recovery — no dead ends.** Where applicable: empty/
   null, invalid input, timeout/network/integration, interruption/session-loss,
   permission/auth, back/cancel — each routes back to a productive step; plus the
   **loading/in-progress** state on every async step and the **success/confirmation**
   state. No state strands the user; load-bearing states carry **message intent** —
   error = cause+fix, empty = guide-to-action, success = the result. *Gap* when an
   applicable state is missing, an error path dead-ends, an async step leaps to success
   with no loading state, an error lacks a recovery, or a load-bearing state's message
   intent is unspecified where it matters.
5. **Steps unambiguous + walkable.** A reader follows the narrative without guessing;
   each step names its screen/state + the user action; labels present. *Gap* on an
   ambiguous step or unlabelled node.
6. **Both notations in sync.** Every flow has a Mermaid flowchart AND a numbered
   narrative + branch/error list, same graph; **multi-actor flows use swimlanes**. *Gap*
   when one notation is missing, a node/branch drifts between them, or a multi-actor
   flow hides who-does-what in one undifferentiated lane.
7. **Screens enumerable for wireframing.** The screens index is the complete union of
   every flow's screens/states (incl. loading + success), each with **one canonical
   name** used identically across diagram/narrative/index, nothing orphaned. *Gap* on a
   referenced screen missing from the index, a name that drifts, an orphaned index
   entry, or no index. *(Non-collapsing baseline: the naming + index enumeration.)*
8. **Assumptions/open questions surfaced; flow not journey.** Thin-PRD assumptions are
   stated (challengeable), open questions listed, no silent product decision; the doc
   stays the interaction graph (no emotion/channel-per-step). *Gap* on a buried
   decision, or journey content presented as part of the flow. *(Non-collapsing
   baseline: the flow-vs-journey boundary.)*

**New (structure, resilience, accessibility, quality, amend):**

9. **Navigation & IA frame** (where applicable). The nav/app-shell model + wayfinding is
   present for a multi-surface product; deep-linking (+ prereq guard/resume) and
   cross-device path divergence are addressed where they apply; every **cross-flow
   hand-off resolves to a defined flow** and no flow is orphaned (unreachable + exits
   nowhere). *Gap* on a hand-off to a removed/undefined flow, or a multi-surface product
   whose flows ignore its nav model / a real device divergence. *Collapse:* a
   single-screen / single-flow tool has no app shell, no cross-flow graph, one entry —
   not a gap.
10. **Interaction resilience** (where applicable). Every irreversible/destructive action
    carries a **confirm or undo**; each multi-step flow states resume-vs-restart;
    state-changing steps show **what changed**; optimistic actions define a revert+
    feedback path (and aren't used for payments/deletes). *Gap* on an unguarded
    irreversible action, a silent state-change, a long flow with no stated interruption
    behavior, or an unsafe/revert-less optimistic action. *Collapse:* a read-only flow
    has nothing to guard/persist/confirm — not a gap.
11. **Flow-level accessibility.** Every path is **keyboard-completable** (no trap) and
    **AT-completable** (errors announced, not color/position-only); focus-order is
    managed on step/route change (WCAG 2.2 SC 2.4.3); no required step is mouse-only/
    gesture-only. *Gap* on a mouse-only required step, an error perceivable only
    visually (AT user stranded), or unmanaged focus on step change. *(Non-collapsing
    baseline: keyboard-operable; cross-step focus concern is lighter on a single-screen
    flow but the path must still be keyboard/AT-completable.)* Per-screen pixel WCAG
    (contrast/target-size) is **out of scope** here — that is wireframes/DS.
12. **Flow quality (objective only).** No gratuitous step (the path is no longer than the
    job needs — path-length is judged here, once); irreversible actions are **prevented**
    (guard before the act), not only recovered; no step forces **recall** of what a prior
    step established without carry-forward; like jobs use **consistent** paths. *Gap* on a
    materially-over-long path with no reason, an unprevented irreversible action, a
    cross-step recall burden, or unjustified inconsistency between like flows.
    **Subjective preference is NOT a gap** — "a nicer flow exists" never triggers a
    revise. *Collapse:* a trivial flow trivially holds.
13. **Delta-scoped review** (only when judging an amendment). Review the **diff + its
    ripple**, not the whole doc: untouched flows are unchanged (no unscoped regenerate);
    no cross-flow hand-off points at a removed/renamed flow; no screens-index entry
    orphaned/missing; no previously-reachable path newly stranded; diagram⇄narrative
    synced on the edit; the doc's version bump matches the change class (MAJOR removed/
    renamed flow or removed reachable path · MINOR added · PATCH wording) and the
    changelog matches the diff; breaking removals carry deprecation. *Gap* on any of
    these. *Collapse:* a greenfield first build does not exercise this condition.

14. **Capability routing (n/a when no capability records):** each cross-capability transition explicitly labels the source and target capability IDs; `entry_point`/`exit_point` labels match the capability records.

### Step 3: Decide the verdict

- **approve** — every *applicable* condition passes. A wireframing pass can enumerate
  every screen and walk every path; the path is recoverable, resilient, completable
  (incl. by an AT user), and objectively sound, as written. Approve it even if you can
  imagine stylistic improvements; the bar is the checklist, not perfection.
- **revise** — one or more conditions have a real, named gap (an orphan goal, a flow with
  no entry, a dangling branch, a dead-end error path, a missing loading/success state, an
  unguarded irreversible action, a mouse-only required step, an AT-stranded error, a
  gratuitous-length path, a hand-off to a removed flow, the diagram/narrative out of
  sync, a screen missing from the index, a mis-versioned amendment, etc.).

Do not revise to signal effort or to request nice-to-haves, and never on subjective
taste. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or
`VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or
extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then list findings. On `revise`, every finding is **actionable** — the failed condition,
the exact location, and **how to fix it** — so the author can resolve it in one pass. On
`approve`, findings are optional non-blocking notes.

A good finding names the gap and the fix:

> **revise** — Resilience (cond. 10): in Flow 3 (Account settings), "Delete account" goes
> straight from the button to a success state with no confirm or undo. Fix: add a confirm
> step (or a recoverable soft-delete with undo) before the irreversible deletion, and
> show what was deleted.

> **revise** — Flow accessibility (cond. 11): in Flow 2 (Onboarding), the "reorder
> priorities" step is drag-only with no keyboard alternative, so a keyboard/AT user can't
> complete the path. Fix: add a keyboard-operable reorder (move up/down controls) and
> ensure focus moves to the reordered item.

A bad finding is vague and unactionable:

> The flow could be more robust. *(Which flow? Which condition? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that
  literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not redraw, fix, or fill in the flows.
- **Single-sourced bar.** Judge against the 14 conditions in Step 2 — the same bar the
  author produces to. Do not invent extra conditions or a stricter private standard. In
  particular, condition 12 is **objective only**: subjective preference is never a gap.
- **No false-revise.** A doc that meets every *applicable* condition is approved, even a
  small one for a simple product. Revise only on a real, named gap. The new conditions
  (9–13) each **collapse** on a thin archetype (see Proportionality) — do not manufacture
  a gap from a thin flow legitimately omitting an inapplicable section.
- **No false-approve.** Never approve over a genuine gap. A dead-end path, an orphan goal,
  an unguarded irreversible action, an AT-stranded error, a screen missing from the
  index, or a hand-off to a removed flow is a `revise`.
- **Dead ends + unguarded irreversible actions are blocking.** A path that strands the
  user, or an irreversible action with no confirm/undo, is always a `revise`.
- **F5/F6 boundary.** Per-screen pixel WCAG (contrast/target-size/focus-appearance) is a
  wireframes/DS concern, not condition 11; path-length is judged once, in condition 12,
  not re-judged in 11.
- **Judge against the upstreams the document was given.** Assess against its `depends_on`
  set; a **not-produced** upstream is **never** a revise trigger; a document that ignored
  a **produced** upstream it should have drawn on **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps (dead ends, unguarded irreversible actions,
  orphan goals, missing screens, AT-stranded errors) first, then minor ones.
- Reference the condition number/name in each finding so the author maps it to the bar.
- When citing a location, name the flow + the specific node/step/branch/hand-off.
- Keep approve-notes few and clearly non-blocking.

## Proportionality

"Good enough to wireframe from + walkable + resilient + accessible + sound" scales with
the product. A simple product legitimately has few flows, few edge states, no app shell,
no resilience block — a small, complete doc satisfying every *applicable* condition
**passes**. The new conditions collapse on a thin archetype: **9** (no app shell /
cross-flow graph on a single-screen tool), **10** (nothing to guard on a read-only flow),
**11** (lighter cross-step focus on a single-screen flow, but still keyboard/AT-
completable), **12** (a trivial flow trivially holds), **13** (greenfield doesn't
exercise the delta review). Four conditions are **non-collapsing baseline** — they apply
at every size because the flow is broken without them at any size: cond-2 (a concrete
success state), cond-7 (canonical naming + screens enumeration), cond-8 (flow not
journey), cond-11 keyboard-operability. Judge completeness/quality-of-paths, not flow
count; manufacturing a gap from brevity is the most common reviewer error here.

## Gotchas

- **Approving for completeness instead of walkability/resilience.** Every flow present
  and the doc still un-walkable — a branch with one side missing, an error with no
  recovery, a diagram that drifts, an unguarded delete, an AT-stranded error. Judge
  whether *every path can be walked, recovered, completed, and is sound*, not whether the
  template is filled.
- **Missing the dead-end / the unguarded irreversible.** Both hide on the *unhappy* path;
  the happy path always looks complete. Trace every branch + error to its terminus, and
  every irreversible action to its guard.
- **Missing the silent state-change / the missing loading state.** A step that mutates
  with no "what changed", or an async step that leaps to success, reads complete but is a
  gap (cond. 4/10).
- **One notation only.** Reading the diagram and skipping the narrative (or vice-versa)
  misses a sync defect by construction (cond. 6).
- **Importing pixel-WCAG into cond. 11.** Contrast/target-size are wireframes/DS, not
  flow-level a11y. Don't double-judge.
- **False-revise on a simple product.** A thin flow correctly omits the app-shell,
  resilience, or device-divergence it doesn't have; an inapplicable edge state is not a
  gap. The new conditions collapse — calibrate to product size.
- **Revising on taste (cond. 12).** "I'd design it differently" is never a gap. Condition
  12 is objective only.
- **Re-judging the whole doc on an amendment.** On an amendment, scope the review to the
  delta + ripple (cond. 13); don't re-litigate untouched flows.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a buried verdict won't
  parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming the happy paths and approving without tracing the
  unhappy ones, the irreversible actions, or the AT paths.
- **Nit-pick revise.** Blocking on diagram styling, node shape, or wording dressed up as
  gaps; or revising on subjective preference. Revise is for real, named blockers only.
- **Silent redraw.** Authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a private requirement the author never produced to
  (a journey "emotion per step", a subjective "nicer flow") drifts the review-bar off the
  produce-bar.
- **Judging layout, pixels, or goals.** Where a button sits / its contrast (wireframes/
  DS) or whether a goal is worth building (PRD) — out of scope for this gate.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision.

## Output

A single review result for one user-flows document:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own
  line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition +
  location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts
the user-flows doc for the next phase (wireframing); `revise` returns the findings to the
producer for a bounded revision pass.

## Related

- **`authoring-user-flows`** — the produce half; it writes the flows to the same bar this
  skill judges against. Pairing them single-sources the bar so produce and review do not
  drift.
- A **wireframes-review** skill — the sibling gate for the *next* document down (per-screen
  layout + per-screen pixel accessibility). Distinct gate, distinct bar; this skill judges
  the navigation graph + path completability that feeds it the screen list.
- A **PRD-review** skill — the gate for the *upstream* document (goals/personas/metrics).
  This skill checks coverage against those goals but does not re-judge them.
- A **user-flows template / content-template** tool — owns the section *structure*; this
  skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/completeness-walkability-bar.md` — the 13 conditions expanded with
  per-condition pass/gap signals, proportionality collapses, and worked finding examples.
  Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method, the flow-vs-journey
  boundary, the resilience/accessibility/quality conditions, and the delta-review.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined
  `description` + `when_to_use` at 1,536 chars in the listing.
- Body ~500 lines / 5,000 tokens (soft target — quality takes precedence; flag if consistently over 700 lines / 7,000 tokens) — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens,
  error >50k.
