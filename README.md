# agent-skills

Security, token-efficiency, content-authoring, meta (skill-building), and integration skills for AI coding agents.
Works across **Claude Code, Cursor, GitHub Copilot, Codex,** and **Gemini CLI**.

## Skills in this collection

| Skill | One-line purpose | Category |
|---|---|---|
| [`external-content-sanitizer`](docs/skills/external-content-sanitizer.md) | Defensive runtime sanitizer for external untrusted content (WebFetch / WebSearch / cloned repos) | security |
| [`token-optimization`](docs/skills/token-optimization.md) | Diagnostic + tactic catalog for reducing token usage across 5 layers (system prompt, tool defs, history, tool results, output) | productivity |
| [`content-template-gateway`](docs/skills/content-template-gateway.md) | Gate for any agent-authored structured content (file or external destination) — identifies content-type + variant from intent, enforces template use via hard-refusal directive, forges templates when missing | content authoring |
| [`skill-forge`](docs/skills/skill-forge.md) | Self-learning meta-skill: research a knowledge gap → synthesize a portable SKILL.md (create or improve) with fact-check + self-review; broad topics fan out into multiple skills | meta / authoring |
| [`atlassian-rest-ops`](docs/skills/atlassian-rest-ops.md) | Call the Atlassian Cloud REST API directly (Confluence v2 + Jira v3) via curl — bundled OpenAPI + `$ref`-resolver, per-API patterns, ADF/storage rich-text; no SDK | integration |
| [`github-cli-ops`](docs/skills/github-cli-ops.md) | Perform any github.com operation CLI-first via `gh`, falling back to `gh api` (REST) / `gh api graphql` where no command exists — per-call `GH_TOKEN` auth (no `gh auth switch`), bundled OpenAPI + `$ref`-resolver for all 1,186 ops, `gh secret set` for secret encryption | integration |
| [`design-review`](docs/skills/design-review.md) | Adversarial pre-approval review of a design doc — spec / plan / RFC / ADR — hunts recurring gap categories (+ a plan lens for plans), verifies claims against the codebase (`file:line`, no fabrication), returns severities + a ready / has-blockers verdict; review-only (never edits or approves) | review |
| [`project-document-discovery`](docs/skills/project-document-discovery.md) | Decide which documents a project needs to ship to production (and what it takes to produce each) — turns an idea into a proportional document plan: the set + per-document producer role/tools/skills + an acyclic dependency graph, keyed to project archetype; discovery only (not authoring) | planning |
| [`authoring-prd`](docs/skills/authoring-prd.md) | Author a comprehensive, plannable PRD from a product idea — the *method* + quality bar (evidenced problem, measurable metrics, defensible MVP boundary, testable acceptance criteria, never fabricates evidence), not the section list; composes with a PRD template tool + deep research; produce-side only | content authoring |
| [`reviewing-prd`](docs/skills/reviewing-prd.md) | Judge a finished PRD against a plannability bar (problem evidenced, metrics measurable, MVP boundary defensible, features plannable, no fabricated evidence) — an acceptance gate; emits `VERDICT: approve\|revise` + actionable findings, no false-revise; single-sources its bar from `authoring-prd` | content authoring |
| [`authoring-feature-spec`](docs/skills/authoring-feature-spec.md) | Author a feature spec — elaborate a PRD's named features into implementable, testable detail (trace to PRD, observable behavior, I/O + states, edge cases with handling, Given/When/Then criteria); composes with a feature-spec template tool; assumes the PRD as upstream input | content authoring |
| [`reviewing-feature-spec`](docs/skills/reviewing-feature-spec.md) | Judge a finished feature spec against an implementability + testability bar (every feature traced, behavior unambiguous, I/O + states complete, edge cases with response, criteria independently testable) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-feature-spec` | content authoring |
| [`authoring-user-flows`](docs/skills/authoring-user-flows.md) | Author a user-flows document — the navigation graph of the paths a user takes to each goal (entry points, branches, error/recovery paths, screens traversed); derives flows from the PRD's goals/personas, no dead ends, each flow as a synced Mermaid diagram + numbered narrative; composes with a user-flows template tool | content authoring |
| [`reviewing-user-flows`](docs/skills/reviewing-user-flows.md) | Judge a finished user-flows doc against a completeness + walkability bar (every goal mapped, every flow with entry/exit, every branch resolved, no dead ends, both notations in sync, screens enumerable) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-user-flows` | content authoring |
| [`authoring-wireframes`](docs/skills/authoring-wireframes.md) | Author a wireframes document — the structural lo-fi design of each screen (layout regions, hierarchy, components, affordances, empty/loading/populated/error states) as a textual layout description + ASCII sketch + annotations; one wireframe per flow-named screen; composes with a wireframes template tool | content authoring |
| [`reviewing-wireframes`](docs/skills/reviewing-wireframes.md) | Judge a finished wireframes doc (textual markdown, not Figma) against a buildability + coverage bar (every flow-named screen + all four states, unambiguous layout, components design-system-consistent, affordances + a11y) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-wireframes` | content authoring |
| [`authoring-design-system`](docs/skills/authoring-design-system.md) | Author a design-system document — principles, tokens (color/type/spacing/elevation/motion), a component catalog (anatomy/states/variants/usage/a11y), patterns, accessibility, voice; semantic-token tiering + an archetype-sized catalog covering the screens' real components; textual artifact; composes with a design-system template tool | content authoring |
| [`reviewing-design-system`](docs/skills/reviewing-design-system.md) | Judge a finished design-system doc against a usability + consistency + accessibility bar (tokens referenced by intent, components fully specced, catalog covers the surface area + standard set, numeric WCAG) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-design-system` | content authoring |
| [`authoring-technical-design`](docs/skills/authoring-technical-design.md) | Author a technical design doc (TDD) for one feature/component — the *method* + implementability bar (trace every decision to a requirement, one real alternative with a decision criterion, reference the architecture/api-spec/data-model rather than duplicate, failure modes + testing + rollout); composes with a technical-design template tool; assumes the PRD + feature-spec as upstream input | content authoring |
| [`authoring-architecture-doc`](docs/skills/authoring-architecture-doc.md) | Author a whole-system architecture doc — the *method* + usability bar (boundary first, one responsibility per component, justify each tech choice, a realization per NFR target) recording each key decision as a standalone, linked ADR file (the doc carries only a decisions index); composes with an architecture-doc template tool + an ADR template tool; assumes the PRD + product direction as input | content authoring |
| [`authoring-api-spec`](docs/skills/authoring-api-spec.md) | Author an API specification (the engineering wire contract) — the *method* + no-ambiguity bar (render in the project's style — OpenAPI/SDL/proto — type every field, enumerate the error cases not just the happy path, reference the data-model rather than redefine it); composes with an api-spec template tool; assumes the feature-spec as upstream input | content authoring |
| [`authoring-data-model`](docs/skills/authoring-data-model.md) | Author a data model doc (the persistence/domain model) — the *method* + integrity/queryability bar (derive entities from the feature-spec + access patterns, detect the paradigm — relational or document/NoSQL — make integrity rules explicit, justify each index by an access pattern); composes with a data-model template tool; assumes the feature-spec as upstream input | content authoring |

## Quick install (Claude Code)

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
npx skills add bm629/agent-skills@token-optimization
npx skills add bm629/agent-skills@content-template-gateway
npx skills add bm629/agent-skills@skill-forge
npx skills add bm629/agent-skills@atlassian-rest-ops
npx skills add bm629/agent-skills@github-cli-ops
npx skills add bm629/agent-skills@design-review
npx skills add bm629/agent-skills@project-document-discovery
npx skills add bm629/agent-skills@authoring-prd
npx skills add bm629/agent-skills@reviewing-prd
npx skills add bm629/agent-skills@authoring-feature-spec
npx skills add bm629/agent-skills@reviewing-feature-spec
npx skills add bm629/agent-skills@authoring-user-flows
npx skills add bm629/agent-skills@reviewing-user-flows
npx skills add bm629/agent-skills@authoring-wireframes
npx skills add bm629/agent-skills@reviewing-wireframes
npx skills add bm629/agent-skills@authoring-design-system
npx skills add bm629/agent-skills@reviewing-design-system
npx skills add bm629/agent-skills@authoring-technical-design
npx skills add bm629/agent-skills@authoring-architecture-doc
npx skills add bm629/agent-skills@authoring-api-spec
npx skills add bm629/agent-skills@authoring-data-model
```

For Cursor, GitHub Copilot, Codex, or Gemini CLI — see the
[installation guide](docs/installation.md).

## Documentation

| Doc | Covers |
|---|---|
| [`docs/installation.md`](docs/installation.md) | Per-agent install instructions for all 4 target agents + Gemini bonus; troubleshooting |
| [`docs/skills/external-content-sanitizer.md`](docs/skills/external-content-sanitizer.md) | Deep dive: when to invoke, args, workflow, output format, safety invariants |
| [`docs/skills/token-optimization.md`](docs/skills/token-optimization.md) | Deep dive: 5-layer model, measure-first workflow, per-layer tactics |
| [`docs/skills/content-template-gateway.md`](docs/skills/content-template-gateway.md) | Deep dive: 5-phase workflow (identify / check / enforce / forge / advise), 3 invocation modes, ASCII directive format, destination-agnostic framing |
| [`docs/skills/skill-forge.md`](docs/skills/skill-forge.md) | Deep dive: 8-step workflow (triage / find-research-verify / synthesize / write+self-review), synthesize-only + forge-mark + capability-based deps, multi-skill fan-out |
| [`docs/skills/atlassian-rest-ops.md`](docs/skills/atlassian-rest-ops.md) | Deep dive: find→resolve→curl workflow, per-API patterns (base URL, pagination, errors), ADF vs storage rich-text, credential file convention, bundled OpenAPI + resolver |
| [`docs/skills/github-cli-ops.md`](docs/skills/github-cli-ops.md) | Deep dive: CLI-first + `gh api` fallback workflow, per-call `GH_TOKEN` auth (no `gh auth switch`), the common gh-api-only areas (~1/3 of the surface), bundled OpenAPI + resolver, `gh secret set` encryption |
| [`docs/skills/design-review.md`](docs/skills/design-review.md) | Deep dive: the 8-step review workflow, the 9-category gap rubric + conditional plan lens, verify-against-code (`file:line`, no fabrication, greenfield N/A, bounded), findings + verdict format, review-only guarantees |
| [`docs/skills/project-document-discovery.md`](docs/skills/project-document-discovery.md) | Deep dive: the 6-step selection discipline, the seven lifecycle bands + four domain overlays + per-archetype proportionality, the producer-role + OSS-tooling map, the dependency DAG, discovery-only guarantees |
| [`docs/skills/authoring-prd.md`](docs/skills/authoring-prd.md) | Deep dive: the 5-step workflow (structure-from-template / discover gaps / research / per-section method / self-check), the 8-condition plannability bar, compose-not-restate + never-fabricate guarantees |
| [`docs/skills/reviewing-prd.md`](docs/skills/reviewing-prd.md) | Deep dive: the 8-condition plannability bar, the `VERDICT: approve\|revise` + actionable-findings contract, no-false-revise discipline, single-sourced-from-`authoring-prd` |
| [`docs/skills/authoring-feature-spec.md`](docs/skills/authoring-feature-spec.md) | Deep dive: the per-feature method (PRD-trace / observable behavior / I/O+states / edge-cases-with-handling / Given-When-Then criteria), compose-with-template + PRD-is-upstream guarantees |
| [`docs/skills/reviewing-feature-spec.md`](docs/skills/reviewing-feature-spec.md) | Deep dive: the implementability+testability bar, the `VERDICT: approve\|revise` contract, no-false-revise, single-sourced-with-`authoring-feature-spec` |
| [`docs/skills/authoring-user-flows.md`](docs/skills/authoring-user-flows.md) | Deep dive: the flow-derivation method (goals/personas → flows, no-dead-ends edge sweep, synced Mermaid + numbered narrative), compose-with-template + PRD-is-upstream guarantees |
| [`docs/skills/reviewing-user-flows.md`](docs/skills/reviewing-user-flows.md) | Deep dive: the completeness + walkability bar, the `VERDICT: approve\|revise` contract, no-false-revise, single-sourced-with-`authoring-user-flows` |
| [`docs/skills/authoring-wireframes.md`](docs/skills/authoring-wireframes.md) | Deep dive: the screen-derivation method (one wireframe per flow-named screen, per-screen states, design-system reference), textual layout-desc + ASCII + annotations, structural-lo-fi guarantees |
| [`docs/skills/reviewing-wireframes.md`](docs/skills/reviewing-wireframes.md) | Deep dive: the buildability + coverage bar, judges textual markdown not Figma, the `VERDICT: approve\|revise` contract, single-sourced-with-`authoring-wireframes` |
| [`docs/skills/authoring-design-system.md`](docs/skills/authoring-design-system.md) | Deep dive: the token/component method (semantic-token tiering, surface-area floor + standard set, per-component a11y), textual artifact, precedes-wireframes + compose-with-template guarantees |
| [`docs/skills/reviewing-design-system.md`](docs/skills/reviewing-design-system.md) | Deep dive: the usability + consistency + accessibility bar, the `VERDICT: approve\|revise` contract, no-false-revise of a proportional system, single-sourced-with-`authoring-design-system` |
| [`docs/skills/authoring-technical-design.md`](docs/skills/authoring-technical-design.md) | Deep dive: the design method (structure-from-template / requirement-trace / per-section method / implementability self-check), reference-not-duplicate + feature-altitude + one-real-alternative guarantees |
| [`docs/skills/authoring-architecture-doc.md`](docs/skills/authoring-architecture-doc.md) | Deep dive: the architecture method (boundary-first / responsibility-per-component / realization-per-NFR), the standalone-linked-ADR decision mechanism, sized-to-archetype + compose-with-two-templates guarantees |
| [`docs/skills/authoring-api-spec.md`](docs/skills/authoring-api-spec.md) | Deep dive: the contract method (style-first / type-both-sides / enumerate-error-cases / examples-match-schemas), style-agnostic rigor + reference-the-data-model + contract-not-reference guarantees |
| [`docs/skills/authoring-data-model.md`](docs/skills/authoring-data-model.md) | Deep dive: the modeling method (paradigm detection / access-patterns-first / cardinality + referential rule / justified indexes / stated tradeoffs), paradigm-aware + one-directional-vs-api-spec guarantees |
| [`docs/architecture.md`](docs/architecture.md) | Repo layout, metadata files, why the SKILL.md frontmatter has per-agent `extensions:` blocks |
| [`docs/compatibility.md`](docs/compatibility.md) | Agent compatibility matrix; v1 status vs v2 plugin-packaging roadmap |
| [`docs/contributing.md`](docs/contributing.md) | How to file issues, propose new skills, modify existing ones |

## Why these skills, why together?

Each fills a **genuinely empty niche** in the public skill ecosystem (verified
against skills.sh as of 2026-05-24):

- **`external-content-sanitizer`** is the only **defensive operational
  guardrail** for incoming untrusted content. Other skills in this space
  are either offensive attack playbooks (red team), audit tools (scan
  your own skills for vulnerabilities), or doc-style guidelines.
- **`token-optimization`** is the only **strategic methodology** spanning
  all five token-budget layers. Other skills tackle a single layer
  (caching, context management, or output sizing) in isolation.
- **`content-template-gateway`** is the only **template-enforcement
  gateway** that catches every content-authoring attempt (user or
  agent) — file-bound or external-bound (GitHub PR / issue, Jira
  ticket, commit message, Slack post, Confluence page, etc.) — and
  either returns an existing template with a hard-refusal directive
  or forges a new one. Other template skills are passive — they wait
  to be invoked explicitly, and they only know about files.
- **`skill-forge`** turns a knowledge gap into a portable skill —
  research → fact-check → synthesize (or improve) a `SKILL.md`, with a
  multi-cycle self-review. It's the **meta-skill** that can build the
  others, and the skills it produces are self-contained + portable.
- **`atlassian-rest-ops`** gives **full-coverage** Confluence Cloud v2 +
  Jira Cloud v3 access by calling the REST API directly (`curl` + a
  bundled OpenAPI spec + a `$ref`-resolver) — no SDK, no `pip`, with the
  per-API and ADF/storage rich-text gotchas handled.
- **`github-cli-ops`** gives **full-coverage** github.com access
  **CLI-first** (the `gh` CLI), with `gh api` + a bundled OpenAPI
  `$ref`-resolver for the ~1/3 of the REST surface that has no first-class
  command (teams, checks, packages, code-scanning, dependabot, git-data,
  reactions, apps, …). Per-call `GH_TOKEN` auth means no global
  `gh auth switch`; `gh secret set` handles client-side secret encryption.
  It's the GitHub sibling of `atlassian-rest-ops` under the per-provider
  service-skill pattern.
- **`design-review`** is the only **design-document** reviewer that runs
  *before* code exists and **verifies its findings against the actual
  codebase** (`file:line`, never fabricated). Code-review skills target
  diffs; this targets the spec/plan/RFC/ADR, hunting recurring gap categories
  (bootstrap & ownership, naming honesty, scale, hidden assumptions,
  consistency-with-shipped-code, idempotency/failure, security, necessity,
  completeness) — plus, when the doc is a **plan**, a plan lens (task
  granularity, dependency-DAG, coverage-vs-spec, exit-criteria testability) —
  and returning a `ready` / `has-blockers` verdict. Review-only —
  it recommends; the human approves, the author fixes.
- **`project-document-discovery`** answers a question no other skill in the
  set does: *which documents does this project need to ship to production, and
  what does it take to produce each?* It turns an idea into a **proportional
  document plan** — sized to the project archetype (a thin CLI tool gets a
  handful; a UI product many), each document tagged with its producer role,
  OSS-first tooling, and an acyclic dependency order — guarding against the
  heavy-fixed-taxonomy anti-pattern. Discovery only: it picks the *set*;
  authoring each document is a separate concern (it composes with
  `content-template-gateway`).

Hand-authored or forge-built; see each skill's deep-dive doc for details.

## Status

v2.11.0 — re-audits **`project-document-discovery`**'s dependency model (skill → **v1.2.0**), the first of two
ships for the agent-flow **document-dependency-contract** change. A document's `depends_on` now lists **every
document that *informs* it** — not only the strictly-blocking input — and every catalog entry across the seven
bands + four overlays carries an explicit `depends_on` list; discovery copies those edges into the manifest
**pruned to the project's set** (verified acyclic; the `api-spec`/`data-model` pair stays one-directional). The
effect: a downstream document's producer is handed the full enriching upstream set (e.g. user-flows now consume
the feature-spec, not just the PRD), so produced documents come out more comprehensive. The matching
producer-contract framing pass over the authoring/reviewing skills (consume-the-handed-in-set · self-contained ·
research-using) lands next in v2.12.0. Additive — the skill's selection discipline + proportionality are unchanged.

v2.10.0 — adds the **Engineering cluster** of the agent-flow document-skill library (nineteenth–twenty-second
skills), authoring-only: **`authoring-technical-design`** (a TDD for one feature/component — trace every
decision to a requirement, one real alternative with a decision criterion, reference the
architecture/api-spec/data-model rather than duplicate, failure modes + testing + rollout),
**`authoring-architecture-doc`** (the whole-system structure — boundary first, a responsibility per component,
a realization per NFR target, each key decision recorded as a standalone, linked ADR file with only a
decisions index in the doc), **`authoring-api-spec`** (the engineering wire contract — style-agnostic rigor
across OpenAPI/SDL/proto, every field typed, the error cases enumerated not just the happy path, referencing
the data-model rather than redefining it), and **`authoring-data-model`** (the persistence/domain model —
paradigm-aware across relational and document/NoSQL, integrity rules explicit, each index justified by an
access pattern, one-directional vs the api-spec). Each is a textual markdown artifact whose method + bar are
medium-independent. This cluster has no `reviewing-` siblings — the four engineering docs are gated at runtime
by the generic `design-review` skill, so each authoring skill's self-check bar is that gate's checklist; a
new gateway `adr` template ships alongside for the standalone decision records. Built via the batched build
orchestrator (parallel forge, cap 3, + an independent fresh-reviewer dry-run per skill). Additive — existing
skills unchanged.

v2.9.0 — adds the **Design/UX cluster** of the agent-flow document-skill library (thirteenth–eighteenth
skills): three authoring/reviewing pairs — **`authoring-user-flows`** / **`reviewing-user-flows`** (the
navigation graph: paths, branches, error/recovery, screens — synced Mermaid + numbered narrative, no
dead ends), **`authoring-wireframes`** / **`reviewing-wireframes`** (structural lo-fi screen design as a
textual layout description + ASCII sketch + annotations, all four per-screen states, one wireframe per
flow-named screen), and **`authoring-design-system`** / **`reviewing-design-system`** (tokens + a
component catalog with semantic-token tiering, per-component a11y, and an archetype-sized catalog covering
the screens' real components). Each is a textual markdown artifact (a remote design-tool backend is a
future concern). The reviewers emit `VERDICT: approve|revise` + actionable findings with no-false-revise
discipline; each pair single-sources its bar from one shared dossier so produce and review never drift.
Built via the batched build orchestrator (parallel forge, cap 3, + an independent fresh-reviewer dry-run
per pair). Additive — existing skills unchanged.

v2.8.0 — adds the **Product cluster** of the agent-flow document-skill library (tenth–twelfth
skills): **`reviewing-prd`** (judge a PRD against a plannability bar), **`authoring-feature-spec`**
(elaborate a PRD's features into testable detail), and **`reviewing-feature-spec`** (judge a feature
spec against an implementability+testability bar). The reviewers emit `VERDICT: approve|revise` +
actionable findings with no-false-revise discipline; each authoring/reviewing pair single-sources its
bar from one shared dossier so produce and review never drift. Built via the batched build orchestrator
(parallel forge + independent fresh-reviewer pass per skill). Additive — existing skills unchanged.

v2.7.0 — expands **`project-document-discovery`** to **v1.1.0**: the document-type
catalog grows from five lifecycle bands to **seven** (adds Band 0 project-management/
planning + Band 6 user-facing documentation) plus **four domain overlays** (data/ML,
security/compliance, legal/governance, regulated/validation) triggered only when a
project's domain calls for them. Band 4 gains threat model / DPIA / SBOM; Band 5 gains
SLA-SLO / incident+postmortem / DR / migration; the archetype table adds ML/AI, OSS-library,
and commercial-SaaS rows. Closes coverage gaps from a comprehensive research pass; the new
document types were fresh-reviewer fact-checked (12/12 verified). Additive — the skill's
body, rules, and proportionality discipline are unchanged.

v2.6.0 — adds **`authoring-prd`** (ninth skill): author a comprehensive, plannable
PRD from a product idea — the *method* + quality bar (evidenced problem, measurable
metrics, defensible MVP boundary, testable acceptance criteria), composing with a PRD
template tool + a deep-research capability. Never fabricates evidence (honest flagged
assumptions instead); produce-side only — a companion PRD-review skill asserts the same
bar. Forge-built (deep-research grounded, 3 fresh-reviewer self-review cycles) +
dogfooded on a sample idea. Additive — the existing eight skills are unchanged.

v2.5.0 — adds **`project-document-discovery`** (eighth skill): from a project
idea, decides which documents the project needs to ship to production and what
it takes to produce each — a proportional document plan (the document set +
per-document producer role/tools/skills + an acyclic dependency graph), keyed to
the project archetype. Discovery only (composes with `content-template-gateway`
for authoring). Forge-built (deep-research grounded) + dogfooded on sample
ideas. Additive — the existing seven skills are unchanged.

v2.4.0 — **renames `spec-review` → `design-review`** (it reviews any design
document — spec, plan, RFC, ADR — not just specs) and adds a **conditional plan
lens** (task granularity · dependency-DAG · coverage-vs-spec · exit-criteria
testability) that activates when the reviewed doc is a plan. The `@spec-review`
package path is **removed** (clean break, like `doc-template-gateway` →
`content-template-gateway`); install `@design-review`. The review behavior
(9-category rubric, code-grounded `file:line` verification) is otherwise unchanged.

v2.3.0 — adds **`spec-review`** (seventh skill): an adversarial pre-approval
reviewer for spec / design doc / RFC / plan documents. Hunts a 9-category gap
rubric and **verifies claims against the actual codebase** (`file:line`, no
fabrication, greenfield N/A, bounded), returning severities + a `ready` /
`has-blockers` verdict. Review-only — never edits or approves. Forge-built and
dogfooded on a real spec. Additive — the existing six skills are unchanged.

v2.2.0 — adds **`github-cli-ops`** (sixth skill): full-coverage github.com
access, CLI-first via `gh` with a `gh api` (REST) + bundled-OpenAPI
`$ref`-resolver fallback for the ~1/3 of the API with no first-class command.
Per-call `GH_TOKEN` auth (no `gh auth switch`); `gh secret set` for secret
encryption. Forge-built (3 review cycles) + live-smoked against real github.com.
Additive — the existing five skills are unchanged.

v2.1.0 — adds two skills: **`skill-forge`** (a self-learning meta-skill
that researches a knowledge gap and synthesizes a portable `SKILL.md`)
and **`atlassian-rest-ops`** (direct Confluence / Jira Cloud REST
access via curl + bundled OpenAPI). Additive — the existing three
skills are unchanged.

v2.0.0 — renames the third skill from `doc-template-gateway` to
`content-template-gateway` and widens its scope from doc-files-only
to any agent-authored structured content (any destination). Breaking
for consumers of the v1.1.x `@doc-template-gateway` package path; the
old name simply ceases with no backwards-compat shim. All three skills
continue to work via direct `npx skills add` URL on all five supported
agents.

**Not yet indexed in skills.sh registry** — the repo won't appear in
`npx skills find` or the public leaderboard until a future version
adds the `.claude-plugin/marketplace.json` manifest. Install today by
sharing the direct URL. Pre-rendered per-agent plugin packages are
also future work.

See [architecture.md § Roadmap](docs/architecture.md#roadmap) for the
roadmap.

## License

MIT © 2026 Bhushan Modi. See [LICENSE](LICENSE).
