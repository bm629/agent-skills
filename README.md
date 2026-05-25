# agent-skills

Security, token-efficiency, and documentation skills for AI coding agents.
Works across **Claude Code, Cursor, GitHub Copilot, Codex,** and **Gemini CLI**.

## Skills in this collection

| Skill | One-line purpose | Category |
|---|---|---|
| [`external-content-sanitizer`](docs/skills/external-content-sanitizer.md) | Defensive runtime sanitizer for external untrusted content (WebFetch / WebSearch / cloned repos) | security |
| [`token-optimization`](docs/skills/token-optimization.md) | Diagnostic + tactic catalog for reducing token usage across 5 layers (system prompt, tool defs, history, tool results, output) | productivity |
| [`doc-template-gateway`](docs/skills/doc-template-gateway.md) | Gate for any document creation — identifies doc-type + variant from intent, enforces template use via hard-refusal directive, forges templates when missing | documentation |

## Quick install (Claude Code)

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
npx skills add bm629/agent-skills@token-optimization
npx skills add bm629/agent-skills@doc-template-gateway
```

For Cursor, GitHub Copilot, Codex, or Gemini CLI — see the
[installation guide](docs/installation.md).

## Documentation

| Doc | Covers |
|---|---|
| [`docs/installation.md`](docs/installation.md) | Per-agent install instructions for all 4 target agents + Gemini bonus; troubleshooting |
| [`docs/skills/external-content-sanitizer.md`](docs/skills/external-content-sanitizer.md) | Deep dive: when to invoke, args, workflow, output format, safety invariants |
| [`docs/skills/token-optimization.md`](docs/skills/token-optimization.md) | Deep dive: 5-layer model, measure-first workflow, per-layer tactics |
| [`docs/skills/doc-template-gateway.md`](docs/skills/doc-template-gateway.md) | Deep dive: 5-phase workflow (identify / check / enforce / forge / advise), 3 invocation modes, ASCII directive format |
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
- **`doc-template-gateway`** is the only **template-enforcement gateway**
  that catches every doc-creation attempt (user or agent), identifies the
  doc-type from intent via research, and either returns an existing
  template with a hard-refusal directive or forges a new one. Other
  template skills are passive — they wait to be invoked explicitly.

All hand-authored. See each skill's deep-dive doc for details.

## Status

v1.1.0 — adds `doc-template-gateway`. All three skills work via direct
`npx skills add` URL on all five supported agents.

**Not yet indexed in skills.sh registry** — the repo won't appear in
`npx skills find` or the public leaderboard until v2 adds the
`.claude-plugin/marketplace.json` manifest. Install today by sharing
the direct URL. Pre-rendered per-agent plugin packages are also v2 work.

See [architecture.md § Roadmap](docs/architecture.md#roadmap) for the
v2 milestone breakdown.

## License

MIT © 2026 Bhushan Modi. See [LICENSE](LICENSE).
