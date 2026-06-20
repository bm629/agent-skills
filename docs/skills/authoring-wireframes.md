# authoring-wireframes

Author a **wireframes document** — the low-to-mid-fidelity structural design of each key screen, as a textual/annotated wireframe (layout description + ASCII/markdown box sketch + per-element annotations), not a pixel mockup. The how-to (screen-derivation method + buildability bar), composed with a separate wireframes template tool; assumes the upstream user-flows as input.

## Purpose

The user-flows name the screens; visual design and UI engineering need each screen's *structure* — its layout regions, content hierarchy, the components placed, the navigation affordances, and the per-screen states (empty/loading/populated/error). This skill guides a producer to derive the screen list from the flows (one wireframe per flow-named screen/state), ground each in established UI patterns, reference a design-system's real components where one exists, and cover every state — to a bar an engineer can build the screen structure from.

## When to activate

- ✅ Authoring a wireframes document from the upstream user-flows.
- ✅ The produce step for the wireframes document in a produce→review→accept loop.

### When NOT to activate

- **The navigation graph itself** → `authoring-user-flows` (it's upstream).
- **Reviewing a finished wireframes doc** → `reviewing-wireframes`.
- **High-fidelity visual design / the token system** → `authoring-design-system`.

## Workflow

Take the structure from the wireframes template tool (don't invent an outline). Derive the screen list from the user-flows into an auditable **screen-inventory table**: one wireframe per flow-named screen/state. First fix the global frame every screen inherits — the **layout grid + spacing cadence** (structure, not pixels), ONE shared **app-shell**, and an **objective layout-quality bar** (primary action on the scan path, Gestalt grouping, no gratuitous region, sibling consistency). Per screen: (1) its **purpose + the flow step it serves**; (2) **layout regions + content hierarchy** on the grid; (3) the **components placed** (referencing the design-system where one exists, not invented); (4) **navigation/interaction affordances + data-display** per element; (5) **content & microcopy intent** (no raw data-model identifier as a label, consistent terminology, i18n room); (6) the **per-screen states** — empty / loading / populated / error / success — quality not just presence; (7) **responsive** notes where form-factor matters; (8) **screen-composition accessibility** (landmarks, one-h1, reading/focus order, accessible names, keyboard, target-size ≥24px, focus-not-obscured, non-color-only — pixel contrast + focus-appearance deferred to the design-system). Render each screen as a **structured layout description + an ASCII/markdown box sketch + per-element annotations**, sketch ⇄ annotations in sync. Stay structural lo-fi — no color, type, or pixels. Surface gaps (a flow-named screen with no defined content, a missing component) as explicit assumptions. When **amending**, edit in place as a scoped versioned delta (semver + changelog; a shared-region change applied to all reusing screens in one pass), never redraw untouched screens.

## Output

A buildable wireframes doc meeting the **buildability + coverage bar** (every flow-named screen/state has a wireframe, layout + hierarchy unambiguous, components identified and design-system-consistent, all applicable per-screen states present — empty/loading/populated/error/success — affordances annotated, screen-composition accessibility considered) — the same bar `reviewing-wireframes` asserts. Targets a textual markdown artifact, not binary/Figma assets. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **User-flows is upstream input** — one wireframe per flow-named screen; never a blank page.
- **States by construction** — every screen documents empty/loading/populated/error/success.
- **Composition a11y owned, component contract deferred** — owns landmarks/heading/focus-order/target-reservation; defers pixel contrast + focus-appearance to the design-system.
- **Amends as a versioned delta** — edits in place, applies a shared-region change to all reusing screens in one pass, versions + changelogs; never redraws untouched screens.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.
- **capability-record-aware** — when a `capability_record` (or the full capability list for system-scope) is injected by the caller, entry/exit coverage scope is drawn from it; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
