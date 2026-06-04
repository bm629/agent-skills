# authoring-design-system

Author a **design-system document** — a product's reusable visual + interaction language: principles, design tokens (color, typography, spacing, elevation, motion), a component catalog, patterns, accessibility standards, and voice. The how-to (token/component method + consistency + accessibility bar), composed with a separate design-system template tool; targets a textual markdown artifact (hex/HSL values, type-scale + component spec tables), not rendered swatches.

## Purpose

Screens need a shared vocabulary so the UI stays consistent and accessible. This skill guides a producer to ground tokens and components in established design-system practice, name tokens by intent in a primitive→semantic→component tiering, size the catalog to the product, and specify each component with anatomy + states + variants + usage + accessibility — to a bar a designer and engineer can build a consistent, accessible UI from. It precedes wireframes (which reference its components), one-directionally.

## When to activate

- ✅ Authoring or expanding a design-system document for a product with a real UI.
- ✅ The produce step for the design-system document in a produce→review→accept loop.

### When NOT to activate

- **Per-screen layout** → `authoring-wireframes` (it references this system).
- **Reviewing a finished design system** → `reviewing-design-system`.
- **Shipping a coded component library** (CSS/React) — this is the *document*.

## Workflow

Take the structure from the design-system template tool (don't invent an outline). Always specify the foundations: **principles**, **design tokens** (color incl. semantic roles, typography scale, spacing, elevation, motion), **accessibility standards** (WCAG target, contrast, focus, keyboard), and **voice**. Build the **component catalog** to cover BOTH a hard floor — every component the product's screens actually use, each specced in full (**anatomy + states + variants + usage do/don't + accessibility**) — AND the common standard set, sized to the product archetype. Reference tokens by intent (components use semantic tokens, not raw hex). Where brand direction is thin, surface an explicit assumption — never fabricate.

## Output

A usable design-system doc meeting the **usability + consistency + accessibility bar** (tokens defined + applied consistently, every component fully specced, principles stated, accessibility numeric, the catalog covering the surface-area floor + the standard set) — the same bar `reviewing-design-system` asserts. Targets a textual markdown artifact. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Precedes wireframes** — the vocabulary they draw on; does not depend on them.
- **Accessible + consistent by construction** — semantic tokens, per-component a11y, numeric WCAG.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
