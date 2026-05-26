# agent-skills

Security, token-efficiency, and documentation skills for AI coding agents.
Works across **Claude Code, Cursor, GitHub Copilot, Codex,** and **Gemini CLI**.

## Skills in this collection

| Skill | One-line purpose | Category |
|---|---|---|
| [`external-content-sanitizer`](docs/skills/external-content-sanitizer.md) | Defensive runtime sanitizer for external untrusted content (WebFetch / WebSearch / cloned repos) | security |
| [`token-optimization`](docs/skills/token-optimization.md) | Diagnostic + tactic catalog for reducing token usage across 5 layers (system prompt, tool defs, history, tool results, output) | productivity |
| [`content-template-gateway`](docs/skills/content-template-gateway.md) | Gate for any agent-authored structured content (file or external destination) — identifies content-type + variant from intent, enforces template use via hard-refusal directive, forges templates when missing | content authoring |

## Quick install (Claude Code)

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
npx skills add bm629/agent-skills@token-optimization
npx skills add bm629/agent-skills@content-template-gateway
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

All hand-authored. See each skill's deep-dive doc for details.

## Status

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
