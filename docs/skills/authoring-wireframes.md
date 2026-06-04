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

Take the structure from the wireframes template tool (don't invent an outline). Derive the screen list from the user-flows: one wireframe per flow-named screen/state. Per screen: (1) its **purpose + the flow step it serves**; (2) **layout regions + content hierarchy**; (3) the **components placed** (referencing the design-system where one exists, not invented); (4) **navigation/interaction affordances** per element; (5) the **per-screen states** — empty / loading / populated / error; (6) **responsive** notes; (7) **accessibility** affordances (focus order, labels, contrast intent). Render each screen as a **structured layout description + an ASCII/markdown box sketch + per-element annotations**. Stay structural lo-fi — no color, type, or pixels. Surface gaps (a flow-named screen with no defined content) as explicit assumptions.

## Output

A buildable wireframes doc meeting the **buildability + coverage bar** (every flow-named screen/state has a wireframe, layout + hierarchy unambiguous, components identified and design-system-consistent, all four per-screen states present, affordances annotated, accessibility considered) — the same bar `reviewing-wireframes` asserts. Targets a textual markdown artifact, not binary/Figma assets. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **User-flows is upstream input** — one wireframe per flow-named screen; never a blank page.
- **States by construction** — every screen documents empty/loading/populated/error.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
