# agent-skills

> Skills for agentic coding tools: document authoring with matching review gates, systematic prior-art surveys, and provider integrations.

[![collection](https://img.shields.io/badge/collection-v2.53.0-blue)](CHANGELOG.md)
[![skills](https://img.shields.io/badge/skills-68-brightgreen)](#catalog)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Sixty-eight skills for **Claude Code, Cursor, GitHub Copilot, Codex** and **Gemini CLI**.

Most of the collection is **paired**: a skill that authors an artifact ships alongside a skill
that judges one, and both read their bar from a single shared file. That pairing is the point. An
agent that writes a PRD and then grades its own PRD will approve it — a reviewer written against
conditions it cannot silently relax will not.

## Contents

- [Install](#install) · [Usage](#usage)
- [Catalog](#catalog) — [safety](#safety) · [meta](#meta) · [design gates](#design--planning-gates) · [prior art](#prior-art-surveys) · [documents](#document-library) · [provider ops](#provider-ops) · [Python](#engineering--python--data) · [TypeScript & UI](#engineering--typescript-frontend--ui)
- [Why these together](#why-these-together) · [Documentation](#documentation) · [Contributing](#contributing) · [License](#license)

## Install

```bash
npx skills add bm629/agent-skills
```

Any single skill, by the name in the [catalog](#catalog):

```bash
npx skills add bm629/agent-skills@design-review
```

Per-agent paths, options and troubleshooting: [`docs/installation.md`](docs/installation.md).

## Usage

Skills activate on intent — describe the task and the agent reaches for the matching one. To
invoke one deliberately, name it:

```
Use design-review on docs/specs/auth-v2.md before I approve it.
```

Where a skill has a reviewing twin, run the author, then the reviewer, and treat the verdict as
the gate:

```
Author the PRD with authoring-prd, then run reviewing-prd and fold every blocker.
```

## Catalog

### Safety

| Skill | Purpose |
|---|---|
| [`external-content-sanitizer`](docs/skills/external-content-sanitizer.md) | Neutralize prompt injection in anything fetched, cloned or searched, before an agent reads it. |

<details>
<summary>Install this group only — 1 skill</summary>

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
```

</details>

### Meta

| Skill | Purpose |
|---|---|
| [`skill-forge`](docs/skills/skill-forge.md) | Research a topic you lack and write it up as a new portable skill. |
| [`content-template-gateway`](docs/skills/content-template-gateway.md) | Route any structured writing through a researched template instead of a blank page. |
| [`token-optimization`](docs/skills/token-optimization.md) | Cut token cost and fit work inside a context window. |

<details>
<summary>Install this group only — 3 skills</summary>

```bash
npx skills add bm629/agent-skills@skill-forge
npx skills add bm629/agent-skills@content-template-gateway
npx skills add bm629/agent-skills@token-optimization
```

</details>

### Design & planning gates

| Skill | Purpose |
|---|---|
| [`design-review`](docs/skills/design-review.md) | Adversarial pre-approval review of a spec, plan, RFC or ADR, with every claim verified against the code. |
| [`project-document-discovery`](docs/skills/project-document-discovery.md) | Decide which documents a project actually needs, sized to its archetype. |
| [`reviewing-document-discovery`](docs/skills/reviewing-document-discovery.md) | Judge that document plan before anyone builds to it. |
| [`reviewing-document-set`](docs/skills/reviewing-document-set.md) | Judge a finished set of documents as one corpus — are they mutually coherent? |

<details>
<summary>Install this group only — 4 skills</summary>

```bash
npx skills add bm629/agent-skills@design-review
npx skills add bm629/agent-skills@project-document-discovery
npx skills add bm629/agent-skills@reviewing-document-discovery
npx skills add bm629/agent-skills@reviewing-document-set
```

</details>

### Prior-art surveys

Five domains, each a producer plus a reviewing twin. They share one organising idea: **a domain
with nothing in it and a search that never ran produce identical-looking output**, so the
coverage record is built to keep those apart.

| Domain | Survey | Reviewer |
|---|---|---|
| Open-source code | [`code-prior-art-survey`](docs/skills/code-prior-art-survey.md) | [`reviewing-code-prior-art-survey`](docs/skills/reviewing-code-prior-art-survey.md) |
| Market & competitors | [`market-competitive-prior-art-survey`](docs/skills/market-competitive-prior-art-survey.md) | [`reviewing-market-competitive-prior-art-survey`](docs/skills/reviewing-market-competitive-prior-art-survey.md) |
| Security threats | [`security-prior-art-survey`](docs/skills/security-prior-art-survey.md) | [`reviewing-security-prior-art-survey`](docs/skills/reviewing-security-prior-art-survey.md) |
| Visual & interaction | [`visual-prior-art-survey`](docs/skills/visual-prior-art-survey.md) | [`reviewing-visual-prior-art-survey`](docs/skills/reviewing-visual-prior-art-survey.md) |
| Published user research | [`user-research-prior-art-survey`](docs/skills/user-research-prior-art-survey.md) | [`reviewing-user-research-prior-art-survey`](docs/skills/reviewing-user-research-prior-art-survey.md) |

<details>
<summary>Install this group only — 10 skills</summary>

```bash
npx skills add bm629/agent-skills@code-prior-art-survey
npx skills add bm629/agent-skills@reviewing-code-prior-art-survey
npx skills add bm629/agent-skills@market-competitive-prior-art-survey
npx skills add bm629/agent-skills@reviewing-market-competitive-prior-art-survey
npx skills add bm629/agent-skills@security-prior-art-survey
npx skills add bm629/agent-skills@reviewing-security-prior-art-survey
npx skills add bm629/agent-skills@visual-prior-art-survey
npx skills add bm629/agent-skills@reviewing-visual-prior-art-survey
npx skills add bm629/agent-skills@user-research-prior-art-survey
npx skills add bm629/agent-skills@reviewing-user-research-prior-art-survey
```

</details>

### Document library

Fifteen document types, each with an authoring skill and an acceptance gate.

| Document | Authoring | Reviewing |
|---|---|---|
| PRD | [`authoring-prd`](docs/skills/authoring-prd.md) | [`reviewing-prd`](docs/skills/reviewing-prd.md) |
| Feature spec | [`authoring-feature-spec`](docs/skills/authoring-feature-spec.md) | [`reviewing-feature-spec`](docs/skills/reviewing-feature-spec.md) |
| User flows | [`authoring-user-flows`](docs/skills/authoring-user-flows.md) | [`reviewing-user-flows`](docs/skills/reviewing-user-flows.md) |
| Wireframes | [`authoring-wireframes`](docs/skills/authoring-wireframes.md) | [`reviewing-wireframes`](docs/skills/reviewing-wireframes.md) |
| Design system | [`authoring-design-system`](docs/skills/authoring-design-system.md) | [`reviewing-design-system`](docs/skills/reviewing-design-system.md) |
| Hi-fi UI design | [`authoring-hi-fi`](docs/skills/authoring-hi-fi.md) | [`reviewing-hi-fi`](docs/skills/reviewing-hi-fi.md) |
| Technical design | [`authoring-technical-design`](docs/skills/authoring-technical-design.md) | [`reviewing-technical-design`](docs/skills/reviewing-technical-design.md) |
| Architecture doc | [`authoring-architecture-doc`](docs/skills/authoring-architecture-doc.md) | [`reviewing-architecture-doc`](docs/skills/reviewing-architecture-doc.md) |
| API spec | [`authoring-api-spec`](docs/skills/authoring-api-spec.md) | [`reviewing-api-spec`](docs/skills/reviewing-api-spec.md) |
| Data model | [`authoring-data-model`](docs/skills/authoring-data-model.md) | [`reviewing-data-model`](docs/skills/reviewing-data-model.md) |
| User guide | [`authoring-user-guide`](docs/skills/authoring-user-guide.md) | [`reviewing-user-guide`](docs/skills/reviewing-user-guide.md) |
| Developer guide | [`authoring-developer-guide`](docs/skills/authoring-developer-guide.md) | [`reviewing-developer-guide`](docs/skills/reviewing-developer-guide.md) |
| API reference | [`authoring-api-reference`](docs/skills/authoring-api-reference.md) | [`reviewing-api-reference`](docs/skills/reviewing-api-reference.md) |
| Release runbook | [`authoring-release-runbook`](docs/skills/authoring-release-runbook.md) | [`reviewing-release-runbook`](docs/skills/reviewing-release-runbook.md) |
| Test plan | [`authoring-test-plan`](docs/skills/authoring-test-plan.md) | [`reviewing-test-plan`](docs/skills/reviewing-test-plan.md) |

<details>
<summary>Install this pair set only — 30 skills</summary>

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

</details>

### Provider ops

| Skill | Purpose |
|---|---|
| [`github-cli-ops`](docs/skills/github-cli-ops.md) | Drive GitHub from the CLI — issues, PRs, releases, Actions, Projects, secrets. |
| [`atlassian-rest-ops`](docs/skills/atlassian-rest-ops.md) | Call Jira Cloud v3 and Confluence Cloud v2 REST directly, no SDK. |
| [`jenkins-rest-ops`](docs/skills/jenkins-rest-ops.md) | Trigger and poll Jenkins builds over its REST API. |
| [`netlify-ops`](docs/skills/netlify-ops.md) | Create sites, deploy builds and set custom domains on Netlify. |
| [`cloudflare-pages-ops`](docs/skills/cloudflare-pages-ops.md) | The same, on Cloudflare Pages. |

<details>
<summary>Install this group only — 5 skills</summary>

```bash
npx skills add bm629/agent-skills@github-cli-ops
npx skills add bm629/agent-skills@atlassian-rest-ops
npx skills add bm629/agent-skills@jenkins-rest-ops
npx skills add bm629/agent-skills@netlify-ops
npx skills add bm629/agent-skills@cloudflare-pages-ops
```

</details>

### Engineering — Python & data

| Skill | Purpose |
|---|---|
| [`pydantic-v2`](docs/skills/pydantic-v2.md) | Validate, serialize and configure data with Pydantic v2. |
| [`sqlalchemy`](docs/skills/sqlalchemy.md) | A SQLAlchemy 2.x data layer that runs on SQLite, PostgreSQL and MySQL from one codebase. |
| [`alembic`](docs/skills/alembic.md) | Multi-dialect Alembic migrations over that data layer. |
| [`sql-job-queue`](docs/skills/sql-job-queue.md) | A DB-backed job queue with dependency-driven readiness and long-running stateful jobs. |
| [`rest-api-design`](docs/skills/rest-api-design.md) | Design a REST surface — resources, methods, status codes, RFC-shaped errors. |
| [`python-monorepo-architecture`](docs/skills/python-monorepo-architecture.md) | Split a Python repo into a `uv`-workspace monorepo. |

<details>
<summary>Install this group only — 6 skills</summary>

```bash
npx skills add bm629/agent-skills@pydantic-v2
npx skills add bm629/agent-skills@sqlalchemy
npx skills add bm629/agent-skills@alembic
npx skills add bm629/agent-skills@sql-job-queue
npx skills add bm629/agent-skills@rest-api-design
npx skills add bm629/agent-skills@python-monorepo-architecture
```

</details>

### Engineering — TypeScript, frontend & UI

| Skill | Purpose |
|---|---|
| [`typescript-typecheck`](docs/skills/typescript-typecheck.md) | Run `tsc --noEmit` as a standalone quality gate on a strict config. |
| [`biome`](docs/skills/biome.md) | Lint and format JS/TS with the single Rust toolchain. |
| [`tsdoc`](docs/skills/tsdoc.md) | TSDoc comments the TypeScript toolchain actually understands. |
| [`openapi-ts-client`](docs/skills/openapi-ts-client.md) | Generate a typed TS client from an OpenAPI 3.1 contract. |
| [`tanstack-router`](docs/skills/tanstack-router.md) | Type-safe routing for a Vite + React SPA. |
| [`react-component-testing`](docs/skills/react-component-testing.md) | Component tests with RTL, MSW and vitest-axe under Vitest. |
| [`motion-react`](docs/skills/motion-react.md) | Animate React with Motion, the framer-motion successor. |
| [`ui-illustrations`](docs/skills/ui-illustrations.md) | Choose and place imagery for empty states, onboarding and error pages. |
| [`polyglot-git-hooks`](docs/skills/polyglot-git-hooks.md) | Fast staged-file checks with Lefthook in a polyglot repo. |

<details>
<summary>Install this group only — 9 skills</summary>

```bash
npx skills add bm629/agent-skills@typescript-typecheck
npx skills add bm629/agent-skills@biome
npx skills add bm629/agent-skills@tsdoc
npx skills add bm629/agent-skills@openapi-ts-client
npx skills add bm629/agent-skills@tanstack-router
npx skills add bm629/agent-skills@react-component-testing
npx skills add bm629/agent-skills@motion-react
npx skills add bm629/agent-skills@ui-illustrations
npx skills add bm629/agent-skills@polyglot-git-hooks
```

</details>

## Why these together

**Authoring is paired with judging.** Fifteen document types and five prior-art domains each ship
a producer and a reviewer, and the reviewer's conditions live in one file both halves read. A bar
duplicated across two documents drifts — one saying a count means results while the other says
rows, each looking right alone, the disagreement surfacing only when a document is graded by the
half that did not write it.

**Method, not content.** The authoring skills teach how to produce a document, never what to put
in it. That is what keeps them project-agnostic: a PRD skill that knows your product is a
template wearing a skill's clothes.

**Absence is evidence, and has to be earned.** Every prior-art survey records its coverage so
that "we searched and found nothing" stays distinguishable from "we never searched". The
deterministic validators check shape and arithmetic only; whether a finding is any good belongs
to the reviewing twin. That split is deliberate — a fuzzy heuristic inside a gate produces false
failures and duplicates the reviewer it was meant to support.

Each skill also fills a gap rather than duplicating one: `external-content-sanitizer` is a
defensive guardrail rather than a red-team playbook or a self-audit tool; `design-review` targets
the spec before code exists rather than the diff after; `content-template-gateway` catches every
authoring attempt including external destinations rather than waiting to be invoked on a file.
The per-skill deep dives carry the full reasoning.

## Documentation

| Doc | Contents |
|---|---|
| [`installation.md`](docs/installation.md) | Per-agent install paths, options, troubleshooting |
| [`architecture.md`](docs/architecture.md) | Repo layout, frontmatter design, roadmap |
| [`compatibility.md`](docs/compatibility.md) | Agent compatibility matrix |
| [`contributing.md`](docs/contributing.md) | How to add or change a skill |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |

Every skill has a deep dive under [`docs/skills/`](docs/skills/) covering its design decisions
and the reasoning behind them — linked from its name in the catalog above.

## Contributing

Issues and pull requests welcome — [`docs/contributing.md`](docs/contributing.md) covers what a
change has to clear. Skills are hand-authored or forge-built; either way a new one needs its
deep-dive doc and a catalog entry here.

## License

MIT © 2026 Bhushan Modi. See [LICENSE](LICENSE).
