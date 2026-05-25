---
name: doc-template-gateway
description: >
  Use when anyone (user or agent) is about to create any document —
  engineering (RFC, ADR, runbook, spec, plan), product/business (PRD,
  roadmap), user-facing (README, tutorial), recurring (retrospective,
  meeting notes), personal (resume, blog post), or any other shape.
  This skill is the gate every doc creation passes through. It (1)
  identifies doc-type + variant from your intent via research, (2)
  checks docs/templates/<doc-type>/<variant>/ for an existing template,
  (3) if it exists, returns it plus a hard-refusal directive that you
  MUST follow, (4) if missing, forges a new one via research, then
  returns it under the same directive, (5) on "advise:" intent, helps
  place content that doesn't fit (maps to sections or proposes new
  variant). Modes: use-or-create (default), force-regenerate,
  force-new-variant. Self-contained: prefers a research-capable skill
  if available, else built-in WebSearch + WebFetch.

extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}

version: "1.0.0"
---

# Doc Template Gateway

## Overview

`doc-template-gateway` is the canonical entry point for any document creation in this project. Whenever a user or agent is about to create any document — engineering docs (RFC, ADR, post-mortem, runbook, spec, plan); product/business docs (PRD, one-pager, roadmap); user-facing docs (README, tutorial, release notes); recurring docs (retrospective, status report, meeting notes); personal docs (resume, cover letter, blog post); or any other shape — this skill is invoked first.

The skill (a) **identifies** the doc-type and variant from the user/agent's intent via research, (b) **checks** `docs/templates/<doc-type>/<variant>/` for an existing template, (c) **enforces** template use via a hard-refusal directive if a template exists, (d) **forges** a new template (via a research-backed workflow) if none exists, and (e) **advises** on placing content that doesn't fit when the user asks.

The skill is self-contained: it prefers a research-capable skill when one is installed but falls back to built-in `WebSearch` + `WebFetch` so it works in any environment.

## When to activate

- Anyone (user or agent) is about to create any document file. This is the primary trigger.
- User asks to **re-forge** an existing template (mode `force-regenerate`).
- User asks to **add a new variant** of an existing doc-type (mode `force-new-variant`).
- User says "**advise:** I have content that doesn't fit" — triggers Phase E.
- User invokes the skill explicitly (e.g., `/doc-template-gateway`).

**Do NOT activate when:**

- User wants project structure scaffolding (e.g., "create a Python `uv` workspace"). Different skill.
- User wants to translate an existing template to another language or format. Out of scope.
- User wants to fill in a template with real content (instantiate it). That's the consuming agent's job — this skill only returns the template + directive.
- User is editing an already-drafted document for typos / formatting / clarity. The skill is for *new* doc creation, not editing existing docs.
- User explicitly says "I don't need a template — quick note." (Override case; not blocked but skill doesn't auto-fire.)

## Workflow

### Phase A — Identify

**Inputs:**

- The user/agent's free-text intent (e.g., "I want to write a runbook for restarting the API").
- Optional explicit mode hint (`use-or-create` default, `force-regenerate`, `force-new-variant`).
- Optional explicit doc-type and/or variant override.

**Action sequence:**

1. **Detect mode from intent.** If the user's wording matches a force-regenerate or force-new-variant pattern, set the mode accordingly. Otherwise default to `use-or-create`.
2. **Research doc-type + variant.** Use the fallback research chain: prefer `research-synthesis` skill if active; else any other research-capable skill; else built-in `WebSearch` + `WebFetch`.
3. **Handle ambiguity.** If research returns 2–3 plausible doc-type candidates, present them with one-line descriptions and let the user pick.
4. **Apply slug rules** to produce canonical `<doc-type>` and `<variant>` slugs (lowercase-hyphens; strip doc-type word from variant; truncate at 30 chars; reserved slugs `README`/`template`/`research`/`.*`/`_*`).
5. **Confirm slugs.** Show: *"I'll look for `docs/templates/<doc-type>/<variant>/`. Confirm or rename."*

**Failure handling:** If Phase A cannot identify after research, ask for more context. Up to 2 rounds. Then abort with a `force-new-variant` mode hint.

**Output to Phase B:** `doc-type` slug, `variant` slug, `mode`.

### Phase B — Check

**Inputs from Phase A:** `doc-type`, `variant`, `mode`.

**Action sequence:**

1. **Classify** `docs/templates/<doc-type>/<variant>/`:
   - **Complete** — both `template.md` and `research.md` exist.
   - **Missing** — folder does not exist.
   - **Orphan partial** — folder exists but `template.md` or `research.md` (or `forge:` frontmatter) is missing.
2. **Branch on mode + state:**

   | Mode | State | Next |
   |---|---|---|
   | `use-or-create` | Complete | → Phase C |
   | `use-or-create` | Missing | → Phase D, then C |
   | `use-or-create` | Orphan | → Sub-menu (regen/delete/leave), then re-classify |
   | `force-regenerate` | Complete or Orphan | → Phase D (overwriting), then C |
   | `force-regenerate` | Missing | → Phase D, then C |
   | `force-new-variant` | Complete | → Slug collision; ask for different slug, re-enter B |
   | `force-new-variant` | Missing | → Phase D, then C |
   | `force-new-variant` | Orphan | → Sub-menu first, then re-classify |

**Output to Phase C or D:** validated `doc-type`, `variant`, and a `should_forge` flag.

### Phase C — Enforce

**Inputs:** validated `doc-type`, `variant`. The template files exist at `docs/templates/<doc-type>/<variant>/`.

**Action sequence:**

1. **Load** `template.md` and `research.md`.
2. **Assemble the return payload:**

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

3. **Return the assembled payload** to the caller.

No user prompts. Pure output assembly.

### Phase D — Forge (sub-procedure)

**Invoked from:** Phase B (Missing or Orphan-resolved), or directly when mode is `force-regenerate` / `force-new-variant`.

**Action sequence:**

1. **Initial doc-type research** via fallback chain.
2. **Propose variants** (only when no specific variant was named). Present 2–4 candidates with one-line descriptions and auto-derived slugs. User accepts/edits/redos.
3. **Deep research per variant.** Re-invoke fallback chain with variant's narrower scope. On failure: retry once → sub-menu (retry/skip/cancel).
4. **Emit artifacts:**
   - Write `template.md` then `research.md` into `docs/templates/<doc-type>/<variant>/`. Both carry `forge:` frontmatter (`status: unreviewed`, `forged: <ISO date>`, `reviewed: null`).
   - Update `docs/templates/<doc-type>/README.md` as the variant index.
   - Skipped variants leave no folder.
5. **Print end-of-forge summary** listing emitted + skipped variants.

**Output to Phase C:** the `doc-type` + `variant` of the template the caller asked for.

### Phase E — Advise (sub-procedure)

**Invoked from:** Phase A when intent matches an "advise:" pattern.

**Inputs:** `doc-type` and `variant` of the currently-enforced template, plus user's content that doesn't fit.

**Action sequence:**

1. **Load** the current `template.md` and `research.md`.
2. **Research placement** via fallback chain — how is this kind of content typically placed for this doc-type?
3. **Decide & branch:**
   - **Fits within existing variant** → return placement recommendations (paragraph N → `## SectionName`).
   - **Does not fit** → propose a new variant with the missing section. Ask user: yes (invoke Phase D for the new variant) / no (return best-effort placement) / refine (retry up to 2 rounds).

**Output:** either placement recommendations (plain text) or a new template + directive (via Phase D → Phase C).

## Rules

**Hard rules (never violate):**

- Never return a template without the hard-refusal directive.
- Never overwrite an existing template file outside Phase D and outside `force-regenerate` or `force-new-variant` mode.
- Never declare a skill dependency. The skill is self-contained; the research fallback chain is a runtime preference.

**Preferences (override-able by user choice):**

- Prefer `research-synthesis` if available (fallback order).
- Prefer skip-on-failure over abort-on-failure in Phase D.
- Prefer immediate cancellation without confirmation.

## Output

The skill returns one of:

1. **Phase C payload** — assembled directive + template + research, ASCII-bounded. Returned for any successful `use-or-create` / `force-regenerate` / `force-new-variant` / Phase-E-new-variant path.
2. **Phase E placement recommendations** — plain-text section-mapping. Returned when Phase E's research determines content fits within the existing variant.
3. **Abort signal** — plain-text reason. Returned when user cancels or Phase A exhausts its 2 context-gathering rounds.

Side effects on disk:

- Phase D writes `template.md`, `research.md`, and `README.md` under `docs/templates/<doc-type>/`.
- No other phase writes to disk.

## Progressive disclosure

v1 has no subfolders. The skill body is fully self-contained.

Future v2+ additions may include:

- `references/forge-research-prompts.md` — canned research prompts for common doc-types.
- `assets/directive-template.txt` — the ASCII-bounded directive template.
- `scripts/check-orphans.sh` — helper for Phase B orphan classification.

## Related

- `docs/templates/skill-template.md` — the SKILL.md template this skill follows (standard variant).
- `AGENTS.md` §11 — project-wide "templates first" norm that this skill operationalizes.
- `AGENTS.md` §5 — external content safety norm that governs sanitization of web-sourced research.
- Related skills (not invoked by `doc-template-gateway`, but adjacent): `research-synthesis`, `writing-skills`, `brainstorming`, `external-content-sanitizer`.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap)
- Body ≤ ~500 lines / 5,000 tokens — Claude keeps it in context every turn
- Hard ceiling 30,000 chars (Copilot custom-agent limit when re-rendered as agent)
