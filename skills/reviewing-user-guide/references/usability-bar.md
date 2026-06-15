# The single-sourced 12-condition usability + accuracy bar

The bar `reviewing-user-guide` judges against — **identical to the author's Step-10
self-check in `authoring-user-guide`, numbered the same** (produce-side and review-side do
not drift). This file carries each condition's pass/gap signals + a worked finding, plus the
two overlap guards. Load when a condition is borderline. Grounded per `sources.md`.

## How to use this file

For each condition: **pass** unless there is a *real, named* deficiency. A condition is a
gap only when a real user is blocked or misled — not on phrasing you'd have chosen
differently. Every revise finding names the **condition number + location + concrete fix**.

## The 12 conditions

**1. Goal coverage — one how-to per goal, no orphans.**
- *Pass:* every user goal in the handed-in upstreams (user-flows when present, else
  feature-spec/PRD) has exactly one task how-to; every how-to traces to a goal.
- *Gap:* a goal with no how-to (coverage hole); a how-to with no upstream goal (orphan — may
  signal an invented feature, cross-check cond-4).
- *Finding:* "revise — Goal coverage (cond. 1): user-flows carry 'Reset password' but no
  how-to exists. Fix: add a 'Reset your password' how-to from the flow's happy path."

**2. Four Diataxis modes present AND correctly typed.**
- *Pass:* tutorial (one guaranteed path), how-to (imperative steps), explanation (no steps),
  reference (neutral + complete) — not conflated.
- *Gap:* a how-to written as a concept dump; an explanation that smuggles in steps; a
  tutorial that branches. (The #1 doc-confusion defect — read each section for what it *is*,
  not its title.)

**3. End-user feature/config reference complete.**
- *Pass:* every user-facing feature/setting/CLI command is documented; mirrors the product;
  describes, doesn't instruct.
- *Gap:* a user-facing feature/setting/command missing or stale. *Not a gap:* omitting HTTP
  endpoints — that's the api-reference, not this product surface.

**4. Steps accurate to the actual product behavior — incl. UI terminology.**
- *Pass:* every step matches a handed-in upstream behavior; controls named by their **exact
  product/design-system label**; no invented step/setting/screen.
- *Gap:* a step contradicting the upstream; a fabricated feature (hard fail); a control named
  by the wrong label ("Click Save" when the button reads "Apply").

**5. Procedure mechanics sound.**
- *Pass:* numbered steps, one action per step, second person, present tense, imperative,
  task-based headings, exact labels.
- *Gap:* unnumbered prose blobs; several actions per step; noun-phrase/feature-named headings.

**6. Troubleshooting covers the known error states.**
- *Pass:* every upstream error/recovery path is a symptom → cause → fix entry organized by
  user-visible symptom; FAQ + a "get more help" pointer.
- *Gap:* a known error state undocumented; entries keyed by internal cause the user can't
  navigate.

**7. Usable by the target audience.**
- *Pass:* a real (non-technical) user can accomplish every supported goal from the guide
  alone; prerequisites stated; screens described + wireframe-linked.
- *Gap:* an ambiguity, missing prerequisite, or undefined step blocks the user mid-task.
- *Overlap guard:* language comprehensibility (jargon/readability) is **cond-10**, not here.

**8. Assumptions/gaps surfaced.**
- *Pass:* where an upstream was absent/thin, the assumptions are stated (challengeable).
- *Gap:* a missing upstream answer fabricated to look complete instead of flagged.

**9. Amend is a scoped, swept, versioned delta** (n/a on a greenfield first build).
- *Detected by input signal:* an existing guide + a change request + the changed upstreams.
- *Pass:* the delta meets the bar on what it touched; the **staleness sweep is complete** —
  no changed/removed/renamed capability still referenced by a stale step / reference entry /
  screen link / troubleshooting entry / glossary term (a structural "find every reference"
  check across ALL modes); internal coherence holds (tutorial runs, modes typed, reference
  mirrors); revision-history updated; superseded/removed marked.
- *Gap:* an incomplete sweep (a stale reference survives in another mode — the most common
  amend defect); broken coherence; missing change-history; an unmarked removal.
- *Finding:* "revise — Amend (cond. 9): the 'Sharing' setting was renamed 'Visibility'
  upstream; the how-to was updated but the glossary + a troubleshooting entry still say
  'Sharing'. Fix: sweep and update both; add a revision-history row."

**10. Plain language / readability.**
- *Pass:* a non-technical reader can follow it — purpose-first; reasonable sentence length;
  every term/acronym defined on first use (collected in the glossary); no unexplained
  acronym; audience-fit reading level.
- *Gap:* unexplained jargon / a bare acronym blocks the reader mid-step.
- *Judged by OUTCOME, never a readability score* (a Flesch-Kincaid number is an author aid).
- *Overlap guard (vs cond-7):* a jargon/readability defect is cond-10; an unfollowable-flow /
  missing-prerequisite defect is cond-7. One defect → one finding under the owning condition.

**11. Accessibility (proportional).**
- *Pass:* meaningful link text (no bare "click here"); headings nest correctly; no step
  relies on color alone ("the green button") or location alone ("the button on the right");
  described screens carry alt-text intent.
- *Gap:* a bare-link / color-only / location-only instruction that blocks a reader who can't
  perceive the cue.
- *Proportional:* n/a where there are no links/images/color cues. **Out of scope:** pixel
  contrast, focus appearance, rendered search (the design-system / rendered docs-site owns
  them) — never revise here for them.

**12. Findability / start-here.**
- *Pass:* a first-time reader can **locate** the start-here (the tutorial) and their goal's
  section across the doc set without already knowing the product (a §1 signpost / navigable
  structure).
- *Gap:* no start-here orientation and a reader can't tell which document answers their
  question.
- *Overlap guard (vs cond-1/cond-2):* findability is whether the reader can *locate* the
  sections — distinct from cond-1 (the guide is *organized* by goal) and cond-2 (the modes
  are *typed*). Trivially holds for a one-page guide; do NOT re-flag under cond-12 a defect
  already caught by cond-1/cond-2.

## Proportionality (the no-false-revise guard)

The bar scales with the product. A thin product's guide legitimately: collapses sections it
doesn't need; has nothing to amend (cond-9 n/a on first build); has no jargon to define
(cond-10 trivially passes); has no images/color cues (cond-11 n/a); is trivially findable
(cond-12). Judge coverage of the goals the upstreams carry + accuracy + followability — not
section/word count. A small complete guide that satisfies every *applicable* condition
passes. The only hard floor at any size: a goal the upstreams carry must have a how-to
(cond-1).

## The two overlap guards (load-bearing — stop the double-penalty)

- **cond-10 ↔ cond-7.** A jargon/readability defect is cond-10; an unfollowable-flow /
  missing-prerequisite defect is cond-7. Never flag one unexplained acronym under both.
- **cond-12 ↔ cond-1/cond-2.** A navigation/findability defect is cond-12; a coverage defect
  is cond-1; a mode-typing defect is cond-2. Never flag one missing start-here under both.

A single defect yields a single finding under the condition that owns it.
</content>
