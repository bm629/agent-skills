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

## Quick install (Claude Code)

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
npx skills add bm629/agent-skills@token-optimization
npx skills add bm629/agent-skills@content-template-gateway
npx skills add bm629/agent-skills@skill-forge
npx skills add bm629/agent-skills@atlassian-rest-ops
npx skills add bm629/agent-skills@github-cli-ops
npx skills add bm629/agent-skills@design-review
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

Hand-authored or forge-built; see each skill's deep-dive doc for details.

## Status

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
