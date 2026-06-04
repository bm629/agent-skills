# reviewing-design-system

Judge a **finished design-system document** and decide whether a designer and engineer can build a consistent, accessible UI from it — an acceptance gate, not authoring. The review half of the design-system pair; single-sources its bar from the same dossier as `authoring-design-system`.

## Purpose

A design-system doc is a product's reusable visual + interaction language. This skill is the gate that decides whether it's usable: it judges a **textual markdown artifact** (values + spec tables), not rendered swatches, against a **usability + consistency + accessibility bar**, and emits a machine-parseable verdict so produce → review → accept can run as a loop.

## When to activate

- ✅ Judging a finished/draft design-system doc before it's accepted for build.
- ✅ The review step of a produce→review→accept document loop.

### When NOT to activate

- **Authoring a design system** → `authoring-design-system` (the producer revises on findings).
- **Per-screen layout** → `reviewing-wireframes`.
- **Navigation paths** → `reviewing-user-flows`.

## The usability + consistency + accessibility bar

Judges each, pass/gap: **principles** stated; **tokens** defined (color/type/spacing/elevation/motion) and **referenced by intent** (components use semantic tokens, not raw values); every **component fully specced** (anatomy, states, variants, usage, accessibility); the **catalog covers** the components the screens use **plus** the archetype-sized standard set; **accessibility numeric** (WCAG contrast/focus/keyboard); nothing **fabricated**. Single-sourced from the shared dossier so the produce-bar and review-bar match. Sized to the archetype — a proportionally-small system that still covers its surface area is not faulted.

## Output

Exactly `VERDICT: approve|revise` plus **actionable** findings (the failed condition + the fix). **Approves** a system that meets the bar — no false-revise — and **revises** only on a real, named gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never writes the doc.
- **Single-sourced bar** — same conditions the author produces to; no drift.
- **No false-revise** — approves a proportionally-sized system that covers its surface area.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
