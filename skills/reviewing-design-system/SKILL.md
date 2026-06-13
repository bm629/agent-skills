---
name: reviewing-design-system
description: >
  Use when reviewing or judging a finished design-system document — a product's
  reusable visual + interaction language (principles, DTCG design tokens,
  foundations incl. iconography/grid, a component catalog, patterns, layout +
  internationalization, WCAG 2.2 AA accessibility, voice, lifecycle/governance) —
  deciding whether an engineer can build a consistent, accessible UI from it. Also
  reviews an AMEND (a versioned delta) as a delta-scoped review. A gate, not
  authoring. Judges against a single-sourced usability/consistency/accessibility
  bar: tokens DTCG-typed + referenced by intent (components use semantic tokens,
  not raw values); components fully specced with one API vocabulary; catalog
  covers the screens' components + an archetype-sized standard set; accessibility
  numeric (WCAG 2.2: contrast/focus-appearance/target-size/keyboard); i18n
  addressed or scoped out; governance present above its threshold; nothing
  fabricated. Judges a textual markdown artifact, not rendered swatches. Emits
  exactly `VERDICT: approve|revise` plus actionable findings; approves a system
  meeting the bar (no false-revise of a proportionally-sized one), revises only on
  a named gap. Not for authoring it, not per-screen layout (wireframe-review), not
  navigation paths (user-flow-review), not engineering design docs.
extensions:
  claude:
    when_to_use: "judging a finished design-system document (or an amend delta) against the bar and emitting an approve/revise verdict"
    argument-hint: "<the finished design-system document to review; on an amend, the delta + the prior version>"
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-13
---

# `reviewing-design-system` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished design-system document (or an amend delta) as an acceptance gate — checking a designer/engineer can build a consistent, accessible UI from it, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging design-system pair. Loaded by a reviewer who holds a **finished design-system document** (or an **amend delta** against a prior version), it judges against one question: **can a designer build a consistent UI and an engineer implement it from this document, without asking the author, and does the catalog cover the components the product's screens need?** It applies a fixed **usability + consistency + accessibility checklist** — the same bar the author produces to (`authoring-design-system`), so produce-bar and review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It judges the **textual markdown artifact** (tokens as values + DTCG-shaped + spec tables), not a rendered design file. It is an acceptance gate — it does **not** author, fix, or rewrite the document.

## When to activate

- A finished design-system document needs an accept/revise decision before wireframing / hi-fi / UI engineering builds from it.
- An **amend** (a versioned delta to an existing system) needs a delta-scoped accept/revise decision.
- Re-judging a revised design system after a prior `revise`.

**Do NOT activate when:**

- Authoring or repairing a design system → use `authoring-design-system`.
- Reviewing a **wireframes / per-screen layout** doc → use a wireframe-review skill (this judges the reusable vocabulary one layer up).
- Reviewing a **user-flows** doc → use a user-flow-review skill.
- Reviewing an **engineering design doc** (architecture/ADR/RFC) → use a design-review skill.
- Checking template/section conformance → a template concern; this judges *quality against the bar*.
- Grading a **coded** component library → this judges the *document*.

## Workflow

### Step 1: Read the whole document with fresh, independent eyes

Read end to end without the author's framing. Your stance is a gatekeeper for the *next* steps (wireframing + hi-fi + UI engineering): a finding carries weight only when it shows a designer/engineer **cannot build a consistent, accessible UI as written**. Identify the **product archetype** (thin CLI/utility vs content app vs full UI product) and, where available, the flows/screen list — the coverage + proportionality conditions calibrate to it. **If the artifact is an amend delta**, also read the prior version and the change scope (Step 2b).

### Step 2: Run the checklist — judge each condition

For each, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have chosen a different palette" is not a gap. Capture the exact location for each gap. These conditions are the single-sourced bar (the (reviewing+both) angles the author produces to); do not add private ones. Each names its **proportionality collapse** — when it legitimately doesn't apply.

1. **Principles stated.** 3–6 actionable principles (not platitudes). *Gap* when absent or platitudes.
2. **Tokens defined, DTCG, intent-named, consistently applied.** Color (incl. semantic role tokens), type scale, spacing, elevation, motion defined as named tokens with concrete values; expressed in the **W3C DTCG format** (typed `$value` + aliasing) — **required at any size**, no values-table exception; components reference **semantic** tokens, never raw values (`#1A73E8`, `16px`). *Gap* when a token family is missing/valueless, tokens are a flat hex list with no DTCG structure, or a component spec references a raw value. *Collapse:* none for DTCG (universal); modern color spaces (Oklch/P3) are proportional — sRGB-only is not a gap.
3. **Foundations breadth.** Grid/layout + density, iconography (grid/stroke/sizes/style), and elevation/motion are present where the archetype needs them. *Gap* when a UI product omits a grid or an icon foundation it clearly uses. *Collapse:* a thin/utility product with no icons or complex layout legitimately omits these.
4. **Theming via alias-swap.** Light/dark and (where present) multi-brand re-point semantic aliases over one fixed tier — not forked components. *Gap* when a theme is implemented by duplicating/forking components. *Collapse:* single-brand single-theme need not belabor it.
5. **Component completeness (per component).** Every catalogued component carries all five: anatomy, states, variants, usage do/don't, accessibility. *Gap* when any component is missing one (e.g. variants but no states / no a11y).
6. **Component API consistency.** One property/option/default vocabulary across the catalog (the same variation axis named the same — not `type` here, `mode` there); shared values compose. *Gap* on API drift across components. *Collapse:* a tiny catalog trivially holds.
7. **Catalog coverage — both floors.** Covers every component the product's flows/screens use (the hard floor, fully specced) AND the archetype-sized standard set. *Gap* when a real screen needs a component the catalog omits/under-specs. *Collapse:* the standard set scales with the archetype (no maximalism).
8. **Patterns present.** The recurring multi-component scenarios the flows need (form validation, empty state, destructive-confirm, …). *Gap* when a needed pattern is absent.
9. **Layout + internationalization.** Breakpoints/grid/focus-order stated; for a localized product, i18n/RTL addressed (text-expansion, logical properties, RTL/bidi, locale fonts). *Gap* when a localized product ignores i18n, or a screen that reflows says nothing. *Collapse:* a stated single-locale tool may scope i18n out **explicitly** (the explicit scope-out is not a gap; a silent omission is).
10. **Accessibility numeric, WCAG 2.2 AA.** A stated WCAG 2.2 AA target + checkable thresholds: text ≥4.5:1 (large/UI ≥3:1); a **visible, not-obscured focus** indicator (SC 2.4.7 + 2.4.11, AA) plus the **AAA Focus Appearance** ≥2px/3:1 vs unfocused + adjacent (SC 2.4.13) adopted as a house rule; **target size 24×24** (+ spacing exception); keyboard; reduced-motion; no color-only; per-component role/name/state. *Gap* when accessibility is aspirational/non-numeric, or misses the 2.2-specific criteria. *Collapse:* none — a11y is non-negotiable (but a static info screen needn't belabor states it lacks).
11. **Voice/content present.** Voice + a tone spectrum (clarity over brand voice in high-stakes moments), terminology (one term per concept), component copy rules (button = verb-first; **error = cause + fix**; **empty = guide-to-action**). *Gap* when absent for a product with user-facing copy, or error/empty rules lack cause+fix / guide-to-action. *Collapse:* a product with no user-facing copy is light.
12. **Lifecycle & governance (above the threshold).** For a system with >1 consumer/team or a versioned external release: versioning + changelog, deprecation/migration policy, contribution model, ownership, adoption, and an **audience recorded as a decision** (not an assumed persona). *Gap* above the threshold when governance/versioning is absent, or an assumed audience drives the vocabulary. *Collapse:* **fully omittable** below the threshold (single-maintainer + single-consumer + non-versioned-external) — manufacturing a governance gap there is a false-revise.
13. **Grounded, not boilerplate + usable downstream.** Tokens/components reflect *this* product (archetype-sized); gaps surfaced as assumptions/open-questions, not fabricated; wireframing/hi-fi can reference real components/tokens and engineering can build without asking the author. *Gap* on generic fill, a fabricated brand/contrast answer, or a dangling reference.

**Proportionality.** "Build a consistent UI from it" scales with the product. A thin product's system legitimately collapses the conditions marked above; the **hard floor** (cond. 7a), **DTCG** (cond. 2), and **numeric a11y** (cond. 10) still hold at any size. Judge completeness-of-decisions, not row count. Do not manufacture a gap from brevity.

### Step 2b: If the artifact is an amend (delta) — review the diff, not the whole doc

When judging a versioned delta against a prior version, the bar is **delta-scoped**:

- **Scope-confinement** — only the stated tokens/components changed; no unrelated re-naming, palette churn, or re-tiering. An out-of-scope change is scope-creep → `revise` (or split).
- **Ripple / regression** — every component still references a real semantic token (none orphaned by a rename/remove); the alias layer resolves; theme variants still cohere (no silent dark-mode/brand break).
- **Versioning + changelog accuracy** — the semver bump matches the change class (rename/remove/retype ⇒ MAJOR; additive ⇒ MINOR; fix ⇒ PATCH); the changelog matches the diff.
- **Deprecation-safe** — a breaking change carries a deprecation + migration path; no silent removal.
- **Coherence** — the change fits the existing tiering/intent-naming/catalog API; the delta still satisfies the relevant Step-2 conditions locally.
- **Re-review proportionality** — judge the **delta**; do not re-litigate settled, untouched tokens/components.

### Step 3: Decide the verdict

- **approve** — every applicable condition (or, for a delta, every delta-scoped check) passes; a designer/engineer can build from it as written. Approve even if you can imagine stylistic improvements; the bar is usability + consistency + accessibility, not perfection or maximalism.
- **revise** — one or more real, named gaps block building (undefined/inconsistent/non-DTCG tokens, a raw value in a spec, a component missing a part, API drift, non-numeric or non-2.2 a11y, a coverage hole, a silent i18n omission on a localized product, missing governance above the threshold, an out-of-scope or un-versioned delta, fabricated content).

Do not revise to signal effort or request nice-to-haves.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal `VERDICT: approve` or `VERDICT: revise`, on its own line, no fences/quotes/extra words:

```
VERDICT: approve
```

Then list findings. On `revise`, each is **actionable** — the failed condition + exact location + how to fix — so the author resolves it in one pass. On `approve`, findings are optional non-blocking notes.

Good finding:

> **revise** — Tokens (cond. 2), "Button" spec: `background: #1A73E8` is a raw hex. Fix: reference the semantic token `color.action.primary` (define it in the color section), expressed in DTCG.

Bad finding: "The tokens could be better." *(Which? Why? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line.
- **Judge, never author.** Return findings; do not rewrite/fix the document.
- **Single-sourced bar.** Judge against the Step 2 conditions (+ Step 2b for a delta) — the same bar the author produces to. No private extra conditions.
- **No false-revise.** A system meeting every applicable condition is approved, even a thin one; proportional sizing that still covers the surface area is not a defect.
- **No false-approve.** A real gap is a `revise`.
- **A raw value or non-DTCG token is a consistency gap** (cond. 2). **A component missing one of five parts is a gap** (cond. 5). **API drift is a gap** (cond. 6).
- **Accessibility must be numeric to WCAG 2.2 AA** (cond. 10) — incl. visible + not-obscured focus (AA), the AAA Focus Appearance ≥2px/3:1 house rule, and target-size 24px.
- **The surface-area floor + DTCG + numeric a11y hold at any size** — they never collapse.
- **Governance is omittable below its threshold; required above it** (cond. 12) — don't manufacture a governance gap on a thin internal system.
- **On a delta, review the diff** (Step 2b) — scope-confinement + ripple + semver + deprecation; don't re-litigate untouched parts.
- **Fabrication is a gap, not grounding** (cond. 13).
- **Judge against the upstreams the document was given.** A not-produced upstream is never a revise trigger; a document that ignored a produced upstream it should have drawn on is a fair finding.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first.
- Reference the condition number/name in each finding.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section present yet un-buildable (raw values in specs, a component missing states/a11y, non-numeric contrast). Judge buildability, not template-filled.
- **The raw value / non-DTCG token hiding in a spec.** A token section can look right while a "Button" hard-codes `#1A73E8`, or the tokens are a flat hex list with no DTCG structure — both fail cond. 2.
- **The half-specced component.** Anatomy + variants + usage but no states / no a11y reads complete but isn't (cond. 5).
- **Missing the 2.2-specific a11y.** Generic "≥3:1 focus" without not-obscured (AA, SC 2.4.11) / the ≥2px Focus-Appearance house rule (SC 2.4.13) / 24px target-size misses the bar (cond. 10).
- **False-revise on a thin system.** A thin product's system is correctly small — collapsed sections it doesn't need, i18n scoped out, governance omitted below the threshold. That is right-sizing, not under-specification.
- **Manufacturing a governance gap below the threshold** — a single-maintainer single-consumer system legitimately omits the lifecycle/governance section entirely (cond. 12).
- **Re-litigating the whole doc on a delta** — review the diff (Step 2b); re-opening settled untouched tokens is the delta false-revise.
- **Letting a breaking delta through as a MINOR with no deprecation** — Step 2b version + deprecation checks.
- **Verdict token drift.** "Approved", "LGTM", a buried verdict won't parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop.
- **Nit-pick revise.** Blocking on palette taste / nice-to-haves dressed as gaps.
- **Silent rewrite.** Authoring inside a review.
- **Inventing conditions** (a Figma link, dark-mode where unneeded) — drifts the bar off the produce-bar.
- **Maximalism.** Demanding the full broad standard set / full governance from a thin product.
- **Regenerate-on-delta review.** Grading a delta as if it were a fresh full doc.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines.

## Output

A single review result:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the system for the next phase (wireframing / hi-fi / UI engineering); `revise` returns findings for a bounded revision pass.

## Related

- `authoring-design-system` — the produce half; writes to the same bar this judges. Pairing single-sources the bar.
- A **wireframe-review** skill — the gate for per-screen layout (one layer down).
- A **user-flow-review** skill — the gate for navigation paths.
- A **design-review** skill — the gate for engineering design docs.
- A **design-system template / content-template** tool — owns section *structure*; this judges *quality against the bar*.

## Progressive disclosure

- `references/buildability-bar.md` — the conditions expanded with per-condition pass/gap signals + worked finding examples + the delta-review checks.
- `references/sources.md` — research provenance for the method + the single-sourced bar (shared with the `authoring-design-system` sibling).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
