# content-template-gateway

> Gate for any agent-authored structured content, any destination.
> Identifies content-type + variant from intent via research, enforces
> template use via hard-refusal directive, forges templates when
> missing, advises on placing content that doesn't fit. Self-contained.
> Cross-agent uniform.

**Skill file:** [`skills/content-template-gateway/SKILL.md`](../../skills/content-template-gateway/SKILL.md)
**Version:** 2.0.0

## Purpose

This skill is the **canonical entry point** for any agent-authored
structured content — regardless of destination. It catches content-creation
attempts by user or agent, identifies the content-type + variant via
research, and either:

- **Returns an existing template** with a hard-refusal directive (you
  MUST follow this structure), or
- **Forges a new template** when none exists (research-backed
  workflow), then returns it under the same directive.

It also has an **advise mode** for the common case where the user's
content doesn't fit any section of the current template — it either
suggests placement, or proposes a new variant template with the
missing section.

Content-type and destination are **orthogonal axes**. The same
content-type (e.g., a spec, an RFC, a runbook) can land in a local
markdown file, a Confluence page, a Notion doc, a Google Drive
document, or any other destination. The template is driven by
content-type; the destination is incidental metadata carried into
the Phase C directive so the consuming agent knows where the result
is going.

The skill is fully self-contained: no declared skill dependencies.
The research workflow prefers a research-capable skill when one is
installed but falls back to built-in `WebSearch` + `WebFetch` so it
works in any environment.

## When to activate

- ✅ Anyone (user or agent) is about to author any structured content — for any destination
- ✅ Agent is about to do any of: write a doc file, call `gh pr create` / `gh issue create` / `gh pr|issue comment` with a non-trivial body, create a Jira / Linear ticket, compose a multi-paragraph `git commit` body, post a long-form Slack / email message, publish a Confluence / Notion page
- ✅ User asks to re-forge an existing template (mode `force-regenerate`)
- ✅ User asks to add a new variant of an existing content-type (mode `force-new-variant`)
- ✅ User says "advise: I have content that doesn't fit" — triggers Phase E
- ✅ User invokes the skill explicitly (e.g., `/content-template-gateway`)

### When NOT to activate

- User wants project structure scaffolding (Python `uv` workspace, etc.) — different skill
- User wants to translate an existing template to another language or format — out of scope
- User wants to fill in a template with real content (instantiate it) — that's the consuming agent's job; this skill only returns the template + directive
- User is editing already-authored content for typos / formatting / clarity — the skill is for *new* content authoring, not editing
- Single-line / trivial content (one-line commit message, one-line Slack reply) — the skill is for *structured* multi-section content
- User explicitly says "I don't need a template — quick note" — override case

## Workflow (5 phases)

```
Caller invokes with intent → Phase A → Phase B → Phase C
                                          │
                                          ├─ if template missing → Phase D → Phase C
                                          │
                                          └─ if intent is "advise:" → Phase E (may invoke D)
```

| Phase | Role |
|---|---|
| **A. Identify** | Research user/agent intent → content-type + variant + destination + mode (`use-or-create` / `force-regenerate` / `force-new-variant`). Asks for more context if intent is ambiguous (up to 2 rounds). |
| **B. Check** | Classify `docs/templates/<content-type>/<variant>/` as Complete / Missing / Orphan-partial. Branch on mode × state. |
| **C. Enforce** | Load template + research, assemble ASCII-bounded directive payload, return to caller. No prompts. |
| **D. Forge** (sub) | Sub-procedure: initial research → propose 2–4 variants → deep research per variant → emit `template.md` + `research.md` + parent `README.md`. Skipped variants leave no folder. |
| **E. Advise** (sub) | Sub-procedure: research how user's content typically fits this content-type → return section-placement recommendations, OR propose a new variant template (which user can forge via Phase D). |

## Three invocation modes

| Mode | When | Behavior |
|---|---|---|
| `use-or-create` (default) | Normal content authoring | If template exists → Phase C. If missing → Phase D → Phase C. |
| `force-regenerate` | User says "re-forge X" | Skip Phase B, go to Phase D with existing slug, overwrite. |
| `force-new-variant` | User says "create a new variant called Y" | Skip Phase B, run Phase D with the new variant slug. |

Mode is detected by Phase A from the user's phrasing. If ambiguous, Phase A asks.

## Output format (hard-refusal directive)

Phase C assembles a structured plain-text block — ASCII delimiters for
visual prominence; plain text so all LLMs read it uniformly:

```
═══════════════════════════════════════════════════════════════
  TEMPLATE DIRECTIVE — MUST FOLLOW
═══════════════════════════════════════════════════════════════

You are about to author content of type: <content-type>
Variant: <variant>
Destination: <destination>          (file path, gh pr, jira, slack, ...)
Template source: docs/templates/<content-type>/<variant>/template.md

RULES:
  1. You MUST follow the template structure below — section headings,
     order, and required fields are not negotiable.
  2. You MAY add placeholder text or fill in sections, but you MUST
     NOT remove or rename sections.
  3. If your content does not fit any section in the template, STOP
     and invoke content-template-gateway with intent "advise: I have
     content that doesn't fit" — do NOT improvise sections.
  4. You MUST author the content INTO the template before performing
     any destination-side action (writing the file, calling
     `gh pr create`, posting the ticket, sending the message, etc.).
     Do NOT call the destination first and patch later.
  5. If you proceed without this template, you are violating
     the project's "templates first" norm.

═══════════════════════════════════════════════════════════════
  TEMPLATE CONTENT — copy and fill in below
═══════════════════════════════════════════════════════════════

<full template.md content>

═══════════════════════════════════════════════════════════════
  RESEARCH NOTES — for your reference (not required reading)
═══════════════════════════════════════════════════════════════

<research.md content>
```

The `Destination:` line is the key v2 addition: it tells the consuming
agent where the finished content is going (a file path, a `gh pr`
invocation, a Jira ticket, a Slack message, etc.) so that the
template's wording / formatting choices can be tuned at fill-in time.
Rule 4 forbids the common anti-pattern of calling the destination
first (creating a PR with placeholder body, opening a ticket with a
TODO description) and patching later — the template must be filled
BEFORE the destination-side action.

## Storage layout

```
docs/templates/
├── <content-type>/
│   ├── README.md                  # variant index (table of available variants)
│   ├── <variant-1>/
│   │   ├── template.md            # the fill-in-the-blanks artifact
│   │   └── research.md            # sources + reasoning for this variant
│   └── <variant-2>/
│       ├── template.md
│       └── research.md
```

Every emitted file carries a `forge:` frontmatter block:

```yaml
---
forge:
  status: unreviewed         # unreviewed | reviewed
  forged: <ISO date>         # date the file was created / regenerated
  reviewed: null             # ISO date when user approved (null until then)
---
```

## Integration with project rules

This skill operationalizes a **"templates first"** norm — projects
that adopt it typically add a rule to their `AGENTS.md` (or equivalent
agent-instruction file) that says:

> Before drafting any structured agent-authored content (RFC, ADR,
> runbook, spec, plan, PR description, ticket, multi-paragraph commit
> message, Slack / email announcement, etc. — file or external),
> check `docs/templates/<content-type>/` for an existing template.
> If a template exists → use it. If it does not → invoke
> `content-template-gateway` to forge one, then use the resulting
> template.

The skill's description triggers auto-routing across Claude, Cursor,
Codex, Copilot, and Gemini when an agent encounters content-authoring
intent. The project-level rule reinforces the norm.

## Limitations

- **Probabilistic enforcement.** Cross-agent uniformity rules out
  hooks (only Claude Code supports them), so "hard refusal" is
  expressed as instructions in the skill body — agents *should*
  follow but the framework can't force them.
- **No project structure scaffolding.** This skill produces single
  templates for content. Directory-tree scaffolding (e.g., Python
  `uv` workspace) is a separate concern.
- **In-context research.** The research fallback chain loads results
  into the main agent context. May add tokens for repeated invocations.
  A future version may add subagent dispatch to keep main context clean.
- **No instantiation.** The skill returns a template + directive; the
  consuming agent is responsible for filling it in and performing the
  destination-side action.
- **No destination-native template integration.** The skill always uses
  `docs/templates/<content-type>/` as its single source of truth. It
  ignores destination-native templates (e.g., GitHub's
  `.github/PULL_REQUEST_TEMPLATE.md`, Jira's per-project templates).
  Drift between the gateway's template and the destination's native
  template is acceptable — ours is authoritative.

## Migration from v1 (`doc-template-gateway`)

The skill was previously named `doc-template-gateway` with a doc-file
framing. v2 reframes as `content-template-gateway` with a destination-
agnostic framing. There is **no backwards-compatibility shim** — the
old name simply ceases. Consumers re-run:

```bash
npx skills add bm629/agent-skills@content-template-gateway
```

See the v2 redesign spec in the consumer repo
(`docs/superpowers/content-template-gateway/spec/v2.md`) for
rationale and the resolved decisions behind the rename.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
