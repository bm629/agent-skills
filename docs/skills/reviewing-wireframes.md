# reviewing-wireframes

Judge a **finished wireframes document** and decide whether downstream visual design and UI engineering can build the screen structure from it — an acceptance gate, not authoring. The review half of the wireframes pair; single-sources its bar from the same dossier as `authoring-wireframes`.

## Purpose

A wireframes doc is the structural design of each key screen. This skill is the gate that decides whether it's buildable: it judges a **textual markdown wireframe** (layout description + ASCII/markdown box sketch + per-element annotations), not binary/Figma assets, against a **buildability + coverage bar**, and emits a machine-parseable verdict so produce → review → accept can run as a loop.

## When to activate

- ✅ Judging a finished/draft wireframes doc before it's accepted for visual design / build.
- ✅ The review step of a produce→review→accept document loop.

### When NOT to activate

- **Authoring a wireframes doc** → `authoring-wireframes` (the producer revises on findings).
- **The navigation graph** → `reviewing-user-flows`.
- **The visual token system / components** → `reviewing-design-system`.

## The buildability + coverage bar

Judges each, pass/gap: every **flow-named screen and state has a wireframe** (no coverage gap); **all four per-screen states** (empty/loading/populated/error) documented; **layout + hierarchy unambiguous** on a grid with a **shared app-shell** meeting an objective layout-quality bar; **components identified** and consistent with the design-system; **affordances + data-display annotated**; **content & microcopy intent** stated (no raw data-model identifier as a label, placeholder ≠ label, consistent terminology); **screen-composition accessibility** (landmarks/focus-order/target-size — pixel contrast is the design-system's, not judged here); **responsive** behavior; gaps surfaced; stays **structural, not hi-fi**. An **amend** is reviewed as a **scoped versioned delta** (the diff + its ripple to all reusing screens + a version bump matching the change class), n/a on a greenfield build. Single-sourced from the shared dossier so the produce-bar and review-bar match. The user-flows and design-system are cross-check inputs, not what it grades.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + the fix). **Approves** a doc that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the doc.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **Delta-scoped amend** — an amended doc is judged on its diff + ripple + version bump, never re-litigated screen-by-screen.
- **No false-revise** — approves a buildable doc even if stylistically improvable; pixel contrast/focus-appearance belong to the design-system, not judged here.
- **capability-record-aware** — when capability records are injected by the authoring caller, judgment includes entry/exit coverage and system-coverage conditions; n/a when no records were injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
