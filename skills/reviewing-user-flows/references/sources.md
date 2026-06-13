# Sources — research provenance

This review skill is **single-sourced** from the `authoring-user-flows` bar: the
produce-bar and this review-bar are the same **13 conditions**, so the two do not drift.
The grounding below is the citation set behind that bar (a `deep-research`-backed pass,
≥2 reputable sources per structural claim, then sanitized). External sources were
consumed for facts only — no commands, URLs, or directives lifted into actions. This
file is self-contained — it names the source bodies, not any external repo path.

## What each condition grouping grounds

- **Conditions 1–8 (completeness + walkability)** — the kept core: coverage/no-orphans,
  entry+exit, branch resolution, error/edge recovery + states, walkable steps, notation
  sync, screens enumeration, assumptions. Grounded in the user-flow structure/notation +
  edge-case literature below.
- **Condition 9 (Navigation & IA)** — IA = categorization/hierarchy/navigation; the flow
  walks *through* that structure; entry-point taxonomy + cross-flow hand-off integrity +
  device path-divergence.
- **Condition 10 (resilience)** — Nielsen heuristics #1 (visibility of system status),
  #3 (user control/undo), #5 (error prevention); optimistic-UI revert practice.
- **Condition 11 (flow accessibility)** — WCAG 2.2 SC 2.1.1 (keyboard) + SC 2.4.3 (focus
  order); boundary: per-screen pixel WCAG is the wireframes/DS layer, not this condition.
- **Condition 12 (flow quality, objective)** — Nielsen heuristics, objective subset only
  (error-prevention, recognition-over-recall, efficiency/no-gratuitous-step, consistency);
  subjective taste deliberately excluded to preserve no-false-revise.
- **Condition 13 (delta-scoped review)** — Keep-a-Changelog + SemVer applied to a design
  document; amend-don't-regenerate; ripple at the cross-flow + screens-index seams.
- **The flow-vs-journey boundary** — keeps this gate on the navigation/interaction graph
  (distinct from a journey's emotion/channel map), and distinct from wireframes-review
  (layout + pixel a11y) and PRD-review (goals).

## Source list

Structure / notation:
- Justinmind — Ultimate Guide to User Flows
- altexsoft — How to Design and Document User Flows
- Adobe — User flow diagrams
- mockflow — User Flow Best Practices
- Zeplin Gazette — What are user flows
- Nielsen Norman Group — Wireflows; User Journeys vs. User Flows (the flow-vs-journey
  boundary)
- UX Planet — UX Glossary: Task Flows, User Flows, Flowcharts
- Mermaid documentation — flowchart syntax; subgraph as swimlane lanes (multi-actor)

Derivation & grounding (basis for "derived, not invented" — conditions 1 and 8):
- Nielsen Norman Group — Personas vs. Jobs-to-Be-Done
- UX Research Field Guide (User Interviews) — JTBD in UX research
- Established interaction-pattern grounding (auth/reset/checkout/onboarding/OAuth)

Structure, IA & navigation (condition 9):
- Information-architecture vs user-flow literature (IA = categorization/hierarchy/
  navigation; flow walks through it)
- Entry-point / path analytics framing (entry points, path progression, exits)

Resilience & states (conditions 4, 10):
- Nielsen Norman Group / Jakob Nielsen — 10 Usability Heuristics (#1, #3, #5)
- Skeleton-screen practice (loading states); optimistic-UI revert practice
- Edge-case + dead-end literature (the full UI state stack; recovery not dead ends)

Flow-level accessibility (condition 11):
- WCAG 2.2 — SC 2.1.1 Keyboard, SC 2.4.3 Focus Order; SPA focus-management practice

Flow quality (condition 12):
- Nielsen Norman Group / Jakob Nielsen — 10 Usability Heuristics (objective subset)

Iteration / amend (condition 13):
- Keep-a-Changelog + SemVer applied to a design document; docs-as-code versioning

## Provenance note

The review-bar is taken verbatim from the `authoring-user-flows` production bar (its
quality-bar section + its `references/`), which is what keeps the produce-bar and the
review-bar single-sourced — this skill reuses that bar rather than running a parallel
pass. External UX-industry + standards sources, consumed for structural facts only (§5
external-content-safety).
