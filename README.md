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
| [`authoring-user-guide`](docs/skills/authoring-user-guide.md) | Author an end-user guide — the consumer-facing help a (non-technical) user reads: the *method* + usability/accuracy bar (full Diataxis, one how-to per handed-in goal, modes kept distinct, end-user feature/config reference — not the API, steps accurate to the product); composes with a user-guide template tool; assumes the feature-spec + user-flows + wireframes as upstream input | content authoring |
| [`authoring-developer-guide`](docs/skills/authoring-developer-guide.md) | Author developer-tool documentation — the SDK/library/CLI/API-platform adoption + integration narrative: the *method* + adoptability/accuracy bar (goals-not-endpoints, fast first success, concepts before reference, code-centric recipes, runnable accurate code, links — not copies — the api-reference); composes with a developer-guide template tool; assumes the feature-spec + api-reference + PRD as upstream input | content authoring |
| [`authoring-api-reference`](docs/skills/authoring-api-reference.md) | Author a published, consumer-facing API reference — the *method* + usability/contract-consistency bar (derive every endpoint/field/error from the api-spec — no drift, onboarding-first getting-started + auth, a worked example per operation, prose-first yet generation-adaptive); composes with an api-reference template tool; assumes the api-spec as upstream input | content authoring |
| [`reviewing-user-guide`](docs/skills/reviewing-user-guide.md) | Judge a finished end-user guide against a usability + accuracy bar (one how-to per handed-in goal, Diataxis modes correctly typed, feature/config reference complete — not the API, steps accurate, troubleshooting covers error states) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-user-guide` | content authoring |
| [`reviewing-developer-guide`](docs/skills/reviewing-developer-guide.md) | Judge a finished developer guide against an adoptability + accuracy bar (verifiable first success, concepts before recipes, runnable code accurate to the tool, links — not duplicates — the api-reference) with named upstream-accuracy + api-reference-linking checks — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-developer-guide` | content authoring |
| [`reviewing-api-reference`](docs/skills/reviewing-api-reference.md) | Judge a finished published API reference against a usability + contract-consistency bar (every api-spec operation documented with a worked example, every endpoint/shape/error traces to the contract — no drift, getting-started + auth, samples) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-api-reference` | content authoring |
| [`authoring-release-runbook`](docs/skills/authoring-release-runbook.md) | Author a release/deployment runbook — the *method* + executability/safety bar (idempotent copy-paste-safe steps each with an expected result, deploy derived from the architecture-doc + technical-design and verification from the test-plan, blue-green default overridable per project, a documented revert for every forward change, no secret inlined); composes with a release-runbook template tool; assumes the architecture-doc + technical-design + test-plan as upstream input | content authoring |
| [`authoring-test-plan`](docs/skills/authoring-test-plan.md) | Author a test plan / QA verification plan — the *method* + coverage/testability bar (every case traced to a feature-spec behavior or api-spec operation/error, a risk-weighted catalog not the input-permutation cross-product, testable entry/exit criteria, non-functional levels from the NFRs); composes with a test-plan template tool; assumes the feature-spec + api-spec + PRD as upstream input | content authoring |
| [`reviewing-release-runbook`](docs/skills/reviewing-release-runbook.md) | Judge a finished release runbook against an executability + safety bar (every step verified, a complete + safe rollback with a revert for every forward change — load-bearing, concrete escalation/monitoring, no secret inlined, commands accurate to the upstreams) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-release-runbook` | content authoring |
| [`reviewing-test-plan`](docs/skills/reviewing-test-plan.md) | Judge a finished test plan against a coverage + testability bar (every upstream behavior has a traceable case, a risk-weighted catalog — a coverage gap or a combinatorial blow-up is a finding, testable entry/exit, environments specified) — an acceptance gate; emits `VERDICT: approve\|revise` + findings; pairs with `authoring-test-plan` | content authoring |
| [`reviewing-document-set`](docs/skills/reviewing-document-set.md) | Judge a finished SET of documents as one corpus for cross-document coherence (consistency incl. one name per entity, traceability from the root, contradictions, dependency integrity, no divergent duplication, ready-to-plan) — the corpus-level analog of a design review, run after each document's own gate; emits one `VERDICT: approve\|revise` + per-document-attributed findings, no false-revise | content authoring |
| [`pydantic-v2`](docs/skills/pydantic-v2.md) | Write correct, current Pydantic v2 — `BaseModel` + `Field` constraints, `@field_validator`/`@model_validator`, `model_dump*`, `ConfigDict`, `pydantic-settings`, `TypeAdapter`, discriminated unions — and modernize v1-era idioms (`class Config`, `.dict()`, `@validator`); standalone-Pydantic, defers framework wiring to `fastapi` | engineering |
| [`rest-api-design`](docs/skills/rest-api-design.md) | Design a REST/HTTP API surface and its contract — resources/URLs, methods + status codes, one error model (RFC 9457 problem+json), success/pagination envelope, versioning/auth/rate-limit, rendered as an OpenAPI 3.1 contract; the design discipline above the framework, defers handler code to `fastapi`/`pydantic-v2` | engineering |
| [`python-monorepo-architecture`](docs/skills/python-monorepo-architecture.md) | Architect a multi-package Python uv-workspace monorepo (shared lib + app/CLI members) — the cross-package layer: when to split, the workspace wiring (`[tool.uv.workspace]` / `[tool.uv.sources] {workspace=true}`), the acyclic depend-inward dependency direction (apps→core, never app↔app), the import-isolation discipline uv can't enforce (+ optional `import-linter`), member-boundary public API, and safe extraction; owns the workspace wiring, composes with `uv` + `python-project-structure` | engineering |
| [`openapi-ts-client`](docs/skills/openapi-ts-client.md) | Generate a typed TypeScript client from an OpenAPI 3.1 contract (e.g. a FastAPI `/openapi.json`) with `@hey-api/openapi-ts` — typed models, a typed SDK, TanStack Query hooks, and Zod schemas, regenerated from the spec not hand-written; covers the config, the fetch/axios/next clients, the tanstack-query + zod plugins, the regen + CI-drift workflow, and the FastAPI `operationId` fix; defers TanStack Query usage to `tanstack-query` | engineering |
| [`biome`](docs/skills/biome.md) | Lint + format a JS/TS project with Biome v2 — one fast Rust tool (the JS analog of `ruff`): the `biome.json` config (formatter, linter rule groups + `domains`, assist/import-organize, VCS, overrides, monorepo `extends`), the CLI (`biome check --write`, `biome ci`), ESLint/Prettier migration, the v1→v2 deltas (`--apply` → `--write`), and authoring custom rules as GritQL plugins; defers pipeline task-wiring to `turborepo` | engineering |
| [`typescript-typecheck`](docs/skills/typescript-typecheck.md) | Run TypeScript type-checking as a standalone gate — `tsc --noEmit` separate from the bundler (no transpiler type-checks: Vite/esbuild/SWC strip types), a genuinely strict `tsconfig` (beyond `strict: true`), the Vite split-config, composite project references for a monorepo, the CI gate, and the `tsgo`/TS-7.0 status; the TS analog of a `ty` gate, defers the build to `vite` + pipeline to `turborepo` | engineering |
| [`polyglot-git-hooks`](docs/skills/polyglot-git-hooks.md) | Set up Git hooks for a polyglot/monorepo with Lefthook — one `lefthook.yml` running format/lint on staged files at pre-commit and type-check/test at pre-push across mixed-language subtrees (TS + Python) in parallel: install + fresh-clone activation, the schema (`glob`/`root`/`{staged_files}`/`stage_fixed`/`parallel`), a genuinely polyglot (biome + ruff) example, hooks-vs-CI, the `--no-verify` bypass; defers tool flags to `biome`/`ruff`/`ty`/`typescript-typecheck` | engineering |
| [`tsdoc`](docs/skills/tsdoc.md) | Write TSDoc doc-comments on a TypeScript public surface (`@microsoft/tsdoc`) — what to document (exported functions/types/components/hooks) vs skip (private/generated/trivial/type-restating), the block/inline/modifier tag taxonomy, summary-then-`@remarks`, and the cardinal rule (no `{type}` in comments — TS has them); enforcement convention-only by default (`eslint-plugin-tsdoc` optional); the TS analog of a docstring discipline | engineering |

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
npx skills add bm629/agent-skills@authoring-user-guide
npx skills add bm629/agent-skills@authoring-developer-guide
npx skills add bm629/agent-skills@authoring-api-reference
npx skills add bm629/agent-skills@reviewing-user-guide
npx skills add bm629/agent-skills@reviewing-developer-guide
npx skills add bm629/agent-skills@reviewing-api-reference
npx skills add bm629/agent-skills@authoring-release-runbook
npx skills add bm629/agent-skills@authoring-test-plan
npx skills add bm629/agent-skills@reviewing-release-runbook
npx skills add bm629/agent-skills@reviewing-test-plan
npx skills add bm629/agent-skills@reviewing-document-set
npx skills add bm629/agent-skills@pydantic-v2
npx skills add bm629/agent-skills@rest-api-design
npx skills add bm629/agent-skills@python-monorepo-architecture
npx skills add bm629/agent-skills@openapi-ts-client
npx skills add bm629/agent-skills@biome
npx skills add bm629/agent-skills@typescript-typecheck
npx skills add bm629/agent-skills@polyglot-git-hooks
npx skills add bm629/agent-skills@tsdoc
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
| [`docs/skills/authoring-user-guide.md`](docs/skills/authoring-user-guide.md) | Deep dive: the end-user-docs method (full Diataxis, one-how-to-per-handed-in-goal, modes-kept-distinct, end-user-not-API reference, error-sourced troubleshooting), compose-with-template + single-sourced-with-`reviewing-user-guide` guarantees |
| [`docs/skills/authoring-developer-guide.md`](docs/skills/authoring-developer-guide.md) | Deep dive: the developer-experience method (goals-not-endpoints / fast first success / concepts-before-reference / code-centric recipes / links-not-copies-the-api-reference), accurate-runnable-code + single-sourced-with-`reviewing-developer-guide` guarantees |
| [`docs/skills/authoring-api-reference.md`](docs/skills/authoring-api-reference.md) | Deep dive: the consumer-reference method (derive-every-endpoint-from-the-api-spec / onboarding-first / worked-example-per-operation / prose-first-yet-generation-adaptive), no-drift + single-sourced-with-`reviewing-api-reference` guarantees |
| [`docs/skills/reviewing-user-guide.md`](docs/skills/reviewing-user-guide.md) | Deep dive: the usability + accuracy bar (per-handed-in-goal how-to coverage, Diataxis typing, complete end-user reference, accurate steps, error-state troubleshooting), `VERDICT: approve\|revise` contract, no-false-revise, single-sourced-with-`authoring-user-guide` |
| [`docs/skills/reviewing-developer-guide.md`](docs/skills/reviewing-developer-guide.md) | Deep dive: the adoptability + accuracy bar with named upstream-accuracy + api-reference-linking checks (verifiable first success, concepts-before-recipes, runnable accurate code, link-not-duplicate), `VERDICT: approve\|revise` contract, single-sourced-with-`authoring-developer-guide` |
| [`docs/skills/reviewing-api-reference.md`](docs/skills/reviewing-api-reference.md) | Deep dive: the usability + contract-consistency bar (every operation documented, every endpoint/shape/error traces to the handed-in api-spec — the load-bearing no-drift check), `VERDICT: approve\|revise` contract, single-sourced-with-`authoring-api-reference` |
| [`docs/skills/authoring-release-runbook.md`](docs/skills/authoring-release-runbook.md) | Deep dive: the operational method (SRE-grounded, deploy-from-architecture+technical-design, verify-from-test-plan, idempotent copy-paste-safe steps, blue-green-default-overridable, revert-per-forward-change, secrets-by-reference), compose-with-template + single-sourced-with-`reviewing-release-runbook` guarantees |
| [`docs/skills/authoring-test-plan.md`](docs/skills/authoring-test-plan.md) | Deep dive: the test-strategy method (case-per-behavior/operation/error, choose-the-levels, risk-weighted-not-cross-product catalog, testable entry/exit, NFR-sourced non-functional levels), specs-cases-not-scripts + single-sourced-with-`reviewing-test-plan` guarantees |
| [`docs/skills/reviewing-release-runbook.md`](docs/skills/reviewing-release-runbook.md) | Deep dive: the executability + safety bar (per-step verification, complete+safe rollback with a revert per forward change — load-bearing, concrete escalation/monitoring, no-inlined-secret, upstream-accurate commands), `VERDICT: approve\|revise` contract, single-sourced-with-`authoring-release-runbook` |
| [`docs/skills/reviewing-test-plan.md`](docs/skills/reviewing-test-plan.md) | Deep dive: the coverage + testability bar (traceable-case-per-behavior, risk-weighted catalog — coverage-gap and combinatorial-blow-up both findings, testable entry/exit, environments specified), `VERDICT: approve\|revise` contract, single-sourced-with-`authoring-test-plan` |
| [`docs/skills/pydantic-v2.md`](docs/skills/pydantic-v2.md) | Deep dive: the 8-step current-v2 workflow (define / constrain / validate / serialize / configure / settings / structure / errors), the hard v2-only rules, the v1→v2 modernization scope, and the `fastapi` boundary |
| [`docs/skills/rest-api-design.md`](docs/skills/rest-api-design.md) | Deep dive: the 7-step design workflow (resources / methods / status codes / RFC 9457 error model / pagination envelope / versioning-auth-rate-limit / OpenAPI 3.1 contract), the hard rules, and the `fastapi`/`pydantic-v2` handoff |
| [`docs/skills/python-monorepo-architecture.md`](docs/skills/python-monorepo-architecture.md) | Deep dive: the 7-step cross-package workflow (split? / workspace wiring / depend-inward direction / import-isolation enforcement / boundary API / tests / safe extraction), the hard rules, and the `uv` + `python-project-structure` composition |
| [`docs/skills/openapi-ts-client.md`](docs/skills/openapi-ts-client.md) | Deep dive: the 6-step workflow (install / configure / generate / consume SDK / hooks + Zod / FastAPI + regen), the hard rules, the fetch/axios/next clients + v0.73.0 bundling, and the `tanstack-query` hand-off |
| [`docs/skills/biome.md`](docs/skills/biome.md) | Deep dive: the 6-step workflow (install+init / configure / run / CI gate / migrate / GritQL plugin), the hard rules, the v1→v2 deltas, and the `turborepo` hand-off |
| [`docs/skills/typescript-typecheck.md`](docs/skills/typescript-typecheck.md) | Deep dive: the 5-step workflow (why-separate / strict tsconfig / Vite split-config / project references / CI gate), the hard rules, the bundler-doesn't-typecheck rationale, the `tsgo` status, and the `vite`/`turborepo` hand-offs |
| [`docs/skills/polyglot-git-hooks.md`](docs/skills/polyglot-git-hooks.md) | Deep dive: the 6-step workflow (pick / install+activate / schema / polyglot example / hooks-vs-CI / `--no-verify`), the hard rules, the genuinely-polyglot (biome + ruff) example, and the tool-skill hand-offs |
| [`docs/skills/tsdoc.md`](docs/skills/tsdoc.md) | Deep dive: the 5-step workflow (decide / summary+`@remarks` / intent-not-type / right tag / enforcement), the hard rules, the TSDoc-vs-JSDoc rule, and the convention-only-vs-`eslint-plugin-tsdoc` choice |
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

v2.21.0 — adds three **engineering** skills completing the agent-flow dashboard (slice-3) TypeScript toolchain, each
the parity analog of a Python tool: **`typescript-typecheck`** — TypeScript type-checking as a standalone gate
(`tsc --noEmit` separate from the bundler since no transpiler type-checks, a genuinely strict `tsconfig` beyond
`strict: true`, the Vite split-config, composite project references, the CI gate, the `tsgo`/TS-7.0 status), the analog
of a `ty` gate; **`polyglot-git-hooks`** — Git hooks for a polyglot/monorepo with Lefthook (one `lefthook.yml`,
staged-file scoping, a genuinely polyglot `pre-commit` running `biome` + `ruff`, `pre-push` `tsc`/`ty`/tests,
hooks-vs-CI, the `--no-verify` bypass); and **`tsdoc`** — TSDoc doc-comments on a TypeScript public surface (the
block/inline/modifier tag taxonomy, the what-to-document discipline, the cardinal no-`{type}` rule, convention-only
enforcement with `eslint-plugin-tsdoc` as an optional pointer), the analog of a Google-style docstring standard. All
three forged via the skill-build playbook (spec → design-review → plan → design-review → forge → fresh-review →
dry-run verify) and additionally main-thread doc-grounded-verified against the live official docs (which caught and
fixed a Lefthook `jobs:`-versioning inaccuracy). Additive — existing skills unchanged.

v2.20.0 — adds two **engineering** skills for the agent-flow dashboard (slice-3) frontend work: **`openapi-ts-client`** —
generate a typed TypeScript client from an OpenAPI 3.1 contract (e.g. a FastAPI `/openapi.json`) with
`@hey-api/openapi-ts`: typed models, a typed SDK, TanStack Query hooks, and Zod schemas, regenerated from the spec
rather than hand-written (covers the `openapi-ts.config.ts` config, the fetch/axios/next clients + the v0.73.0 client
bundling, the regenerate + CI-drift workflow, and the FastAPI `operationId` fix; defers TanStack Query usage to
`tanstack-query`); and **`biome`** — lint + format a JS/TS project with Biome v2, the JS analog of `ruff` (the
`biome.json` config, the CLI incl. the read-only `biome ci` gate, ESLint/Prettier migration, the v1→v2 deltas, and
authoring custom rules as GritQL plugins; defers pipeline task-wiring to `turborepo`). Both forged via the skill-build
playbook (spec → design-review → plan → design-review → forge → fresh-review → dry-run verify) and dry-run verified.
Additive — existing skills unchanged.

v2.19.0 — adds **`python-monorepo-architecture`** (engineering), the cross-package layer for a multi-package Python
uv-workspace monorepo: when to split a codebase into a shared library plus app/CLI members (and when not — conflicting
deps / divergent `requires-python` aren't one workspace), the workspace wiring it owns (`[tool.uv.workspace]` +
`[tool.uv.sources] {workspace=true}`, single lockfile, `--package`), the acyclic depend-inward dependency direction
(apps→core, never app↔app, the lib depends on no app), the import-isolation discipline uv can't enforce (boundary by
convention + review, with `import-linter` as optional CI enforcement), the member-boundary public API, cross-member
test layout, and safety-net-first extraction. Owns the uv-workspace wiring the `uv` skill lacks and composes with `uv`
(basics) + `python-project-structure` (intra-package). Dry-run verified. Additive — existing skills unchanged.

v2.18.0 — adds the first two **engineering** skills (a new category alongside security, productivity, content-authoring,
meta, and integration), forged for the agent-flow API-building work: **`pydantic-v2`** — write correct, current Pydantic
v2 (the post-v1 API — `ConfigDict`, `model_dump*`, `model_validate*`, `@field_validator`/`@model_validator`,
`pydantic-settings`, `TypeAdapter`, discriminated unions — plus modernizing v1-era idioms like `class Config`,
`.dict()`, `@validator`; standalone-Pydantic, defers framework wiring to the FastAPI layer) and **`rest-api-design`** —
the design discipline above any web framework: resource/URL modeling, method + status-code choice, one error model
(RFC 9457 problem+json by default), a success/pagination envelope, a versioning/auth/rate-limit stance, all rendered as
an OpenAPI 3.1 contract (it produces the decisions and the contract, not the handler code). Both are dry-run verified
and reference each other and the framework layer rather than duplicating it. Additive — existing skills unchanged.

v2.16.0 — adds **`reviewing-document-set`**, a standalone corpus-level reviewer (the analog of `design-review` across a
whole document set). It judges a finished set of project documents for cross-document coherence on six dimensions —
consistency incl. one name per entity, completeness & traceability anchored on the upstream-most document,
contradictions, dependency integrity, no divergent duplication, and ready-to-plan — and emits a single
`VERDICT: approve|revise` with each finding prefixed by the affected document id(s) so a caller can act per document.
Grounded in IEEE 830, requirements traceability, single-source-of-truth, and Definition-of-Ready practice; dry-run
verified (catches seeded cross-document defects, approves a coherent corpus). Additive — existing skills unchanged.

v2.15.0 — completes the **Delivery cluster** (the fifth and final cluster) of the agent-flow document-skill library
(twenty-ninth–thirty-second skills), and with it the entire library: the two go-to-production document pairs.
**`authoring-release-runbook`** + **`reviewing-release-runbook`** (the broad operational go-live runbook —
prerequisites/sign-offs, pre-deploy checks, idempotent copy-paste-safe deploy steps each with an expected result,
post-deploy verification reusing the test-plan exit criteria, a complete + safe rollback with a documented revert for
every forward change, escalation/monitoring; the deploy strategy defaults to blue-green and is overridable per project;
secrets referenced by their store, never inlined) and **`authoring-test-plan`** + **`reviewing-test-plan`** (the QA /
verification strategy plus a risk-weighted test-case catalog — every behavior traced to a case, catalog depth scaled by
risk rather than the input-permutation cross-product, testable entry/exit criteria, non-functional levels from the
NFRs). Each reviewer emits exactly `VERDICT: approve|revise` + actionable findings with no-false-revise discipline and
single-sources its bar from its authoring sibling's dossier so produce and review never drift. Built via the batched
orchestrator (parallel forge, cap 3, + an independent fresh-reviewer dry-run per skill — all four PASS: the authoring
pair produced grounded, executable/traceable docs; the reviewers caught every seeded weak-doc defect, including the
load-bearing rollback-completeness and coverage-gap/combinatorial-blow-up checks, and approved the good docs). With
this the document-skill library is complete across all five clusters (Product, Design/UX, Engineering, User-facing,
Delivery). Additive — existing skills unchanged.

v2.14.0 — completes the **User-facing cluster** of the agent-flow document-skill library (twenty-sixth–twenty-eighth
skills), the second of two sub-batches: the three `reviewing-` siblings of the v2.13.0 authoring trio —
**`reviewing-user-guide`** (judge an end-user guide against a usability + accuracy bar: one how-to per handed-in goal,
the Diataxis modes correctly typed, a complete end-user feature/config reference, steps accurate to the product,
troubleshooting covering the error states), **`reviewing-developer-guide`** (judge a developer guide against an
adoptability + accuracy bar with named upstream-accuracy + api-reference-linking checks: a verifiable first success,
concepts before recipes, runnable code accurate to the tool, links — not duplicates — the api-reference), and
**`reviewing-api-reference`** (judge a published API reference against a usability + contract-consistency bar: every
api-spec operation documented with a worked example, every endpoint/shape/error traced to the handed-in api-spec with
no drift — the load-bearing check). Each emits exactly `VERDICT: approve|revise` + actionable findings with
no-false-revise discipline, and single-sources its bar from its authoring sibling's dossier so produce and review
never drift. Built via the batched orchestrator (parallel forge, cap 3, + an independent fresh-reviewer two-sample
dry-run per skill — all three PASS: catches the seeded weak-doc defects, approves the good doc). With this the
User-facing cluster (6 skills, 3 pairs) is complete. Additive — existing skills unchanged.

v2.13.0 — adds the **authoring half of the User-facing cluster** of the agent-flow document-skill library
(twenty-third–twenty-fifth skills), the first of two sub-batches: **`authoring-user-guide`** (the consumer-facing
end-user guide — full Diataxis incl. an end-user feature/config reference, one how-to per handed-in goal with the
four modes kept distinct, steps accurate to the product, troubleshooting from the real error states),
**`authoring-developer-guide`** (the developer-tool adoption + integration narrative for an SDK/library/CLI/API
platform — goals-not-endpoints, a fast first success, concepts before reference, code-centric integration recipes,
links — never copies — the api-reference), and **`authoring-api-reference`** (the published consumer-facing API
reference derived from the engineering api-spec — onboarding-first getting-started + auth, a worked example per
operation, every endpoint/field/error traced to the contract with no drift, prose-first yet generation-adaptive).
Each is a textual markdown artifact whose method + bar are medium-independent, carries the inline producer-upstream
contract, and composes with a new gateway template (`user-guide` / `developer-guide` / `api-reference`). The
`reviewing-` siblings ship next in v2.14.0 (each single-sourcing its bar from these authoring dossiers). Built via
the batched build orchestrator (parallel forge, cap 3, + an independent fresh-reviewer dry-run per skill — all
three PASS). Additive — existing skills unchanged.

v2.12.0 — completes the **document-dependency-contract** change (ship 2/2, after v2.11.0's discovery re-audit): a
**library-wide producer-upstream contract** pass over all 14 agent-flow document skills (each → **v1.1.0**). Every
`authoring-<type>` now carries an inline `## Inputs` block — **consume the full `depends_on` set the plan hands you**
(don't assume a fixed input), be **self-contained** (produce from whatever context you receive; an absent upstream
becomes an explicit assumption, never fabrication), and **use a research capability where available** for a
comprehensive, exhaustive document. Every `reviewing-<type>` gains the matching hard rule — **judge the document
against the upstreams it was given** (a not-produced upstream is never a revise trigger; a produced-but-ignored one
is a fair finding). Verified end-to-end by a fresh-reviewer multi-`depends_on` dry-run (a richer handed-in set
produces a more comprehensive doc; a leaner set degrades gracefully into surfaced assumptions; the reviewer
neither false-revises nor lets an ignored upstream slip). Also drops the last stray glyphs from the skills'
when-to-activate lists. Additive — each skill's method + quality bar are unchanged.

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
