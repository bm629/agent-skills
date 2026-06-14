---
name: reviewing-hi-fi
description: >
  Use when reviewing/judging a finished (or amended) high-fidelity UI design
  produced AS CODE — an acceptance gate: is the rendered hi-fi a sound build seed?
  The reviewer RE-RENDERS the code itself (headless browser) and vision-reviews the
  fresh screenshots — never trusting handed-in images. Judges a single-sourced bar:
  full coverage vs the wireframes;
  hi-fidelity + seed-not-over-built; visual execution + objective polish + named
  aesthetic heuristics (subjective taste never a gap); token-backed/no-DS-drift;
  real content (no lorem); rendered states; responsive reflow; NUMERIC WCAG 2.2 AA
  on the render (axe-core + vision, no rule disabled); gaps surfaced; an amend as a
  scoped versioned delta. Emits `VERDICT: approve|revise` + actionable findings;
  approves a seed meeting the bar (no false-revise on a thin screen), revises only
  on a named, rendered gap. Requires a vision-capable runtime. Not for authoring
  hi-fi, the structure (wireframes), the token system (design-system), or final code.
extensions:
  claude:
    when_to_use: "judging a finished (or amended) hi-fi code design by re-rendering + vision-reviewing it against the bar and emitting an approve/revise verdict"
    argument-hint: "<the finished hi-fi code/screens; plus the upstream wireframes + design-system if available>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-14
  reviewed: 2026-06-14
---

# `reviewing-hi-fi` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished (or amended) hi-fi design-as-code as an acceptance gate — re-rendering it, vision-reviewing the result against the bar, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging hi-fi pair. Loaded by a reviewer who has a **finished hi-fi (code + its screens)** in hand, it judges one question: **is this rendered hi-fi a sound build seed — covering every wireframe-named screen, visually realized to the bar, accessible on the render, and conformant to the design-system?** It applies a fixed **single-sourced checklist** — the same bar `authoring-hi-fi` produces to — then emits a single machine-parseable verdict plus findings the producer can act on in one pass. It is an acceptance gate — it does **not** author, fix, or re-render-to-improve; it judges and returns findings.

The artifact is **code that renders to pixels**. The reviewer's distinctive move: it **re-renders the code itself** (headless browser, `agent-browser`/Playwright), captures a **fresh screenshot per viewport × state**, and **vision-reviews that fresh render** — it never trusts a handed-in screenshot (which can be stale/cherry-picked) or grades the code by reading alone. This **requires a vision-capable runtime**; a text-only reviewer is degraded (it can read the code but cannot see the render) — say so, and flag if the artifact itself was produced blind.

Two boundaries: hi-fi owns **the rendered visuals + the numeric pixel-WCAG judgment** (the wireframe only reserved them); the **design-system** owns the per-component a11y *contract spec* — this gate judges whether the **rendered composed result achieves** it (spec-vs-realized; no double-judge). It judges *conformance to* the DS + wireframe, never grades them; and it judges a **seed**, not production code (don't revise for missing tests/real backend).

## When to activate

- A finished hi-fi design-as-code needs an accept/revise decision before the human visual gate / the build milestone.
- You are the independent reviewer / gate for a hi-fi a producer just rendered.
- Re-judging a revised hi-fi after a prior `revise`, or reviewing an **amended** hi-fi as a scoped delta (see cond. 13).

**Do NOT activate when:**

- Authoring or repairing a hi-fi → use `authoring-hi-fi`. This skill never writes or re-renders to improve.
- Judging the screen **structure** (layout regions, component selection, states-as-structure) → that is the upstream **wireframes** (`reviewing-wireframes`).
- Judging the **token system / component catalog / per-component a11y contract** → that is the **design-system** (`reviewing-design-system`); this gate checks the rendered result *conforms*.
- Re-deciding which screens/transitions exist → that is **user-flows**.
- Judging final **production code** (tests, real backend, perf) → this is a seed; the build phase owns that.

## Workflow

### Step 1: Re-render the code + read the whole hi-fi with fresh, independent eyes

Render the hi-fi code yourself at the target viewports and capture a fresh screenshot per state — **do not trust a handed-in screenshot**. If you cannot render (no headless browser) or cannot see the render (text-only runtime), say so: the review is **degraded** and you judge only what the code statically shows (flag it). Read the code + the screens end to end. If the upstream wireframes and/or design-system were provided, skim them so Step 2 can cross-check coverage + conformance.

### Step 2: Run the checklist — judge each condition on the RENDER

For each condition decide **pass** or **gap**, against the **fresh render** (not the code text alone). A condition fails only on a *real, named* deficiency — "I'd have used a different hue/layout" is **not** a gap (out-of-set subjective taste is excluded). Capture the exact location (which screen / which state / which viewport). Each condition is **proportional to the screen's archetype** — a thin/static screen legitimately collapses the interactive/stateful/responsive sub-checks; don't manufacture a gap from brevity.

1. **Full coverage vs the wireframes.** Every wireframe-named screen + flow-visited state is rendered. *Gap* when one is un-rendered (cross-check the wireframes; if absent, check the doc's own inventory + note the missing input). *Non-collapsing baseline.* (On an **amend**, the pre-existing inventory satisfies whole-artifact coverage — don't re-litigate untouched screens; cond-13 owns delta-introduced coverage regressions.)
2. **Fidelity + scope.** Hi-fidelity visuals reached (not wireframe-grey / default-browser styling); no invented structure/nav/screen beyond the wireframe; and it is judged as a **seed** — NOT revised for lacking tests/real-backend/routing, NOT approved if it claims production-readiness it isn't. *Non-collapsing baseline.*
3. **Visual execution + hierarchy.** The DS visual language is realized on the render (color/type/spacing/elevation/radius/icons/imagery); the primary element is visually dominant; hierarchy legible. *Gap* on a flat, undifferentiated, or unstyled screen. *Collapse:* a one-element screen needs little hierarchy.
4. **Polish — objective + named heuristics.** Objective: grid-aligned, consistent scale, no clipped/overlapping/orphaned element, on-token, sibling-consistent. Named heuristics (each articulable): balance, whitespace & restraint, spacing rhythm, focal clarity, aesthetic cohesion. *Gap* only on an objective failure OR a **named** heuristic failure (state WHICH heuristic + why). Subjective out-of-set taste ("a nicer hue/layout exists") is **NOT** a gap. *Collapse:* a trivial screen trivially holds.
5. **Token-backed / no DS drift.** Every visual value traces to a DS token (Tailwind token-utility / CSS var / shadcn token); no raw `#hex`/`px`/`bg-blue-500` bypassing a token; no local override of a DS token/component; a missing token/component is surfaced, not inlined. *Gap* on any off-token raw value or drift. *Non-collapsing baseline.*
6. **Rendered + vision-reviewed (by you).** You re-rendered the code, captured a fresh screenshot, and it renders without breakage + matches the wireframe structure + the DS. *Gap* when the screen fails to render, renders broken, or diverges from the wireframe. A review done off a handed-in image or code-read-only is incomplete. *Non-collapsing baseline (the mechanism IS the gate).*
7. **Content realism.** Real, representative content — **no lorem/placeholder filler**; realistic + edge data (long strings, overflow) exercised. *Gap* on lorem or only-tidy-data. *Non-collapsing baseline.*
8. **Rendered states + quality.** Each flow-visited state is **rendered** (a screenshot, not a note): empty (reason + guide-to-action), loading (a skeleton mirroring the layout, not a bare spinner), populated, error (plain-language cause + recovery), success, partial. *Gap* when an applicable state is un-rendered or empty-shell. *Collapse:* a static screen has only populated.
9. **Responsive reflow.** Rendered + correct at the target viewports; mobile content-priority + adaptive nav where form-factor matters; touch targets sized. *Gap* when a responsive surface is shown at one width only or reflows broken. *Collapse:* a single-form-factor surface (stated reason).
10. **Numeric WCAG 2.2 AA on the render.** axe-core clean **with no rule disabled** (necessary, not sufficient — axe can't see focus *appearance*, keyboard/focus order, contrast over imagery, or reduced-motion; judge those on the render + a manual/AT spot-check) + (judged on the render): text contrast ≥4.5:1 / large+UI ≥3:1 (SC 1.4.3/1.4.11); focus visible (2.4.7) + not-obscured (2.4.11) + appearance ≥2px/3:1 (2.4.13, house rule); target ≥24px (2.5.8); keyboard operable + logical focus order; reduced-motion honored. *Gap* on a measured failure or a suppressed rule. Fix belongs in the token layer. *Baseline:* contrast + landmarks + names always; focus/target/motion where interactive/animated. **Spec-vs-realized:** judge whether the RENDER achieves the threshold, not whether the DS doc states it (that's the design-system gate).
11. **DS conformance.** The rendered result conforms to the design-system (components are the DS's or faithful to its contract; no contradiction). A finding about the DS's *own* quality is out-of-lane — surface it, route it to the DS gate. *Non-collapsing baseline.*
12. **Gaps surfaced, not invented.** Undefined screen/content, a missing DS token/component, a degraded (no-render) production = explicit assumptions/open-questions. *Gap* when the doc papers over a gap with an invented token/component or a faked screenshot. An honestly-labelled assumption is **not** a gap.
13. **Delta-scoped review (amended hi-fi only).** Review the **diff + the re-rendered changed screens**, not the whole artifact: scope-confined (untouched screens' code byte-stable + their screenshots not re-captured); ripple-clean (a changed token reached **all** consuming screens + none hand-edited off-token; no consumer left stale; no wireframe-named screen newly un-rendered; no component-name drift; every changed screen's screenshot re-captured — no stale render); the changed screens **re-vision-reviewed** (still meet polish + WCAG + DS-conformance on the new render); the doc's own version bump correct for the change class; a breaking removal carries deprecation; changelog matches the diff. *Gap* on any of these. *N/A* for a greenfield first build.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes on the render. The hi-fi is a sound build seed: covered, visually realized to the bar, accessible, DS-conformant. Approve even if you can imagine visual improvements; the bar is the conditions, not perfection. A thin screen with proportionally collapsed conditions still approves.
- **revise** — one or more conditions have a real, named gap (an un-rendered screen, wireframe-grey fidelity, an off-token raw value, a contrast failure on the render, lorem content, a missing rendered state, a named-heuristic failure, a bad delta).

Do not revise to signal effort or request nice-to-haves; do not revise on out-of-set subjective taste (cond. 4) or on the design-system's own quality (cond. 11) or for seed-only-gaps like missing tests (cond. 2). A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location (which screen / state / viewport), and **how to fix it** (with the fix at the token layer where it's a contrast/token issue) — so the producer resolves it in one pass. On `approve`, findings are optional non-blocking notes.

A good finding names the gap and the fix:

> **revise** — Numeric WCAG (cond. 10): on the rendered Projects-empty screen, the "New project" button is `--muted` on white at 2.9:1 (below 4.5:1, SC 1.4.3). Fix: bind the button to the `--primary` token (don't recolor one button off-token); re-render to confirm ≥4.5:1.

A bad finding is vague: *"The contrast could be better somewhere."*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line. Downstream tooling parses it.
- **Re-render; never trust a handed-in screenshot.** Render the code yourself + vision-review the fresh result (cond. 6). A code-read-only or trust-the-image review is incomplete; a degraded (no-render/text-only) run must be flagged.
- **Judge, never author.** Return findings; do not rewrite or re-render-to-improve. The producer revises.
- **Single-sourced bar.** Judge against the Step-2 conditions — the same bar the author produces to. No private stricter standard, no invented extra condition.
- **No false-revise.** A seed meeting every applicable condition is approved, even a thin one. Out-of-set subjective taste is never a gap; seed-only gaps (no tests/backend) are never a gap.
- **No false-approve.** An un-rendered screen, off-token raw value, contrast failure on the render, lorem content, or invented token/component is a `revise`.
- **Numeric a11y on the render; never accept a disabled rule.** Judge contrast/focus/target on the rendered pixels; a suppressed axe rule used to pass is itself a finding.
- **Spec-vs-realized, stay in lane.** Judge whether the RENDER achieves the WCAG threshold + conforms to the DS — do NOT grade the DS's own contract/quality (that's `reviewing-design-system`) or the screen structure (that's `reviewing-wireframes`).
- **Seed, not production.** Don't revise for missing tests/real-backend/routing — those are the build phase's.
- **Judge against the upstreams given.** A *not-produced* upstream is never a revise trigger; a *produced-but-ignored* upstream (a wireframe screen left un-rendered; a DS token bypassed) **is** a fair finding.
- **Amend = delta review.** On an amendment, review the diff + ripple + re-vision-review the delta (cond. 13); don't re-litigate untouched screens.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first (un-rendered screen, contrast failure, off-token drift, lorem), then minor (a single heuristic nit).
- Reference the condition number/name in each finding.
- Keep approve-notes few and clearly non-blocking.
- When a cross-check input (wireframes or design-system) is absent, or a render was degraded, say so once rather than silently assuming.

## Gotchas

- **Trusting the handed-in screenshot.** A supplied image can be stale or cherry-picked — re-render the code yourself (cond. 6); that IS the gate.
- **Reviewing the code by reading it.** Code that reads fine can render broken — you must render + look (cond. 6).
- **Grading the design-system.** Revising because a DS token value or component contract seems off is out-of-lane — judge whether the render conforms (cond. 11); route DS-quality findings to the DS gate.
- **Double-judging WCAG.** The DS states the per-component thresholds; this gate judges whether the RENDER achieves them (spec-vs-realized) — not a re-grade of the DS's stated numbers.
- **Revising a seed for prod gaps.** No tests / mock data / single-file / CDN are seed allowances, not gaps (cond. 2).
- **Revising on taste.** "A nicer hue/layout exists" is out-of-set subjective taste — cond. 4 judges the objective subset + the named heuristics (state which one fails). Manufacturing a taste gap is a false-revise.
- **Letting lorem pass.** Placeholder filler hides overflow/tone/a11y problems — it's a `revise` (cond. 7).
- **Letting an off-token value pass.** A raw `#hex`/`px` that bypasses the token map is drift (cond. 5) — fix at the token layer.
- **Re-reviewing the whole artifact on an amend.** Review the diff + ripple + re-vision-review the delta (cond. 13); re-litigating untouched screens is noise.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph won't parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming the code/screens and approving — the gate exists to catch un-rendered screens, contrast failures, and DS drift before the build seeds from them.
- **Nit-pick revise.** Blocking on visual taste, a DS token value, or seed-only gaps dressed as defects. Revise is for real coverage/fidelity/a11y/conformance blockers only.
- **Trust-the-image review.** Grading a handed-in screenshot instead of re-rendering — defeats the gate's whole point.
- **Silent re-render-to-fix.** "Easier to just tweak the code" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** "It should also pass AAA / add motion / a different layout" — that drifts the bar past the single-sourced conditions.
- **Grading the wrong artifact.** Judging the structure (wireframes) or the token catalog (design-system) instead of the rendered hi-fi — stay in lane.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, one token.

## Output

A single review result for one hi-fi design:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the hi-fi for the human visual gate / the build milestone; `revise` returns the findings to the producer for a bounded revision pass.

**Worked finding (a real revise).** Hand-off: a hi-fi "Settings" screen, code only, one screenshot supplied. The reviewer re-renders at 360/768/1280: at 360 the form fields overflow the viewport (no reflow), the section heading uses a raw `#1a1a1a` (off-token), and axe flags the toggle's label. Verdict: `revise` — cond. 9 (Settings reflows broken at 360: fields overflow; fix: stack the field group + single-column below 768), cond. 5 (heading uses raw `#1a1a1a`; fix: bind to `--foreground`), cond. 10 (toggle missing an accessible name, axe `label`; fix: add `aria-label`). The supplied screenshot (desktop, populated) looked fine — the gate caught it only by re-rendering at all viewports.

## Related

- **`authoring-hi-fi`** — the produce half; writes to the same bar this skill judges. Pairing single-sources the bar so produce + review don't drift.
- **`reviewing-wireframes`** — the sibling gate for the screen structure; the wireframes are a *cross-check input* here (coverage), not what this skill grades.
- **`reviewing-design-system`** — the sibling gate for the token system + the per-component a11y *contract*; the design-system is a *cross-check input* here (conformance), and this gate judges the *realized* render against it (spec-vs-realized).
- **`agent-browser`** (+ `playwright-best-practices`) — renders + screenshots the code so the reviewer can vision-review it; this skill drives it.
- A **hi-fi template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/buildability-bar.md` — the 13 conditions expanded with per-condition pass/gap signals + worked findings (incl. the spec-vs-realized WCAG boundary, the named-heuristic polish call, the seed-not-prod line, and the delta-review). Load when a borderline condition needs a sharper call.
- `references/sources.md` — research provenance for the method + the single-sourced bar (shared with the `authoring-hi-fi` sibling).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
