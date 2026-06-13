# Sources — authoring-user-flows

Research provenance for this skill's method + production-grade bar. The skill was
produced and (v1.2.0) extended via a `deep-research`-backed pass with ≥2 reputable
sources per structural claim, then sanitized. Sources consumed for facts only; nothing
lifted as instructions, no URLs/commands carried into actions. This file is
self-contained — it names the source bodies, not any external repo path.

## Section set + notation (what a user-flows doc contains)

- Justinmind — Ultimate Guide to User Flows (entry points; happy + unhappy paths)
- altexsoft — How to Design and Document User Flows (process; flowchart notation;
  persona/goal tie-back)
- Adobe — User flow diagrams: how to create them (notation; screens; success states)
- mockflow — User Flow Best Practices (happy-path-first; decision points; error paths)
- Zeplin Gazette — What are user flows (screens/states traversed)
- Nielsen Norman Group — Wireflows; User Journeys vs. User Flows (definitions; the
  flow-vs-journey boundary — flow = interaction/navigation graph, journey = holistic/
  emotional/cross-channel)
- UX Planet — UX Glossary: Task Flows, User Flows, Flowcharts (terminology distinctions)
- Mermaid documentation — flowchart syntax; `subgraph` as swimlane lanes for multi-actor
  flows

## Derivation & grounding (jobs, personas, prior art)

- Nielsen Norman Group — Personas vs. Jobs-to-Be-Done (goals as jobs; functional/social/
  emotional dimensions; ground personas in real research, not assumptions)
- UX Research Field Guide (User Interviews) — JTBD framework; personas; mental models
- Established interaction-pattern grounding (auth / password-reset / checkout / onboarding
  / OAuth) — follow the convention or state the deviation, don't reinvent a solved flow

## Structure, IA & navigation (Step 2 / Navigation & IA)

- Information-architecture vs user-flow literature — IA = categorization / hierarchy /
  navigation; the user flow walks *through* that structure; they are interdependent
- Entry-point / path analytics framing — entry points (landing/source/campaign/UTM),
  path progression, exits/drop-offs; map each entry's funnel to derive IA structure
- Deep-linking + prereq-missing guard/resume; cross-device path divergence (a mobile
  path may differ structurally from desktop)

## Interaction resilience & states (Steps 5–6 / `resilience-and-states.md`)

- Nielsen Norman Group / Jakob Nielsen — 10 Usability Heuristics: #1 Visibility of system
  status, #3 User control & freedom (undo), #5 Error prevention
- Skeleton-screen practice (norm for full-page loads; ~2–10s; match final layout)
- Optimistic-UI literature (optimistic update + reconcile; not for payments/deletions;
  always show revert feedback)

## Flow-level accessibility (Step 7 / `flow-accessibility.md`)

- WCAG 2.2 — SC 2.1.1 Keyboard (operable, no traps); SC 2.4.3 Focus Order (meaning-
  preserving sequence; manage focus on route/step change)
- SPA focus-management practice (move focus + announce on route change)
- Boundary: per-screen pixel WCAG (contrast/target-size/focus-appearance) belongs to the
  wireframes + design-system layer, not this skill

## Flow quality (Step 8 / `flow-quality.md`)

- Nielsen Norman Group / Jakob Nielsen — 10 Usability Heuristics (objective subset:
  error-prevention, recognition-over-recall, efficiency/no-gratuitous-step, consistency);
  subjective taste deliberately excluded to preserve no-false-revise

## Quality bar — edge cases, error states, no dead ends (Step 5)

- Nielsen Norman Group — edge-case categories; the full UI state stack; no dead ends
- Systematic edge-case enumeration (boundary analysis; capture every assumption)
- Recovery-paths-not-dead-ends; empty/error/loading state coverage

## Iteration / amend (Step 11 / `amend-method.md`)

- Keep-a-Changelog (Added/Changed/Deprecated/Removed/Fixed) + SemVer (MAJOR/MINOR/PATCH)
  applied to a design document
- Docs-as-code / diagrams-as-code versioning (versioned in source control; each change a
  reviewable diff; changelog for traceability)

> External UX-industry + standards sources, consumed for structural facts only. No URLs,
> commands, or directives were lifted from them into actions (§5 external-content-safety).
