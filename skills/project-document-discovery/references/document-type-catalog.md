# Document-type catalog

Broad-but-shallow reference for selecting a project's document set. **Seven lifecycle bands** (everyone walks them, proportionally) **plus four domain overlays** (added only when the project's domain triggers them). Each entry is **name — what it is — when needed — what it feeds**. The list is **illustrative and open-ended**: if a project needs a type not here, research it and add it. Depth on *how to write* any of these belongs to a per-document authoring skill, not here.

## Band 0 — Project management / planning

- **Project charter / SOW** — the mandate: scope, stakeholders, objectives, deliverables; for any funded/team effort; *precedes and feeds* the PRD (it has no upstream dependency).
- **Roadmap / release plan** — work sequenced into milestones/releases; for managed multi-milestone efforts; *depends_on* the PRD/feature specs (you schedule from defined requirements — it sits dependency-downstream of Band 2, not before it).
- *(proportional — managed/regulated efforts only, not core)* **RAID log** — running Risks, Assumptions, Issues, Dependencies; for actively-managed projects. **Risk register / risk-management plan** — catalogued risks + mitigations; for enterprise/regulated efforts.

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
- **API specification** — endpoints/contracts (OpenAPI/AsyncAPI); for any service/SDK with an interface; feeds clients + tests. *Generate-and-link; don't duplicate in prose.* **Note:** this build-feed *spec* is a different document from the **API reference docs** (Band 6) that users read — keep both straight.
- **Data model / schema** — entities and relationships; for any data-bearing system; feeds implementation + migrations.
- **NFRs / security** — performance, scaling, threat model; for production systems; feeds architecture + readiness.
- **Threat model** — enumerated threats + mitigations (STRIDE / attack tree); for any security-sensitive system; feeds architecture + the security review.
- **DPIA / privacy impact assessment** — a documented privacy-risk assessment; GDPR-required when processing is likely high-risk to individuals; feeds security + compliance.
- **SBOM (software bill of materials)** — a machine-readable inventory of components/dependencies; increasingly mandated (e.g. US EO 14028, EU CRA); feeds supply-chain security + compliance. *Generate-and-link.*

## Band 5 — Delivery / go-to-production

- **Test plan / strategy + cases** — what's tested and how; for anything shipping; feeds QA + release.
- **CI/CD plan** — build/test/deploy automation approach; for any repeatable delivery; feeds the pipeline.
- **Deployment runbook** — how to deploy + respond to known failures; for operated services; feeds on-call/incident response.
- **Production-readiness review** — the pre-launch checklist (monitoring, SLOs, rollback); before first production release; feeds the release gate.
- **Observability / monitoring plan** — metrics, logs, alerts; for operated services; feeds the runbook.
- **Rollback plan** — how to revert safely; for risky/production releases; feeds the release gate.
- **SLA / SLO / SLI definitions** — reliability targets + the service agreement; for operated services; feeds monitoring + the runbook (distinct from the monitoring plan: this sets the *targets*, that wires the *signals*).
- **Incident-response plan + postmortem template** — how to respond to and learn from incidents; for operated services; feeds on-call + continuous improvement.
- **Disaster-recovery (DR) plan** — recover from major loss: RTO/RPO, backups, failover; for production services; feeds readiness (distinct from rollback: DR is whole-system recovery, rollback is a release revert).
- **Migration / cutover plan** — moving data/systems + the cutover and its rollback; when replacing or migrating a system; feeds the release.

## Band 6 — User-facing documentation

The product's own shippable docs — for many archetypes (CLI, library, SaaS) these *are* the ship-blocking deliverable, not a build by-product.

- **README** — entry point / orientation; for every project; feeds first use + onboarding.
- **End-user guide / manual** — how to use the product; for any user-facing product; feeds adoption + support.
- **Getting-started / quickstart / install guide** — the first-run path; for CLI, library, API, or app; feeds onboarding.
- **API reference docs** — the published, navigable interface docs users read; for any library/SDK/API; feeds integration. *(The human-read deliverable — distinct from the Band-4 API specification, which is the OpenAPI build-feed.)*
- **Release notes** — a curated, human summary of what changed per release; for anything shipping iteratively; feeds users + stakeholders.
- **Changelog** — a running record of every change by version; for libraries/SDKs and any versioned artifact; feeds maintainers + integrators.

## Domain overlays

Overlays are document sets keyed to a project's **domain**, layered on top of whatever lifecycle bands the archetype walks — **added only when the trigger holds, and additive** (an overlay is not a lifecycle phase). A thin tool triggers none; an ML SaaS may trigger two.

### Data / ML overlay
*Trigger: the product trains/serves models or moves data at meaningful scale.*

- **Model card** — a model's intended use, performance, and limits; feeds responsible-use + review.
- **Datasheet for datasets** — a dataset's provenance, collection, and bias; feeds data review.
- **Data dictionary** — names/definitions/types of data elements; feeds implementation + analytics.
- **Data lineage / data-flow doc** — where data originates, transforms, and lands; feeds governance + impact analysis.
- **Eval / experiment plan** — benchmarks, eval harness, success bar; feeds model acceptance.
- **Data contract** — a producer↔consumer schema/SLA commitment; feeds pipeline reliability.

### Security / compliance overlay
*Trigger: regulated, handles sensitive data, or runs a formal security program.* (The load-bearing threat model / DPIA / SBOM live in Band 4.)

- **Security review / pentest report** — findings from a security assessment; feeds the release gate.
- **Compliance mapping** — controls mapped to SOC 2 / ISO 27001 / HIPAA; feeds audit.
- **Data processing agreement (DPA)** — data-handling contract terms; feeds legal + privacy.

### Legal / governance overlay
*Trigger: published / open-source, or public commercial.*

- **LICENSE** — the legal license; feeds distribution.
- **CONTRIBUTING** — how to contribute; feeds the community.
- **CODE_OF_CONDUCT** — community standards; feeds governance.
- **SECURITY.md** — how to report a vulnerability; feeds responsible disclosure.
- **GOVERNANCE** — roles + decision process; feeds larger OSS projects.
- **Terms of Service / Privacy Policy / EULA** — legal terms for users; feeds a public commercial launch.
- **Third-party license / NOTICE attribution** — dependency-license compliance; feeds distribution.

### Regulated / validation overlay
*Trigger: FDA / medical / pharma / safety-critical.*

- **Requirements traceability matrix (RTM)** — requirement → design → test linkage; feeds audit + validation.
- **Validation protocols (IQ / OQ / PQ)** — install / operational / performance qualification; feeds validation.
- **Validation summary report** — the compiled validation evidence; feeds the regulatory submission.

**See also (research-on-gap):** documents not catalogued here but sometimes needed — RACI, capacity/scaling plan, backup/restore policy, go-to-market/launch plan, training/enablement plan, configuration-management plan, data-retention policy. Research a type before placing it; never guess its purpose.

## Proportionality — load-bearing vs skip, by archetype

| Archetype | Load-bearing | Usually skip |
|---|---|---|
| CLI tool / small library | README, brief design note, API reference docs | PRD, UX docs, formal architecture |
| Library / SDK | API reference docs, user guide, examples, changelog **+ Legal/gov overlay if OSS** | UX docs, deployment runbook |
| API service | PRD/feature list, API spec (OpenAPI), data model, test plan, deployment/runbook | wireframes, design system |
| Web / mobile app | PRD, feature specs, user flows, wireframes, design system, architecture, API spec, test + release plan, README/user guide | (heavy end — most bands apply) |
| Data pipeline | requirements, data model/schema, architecture, runbook, monitoring **+ Data/ML overlay if ML** | UX docs |
| ML / AI product | PRD, architecture, data model, test plan, **+ Data/ML overlay** (model card, datasheet, eval plan) | heavy UX (unless user-facing) |
| OSS library | API reference docs, user guide, changelog, examples, **+ Legal/governance overlay** (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY.md) | PRD, UX docs, deployment runbook |
| Commercial SaaS | PRD, feature specs, user flows, wireframes, architecture, API spec, test + release plan, **+ Legal overlay** (ToS, privacy policy) | (heavy end — most bands apply) |

Lean/MVP context → trim the optional bands to *minimum viable documentation* (keep the load-bearing). Enterprise/regulated → front-load more (charter/SOW, BRD, SRS, NFRs, readiness) and expect the Security/compliance + Regulated/validation overlays. **Band 0 and Band 6 are proportional too:** a thin CLI tool needs only a README (Band 6) and maybe a charter-lite (Band 0), and triggers no overlay — never bloat a small project with the full set. Never cut the load-bearing band to "stay lean."

## Common dependency edges (planning + requirements → design → delivery → docs)

- `charter / sow` — *precedes everything; no upstream depends_on* (it feeds the PRD)
- `prd depends_on` (analysis docs, if any)
- `roadmap / release-plan depends_on prd` (and feature specs)
- `feature-specs depends_on prd`
- `architecture depends_on prd` (and feature specs)
- `api-spec depends_on architecture`
- `data-model depends_on architecture`
- `user-flows depends_on prd`
- `wireframes depends_on user-flows` (or prd)
- `component-specs depends_on design-system`
- `threat-model depends_on architecture`; `dpia depends_on prd` (the data flows)
- `test-plan depends_on feature-specs` (+ api-spec)
- `model-card depends_on` the trained model + eval plan; `rtm depends_on` requirements + tests
- `user-guide / api-reference-docs / release-notes depends_on` the built feature (+ api-spec) — typically late
- `runbook / release-plan / dr-plan depends_on` (architecture + deployment) — typically last

Verify the assembled graph is **acyclic**; dependencies never flow backward (a PRD never depends on the architecture; a charter never depends on the PRD).

## Producer role + tooling quick map (OSS-first)

| Document band | Producer role (illustrative) | OSS-first tools |
|---|---|---|
| Planning / PM (Band 0) | project lead / PM (`idea-strategist × delivery`) | Markdown-in-repo, an issue tracker |
| Product/requirements | product strategist / PM / BA (`idea-strategist × product`) | Markdown-in-repo, a docs store |
| Design/UX | UX designer (`designer × ux`) | Penpot (open Figma alternative), Wireflow |
| Architecture/eng | systems architect (`designer × system`) | C4 / arc42, Markdown, OpenAPI, schema generators |
| Delivery/go-to-prod | QA / SRE / DevOps (`engineer × devops`) | Markdown checklists/runbooks |
| User-facing docs (Band 6) | technical writer (`engineer × docs`) | Markdown, a docs site (MkDocs / Docusaurus), OpenAPI renderers |
| Data / ML overlay | ML engineer / data scientist (`engineer × ml`) | Markdown, model-card / datasheet templates |

Titles vary by org (PM vs BA vs founder all produce PRDs); name the *role kind*, not a fixed title. Proprietary tools (Figma, Confluence) are options, never requirements.
