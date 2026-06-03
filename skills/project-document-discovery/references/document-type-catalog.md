# Document-type catalog

Broad-but-shallow reference for selecting a project's document set. Five lifecycle bands; each entry is **name — what it is — when needed — what it feeds**. The list is **illustrative and open-ended**: if a project needs a type not here, research it and add it. Depth on *how to write* any of these belongs to a per-document authoring skill, not here.

## Band 1 — Analysis / discovery

- **Problem statement** — the need being solved; when there's any ambiguity about the "why"; feeds the PRD.
- **Market / competitor scan (MRD)** — the landscape and differentiation; for commercial products; feeds the PRD/business case.
- **Business case (BRD)** — business goals, constraints, success criteria; for funded/enterprise efforts; feeds the PRD.
- **User research / personas** — who the users are and their behaviors; for user-facing products; feeds the PRD + design.
- **Success metrics** — how success is measured; whenever outcomes must be tracked; feeds release/analytics.

## Band 2 — Product / requirements (usually load-bearing)

- **PRD** — what to build: features, behaviors, interactions; for almost any feature-bearing product; feeds design, architecture, planning. **The keystone document.**
- **Feature list / feature specs** — the enumerated features and their detail; whenever there is more than a trivial feature set; feeds decomposition/planning.
- **User stories + acceptance criteria** — features from the user's view with done-conditions; agile teams; feeds tests + decomposition.
- **SRS** (software requirements spec) — a detailed functional blueprint; for regulated/large systems; feeds architecture + tests.

## Band 3 — Design / UX (for UI-bearing products)

- **User flows** — start-to-finish journeys through tasks; for any non-trivial UI; feeds wireframes + tests.
- **Information architecture / sitemap** — pages/screens and their links; for multi-screen products; feeds wireframes + navigation.
- **Wireframes** — low-fidelity screen structure (no visual styling); for any UI; feeds mockups + component specs + front-end build.
- **Hi-fi mockups** — visual design of screens; when visual fidelity matters; feeds front-end build.
- **Design system / tokens** — reusable UI building blocks + styles; for products with many screens/teams; feeds component specs.
- **Component & interaction specs** — how each element behaves, annotated for developers; for complex UIs; feeds front-end build.
- **Accessibility notes** — a11y requirements; for public/inclusive products; feeds build + QA.

## Band 4 — Architecture / engineering

- **Architecture overview** — system structure (e.g. C4 Context/Container/Component); for any non-trivial system; feeds code + API spec + data model.
- **ADRs** (architecture decision records) — the *why* behind significant decisions; whenever consequential choices are made; feeds future maintenance.
- **HLD / LLD** — high- then low-level design; for larger systems; feeds implementation.
- **API specification** — endpoints/contracts (OpenAPI/AsyncAPI); for any service/SDK with an interface; feeds clients + tests. *Generate-and-link; don't duplicate in prose.*
- **Data model / schema** — entities and relationships; for any data-bearing system; feeds implementation + migrations.
- **NFRs / security** — performance, scaling, threat model; for production systems; feeds architecture + readiness.

## Band 5 — Delivery / go-to-production

- **Test plan / strategy + cases** — what's tested and how; for anything shipping; feeds QA + release.
- **CI/CD plan** — build/test/deploy automation approach; for any repeatable delivery; feeds the pipeline.
- **Deployment runbook** — how to deploy + respond to known failures; for operated services; feeds on-call/incident response.
- **Production-readiness review** — the pre-launch checklist (monitoring, SLOs, rollback); before first production release; feeds the release gate.
- **Observability / monitoring plan** — metrics, logs, alerts; for operated services; feeds the runbook.
- **Rollback plan** — how to revert safely; for risky/production releases; feeds the release gate.

## Proportionality — load-bearing vs skip, by archetype

| Archetype | Load-bearing | Usually skip |
|---|---|---|
| CLI tool / small library | README, brief design note, usage/API reference | PRD, UX docs, formal architecture |
| Library / SDK | API reference, usage guide, examples, changelog | UX docs, deployment runbook |
| API service | PRD/feature list, API spec (OpenAPI), data model, test plan, deployment/runbook | wireframes, design system |
| Web / mobile app | PRD, feature specs, user flows, wireframes, design system, architecture, API spec, test + release plan | (heavy end — most bands apply) |
| Data pipeline | requirements, data model/schema, architecture, runbook, monitoring | UX docs |

Lean/MVP context → trim the optional bands to *minimum viable documentation* (keep the load-bearing). Enterprise/regulated → front-load more (BRD, SRS, NFRs, readiness). Never cut the load-bearing band to "stay lean."

## Common dependency edges (requirements → design → delivery)

- `prd depends_on` (analysis docs, if any)
- `feature-specs depends_on prd`
- `architecture depends_on prd` (and feature specs)
- `api-spec depends_on architecture`
- `data-model depends_on architecture`
- `user-flows depends_on prd`
- `wireframes depends_on user-flows` (or prd)
- `component-specs depends_on design-system`
- `test-plan depends_on feature-specs` (+ api-spec)
- `runbook / release-plan depends_on` (architecture + deployment) — typically last

Verify the assembled graph is **acyclic**; dependencies never flow backward (a PRD never depends on the architecture).

## Producer role + tooling quick map (OSS-first)

| Document band | Producer role (illustrative) | OSS-first tools |
|---|---|---|
| Product/requirements | product strategist / PM / BA (`idea-strategist × product`) | Markdown-in-repo, a docs store |
| Design/UX | UX designer (`designer × ux`) | Penpot (open Figma alternative), Wireflow |
| Architecture/eng | systems architect (`designer × system`) | C4 / arc42, Markdown, OpenAPI, schema generators |
| Delivery/go-to-prod | QA / SRE / DevOps (`engineer × devops`) | Markdown checklists/runbooks |

Titles vary by org (PM vs BA vs founder all produce PRDs); name the *role kind*, not a fixed title. Proprietary tools (Figma, Confluence) are options, never requirements.
