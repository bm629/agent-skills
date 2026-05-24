# Architecture

How this repo is structured, what each top-level file does, and why
the decisions were made.

## Repo layout

```
agent-skills/
├── skills/                                  # canonical source — universal SKILL.md files
│   ├── external-content-sanitizer/
│   │   ├── SKILL.md                          # the skill itself, with per-agent extensions frontmatter
│   │   └── references/                       # on-demand reference docs loaded by the agent
│   │       ├── flagged-sources-format.md
│   │       ├── injection-patterns.md
│   │       └── severity-rules.md
│   └── token-optimization/
│       ├── SKILL.md
│       └── references/
│           ├── agent-loop-patterns.md
│           ├── context-management.md
│           ├── measurement-and-budgets.md
│           ├── output-and-verification.md
│           └── prompt-caching.md
├── docs/                                     # human-readable documentation
│   ├── installation.md
│   ├── architecture.md
│   ├── compatibility.md
│   ├── contributing.md
│   └── skills/
│       ├── external-content-sanitizer.md     # deep dive for GitHub browsers
│       └── token-optimization.md             # same
├── README.md                                 # landing page; links into docs/
├── LICENSE                                   # MIT
├── package.json                              # npm-discoverable metadata
└── .gitignore
```

## Role of each top-level file

| File / directory | Purpose |
|---|---|
| `skills/<name>/SKILL.md` | The skill itself. Universal source; per-agent translation happens at `npx skills add` install time |
| `skills/<name>/references/` | On-demand reference docs the agent loads only when needed (not in every-turn context) |
| `docs/` | Human-readable documentation for GitHub browsers; mirrors the SKILL.md content in narrative form |
| `README.md` | Landing page. Terse (≤200 lines). Links into `docs/` for everything else |
| `LICENSE` | MIT |
| `package.json` | npm-discoverable metadata; `files:` field lists what gets included in a publish |
| `.gitignore` | OS noise, editor noise, env files, future tooling caches |

## Why SKILL.md has per-agent `extensions:` blocks

Each `SKILL.md` declares an `extensions:` block in YAML frontmatter
naming all five supported agents (claude, copilot, cursor, gemini,
codex). This is the **universal contract**: the same SKILL.md can be
translated to any agent's native format by reading its extensions block.

The `npx skills add ... -a <agent>` CLI does this translation at
install time:

| Agent | Translation target |
|---|---|
| Claude Code | Copy SKILL.md directly to `.claude/skills/<name>/SKILL.md` |
| Cursor | Convert to MDC format: `.cursor/rules/<name>.mdc` |
| GitHub Copilot | Convert to chatmode: `.github/chatmodes/<name>.chatmode.md` |
| Codex | Convert to TOML: `.codex/agents/<name>.toml` |
| Gemini CLI | `.gemini/skills/<name>/SKILL.md` (similar to Claude) |

## Why we do NOT bundle pre-rendered per-agent dotfile dirs (v1)

Some skill repos (e.g., `obra/superpowers`, `juliusbrussee/caveman`)
bundle pre-rendered per-agent directories like `.cursor-plugin/`,
`.codex-plugin/`, `.opencode/`. This lets users `git clone` and have
it work in any agent without running the CLI.

v1 of `bm629/agent-skills` deliberately skips this. Reasons:

1. **Sync risk** — every SKILL.md edit would require regenerating each
   per-agent file. Easy to forget; drift breaks installs silently.
2. **Smaller repo** — pre-rendering 4–5 agent formats roughly 4–5×s
   the file count and total size.
3. **CLI handles it** — `npx skills add ... -a <agent>` does the same
   translation on-demand. The "direct git clone" use case is rare.

v2 plans to add pre-rendered dirs **with a regen script** so the
canonical SKILL.md remains the source of truth. See the [Roadmap](#roadmap)
below.

## Why two skills in one repo (not two repos)

A multi-skill collection beats two single-skill repos for several
reasons:

- **Single LICENSE / README / metadata** to maintain
- **Shared install pool** — install counts on skills.sh pool together;
  better discoverability
- **Easier to add a 3rd / 4th skill** — just drop a directory in
  `skills/`, add an entry to `marketplace.json`
- **Matches the established convention** — `obra/superpowers`,
  `vercel-labs/agent-skills`, `anthropics/skills` all use this pattern

The skills don't have to be thematically related — `obra/superpowers`
mixes TDD, debugging, git worktrees, and code review under one umbrella.

## How users find this repo in v1

v1 does **NOT** ship with the `.claude-plugin/marketplace.json`
manifest skills.sh uses for registry indexing. Concretely:

- ✅ `npx skills add bm629/agent-skills@<skill>` works for anyone who
  knows the URL — the CLI reads `skills/<skill>/SKILL.md` directly
  from the GitHub repo structure
- ❌ The repo will NOT appear in `npx skills find` search results
- ❌ The repo will NOT appear on the skills.sh leaderboard
- ❌ Install counts are NOT tracked by the registry

Distribution at v1 is **direct URL sharing**: the README, this docs
folder, and people you tell about it.

v2 adds the `.claude-plugin/` manifest and the registry indexing
unlocks automatically (see [Roadmap](#roadmap) below).

## Roadmap

### v1 (this release)

- Two skills, CLI-translation-based multi-agent support
- Six docs files covering install, deep dives, architecture, compat,
  contributing
- Direct URL distribution (no skills.sh registry indexing yet)

### v2 (planned, separate spec)

- **skills.sh registry indexing** — add `.claude-plugin/marketplace.json`
  and `.claude-plugin/plugin.json` so the repo appears in `npx skills
  find` and on the skills.sh leaderboard
- **Pre-rendered per-agent dotfile dirs**:
  - `.cursor-plugin/` (Cursor MDC files)
  - `.codex-plugin/` (Codex TOML files)
  - `.opencode/` or equivalent (Copilot chatmodes)
- A regen script (`scripts/render-plugins.sh`) that rebuilds the
  per-agent dirs from canonical SKILL.md whenever they change
- `docs/compatibility.md` matrix flips from "CLI translation only,
  not indexed" → "fully packaged plugin per agent, registry-indexed"

### v3+

- Third + fourth skill (when authored)
- Optional CI to enforce SKILL.md ↔ per-agent dir sync
- Possible move to a GitHub org if more skills are authored
