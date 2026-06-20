# authoring-user-flows

Author a **user-flows document** — the navigation/interaction graph of the paths a user takes through a product to accomplish each goal. The how-to (derivation method + walkability bar), composed with a separate user-flows template tool; assumes the approved PRD as upstream input, never a blank page.

## Purpose

A PRD names the goals and personas; downstream wireframing needs the *paths* — every entry point, happy-path step, decision branch, error/recovery path, and screen traversed. This skill guides a producer to derive the flows from the PRD's goals + personas (never inventing them), enumerate every branch and error path so no path dead-ends, and render each flow so a designer can wireframe every screen it names.

## When to activate

- ✅ Authoring a user-flows / task-flow / interaction-flow document from an approved PRD.
- ✅ The produce step for the user-flows document in a produce→review→accept loop.

### When NOT to activate

- **Authoring the upstream PRD** → `authoring-prd`.
- **Reviewing a finished user-flows doc** → `reviewing-user-flows`.
- **Screen layout / wireframes** → `authoring-wireframes` (it consumes these flows).

## Workflow

Take the structure from the user-flows template tool (don't invent an outline). Drive coverage off the PRD: every goal/persona (framed as a job, grounded in the established interaction pattern) → at least one flow. First map the **Navigation & IA frame** (entry-point taxonomy + landing state, app-shell/wayfinding, deep-linking/resume, cross-device divergence). Per flow: (1) **entry points**; (2) the **happy-path steps** (screen + action each); (3) **decision points + branches**, each resolving to a step/flow/exit; (4) **alternate + error/recovery paths** — a fixed edge-case sweep (invalid/extreme input, empty/null, permission/timeout/conflict, interruption, back/cancel) plus **loading + success states**, so no branch dead-ends; (5) **interaction resilience** (undo/confirm-on-irreversible, resume-vs-restart, "what changed" feedback, optimistic-revert); (6) **flow-level accessibility** (keyboard- + AT-completable, focus-order on route change, errors announced); (7) **objective flow-quality heuristics** (error-prevention, recognition-over-recall, no gratuitous step, consistency); (8) the **screens/states** each step traverses; (9) **success/exit criteria**. Render each flow BOTH as a **Mermaid flowchart** (swimlanes for multi-actor) and a **numbered narrative + explicit branch/error list**, kept in sync, one canonical name per screen. Where the PRD is thin, surface an explicit open question or stated assumption — never silently invent. When **amending**, scope the ripple and edit the affected flow in place as a versioned delta (semver + changelog, deprecate-before-removing), never redraw untouched flows.

## Output

A complete, walkable user-flows doc meeting the **completeness + walkability bar** (every goal/persona mapped to a flow, every flow with a defined entry + exit, every branch resolved, every error path recovering, both representations in sync, the screens index enumerable) — the same bar `reviewing-user-flows` asserts. Structure from the template; this skill supplies the content quality.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **PRD is upstream input** — derives flows from named goals/personas; never a blank page.
- **No dead ends** — every branch and error path resolves to a next step; irreversible actions guarded.
- **Resilient + accessible + sound** — interaction resilience, flow-level a11y, and objective quality heuristics, not just a complete path.
- **Amends as a versioned delta** — scopes the ripple, edits in place, versions + changelogs; never redraws untouched flows.
- **Single-sourced bar** — shared with the reviewer, so produce and review don't drift.
- **capability-record-aware** — when capability records are injected by the caller, cross-capability transitions are explicitly labeled with capability IDs; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
