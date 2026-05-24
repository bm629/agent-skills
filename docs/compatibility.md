# Compatibility

`agent-skills` v1 is a **skills release** — fully usable across 5 agents
via `npx skills add ... -a <agent>` (the CLI translates the universal
`SKILL.md` into each agent's native format at install time).

**v1 is NOT indexed in the skills.sh registry.** The repo doesn't ship
the `.claude-plugin/marketplace.json` manifest skills.sh uses for
discovery. Install today by sharing the direct URL.

Full **plugin packaging** (pre-rendered per-agent dotfile dirs so
direct `git clone` works without the CLI) AND **registry indexing**
are both v2 milestones. See
[architecture.md § Roadmap](architecture.md#roadmap).

## v1 compatibility matrix

| Agent | v1 status | Install command | v2 plan |
|---|---|---|---|
| **Claude Code** | ✅ Installable via direct URL | `npx skills add bm629/agent-skills@<skill>` (default) | + skills.sh registry indexing |
| **Cursor** | ✅ Via CLI translation | `npx skills add bm629/agent-skills@<skill> -a cursor` | Pre-rendered `.cursor-plugin/` |
| **GitHub Copilot** | ✅ Via CLI translation | `npx skills add bm629/agent-skills@<skill> -a github-copilot` | Pre-rendered `.github/chatmodes/` |
| **Codex** | ✅ Via CLI translation | `npx skills add bm629/agent-skills@<skill> -a codex` | Pre-rendered `.codex-plugin/` |
| **Gemini CLI** (bonus) | ✅ Via CLI translation | `npx skills add bm629/agent-skills@<skill> -a gemini` | Pre-rendered `.opencode/` or equivalent |

## Version requirements

| Component | Required | Notes |
|---|---|---|
| Node.js | ≥ 18 | For `npx`; the skills CLI runs in Node ≥ 18 |
| `skills` CLI | latest (`npx -y skills`) | Auto-fetched on first `npx skills` invocation |
| Claude Code | any | Skill installs to `.claude/skills/<name>/SKILL.md`; no Claude version constraint |
| Cursor | recent (within ~6 months) | Older Cursor versions may not support all MDC frontmatter fields |
| GitHub Copilot | with chatmodes support | Chatmodes shipped 2025; older Copilot doesn't read `.github/chatmodes/` |
| Codex | ≥ 0.5.0 | `extensions.codex.compatibility: ">=0.5.0"` declared in `external-content-sanitizer/SKILL.md` |
| Gemini CLI | any | `extensions.gemini.kind: local` — no specific version pin |

## Known gotchas

### Cursor MDC format strictness

Cursor's MDC format expects specific frontmatter fields (`alwaysApply`,
`globs`, etc.) — these are declared in `extensions.cursor` for both
skills. If Cursor logs a frontmatter parse warning after install, file
an issue and we'll harden the translation.

### GitHub Copilot chatmode discovery timing

Copilot scans `.github/chatmodes/` at startup. After
`npx skills add ... -a github-copilot`, restart Copilot before
expecting the chatmode to appear in the picker.

### Codex TOML strict typing

Codex agents are TOML; the `extensions.codex` frontmatter values
become TOML values. `compatibility: ">=0.5.0"` is a string in YAML →
quoted string in TOML. No issues at v1; flagged here as a thing to
watch.

### `external-content-sanitizer` and the `docs/security/` runtime dir

The skill writes to `docs/security/flagged-sources.md` in the
workspace root. **The skill creates this file on first flag.** If your
workspace has no `docs/` dir, the skill creates it. If your workspace
disallows top-level dir creation, this is a real conflict — file an
issue.

### Workspace-relative paths in the skill

`external-content-sanitizer` documents paths like
`<WORKSPACE_ROOT>/docs/security/flagged-sources.md` — the skill is
**workspace-aware**, it finds the workspace root via the agent's
context (or falls back to the current working directory).

For agents that don't expose a workspace root (rare), the skill
treats CWD as the workspace.

## Reporting compatibility issues

If a skill doesn't install or doesn't activate on your agent:

1. Check Node version: `node --version` (must be ≥ 18)
2. Check the install path exists per the matrix above
3. Open SKILL.md / `.cursor/rules/<name>.mdc` / etc. — confirm the
   frontmatter parsed and the body is intact
4. If broken, file an issue at
   [github.com/bm629/agent-skills/issues](https://github.com/bm629/agent-skills/issues)
   with:
   - Agent name + version
   - Install command you ran
   - First 30 lines of the installed file
   - Any error output from the install
