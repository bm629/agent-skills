# authoring-user-guide

Author an **end-user guide** — the consumer-facing help the (typically non-technical) person USING a product reads to accomplish their goals: a getting-started tutorial, task-oriented how-to guides, conceptual explanation, an end-user feature/configuration reference (features, settings, CLI commands — not the HTTP API), and troubleshooting/FAQ. The how-to (a derivation method + a usability/accuracy bar), composed with a separate user-guide template tool and a research capability; targets a textual markdown artifact (numbered steps + fenced command/config snippets + screens described in words with wireframe links).

## Purpose

A user guide is the help a real end user relies on to get value from a product. This skill carries the producer's judgment — not the section list — guiding a producer to span the full Diataxis quadrant (tutorial / how-to / explanation / reference) plus troubleshooting, derive one how-to per user goal from the handed-in upstreams, keep the four modes distinct (a how-to is imperative steps, not a concept dump), hold every step accurate to the actual product behavior, and source troubleshooting from the real error states. The bar to clear: a real user can accomplish every goal the product supports from the guide alone, and the steps match what the product actually does.

## When to activate

- Authoring the end-user documentation for a product from its handed-in upstream docs (typically a feature-spec + user-flows + wireframes).
- Producing a getting-started tutorial, task how-to guides, conceptual explanation, an end-user feature/settings reference, and troubleshooting/FAQ.
- Filling a user-guide template with researched, goal-complete, behavior-accurate end-user content.

### When NOT to activate

- **The developer-tool adoption/integration narrative** (install, concepts, integration recipes for a developer) → `authoring-developer-guide`.
- **The HTTP/SDK API endpoint catalog** (the published per-endpoint reference) → `authoring-api-reference`.
- **The internal engineering docs** (feature-spec, api-spec, architecture, data-model) → those are upstream/engineering, not end-user help.
- **Reviewing a finished user guide** → `reviewing-user-guide` (the paired acceptance gate).

## Workflow

Take the section structure from the user-guide template tool (don't invent an outline). Read the full handed-in `depends_on` set; enumerate the user goals — from the user-flows when present, else from the feature-spec/PRD (coverage degrades gracefully; never assume user-flows is always handed in). Research to ground the guide in established end-user-docs practice (the Diataxis framework, task-oriented minimalism, a reputable docs style guide). Then fill each mode to method: a getting-started tutorial (one guaranteed first-success path); one task-oriented how-to per goal (imperative steps); conceptual explanation (the mental model, no numbered steps); a complete end-user feature/configuration reference (features, settings, commands — not the HTTP API); troubleshooting/FAQ sourced from the upstreams' error states; a glossary. Describe screens in words and link the wireframes; trace every step to the feature-spec behavior; surface any missing-upstream gap as an explicit assumption rather than fabricating. Self-check against the usability/accuracy bar before handoff.

## Output

A comprehensive end-user guide meeting the **usability/accuracy bar** (every handed-in goal has a how-to; the four Diataxis modes present and correctly typed; the end-user feature/config reference complete; steps accurate to the product behavior; troubleshooting covers the known error states; usable by the target user; nothing fabricated). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same bar the paired `reviewing-user-guide` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **One how-to per goal, no orphans** — goals taken from the handed-in upstreams (user-flows when present, else the feature-spec/PRD).
- **Diataxis modes correctly typed** — tutorial, how-to, explanation, and reference stay distinct; a how-to is steps, not a concept dump.
- **End-user, not developer/API** — the product feature/config reference, never the endpoint catalog (`api-reference`) or the developer adoption narrative (`developer-guide`).
- **Single-sourced bar** — shared with `reviewing-user-guide`, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
