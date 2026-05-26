---
name: content-template-gateway
description: >
  Use when anyone (user or agent) is about to author any structured
  content — RFC, ADR, runbook, spec, plan, PRD, README, retrospective,
  blog post, PR description, issue body, ticket, multi-paragraph commit
  message, announcement, or any other shape — regardless of destination
  (local file, GitHub, Jira, Linear, Slack, email, Confluence, Notion,
  Google Drive, etc.). This skill is the gate every content-authoring
  action passes through. It (1) identifies content-type + variant from
  intent via research, (2) checks docs/templates/<content-type>/<variant>/
  for an existing template, (3) if it exists, returns it plus a
  hard-refusal directive that you MUST follow, (4) if missing, forges
  a new one via research, then returns it under the same directive,
  (5) on "advise:" intent, helps place content that doesn't fit (maps
  to sections or proposes new variant). Modes: use-or-create (default),
  force-regenerate, force-new-variant. Self-contained: prefers a
  research-capable skill if available, else built-in WebSearch + WebFetch.

extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}

version: "2.0.0"
---

# Content Template Gateway

## Overview

`content-template-gateway` is the canonical entry point for any agent-authored structured content in this project — regardless of destination. Whenever a user or agent is about to author content that will land in any of these targets, this skill is invoked first:

- **Content-types** (template-driving): RFC, ADR, post-mortem, runbook, spec, plan, PRD, one-pager, roadmap, README, tutorial, release notes, retrospective, status report, meeting notes, resume, cover letter, blog post, GitHub PR description / issue body / PR-or-issue comment, Jira or Linear ticket, multi-paragraph commit message, Slack or email announcement, or any other structurally-templated shape.
- **Destinations** (orthogonal — the same content-type can land in any of these): local markdown file, GitHub (PR / issue / comment body via `gh ...`), Jira / Linear (API or web), Confluence, Notion, Google Drive, Slack, email, or any future system that accepts structured agent-authored prose. Content-type drives template choice; destination is incidental metadata carried into the Phase C directive.

The skill (a) **identifies** the content-type and variant from the user/agent's intent via research, (b) **checks** `docs/templates/<content-type>/<variant>/` for an existing template, (c) **enforces** template use via a hard-refusal directive if a template exists, (d) **forges** a new template (via a research-backed workflow) if none exists, and (e) **advises** on placing content that doesn't fit when the user asks.

The skill is self-contained: it prefers a research-capable skill when one is installed but falls back to built-in `WebSearch` + `WebFetch` so it works in any environment.

## When to activate

- **User asks to author any structured content** — for any destination. Primary trigger.
- **Agent is about to author structured content for any destination.** Even when the user did NOT explicitly request a template — if YOU (the agent) are about to perform any of the following, this skill activates first. This is just as required as the user-initiated trigger. Examples (non-exhaustive):
  - Write a new doc-shaped file: `temp-spec-*.md`, `temp-plan-*.md`, `docs/<type>/<name>.md`, README for a subdirectory, or any structurally-templated artifact.
  - Call `gh pr create`, `gh issue create`, `gh pr comment`, `gh issue comment` with a non-trivial body.
  - Create a Jira / Linear ticket or write its description body.
  - Compose a multi-paragraph `git commit` body.
  - Post a long-form Slack / email message; publish a Confluence / Notion page.
- User asks to **re-forge** an existing template (mode `force-regenerate`).
- User asks to **add a new variant** of an existing content-type (mode `force-new-variant`).
- User says "**advise:** I have content that doesn't fit" — triggers Phase E.
- User invokes the skill explicitly (e.g., `/content-template-gateway`).

**Do NOT activate when:**

- User wants project structure scaffolding (e.g., "create a Python `uv` workspace"). Different skill.
- User wants to translate an existing template to another language or format. Out of scope.
- User wants to fill in a template with real content (instantiate it). That's the consuming agent's job — this skill only returns the template + directive.
- User is editing already-authored content for typos / formatting / clarity. The skill is for *new* content authoring, not editing existing content.
- User explicitly says "I don't need a template — quick note." (Override case; not blocked but skill doesn't auto-fire.)
- Single-line / trivial content (one-line commit message, one-line Slack reply, terse code comment). The skill is for *structured* multi-section content.

## Workflow

### Phase A — Identify

**Inputs:**

- The user/agent's free-text intent (e.g., "I want to write a runbook for restarting the API", or "I'm about to `gh pr create` for the auth refactor").
- The **destination** hint (file path, `gh pr`, `gh issue`, `jira`, `linear`, `slack`, `commit-msg`, `confluence`, etc.). Inferred from intent wording or the imminent tool call; ask if unclear.
- Optional explicit mode hint (`use-or-create` default, `force-regenerate`, `force-new-variant`).
- Optional explicit content-type and/or variant override.

**Action sequence:**

1. **Detect mode from intent.** Set mode based on the user's wording:
   - `force-regenerate` triggers: "re-forge X", "regenerate the X template", "refresh X", "update the X template", "redo X".
   - `force-new-variant` triggers: "add a new variant", "create a variant called X", "new variant of Y called X".
   - Otherwise default to `use-or-create`.
2. **Research content-type + variant.** Use the fallback research chain: prefer `deep-research` skill (199-biotechnologies/claude-deep-research-skill — multi-source with credibility scoring + citation tracking) if active; else any other research-capable skill; else built-in `WebSearch` + `WebFetch`. (See `## Research methodology` for how to actually do the research.)
3. **Handle ambiguity.** If research returns 2–3 plausible content-type candidates, present them with one-line descriptions and let the user pick.
4. **Apply slug rules** to produce canonical `<content-type>` and `<variant>` slugs (lowercase-hyphens; strip content-type word from variant; truncate at 30 chars; reserved variant slugs `README`/`template`/`research`/`.*`/`_*`).
5. **Confirm slugs.** Show: *"I'll look for `docs/templates/<content-type>/<variant>/`. Confirm or rename."*

**Failure handling:** If Phase A cannot identify after research, ask for more context. Up to 2 rounds. Then abort with a `force-new-variant` mode hint.

**Output to Phase B:** `content-type` slug, `variant` slug, `mode`, `destination`.

### Phase B — Check

**Inputs from Phase A:** `content-type`, `variant`, `mode`, `destination`.

**Action sequence:**

1. **Classify** `docs/templates/<content-type>/<variant>/`:
   - **Complete** — both `template.md` and `research.md` exist.
   - **Missing** — folder does not exist.
   - **Orphan partial** — folder exists but `template.md` or `research.md` (or `forge:` frontmatter) is missing.
2. **Branch on mode + state:**

   | Mode | State | Next |
   |---|---|---|
   | `use-or-create` | Complete | → Phase C |
   | `use-or-create` | Missing | → Phase D, then C |
   | `use-or-create` | Orphan | → Orphan sub-menu (see below), then re-classify |
   | `force-regenerate` | Complete or Orphan | → Phase D (overwriting), then C |
   | `force-regenerate` | Missing | → Phase D, then C |
   | `force-new-variant` | Complete | → Slug collision; ask for different slug, re-enter B |
   | `force-new-variant` | Missing | → Phase D, then C |
   | `force-new-variant` | Orphan | → Orphan sub-menu first, then re-classify |

**Orphan sub-menu (referenced from the table above):**

For each orphan variant folder detected, prompt the user:

> Partial variant folder detected: `<content-type>/<slug>` (missing: `template.md` and/or `research.md` and/or `forge:` frontmatter).
> What would you like to do?
>   1. Regenerate it (re-run Phase D for this slug)
>   2. Delete it
>   3. Leave alone (skip; surface again next run)

Apply the choice, then re-classify the folder and continue per the branch table.

**Output to Phase C or D:** validated `content-type`, `variant`, `destination`, and a `should_forge` flag.

### Phase C — Enforce

**Inputs:** validated `content-type`, `variant`, `destination`. The template files exist at `docs/templates/<content-type>/<variant>/`.

**Action sequence:**

1. **Load** `template.md` and `research.md`.
2. **Assemble the return payload:**

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

3. **Return the assembled payload** to the caller.

No user prompts. Pure output assembly.

### Phase D — Forge (sub-procedure)

**Invoked from:** Phase B (Missing or Orphan-resolved), or directly when mode is `force-regenerate` / `force-new-variant`.

**Action sequence:**

1. **Initial content-type research** via fallback chain. (See `## Research methodology` for how.)
2. **Propose variants.** Skip this step entirely when mode is `force-regenerate` or `force-new-variant` — the variant is already named in Phase A's output. Otherwise (mode = `use-or-create`), present 2–4 candidates with one-line descriptions and auto-derived slugs. User accepts the list / edits it / asks for a fresh research pass.
3. **Deep research per variant.** Re-invoke fallback chain with variant's narrower scope. (See `## Research methodology`.) On failure: retry once → sub-menu (retry / skip / cancel).
4. **Emit artifacts** (in this order):
   1. For each variant: write `template.md` then `research.md` into `docs/templates/<content-type>/<variant>/`. Both carry `forge:` frontmatter (`status: unreviewed`, `forged: <YYYY-MM-DD>`, `reviewed: null`).
   2. After ALL variants are written, update `docs/templates/<content-type>/README.md` as the variant index.
   3. Skipped variants leave no folder and are excluded from `README.md`.
5. **Print end-of-forge summary** to the caller in this format:

   ```
   Forge complete for `<content-type>`.

   Emitted:
     • <variant-1>  (docs/templates/<content-type>/<variant-1>/)
     • <variant-2>  (docs/templates/<content-type>/<variant-2>/)

   Skipped (research failed):
     • <variant-3> — retry by re-invoking with mode `force-new-variant`
   ```

   The "Skipped" block is omitted entirely if all variants succeeded.

**Output to Phase C:** the `content-type` + `variant` of the template the caller asked for.

### Phase E — Advise (sub-procedure)

**Invoked from:** Phase A when intent matches an "advise:" pattern.

**Inputs:** `content-type` and `variant` of the currently-enforced template, plus user's content that doesn't fit.

**Action sequence:**

1. **Load** the current `template.md` and `research.md`.
2. **Research placement** via fallback chain — how is this kind of content typically placed for this content-type? (See `## Research methodology`.)
3. **Decide & branch:**
   - **Fits within existing variant** → return placement recommendations (paragraph N → `## SectionName`).
   - **Does not fit** → propose a new variant with the missing section. Ask user: yes (invoke Phase D for the new variant) / no (return best-effort placement to the existing variant) / refine (user describes what to change about the proposal; up to 2 refinement rounds, then accept the best version or abort with a placement-recommendation fallback).

**Output:** either placement recommendations (plain text) or a new template + directive (via Phase D → Phase C).

## Research methodology

All research calls (Phase A; Phase D Steps 1 and 3; Phase E) follow this methodology.

### Goal per research call

- **Phase A — Identify.** "What content-type is this? What variants exist? Which variant best matches the user's intent?"
- **Phase D Step 1 — Initial.** "What is this content-type in general? Canonical examples?"
- **Phase D Step 3 — Per-variant deep.** "For THIS specific variant, what sections / structure does it conventionally have?"
- **Phase E — Placement.** "For this content in the context of this template, where does it conventionally go, or does it require a new variant?"

### Source-quality tiers (prefer top of list)

1. **Official / canonical references** — original specifications (e.g., Michael Nygard's ADR post for ADRs), official documentation, language/framework reference docs, destination-platform docs (GitHub's PR template guidance, Atlassian's Jira ticket guides).
2. **Multiple corroborating engineering blogs** — well-established sources like Google SRE Book, Atlassian Handbook, GitLab docs, well-known company engineering blogs.
3. **Single reputable source** — usable, but mark as single-source in `research.md`.
4. **Avoid** — individual Stack Overflow answers (without corroboration), AI-generated content farms, individual tutorials with no provenance.

### Query pattern (broad → narrow)

1. **Broad:** "what is a `<content-type>`" — confirm the high-level shape.
2. **Structure:** "`<content-type>` template / sections / structure"
3. **Variants:** "`<content-type>` variants / types"
4. **Examples:** "`<content-type>` example" — verify proposed sections appear in real instances.

### Minimum sources before declaring a section "canonical"

- **2+ independent sources** must include a section before treating it as canonical for the variant.
- **1 source only** → include in template but mark the section in `research.md` as "single-source; verify before relying on it."
- **Contradictory sources** → present both interpretations in `research.md`; pick based on user's likely context, or ask the user.

### Verification checks before emitting

- [ ] Every section in the proposed `template.md` appears in at least 2 real-world examples for that variant.
- [ ] Variants are meaningfully distinct — if two proposed variants have 90%+ section overlap, they're not really different variants (merge or rename).
- [ ] Section names use common terminology (don't invent new names).

### Stop criteria

- 2–3 sources agree on the structural shape → enough.
- New queries return content already seen → stop.
- Token / time budget reached → stop and commit to best-effort; flag in `research.md`.

## Rules

**Hard rules (never violate):**

- Never return a template without the hard-refusal directive.
- Never overwrite an existing template file outside Phase D and outside `force-regenerate` or `force-new-variant` mode.
- Never declare a skill dependency. The skill is self-contained; the research fallback chain is a runtime preference.
- Never enumerate trigger commands in the SKILL.md body beyond example illustration. The `When to activate` list is illustrative, not closed — agents apply the underlying principle ("structured agent-authored content for any destination") to any new tool / API / system.

**Preferences (override-able by user choice):**

- Prefer `deep-research` skill (199-biotechnologies/claude-deep-research-skill) if available (fallback order).
- Prefer skip-on-failure over abort-on-failure in Phase D.
- Prefer immediate cancellation without confirmation.

## Output

The skill returns one of:

1. **Phase C payload** — assembled directive + template + research, ASCII-bounded. Returned for any successful `use-or-create` / `force-regenerate` / `force-new-variant` / Phase-E-new-variant path.
2. **Phase E placement recommendations** — plain-text section-mapping. Returned when Phase E's research determines content fits within the existing variant.
3. **Abort signal** — plain-text reason. Returned when user cancels or Phase A exhausts its 2 context-gathering rounds.

Side effects on disk:

- Phase D writes `template.md`, `research.md`, and `README.md` under `docs/templates/<content-type>/`.
- No other phase writes to disk.
- The skill never writes to external destinations (files outside `docs/templates/`, GitHub, Jira, Slack, etc.). The caller performs the destination-side action AFTER receiving the Phase C payload.

## Progressive disclosure

The skill body is fully self-contained.

Future additions may include:

- `references/forge-research-prompts.md` — canned research prompts for common content-types.
- `assets/directive-template.txt` — the ASCII-bounded directive template.
- `scripts/check-orphans.sh` — helper for Phase B orphan classification.

## Related

- Related skills (not invoked by `content-template-gateway`, but adjacent): `deep-research`, `writing-skills`, `brainstorming`, `external-content-sanitizer`.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap)
- Body ≤ ~500 lines / 5,000 tokens — Claude keeps it in context every turn
- Hard ceiling 30,000 chars (Copilot custom-agent limit when re-rendered as agent)
