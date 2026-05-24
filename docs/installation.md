# Installation

`agent-skills` ships as a multi-skill collection installable via the
[skills.sh](https://skills.sh) CLI. The CLI handles per-agent
translation at install time, so the same source `SKILL.md` lands as
the right format for each agent.

## Prerequisites

- **Node.js ≥ 18** — for `npx`
- One of the supported agents installed locally:
  Claude Code, Cursor, GitHub Copilot, Codex, or Gemini CLI

Verify `npx` works:

```bash
npx --version
```

No global install needed; `npx -y skills` fetches the latest skills CLI
on demand.

## Install a single skill

The canonical pattern is:

```bash
npx skills add bm629/agent-skills@<skill-name> -a <agent>
```

Where:
- `<skill-name>` is `external-content-sanitizer` or `token-optimization`
- `<agent>` is one of: `claude-code` (default), `cursor`, `github-copilot`, `codex`, `gemini`

Omit `-a` to default to Claude Code (the most common case).

### Claude Code

```bash
npx skills add bm629/agent-skills@external-content-sanitizer
npx skills add bm629/agent-skills@token-optimization
```

Installs to `.claude/skills/<name>/SKILL.md`.

### Cursor

```bash
npx skills add bm629/agent-skills@external-content-sanitizer -a cursor
npx skills add bm629/agent-skills@token-optimization -a cursor
```

The CLI translates the SKILL.md into Cursor's `.cursor/rules/<name>.mdc`
format using the `extensions.cursor` block from the skill's frontmatter.

### GitHub Copilot

```bash
npx skills add bm629/agent-skills@external-content-sanitizer -a github-copilot
npx skills add bm629/agent-skills@token-optimization -a github-copilot
```

Installs to `.github/chatmodes/<name>.chatmode.md`.

### Codex

```bash
npx skills add bm629/agent-skills@external-content-sanitizer -a codex
npx skills add bm629/agent-skills@token-optimization -a codex
```

Installs to `.codex/agents/<name>.toml`.

### Gemini CLI (bonus)

```bash
npx skills add bm629/agent-skills@external-content-sanitizer -a gemini
npx skills add bm629/agent-skills@token-optimization -a gemini
```

Uses the `extensions.gemini` frontmatter block (`kind: local`,
`max_turns: 10`, `timeout_mins: 5` for external-content-sanitizer).

## Install all skills at once

```bash
npx skills add bm629/agent-skills --all
```

This pulls the whole `agent-skills` collection into your default agent.
Add `-a <agent>` to target a specific one.

## Install on multiple agents at once

```bash
npx skills add bm629/agent-skills@external-content-sanitizer -a '*'
```

The `-a '*'` wildcard installs into every agent the CLI detects on your
machine.

## Update / remove

```bash
# Update all installed skills to the latest version
npx skills update

# Update only this collection
npx skills update bm629/agent-skills

# Remove a single skill
npx skills remove external-content-sanitizer

# Remove the whole collection
npx skills remove --all -a '*'
```

## Verifying the install

After installing, the skill appears in the target agent's discovery
location:

| Agent | Path to check |
|---|---|
| Claude Code | `./.claude/skills/<name>/SKILL.md` |
| Cursor | `./.cursor/rules/<name>.mdc` |
| GitHub Copilot | `./.github/chatmodes/<name>.chatmode.md` |
| Codex | `./.codex/agents/<name>.toml` |
| Gemini CLI | `./.gemini/skills/<name>/SKILL.md` |

Open the file to confirm the content arrived intact. The
`description:` frontmatter should match what's in the
[main SKILL.md](../skills/external-content-sanitizer/SKILL.md).

## Troubleshooting

### `npx skills not found`

Make sure Node ≥ 18 is installed (`node --version`). If you have an
older Node, upgrade via your package manager or [nvm](https://github.com/nvm-sh/nvm).

### Agent not detected by `--all` / `-a '*'`

The CLI auto-detects agents by looking for their dotfile directories
(`.claude/`, `.cursor/`, etc.) in the current working directory. If the
agent isn't detected, either:
- Run from a project that already has the agent initialized
- Specify the agent explicitly: `-a cursor` instead of `-a '*'`

### Install path collisions

If a skill with the same name already exists at the target path, the
CLI refuses to overwrite. Force-replace with:

```bash
npx skills remove <name> -a <agent>
npx skills add bm629/agent-skills@<name> -a <agent>
```

### "Skill installed but agent doesn't see it"

For Cursor / Codex / GitHub Copilot, restart the agent after install —
they typically scan their config dirs at startup.

For Claude Code, run `/skills list` inside the session; the skill
should appear after the file lands on disk.

## Direct git clone (advanced)

For users who want to bypass the CLI and clone the repo directly into
their project:

```bash
cd your-project
git clone https://github.com/bm629/agent-skills .agent-skills-source
cp -r .agent-skills-source/skills/external-content-sanitizer .claude/skills/
```

This works for **Claude Code only at v1** because the SKILL.md format
is what Claude Code natively reads. For other agents, the SKILL.md
needs translation to their format — use `npx skills add` instead, or
wait for v2 (which will pre-render per-agent plugin packages).
