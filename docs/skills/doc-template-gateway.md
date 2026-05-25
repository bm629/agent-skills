# doc-template-gateway

> Gate for any document creation. Identifies doc-type + variant from
> intent via research, enforces template use via hard-refusal directive,
> forges templates when missing, advises on placing content that
> doesn't fit. Self-contained. Cross-agent uniform.

**Skill file:** [`skills/doc-template-gateway/SKILL.md`](../../skills/doc-template-gateway/SKILL.md)
**Version:** 1.0.0

## Purpose

This skill is the **canonical entry point** for any document creation
in a project. It catches doc-creation attempts by user or agent,
identifies the doc-type + variant via research, and either:

- **Returns an existing template** with a hard-refusal directive (you
  MUST follow this structure), or
- **Forges a new template** when none exists (research-backed
  workflow), then returns it under the same directive.

It also has an **advise mode** for the common case where the user's
content doesn't fit any section of the current template — it either
suggests placement, or proposes a new variant template with the
missing section.

The skill is fully self-contained: no declared skill dependencies.
The research workflow prefers a research-capable skill when one is
installed but falls back to built-in `WebSearch` + `WebFetch` so it
works in any environment.

## When to activate

- ✅ Anyone (user or agent) is about to create any document file
- ✅ User asks to re-forge an existing template (mode `force-regenerate`)
- ✅ User asks to add a new variant of an existing doc-type (mode `force-new-variant`)
- ✅ User says "advise: I have content that doesn't fit" — triggers Phase E
- ✅ User invokes the skill explicitly (e.g., `/doc-template-gateway`)

### When NOT to activate

- User wants project structure scaffolding (Python `uv` workspace, etc.) — different skill
- User wants to translate an existing template to another language or format — out of scope
- User wants to fill in a template with real content (instantiate it) — that's the consuming agent's job; this skill only returns the template + directive
- User is editing an already-drafted document for typos / formatting / clarity — the skill is for *new* doc creation, not editing
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
| **A. Identify** | Research user/agent intent → doc-type + variant + mode (`use-or-create` / `force-regenerate` / `force-new-variant`). Asks for more context if intent is ambiguous (up to 2 rounds). |
| **B. Check** | Classify `docs/templates/<doc-type>/<variant>/` as Complete / Missing / Orphan-partial. Branch on mode × state. |
| **C. Enforce** | Load template + research, assemble ASCII-bounded directive payload, return to caller. No prompts. |
| **D. Forge** (sub) | Sub-procedure: initial research → propose 2–4 variants → deep research per variant → emit `template.md` + `research.md` + parent `README.md`. Skipped variants leave no folder. |
| **E. Advise** (sub) | Sub-procedure: research how user's content typically fits this doc-type → return section-placement recommendations, OR propose a new variant template (which user can forge via Phase D). |

## Three invocation modes

| Mode | When | Behavior |
|---|---|---|
| `use-or-create` (default) | Normal doc creation | If template exists → Phase C. If missing → Phase D → Phase C. |
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

You are about to draft a document of type: <doc-type>
Variant: <variant>
Template source: docs/templates/<doc-type>/<variant>/template.md

RULES:
  1. You MUST follow the template structure below — section headings,
     order, and required fields are not negotiable.
  2. You MAY add placeholder text or fill in sections, but you MUST
     NOT remove or rename sections.
  3. If your content does not fit any section in the template, STOP
     and invoke doc-template-gateway with intent "advise: I have
     content that doesn't fit" — do NOT improvise sections.
  4. If you proceed without this template, you are violating
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

## Storage layout

```
docs/templates/
├── <doc-type>/
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

> Before drafting a new document, check `docs/templates/<doc-type>/`
> for an existing template. If a template exists → use it. If it
> does not → invoke `doc-template-gateway` to forge one, then use the
> resulting template.

The skill's description triggers auto-routing across Claude, Cursor,
Codex, Copilot, and Gemini when an agent encounters doc-creation
intent. The project-level rule reinforces the norm.

## Limitations (v1)

- **Probabilistic enforcement.** Cross-agent uniformity rules out
  hooks (only Claude Code supports them), so "hard refusal" is
  expressed as instructions in the skill body — agents *should*
  follow but the framework can't force them.
- **No project structure scaffolding.** This skill produces single-file
  templates for documents. Directory-tree scaffolding (e.g., Python
  `uv` workspace) is a separate concern.
- **In-context research.** The research fallback chain loads results
  into the main agent context. May add tokens for repeated invocations.
  v2 may add subagent dispatch to keep main context clean.
- **No instantiation.** The skill returns a template + directive; the
  consuming agent is responsible for filling it in.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
