# agent-skills

Security, token-efficiency, content-authoring, meta (skill-building), integration, and
engineering skills for AI coding agents.
Works across **Claude Code, Cursor, GitHub Copilot, Codex,** and **Gemini CLI**.

Skills are grouped by category below — each section lists its skills (every name links
to a deep-dive doc) and carries its own install block, so you can adopt one category at
a time. For Cursor, GitHub Copilot, Codex, or Gemini CLI see the
[installation guide](docs/installation.md).

## Security & content safety

| Skill | One-line purpose |
|---|---|
| [`external-content-sanitizer`](docs/skills/external-content-sanitizer.md) | Defensive runtime sanitizer for external untrusted content (WebFetch / WebSearch / cloned repos) |

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
```

## Meta & productivity

| Skill | One-line purpose |
|---|---|
| [`skill-forge`](docs/skills/skill-forge.md) | Self-learning meta-skill: research a knowledge gap → synthesize a portable SKILL.md (create or improve) with fact-check + self-review; broad topics fan out into multiple skills |
| [`token-optimization`](docs/skills/token-optimization.md) | Diagnostic + tactic catalog for reducing token usage across 5 layers (system prompt, tool defs, history, tool results, output) |
| [`content-template-gateway`](docs/skills/content-template-gateway.md) | Gate for any agent-authored structured content (file or external destination) — identifies content-type + variant from intent, enforces template use via hard-refusal directive, forges templates when missing |

```bash
npx skills add bm629/agent-skills@skill-forge
npx skills add bm629/agent-skills@token-optimization
npx skills add bm629/agent-skills@content-template-gateway
```

## Design & planning gates

| Skill | One-line purpose |
|---|---|
| [`design-review`](docs/skills/design-review.md) | Adversarial pre-approval review of a design doc — spec / plan / RFC / ADR — hunts recurring gap categories (+ a plan lens for plans), verifies claims against the codebase (`file:line`, no fabrication), returns severities + a ready / has-blockers verdict; review-only (never edits or approves) |
| [`project-document-discovery`](docs/skills/project-document-discovery.md) | Classify a project across 10 dimensions, identify its distinct capability areas (4-signal algorithm), and produce a capability-scoped document manifest — three-key JSON `{capability_map, product_capabilities, manifest}`; per-capability fan-out; all five meta-sections populated; archetype-level author/reviewer role pairs + both authoring and reviewing skill per document; amend via T1-T5 delta protocol; every skill carries a per-project purpose + requirements, and skill/role entries carry null resolution fields (`resolved_id`/`match_status`) the approval gate writes; discovery only (not authoring). v6.0.0. |
| [`reviewing-document-discovery`](docs/skills/reviewing-document-discovery.md) | Judge a produced document plan/manifest against a fourteen-condition soundness bar single-sourced 1:1 with `project-document-discovery`'s Self-check — an acceptance gate; emits `VERDICT: approve\|revise`; no false-revise on a lean plan; condition 13 also expects per-skill purpose + requirements and null resolution fields. v1.5.0. |
| [`reviewing-document-set`](docs/skills/reviewing-document-set.md) | Judge a finished SET of documents as one corpus against an eight-dimension cross-document coherence bar — the corpus-level analog of a design review, run after each document's own gate; emits one `VERDICT: approve\|revise` + per-document-attributed findings, no false-revise |
| [`code-prior-art-survey`](docs/skills/code-prior-art-survey.md) | Run the search wave of a systematic open-source code prior-art survey — two procedures over schema-validated contracts: derive a typed keyword map (6 group types, provenance + relation-kind expansions, vocabulary probe, negative terms, registry-drawn active sources, delta lineage), and execute one of 9 search angles (host metadata / curated catalogs / registries+dependents / code-content / competitor directories / community / academic / model hubs / platform registries) into reproducible coverage cells + dedup-honest candidate records; a deterministic validator gates both artifacts (coverage completeness computed from the map × a machine-readable source registry). Popularity ranks, never excludes. Adds the EXTRACT wave: deep-read one candidate repo into a 10-section analysis + a durable frontmatter block (verdict enum, holistic 0-10 score, SPDX license, purl deps), with a cheap relevance skim that bails on off-scope repos before the expensive read. v1.3.0. |
| [`reviewing-code-prior-art-survey`](docs/skills/reviewing-code-prior-art-survey.md) | Judge a produced prior-art search artifact — keyword map or per-angle search output — against the eighteen-condition bar single-sourced with `code-prior-art-survey` (an acceptance gate, not authoring): conditions 7+11 discharged by one run of the co-installed producer's validator, judgment conditions walked with explicit gap-vs-not calibration, a delta lens for inheriting maps, plus extraction due-diligence conditions 13-18 (deep-read fidelity, depth, bail integrity, verdict groundedness, score defensibility, safety); emits exactly one verdict — a terminal `VERDICT: approve\|revise` line by default, or the caller's named equivalent — with condition-named findings; review-only, no false-revise — a thin-but-honest result in a thin domain meets the bar. v1.3.0. |

```bash
npx skills add bm629/agent-skills@design-review
npx skills add bm629/agent-skills@project-document-discovery
npx skills add bm629/agent-skills@reviewing-document-discovery
npx skills add bm629/agent-skills@reviewing-document-set
npx skills add bm629/agent-skills@code-prior-art-survey
npx skills add bm629/agent-skills@reviewing-code-prior-art-survey
```

## Document library — authoring + reviewing pairs

Fifteen SDLC document types, each with an authoring skill (the production method +
quality bar) and a reviewing twin (the acceptance gate emitting
`VERDICT: approve|revise`). Names link to each skill's deep-dive doc.

| Document type | Authoring | Reviewing |
|---|---|---|
| PRD | [`authoring-prd`](docs/skills/authoring-prd.md) | [`reviewing-prd`](docs/skills/reviewing-prd.md) |
| Feature spec | [`authoring-feature-spec`](docs/skills/authoring-feature-spec.md) | [`reviewing-feature-spec`](docs/skills/reviewing-feature-spec.md) |
| User flows | [`authoring-user-flows`](docs/skills/authoring-user-flows.md) | [`reviewing-user-flows`](docs/skills/reviewing-user-flows.md) |
| Wireframes | [`authoring-wireframes`](docs/skills/authoring-wireframes.md) | [`reviewing-wireframes`](docs/skills/reviewing-wireframes.md) |
| Design system | [`authoring-design-system`](docs/skills/authoring-design-system.md) | [`reviewing-design-system`](docs/skills/reviewing-design-system.md) |
| Hi-fi UI design | [`authoring-hi-fi`](docs/skills/authoring-hi-fi.md) | [`reviewing-hi-fi`](docs/skills/reviewing-hi-fi.md) |
| Technical design (TDD) | [`authoring-technical-design`](docs/skills/authoring-technical-design.md) | [`reviewing-technical-design`](docs/skills/reviewing-technical-design.md) |
| Architecture doc (+ ADRs) | [`authoring-architecture-doc`](docs/skills/authoring-architecture-doc.md) | [`reviewing-architecture-doc`](docs/skills/reviewing-architecture-doc.md) |
| API spec (wire contract) | [`authoring-api-spec`](docs/skills/authoring-api-spec.md) | [`reviewing-api-spec`](docs/skills/reviewing-api-spec.md) |
| Data model | [`authoring-data-model`](docs/skills/authoring-data-model.md) | [`reviewing-data-model`](docs/skills/reviewing-data-model.md) |
| User guide | [`authoring-user-guide`](docs/skills/authoring-user-guide.md) | [`reviewing-user-guide`](docs/skills/reviewing-user-guide.md) |
| Developer guide | [`authoring-developer-guide`](docs/skills/authoring-developer-guide.md) | [`reviewing-developer-guide`](docs/skills/reviewing-developer-guide.md) |
| API reference | [`authoring-api-reference`](docs/skills/authoring-api-reference.md) | [`reviewing-api-reference`](docs/skills/reviewing-api-reference.md) |
| Release runbook | [`authoring-release-runbook`](docs/skills/authoring-release-runbook.md) | [`reviewing-release-runbook`](docs/skills/reviewing-release-runbook.md) |
| Test plan | [`authoring-test-plan`](docs/skills/authoring-test-plan.md) | [`reviewing-test-plan`](docs/skills/reviewing-test-plan.md) |

```bash
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
npx skills add bm629/agent-skills@authoring-hi-fi
npx skills add bm629/agent-skills@reviewing-hi-fi
npx skills add bm629/agent-skills@authoring-technical-design
npx skills add bm629/agent-skills@reviewing-technical-design
npx skills add bm629/agent-skills@authoring-architecture-doc
npx skills add bm629/agent-skills@reviewing-architecture-doc
npx skills add bm629/agent-skills@authoring-api-spec
npx skills add bm629/agent-skills@reviewing-api-spec
npx skills add bm629/agent-skills@authoring-data-model
npx skills add bm629/agent-skills@reviewing-data-model
npx skills add bm629/agent-skills@authoring-user-guide
npx skills add bm629/agent-skills@reviewing-user-guide
npx skills add bm629/agent-skills@authoring-developer-guide
npx skills add bm629/agent-skills@reviewing-developer-guide
npx skills add bm629/agent-skills@authoring-api-reference
npx skills add bm629/agent-skills@reviewing-api-reference
npx skills add bm629/agent-skills@authoring-release-runbook
npx skills add bm629/agent-skills@reviewing-release-runbook
npx skills add bm629/agent-skills@authoring-test-plan
npx skills add bm629/agent-skills@reviewing-test-plan
```

## Provider ops (integrations)

| Skill | One-line purpose |
|---|---|
| [`atlassian-rest-ops`](docs/skills/atlassian-rest-ops.md) | Call the Atlassian Cloud REST API directly (Confluence v2 + Jira v3) via curl — bundled OpenAPI + `$ref`-resolver, per-API patterns, ADF/storage rich-text; no SDK |
| [`github-cli-ops`](docs/skills/github-cli-ops.md) | Perform any github.com operation CLI-first via `gh`, falling back to `gh api` (REST) / `gh api graphql` where no command exists — per-call `GH_TOKEN` auth (no `gh auth switch`) from caller-injected credentials, bundled OpenAPI + `$ref`-resolver for all 1,186 ops, `gh secret set` for secret encryption |
| [`jenkins-rest-ops`](docs/skills/jenkins-rest-ops.md) | Drive a Jenkins server's Remote Access REST API via curl — trigger/poll/status/console + job CRUD + build management; HTTP-Basic `user:API_TOKEN`, the async queue-item→build poll + token-exempt CSRF crumb handled; no official OpenAPI (unofficial swaggy-jenkins cross-check); caller-injected credentials |
| [`netlify-ops`](docs/skills/netlify-ops.md) | Drive Netlify web-hosting CLI-first via the `netlify` CLI (reads `NETLIFY_AUTH_TOKEN`, never `netlify login`) with a REST fallback on the official OpenAPI — sites/deploys/domains/DNS; the digest-deploy protocol + rate limits handled; caller-injected credentials |
| [`cloudflare-pages-ops`](docs/skills/cloudflare-pages-ops.md) | Drive Cloudflare Pages CLI-first via Wrangler (reads `CLOUDFLARE_API_TOKEN`+`CLOUDFLARE_ACCOUNT_ID`, never `wrangler login`) with a REST fallback on the official OpenAPI (Pages slice) — projects/deploys/domains; the multipart-deploy + Direct-Upload-vs-Git + `{success,…}` envelope handled; caller-injected credentials |

```bash
npx skills add bm629/agent-skills@atlassian-rest-ops
npx skills add bm629/agent-skills@github-cli-ops
npx skills add bm629/agent-skills@jenkins-rest-ops
npx skills add bm629/agent-skills@netlify-ops
npx skills add bm629/agent-skills@cloudflare-pages-ops
```

## Engineering — Python & data

| Skill | One-line purpose |
|---|---|
| [`pydantic-v2`](docs/skills/pydantic-v2.md) | Write correct, current Pydantic v2 — `BaseModel` + `Field` constraints, validators, `model_dump*`, `ConfigDict`, `pydantic-settings`, `TypeAdapter`, discriminated unions — and modernize v1-era idioms; standalone-Pydantic, defers framework wiring to `fastapi` |
| [`rest-api-design`](docs/skills/rest-api-design.md) | Design a REST/HTTP API surface and its contract — resources/URLs, methods + status codes, one error model (RFC 9457), success/pagination envelope, versioning/auth/rate-limit, rendered as an OpenAPI 3.1 contract; the design discipline above the framework |
| [`python-monorepo-architecture`](docs/skills/python-monorepo-architecture.md) | Architect a multi-package Python uv-workspace monorepo — when to split, the workspace wiring, the acyclic depend-inward dependency direction, import-isolation discipline, member-boundary public API, safe extraction |
| [`sqlalchemy`](docs/skills/sqlalchemy.md) | Build a portable SQLAlchemy 2.x relational data layer that runs unchanged on SQLite + PostgreSQL + MySQL — the typed ORM, one-engine-per-process + short-lived sessions, a sync/async driver matrix, the cross-dialect gotcha set; defers migrations to `alembic` |
| [`alembic`](docs/skills/alembic.md) | Run Alembic migrations on a SQLAlchemy 2.x layer across SQLite + PostgreSQL + MySQL from one history — env wiring, the revision → autogenerate → review → upgrade workflow, the SQLite batch gotcha, the `create_all()`-vs-Alembic decision |
| [`sql-job-queue`](docs/skills/sql-job-queue.md) | Build a DB-backed ready-set job scheduler on SQLAlchemy 2.x — dependency-driven readiness, the three per-dialect lease branches (`FOR UPDATE SKIP LOCKED` vs `BEGIN IMMEDIATE`), crash-resume, fair-share, the tick loop, at-least-once idempotency |

```bash
npx skills add bm629/agent-skills@pydantic-v2
npx skills add bm629/agent-skills@rest-api-design
npx skills add bm629/agent-skills@python-monorepo-architecture
npx skills add bm629/agent-skills@sqlalchemy
npx skills add bm629/agent-skills@alembic
npx skills add bm629/agent-skills@sql-job-queue
```

## Engineering — TypeScript, frontend & UI

| Skill | One-line purpose |
|---|---|
| [`openapi-ts-client`](docs/skills/openapi-ts-client.md) | Generate a typed TypeScript client from an OpenAPI 3.1 contract with `@hey-api/openapi-ts` — typed models, SDK, TanStack Query hooks, Zod schemas, regenerated from the spec not hand-written; the regen + CI-drift workflow |
| [`biome`](docs/skills/biome.md) | Lint + format a JS/TS project with Biome v2 — one fast Rust tool (the JS analog of `ruff`): config, CLI, ESLint/Prettier migration, v1→v2 deltas, GritQL plugins |
| [`typescript-typecheck`](docs/skills/typescript-typecheck.md) | Run TypeScript type-checking as a standalone gate — `tsc --noEmit` separate from the bundler, a genuinely strict `tsconfig`, the Vite split-config, composite project references, the CI gate |
| [`tsdoc`](docs/skills/tsdoc.md) | Write TSDoc doc-comments on a TypeScript public surface — what to document vs skip, the tag taxonomy, summary-then-`@remarks`, no `{type}` in comments |
| [`polyglot-git-hooks`](docs/skills/polyglot-git-hooks.md) | Set up Git hooks for a polyglot/monorepo with Lefthook — one `lefthook.yml` running format/lint at pre-commit and type-check/test at pre-push across mixed-language subtrees (TS + Python) in parallel |
| [`react-component-testing`](docs/skills/react-component-testing.md) | The RTL + MSW + vitest-axe component-test layer for a Vite + React + TS SPA — render a real tree, drive it like a user, mock the network boundary with MSW (not the module), assert runtime a11y |
| [`tanstack-router`](docs/skills/tanstack-router.md) | Set up + use TanStack Router in a Vite + React + TS SPA — the type-safe route tree, file-based + code-based routing, validated search params, loaders + the TanStack Query handshake, code-splitting, a memory-history test harness |
| [`motion-react`](docs/skills/motion-react.md) | Implement animation in a React SPA with Motion (the framer-motion successor: `motion` pkg, `motion/react`) — enter/exit, variants + stagger, AnimatePresence, layout/shared-element transitions, number tickers, drag/Reorder — with reduced-motion a11y first-class, transform/opacity performance discipline, product-UI restraint, and a choosing-the-tool framework (CSS/Radix `data-state` and AutoAnimate before Motion) |
| [`ui-illustrations`](docs/skills/ui-illustrations.md) | Add illustration/imagery to a web app UI — empty states, onboarding, error pages — sourcing from unDraw/Storyset/LottieFiles with license compliance, recoloring SVGs to design tokens (light+dark), correct SVG-in-React/Vite integration (CLS + bundle discipline), animated imagery with reduced-motion a11y, and empty-state craft |

```bash
npx skills add bm629/agent-skills@openapi-ts-client
npx skills add bm629/agent-skills@biome
npx skills add bm629/agent-skills@typescript-typecheck
npx skills add bm629/agent-skills@tsdoc
npx skills add bm629/agent-skills@polyglot-git-hooks
npx skills add bm629/agent-skills@react-component-testing
npx skills add bm629/agent-skills@tanstack-router
npx skills add bm629/agent-skills@motion-react
npx skills add bm629/agent-skills@ui-illustrations
```

## Documentation

| Doc | Covers |
|---|---|
| [`docs/installation.md`](docs/installation.md) | Per-agent install instructions for all 4 target agents + Gemini bonus; troubleshooting |
| [`docs/architecture.md`](docs/architecture.md) | Repo layout, metadata files, why the SKILL.md frontmatter has per-agent `extensions:` blocks |
| [`docs/compatibility.md`](docs/compatibility.md) | Agent compatibility matrix; v1 status vs v2 plugin-packaging roadmap |
| [`docs/contributing.md`](docs/contributing.md) | How to file issues, propose new skills, modify existing ones |

Every skill has a deep-dive doc under [`docs/skills/`](docs/skills/) — linked from its
name in the category tables above.

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

v2.40.0 — **caller-specified verdict form** — `reviewing-code-prior-art-survey` → **v1.3.0**. The hard rule "exactly one terminal `VERDICT: approve|revise` line — nothing after it" is relaxed from a fixed FORM to a fixed CARDINALITY: exactly one verdict, never two, in a terminal line by default or in the caller's named equivalent (a structured comment row, a JSON key) where its brief replaces that line. Emitting both forms is now the named violation. Motivated by a real caller whose comment layout carries the decision in a `Verdict:` table row and explicitly replaces the terminal line — under the old wording that caller and the skill's hard rule could not both be obeyed. Synced across SKILL.md (description, Step 3, Rules, Output) and the deep-dive doc. Same pass fixes pre-existing doc drift in the deep-dive: its Purpose paragraph still said "two artifacts" and "twelve-condition bar" while the body and its own next heading say three and eighteen.

v2.39.0 — **prior-art pair: typed degradation** — `code-prior-art-survey` → **v1.3.0** and `reviewing-code-prior-art-survey` → **v1.2.0**. A survey that cannot reach a source, or cannot fetch a repository, must now say so in a TYPED field with a cause — never as a silent zero-hit cell, and never as prose in the notes. Producer: a search coverage cell gains `status: searched|partial|unreachable` plus `cause` (`search-output.schema.json`), and an extraction skip gains a third reason `unavailable` plus `cause` (`extract-output.schema.json`) for a repo that exists but could not be retrieved — distinct from `vanished`, which means gone. Reviewer: conditions 7, 10 and 15 assert the new contract — an unreachable source is a gap only when it is UNTYPED or its attempts are unrecorded, a genuinely down source recorded with its attempts is the contract working rather than a defect, and the registry's `fallbacks` must be tried before `unreachable` is claimed, so it cannot become the cheap exit from a merely slow source. Condition 15 retitled to "a skip carries a reason, and the evidence that reason demands". Ships with new fixtures (`search-output.degraded.yaml`, `extract-output.skip-unavailable.md`), ~145 lines of added validator tests, and regenerated validation proofs. *(Backfilled 2026-07-20: this release shipped in `c24244e` with its version bumps but without its Status entry; reconstructed from the phase B–G commits.)*

v2.38.0 — **prior-art pair: the EXTRACT wave** — `code-prior-art-survey` → **v1.2.0** (additive): a third procedure deep-reads ONE candidate repository into `extract/<repo_id>.md` — a YAML frontmatter machine block (`schema_version`, canonical `repo_id`, `code_repository`, a four-value borrow `verdict`, a holistic integer 0-10 production-quality `score`, an **SPDX** `license`, **purl** `key_deps`, capability tags, pattern names, `extracted_at`) above a fixed 10-section analysis body. A cheap relevance skim runs FIRST (README, or tree + manifest + entry + docs when it is absent/empty/thin) and bails on a confident "touches none of the scope" into a frontmatter-only skip record (`reason: irrelevant|vanished`, a non-trivial `bail_rationale`) — uncertainty KEEPS the repo, so the expensive read is spent only where it pays. Ships a third authoritative JSON Schema (a full/skip discriminated union), an `extract` validator subcommand (frontmatter parse + schema + the 10 headings + bail-rationale non-triviality; shape-only by design — relevance correctness is the reviewer's judgment, so the validator stays portable and cannot false-fail a genuine bail), three new references (extraction template, the ten-signal holistic quality rubric, the output guide incl. an additive-only durability policy), and three fixtures. Format grounded in deep research (Structured MADR's frontmatter+body+JSON-Schema pattern; OpenSSF Scorecard's 0-10; SPDX + purl as the durable identifier vocabularies). `reviewing-code-prior-art-survey` → **v1.1.0**: extraction conditions 13-18 (deep-read fidelity, depth-not-skim, bail integrity, verdict groundedness, score defensibility, safety honesty) with IS/NOT-a-gap calibration; conditions 11 and 12 generalized across artifact kinds (1-12 keep their numbers). Verified by a live gate: a real GPL-3.0 `freqtrade` deep-read validates and is APPROVED, while a planted verdict-gap copy and an uncertainty-worded bail both pass the validator yet are correctly REVISED under conditions 16 and 15 — the shape-vs-judgment split working as designed. 41 validator tests green.

v2.37.0 — **prior-art pair currency + audit improvements** — `code-prior-art-survey` → **v1.1.0** (additive): the source registry grows to 69 — `software-heritage` (a1: origin search over the 421M-project preservation archive; the only source that surfaces DEAD/vanished prior art, with dead-origin extraction guidance via the owner-less id + `archived: true` conventions) and `pwc-plus` (a7: the community PapersWithCodePlus rebuild as a third paper→code resolver, chained into catalyzex's fallbacks); the a4 brief notes grep.app's official MCP interface for agent callers; and the Output bar's item 10 aligns to the pair's shared wording ("; nothing silently narrowed"). `reviewing-code-prior-art-survey` → **v1.0.1** (patch): the now-resolved bar-alignment nit note removed from `references/conditions.md`. Driven by a multi-angle post-ship production audit (registry currency web-verified: sourcegraph/grep.app/catalyzex/opencodepapers/libraries.io/deps.dev all alive; fallback chains validated); all changes fact-checked by a fresh reviewer against live sources (0 Critical / 0 Important) with the validator suite green (27 tests) and both fixtures exit 0.

v2.36.0 — **`reviewing-code-prior-art-survey` v1.0.0** — completes the prior-art pair: the acceptance gate over `code-prior-art-survey`'s two artifacts (keyword map + per-angle search output). Judges the twelve-condition bar single-sourced with the producer — the deterministic pair (7 coverage-proven + 11 schema-valid) discharged by ONE run of the co-installed producer's validator (which recomputes coverage from the map × its own source registry; never re-implemented), the judgment conditions (typed coverage, expansion quality, disambiguation, scope honesty, source contract, self-description, candidate integrity, boundary honesty, failure transparency) walked from a `references/conditions.md` where every condition carries an explicit IS-a-gap / NOT-a-gap calibration, and proportionality (12) gating every finding — no false-revise: zero-hit-heavy coverage and thin-but-honest results in thin domains meet the bar. Includes a delta lens judging inheriting keyword maps as scoped deltas (findings against untouched inherited groups are themselves defects). Emits exactly one terminal `VERDICT: approve\|revise` with condition-named findings; review-only; ships no schemas/scripts by design (the contracts and validator belong to the producer). Forged spec-guided via the full skill-forge pipeline (2 cold fresh-reviewer cycles, 0 Critical) and verified by a dual-sample gate: clean fixtures → approve (no false-revise), a planted condition-3 gap → revise naming the condition, a delta map → approve without re-litigating inherited groups.

v2.35.0 — **`code-prior-art-survey` v1.0.0** — a new **design & planning-gate** skill: the search wave of a systematic open-source code prior-art survey, as two procedures over one set of schema-validated contracts. Procedure 1 derives a typed keyword map (six group types, 3–8 provenance-stamped expansions with SKOS-style relation kinds, a vocabulary probe with graceful degradation, negative terms, a visible scope guard, justified filters where popularity floors rank but never exclude, a registry-drawn active-source contract, seeds, and delta lineage). Procedure 2 executes one of nine mechanism-based search angles (a1 host metadata / a2 curated catalogs / a3 registries + dependents graph / a4 code-content search / a5 competitor directories / a6 community mining / a7 academic code / a8 model hubs / a9 platform registries — the last three trigger-gated) into PRISMA-style coverage cells (exact queries + timestamp + count, zero-hits mandatory) and dedup-honest candidate records (canonical `host__owner__name` ids, fork/mirror/archived flags, `as_of`-stamped signals). Ships two authoritative JSON Schemas, a machine-readable 67-source registry that doubles as the validator's per-angle applicability input, nine comprehensive per-source angle briefs, and a deterministic validator (`scripts/validate_prior_art.py`, 27-test suite) that computes coverage completeness from the map × the registry. Forged via the full skill-forge pipeline with five cold fresh-reviewer cycles (0 Critical throughout) and a live dry-run gate on a real domain. v1 covers the search wave only; screening/extraction/synthesis and the `reviewing-code-prior-art-survey` twin land later.

v2.34.0 — **doc-drift sync + hi-fi bar reconciliation** — an audit of all deep-dive docs against their shipped SKILL.md found 11 stale docs, now synced (no skill behavior changed): `project-document-discovery` (v3.0.0→6.0.0 header; `prior_art_triggers` is model-authored not injected; clusters drop `team`, add `integrations`+`business`; the user-flows/release-runbook/eval-plan/technical-design/model-card selection rules; T1–T5 amend + greenfield Steps 1–9), `reviewing-document-discovery` (→1.5.0), `atlassian-rest-ops` (→1.1.0), `token-optimization` (5→9 workflow steps + the cross-agent table), `external-content-sanitizer` (the two real normal/aborted output shapes + severity-tagged marker), `netlify-ops` (drop the misattributed `{success}` envelope), and the shared-bar condition counts in `authoring-prd` (→12), `authoring-architecture-doc` (→10), `authoring-api-spec` (→11), `authoring-data-model` (→9). The audit also surfaced a genuine skill-vs-skill inconsistency: `authoring-hi-fi`'s self-check enumerated 13 conditions while its single-sourced twin `reviewing-hi-fi` enumerated 14 — the missing item being the **capability-boundary** condition (already an `authoring-hi-fi` hard rule, just absent from the numbered self-check). Reconciled by adding it as `authoring-hi-fi` condition 14 (**→ v1.2.0**), so both halves of the pair now assert the same 14-condition bar.

v2.33.0 — **UI animation + illustration skills, sectioned README** — adds two **frontend/UI engineering** skills forged for modern product-UI revamps: **`motion-react`** — implement animation in a React SPA with Motion (the framer-motion successor: `motion` package, `motion/react` import): core enter/exit, variants + `delayChildren: stagger()` orchestration (12.22.0 floor; `staggerChildren` deprecated in 12.21.0), AnimatePresence (modes, stable keys, direction-aware exits via `custom`/`usePresenceData`, in-place content swaps), layout + `layoutId` shared elements + `Reorder` drag-to-reorder (pointer-only a11y caveat), motion values + imperative `animate()` (number tickers, drag thresholds, sanctioned `useScroll` one-liners), a **four-layer reduced-motion contract** (MotionConfig root posture; `useReducedMotion` overrides; imperative animation is NOT governed by MotionConfig and needs an explicit gate; CSS-side media query) mapped to WCAG 2.3.3/2.2.2, transform/opacity performance discipline (with the height-reveal carve-out + `originX` on scale fills), product-UI restraint rules, a choosing-the-tool framework (CSS/Radix `data-state` and AutoAnimate before Motion; View Transitions named), Radix `forceMount` + frozen-outlet router integration (Next.js App Router scoped out), and deterministic tests (`MotionGlobalConfig.skipAnimations`, matchMedia stub, Playwright `reducedMotion`); and **`ui-illustrations`** — add illustration/imagery to a web app UI: the placement doctrine (empty states/onboarding/errors/success yes; data surfaces no; auth split-panel the exception), sourcing from unDraw/Storyset/LottieFiles with the license traps mapped (dated snapshots + a check-at-adoption practice; Storyset's attribution-removal tier is inconsistently named at the source), one-style-family discipline, token-driven SVG recolor for light+dark, inline-vs-`<img>` integration with CLS + bundle rules, animated imagery via `lottie-react` with an SSR-safe reduced-motion hook + explicit pause/play (runtime `autoplay` changes don't stop a running animation), WCAG 2.2.2 stated precisely (>5 s TOTAL, looping or not), and empty-state craft (anatomy, four variants, never mislabel an error as emptiness). Both forged 2026-07-11 via the full skill-forge pipeline with multi-cycle cold fresh-reviewer verification against live sources. This release also **restructures the README** into per-category sections (each with its own install block), fixes two glued table rows (`github-cli-ops`/`jenkins-rest-ops` in both tables), slims the Documentation table to the general docs (deep-dives are linked from the category tables), and aligns `package.json`'s drifted `version` with this ledger.

v2.32.0 — **skill intent + resolution fields** — `project-document-discovery` → **v6.0.0** and `reviewing-document-discovery` → **v1.5.0**. The headline change (6.0.0, BREAKING): every `manifest.skills` entry now carries a REQUIRED per-project `purpose` + a non-empty `requirements` list (discrete capabilities), populated for every skill — feeding a downstream dashboard approval gate's display + strict match; and every skill AND role entry gains backend-written `resolved_id` + `match_status` (`complete`|`partial`|`none`|null), emitted `null` at discovery and written by the gate when it matches each entry to an installed skill/role. `scripts/validate.py` gains a resolution-consistency check (`match_status` complete/partial ⇒ `resolved_id` set; none/null ⇒ null); emitted `manifest.version` → 3. `reviewing-document-discovery` condition 13 tracks it (v1.5.0 — expects the populated intent + carves out the discovery-time null resolution fields as not-a-gap). Live-smoked: a greenfield discovery emitted `version: 3` with 30 skills all carrying per-project purpose + requirements + null resolution and passed the validator.

v2.31.0 — **manifest review roles + docs catch-up** — `project-document-discovery` → **v5.0.0** and `reviewing-document-discovery` → **v1.4.0**. The headline change (5.0.0, BREAKING): the generated manifest gains its missing review dimension — `manifest.roles` now derives the archetype-level author/reviewer PAIR (`document-author` + `document-reviewer` for engineer/strategist; `designer` + `design-reviewer` for designer), role entries become **pure personas** (`skills`/`tools` dropped — resolved from the document entry + top-level sections at dispatch), each document entry's singular `role` becomes `roles: [author, reviewer]` (exactly two, fixed order) and carries BOTH its authoring and reviewing skill, and the emitted `manifest.version` → 2; `scripts/validate.py` gains a roles referential-integrity check + an archetype→pair consistency check; `reviewing-document-discovery` conditions 3/13 track it (v1.4.0). This release also **catches up the companion docs** that drifted: the README rows + deep-dives were stale at v3.0.0/v1.2.0 while the SKILL.md files had already shipped through **v3.3.0** (`project-document-discovery` document-fan-out proportionality — per-capability technical-design/model-card/user-flows gating, rule-selected user-flows/release-runbook/eval-plan, phantom `nfrs-security` edge removed) and **v4.0.0** (capability-map v2 — 10 grounded classification clusters with research-grounded enums, model-authored + validator-guaranteed `prior_art_triggers`; `reviewing-document-discovery` → v1.3.0 Condition 10 realigned) without their own Status entries.

v2.30.0 — **manifest v3.0.0** — `project-document-discovery` v2.0.0 → **v3.0.0** (BREAKING: Phase B gains Step 8 to populate all five manifest meta-sections — `capabilities:`, `roles:`, `skills:`, `tools:`, `amendments: []` — from the document set using new `references/manifest-schema.md`; document entries: `capabilities: [...]` array → `capability: "..."` scalar; manifest: `providers:` renamed to `capabilities:` and populated; output contract explicit: skill returns one three-key JSON, caller writes two files; self-check extended from eleven to fourteen items — items 12 manifest structure, 13 meta-sections populated, 14 capability scalar); `reviewing-document-discovery` v1.1.0 → **v1.2.0** (additive: two new meta-section conditions 13/14 — fourteen-condition bar).

v2.29.0 — **capability_record context injection** across all 8 authoring + 8 reviewing doc-library skills. Each authoring skill optionally consumes a caller-injected `capability_record` (single record for per-capability docs: feature-spec/data-model/api-spec/wireframes/hi-fi; full capability list for system-scope docs: prd/architecture-doc/user-flows/system-wireframes) to scope its output to the capability boundary — graceful fallback when no record is injected. Each reviewing twin gains a matching capability-boundary checklist condition (n/a when no record was injected). Body budget softened to a soft target (~500 lines / flag if consistently over 700) across all 16 skills. Version bumps: `authoring-feature-spec` / `authoring-wireframes` / `authoring-prd` / `authoring-user-flows` → **v1.3.0**; `authoring-data-model` / `authoring-api-spec` / `authoring-architecture-doc` → **v1.3.0**; `authoring-hi-fi` → **v1.1.0**; `reviewing-feature-spec` / `reviewing-wireframes` / `reviewing-prd` / `reviewing-user-flows` → **v1.3.0**; `reviewing-data-model` / `reviewing-api-spec` / `reviewing-architecture-doc` / `reviewing-hi-fi` → **v1.1.0**. Condition bars: reviewing-feature-spec 10→11, reviewing-data-model 9→10, reviewing-api-spec 11→12, reviewing-prd 12→13, reviewing-architecture-doc 10→11, reviewing-hi-fi 13→14, reviewing-user-flows/wireframes +1 routing/coverage condition each.

v2.29.0 — **`atlassian-rest-ops` v1.0.0 → v1.1.0** (additive): bundles `scripts/md_to_adf.py`, a stdlib Markdown → ADF converter (headings, bold, inline code, links, bullet/ordered lists, fenced code blocks, GFM tables) with a `.validation.md` proof. Pipe a Markdown comment/description through it (`python3 scripts/md_to_adf.py < body.md`) to post it as native ADF in Jira instead of raw Markdown (which renders `##`/`**`/`|` literally). No change to the existing `curl`/resolver flow.

v2.28.0 — **capability-map update** — `project-document-discovery` v1.3.0 → **v2.0.0** (BREAKING restructure: two-phase workflow Phase A classify+identify via 4-signal algorithm + Phase B fan-out manifest; output contract now three-key JSON `{capability_map, product_capabilities, manifest}` where `manifest` is nested; per-capability fan-out rules with `design` capability for wireframes/hi-fi; T1-T5 amend delta protocol with two-prompt pipeline; eleven-item self-check); `reviewing-document-discovery` v1.0.0 → **v1.1.0** (additive: three new output-contract conditions 10/11/12 — twelve-condition bar). Adds `references/reference-architectures.md` (4-signal algorithm, 10-domain table, sizing tests, seam contract guide) and `schemas/capability-map.schema.json` (JSON Schema 2020-12) inside `project-document-discovery`.

v2.27.0 — **documentation sync** (no skill behavior changed). Adds the previously-undocumented per-skill doc pages + README rows + install lines for seven skills: the **`reviewing-technical-design`** (11-condition), **`reviewing-architecture-doc`** (10-condition), **`reviewing-data-model`** (9-condition), and **`reviewing-api-spec`** (11-condition, style-agnostic) reviewer twins; the **`authoring-hi-fi`** + **`reviewing-hi-fi`** hi-fi-as-code pair (the render→vision-review loop, 13-point bar); and **`reviewing-document-discovery`** (9-condition, single-sourced with `project-document-discovery`'s Self-check). Also re-syncs every `docs/skills/*.md` page to its current `SKILL.md` after the document-skills production-grade program — the reviewer condition counts (e.g. `reviewing-prd` 8→12, `reviewing-document-set` 6→8 dimensions, `reviewing-feature-spec` →10, `reviewing-user-guide` →12, `reviewing-developer-guide` →14), the new **iteration/amend** method across the authoring + reviewing pairs, `project-document-discovery`'s explicit Self-check + amend, and the `design-review` scope carve-outs (technical-design / architecture-doc / data-model / api-spec route to their dedicated reviewers).

v2.26.0 — removes **`penpot-rest-ops`**. Visual-design authoring (wireframes/hi-fi, components, tokens) is editor/browser-bound in Penpot (same as Figma) — the REST API only does file-shell plumbing, so the skill is not useful for the headless agent-flow. The other three v2.25.0 provider ops skills (`jenkins-rest-ops`, `netlify-ops`, `cloudflare-pages-ops`) remain.

v2.25.0 — adds **four integration provider ops skills** for the agent-flow per-provider service-skill pattern, each a pure consumer of **caller-injected** credentials (token by variable name, `.env`-then-env-var, no account resolution): **`penpot-rest-ops`** (the Penpot design API as a command RPC — `POST /api/rpc/command/<cmd>` + `Authorization: Token`; bundled OpenAPI + `$ref`-resolver; the `Accept: application/json` transit trap), **`jenkins-rest-ops`** (the Jenkins Remote Access REST API — the async queue-item→build poll + the token-exempt CSRF crumb; no official OpenAPI, so an unofficial swaggy-jenkins cross-check + an official-docs CORE path index), **`netlify-ops`** (CLI-first on the `netlify` CLI + a REST fallback on the official OpenAPI — sites/deploys/domains/DNS + the digest-deploy protocol), and **`cloudflare-pages-ops`** (CLI-first on Wrangler + a REST fallback on the official OpenAPI Pages slice — projects/deploys/domains + the multipart deploy + the `{success,…}` envelope). Each carries a bundled OpenAPI (or slice) + an endpoint index + per-op validated scripts; none runs an interactive login.

v2.24.0 — restructures the two provider ops skills (**`atlassian-rest-ops`**, **`github-cli-ops`**) to consume **caller-injected** credentials instead of self-resolving from a `.service-accounts.yaml` record: Step 1 + the reference docs now receive `base_url`/`email`/`host` + the acting capability from the caller and resolve the token by an ordered load rule (the project `.env` value if that file exists and defines the var, else the environment variable of that name — no scope-walk, no `--account`), with a clearly-optional "Standalone usage" appendix for the by-hand record+`.env` bridge. The `scripts/*.sh` and their fixed env-var interface are unchanged.

v2.23.0 — adds three **engineering** skills, the SQL/scheduler skill set for agent-flow's DB-backed scheduler (the
global ready-set scheduler that replaces per-project state behind a State seam): **`sqlalchemy`** — build a portable
SQLAlchemy 2.x relational data layer that runs unchanged on SQLite + PostgreSQL + MySQL (the typed ORM-first
`DeclarativeBase` / `Mapped[...]` / `mapped_column`, one-engine-per-process + short-lived sessions, sync-first with an
async aside + a per-dialect driver matrix, and the load-bearing cross-dialect gotcha set — row locking, `JSON` vs PG
`JSONB`, upsert `ON CONFLICT` vs `ON DUPLICATE KEY UPDATE`, autoincrement/identity, isolation — that silently differs
per engine); **`alembic`** — run Alembic migrations on that layer across all three dialects from one history (wire
`env.py`/`alembic.ini` to `Base.metadata` with the URL from the environment, the revision → autogenerate → review →
upgrade/downgrade workflow + `merge`, the autogenerate-drafts-you-review discipline against its data-losing blind spots,
the SQLite batch move-and-copy gotcha — SQLite can't `ALTER` most schema so the same `batch_alter_table` code recreates
on SQLite and emits plain `ALTER` on PG/MySQL — and the `create_all()`-vs-Alembic decision + the baseline-stamp adoption
path); and **`sql-job-queue`** — build a DB-backed ready-set scheduler on SQLAlchemy 2.x (a single-box embeddable tick
loop where the DB is the sole durable substrate and readiness is dependency-driven: the generic `jobs`/`job_deps` model,
the ready-set query, the **three per-dialect lease branches** — `FOR UPDATE SKIP LOCKED` on PostgreSQL + MySQL 8 vs
`BEGIN IMMEDIATE` on SQLite — crash-resume via heartbeat + lease-expiry reclaim + a hung-worker timeout, weighted
fair-share over `group_key`, the scan→rank→lease→dispatch→persist→reclaim tick loop, and the at-least-once idempotency
contract with its atomic-finalize guard; it composes `sqlalchemy`'s `with_for_update(skip_locked=...)` locking primitive
rather than re-teaching it). All three are sync-first and multi-dialect; `alembic` and `sql-job-queue` build on
`sqlalchemy`'s data layer. Forged via the skill-build playbook (spec → design-review → plan → design-review → forge →
fresh-review). Additive — existing skills unchanged.

v2.22.0 — adds two **engineering** skills, the Phase-0 prerequisites for the agent-flow dashboard (slice-3) frontend
build: **`react-component-testing`** — the RTL + MSW + `vitest-axe` component-test layer for a Vite + React + TS SPA
under Vitest/jsdom (the network-boundary principle — mock with MSW so a generated `@hey-api/openapi-ts` client +
serialization run and contract drift surfaces, never module-mock; the jsdom env explicitly not happy-dom which breaks
axe; accessible queries; always-await `user-event` v14; the MSW `setupServer` lifecycle; a per-test TanStack Query
client; runtime a11y via `toHaveNoViolations`; jsdom-primary with a Vitest-browser-mode reference); and
**`tanstack-router`** — set up + use TanStack Router in a Vite + React + TS SPA (the type-safe route tree with the
`Register` merge, the `tanstackRouter` Vite plugin, file-based-primary + code-based routing, validated search params,
route loaders + the TanStack Query `ensureQueryData`↔`useSuspenseQuery` handshake framed through routing, code-splitting,
preloading, auth routes, route masking, and a memory-history test harness consumed by `react-component-testing`; defers
query mechanics to `tanstack-query`, fences out TanStack Start). Both forged via the skill-build playbook (spec →
design-review → plan → design-review → forge → fresh-review) and **main-thread doc-grounded-verified** against the live
official docs (which confirmed the happy-dom/axe caveat + vitest-axe API, and the `tanstackRouter` plugin export +
Zod-v3/v4 adapter split). Additive — existing skills unchanged.

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
