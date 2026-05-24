# Contributing

Thanks for your interest in `agent-skills`. This collection is
small + hand-authored; contributions are welcome under the
[MIT license](../LICENSE).

## Quick options

| You want to... | Do this |
|---|---|
| Report a bug or request a feature | File an [issue](https://github.com/bm629/agent-skills/issues) |
| Modify an existing skill | Open a PR against `skills/<name>/SKILL.md` (or its `references/`) |
| Propose a new skill | See [adding a new skill](#adding-a-new-skill) below |
| Improve docs | PR against `docs/` or `README.md` |
| Suggest a v2 plugin-packaging format | Issue first (design discussion) |

## Filing an issue

Include:

- Which skill (`external-content-sanitizer` or `token-optimization`)
- Which agent (Claude Code, Cursor, GitHub Copilot, Codex, Gemini CLI)
- Node version (`node --version`)
- Steps to reproduce
- Expected vs actual behavior

For sanitizer issues specifically, **do not paste the prompt-injection
content that triggered the bug** — describe the structure (e.g., "URL
with a base64 query string containing the word 'instructions'") so we
can reproduce without re-exposing the payload.

## Modifying an existing skill

1. Fork the repo
2. Branch from `main`: `git checkout -b fix/<short-description>`
3. Edit `skills/<name>/SKILL.md` or `skills/<name>/references/<file>.md`
4. If your change affects user-visible behavior, also update the
   corresponding deep-dive doc in `docs/skills/<name>.md`
5. **Bump the `version:` field** in the SKILL.md frontmatter:
   - patch (1.0.3 → 1.0.4) for typos, clarifications, doc-only changes
   - minor (1.0.3 → 1.1.0) for new patterns / tactics / behavior that's backward-compatible
   - major (1.0.3 → 2.0.0) for breaking changes to args, output format, or pattern_class names
6. Open a PR with:
   - What changed
   - Why
   - Any breaking-change notes
   - Agent test results if relevant

## Adding a new skill

1. Decide if it really needs to be a new skill, or if it should be a
   `references/<topic>.md` inside an existing skill. A skill is
   warranted when the new behavior has its own activation triggers,
   its own workflow, and its own contract.
2. Create `skills/<new-skill-name>/SKILL.md` following the structure of
   the existing two:
   - `---` frontmatter with `name`, `description` (≤1,024 chars,
     leading with "Use when..."), `extensions:` block for all 5
     agents, and `version: "1.0.0"`
   - `# <Skill Name>` heading
   - `## Overview`, `## When to activate`, `## Workflow`, `### Hard rules`
3. Add `skills/<name>/references/` for any topic-specific deep dives
   (rule of thumb: anything that doesn't need to be in the agent's
   every-turn context goes in references/, loaded on-demand)
4. ~~Add the skill to `.claude-plugin/marketplace.json` under `plugins[]`~~ — deferred to v2 (registry indexing). At v1, the README skills table is the only catalog
5. Create `docs/skills/<name>.md` with the deep-dive doc
6. Update `README.md` table + `docs/installation.md` per-agent
   commands
7. Open a PR

## Style conventions

| Aspect | Convention |
|---|---|
| Frontmatter `description` | ≤ 1,024 chars; lead with "Use when..."; include user-spoken keywords |
| Body length | Soft-target ~500 lines / ~5,000 tokens; overflow → `references/<topic>-extras.md` |
| Tables | Use `|` markdown tables when comparing options |
| Code blocks | Triple-backtick with language tag when applicable |
| Emojis | Avoid in code/SKILL.md; OK in docs README headings if user-facing |
| Per-agent extensions | Always declare all 5 agents (`claude`, `copilot`, `cursor`, `gemini`, `codex`), even if empty `{}` |

## Versioning policy

`agent-skills` follows **semver per-skill** AND **semver for the
collection** as a whole (`package.json` and `.claude-plugin/plugin.json`):

- Individual skill version (`SKILL.md` frontmatter): governs the
  skill's own contract
- Collection version (`package.json`): bumps when any skill's major
  version bumps, when adding a new skill, or when removing a skill

## License of contributions

By submitting a PR, you agree your contribution is licensed under the
project's [MIT license](../LICENSE). No CLA required.

## Code of conduct

Be excellent. Disagreements are fine; personal attacks are not. The
maintainer reserves the right to lock or close threads that aren't
moving forward constructively.
