# authoring-prd

Author a **comprehensive, plannable Product Requirements Document** from a product idea — the *method* and the *quality bar*, not the section list. Composes with a separate PRD template tool (which owns the structure) and a deep-research capability (to ground each section). Produce-side only: it writes PRDs, it does not review them or author other document types.

## Purpose

A template gives you a PRD's skeleton; it does not tell you how to fill it *well*. This skill is the how-to layer: how to ground the problem in evidence, define success metrics that are actually measurable, draw a defensible MVP boundary, write requirements + acceptance criteria an engineer can build to, and surface risks/open questions — to a bar from which the downstream build can be **planned** (milestones and tasks derivable from the doc). It assumes the producer is handed a product idea (and any upstream context) and **elaborates** it; it never produces generic boilerplate, and it never fabricates evidence to look grounded.

## When to activate

- ✅ Authoring a new PRD from a product idea or brief.
- ✅ Expanding a thin idea into a comprehensive requirements doc (a product or a substantial feature).
- ✅ **Amending an existing PRD** as a versioned, changelogged delta (a new/changed requirement, a scope shift).
- ✅ Filling a PRD template with researched, decision-complete content.

### When NOT to activate

- **Reviewing/grading a finished PRD** → use a PRD-review skill.
- **Authoring a different document type** (architecture doc, runbook, wireframes) → use that type's skill.
- A one-line note or a trivial change that needs no requirements doc.

## Workflow

1. **Take the structure from the template tool** — get the section set from a PRD template (comprehensive variant); do not invent or restate an outline. This skill supplies the method that fills those sections.
2. **Load the idea + context; discover gaps; commit to elaborating it** — before drafting, fill knowledge gaps (problem, metrics, users, constraints); tie every section to *this* idea; make thin-idea assumptions explicit, or raise the thin-idea blocker if the problem can't even be credibly assumed.
3. **Research to ground each section** — a deep-research pass grounds the problem/users/market/metric baselines. If no research capability is available, flag assumptions and list them under "validate before build" — never fabricate evidence or citations.
4. **Apply the per-section method** — problem *evidenced* (not asserted); 2–4 measurable success metrics each with a target + measurement method, defined before building, with a guardrail/counter-metric where the headline metric is gameable; explicit MVP vs out-of-scope/non-goals + release criteria; functional + a non-functional taxonomy with numeric targets; user stories with checkable acceptance criteria; a traceable problem→goal→metric→feature→AC chain; named dependencies; risks + a pre-mortem; jargon-free, no vague adjectives standing in for requirements.
5. **Self-check against the plannability bar** before handing off (below).
6. **Amend an existing PRD as a versioned delta** (when iterating) — scope the change, edit in place (don't regenerate), bump the doc version + add a changelog entry, mark superseded content, and analyze the downstream ripple.

## The plannability quality bar

A PRD is "good" when the build can be planned from it. The 12 conditions: (1) evidenced problem (framed as a job); (2) defined users; (3) measurable success metrics, with a guardrail where the headline metric is gameable; (4) defensible MVP boundary with non-goals; (5) concrete features + acceptance criteria specific enough to derive milestones; (6) grounded, not assumed (no fabrication; thin-idea assumptions flagged; too-thin → blocker); (7) risks, dependencies-context + open questions surfaced; (8) clear, unambiguous, no vague adjectives; (9) an NFR taxonomy with a numeric/checkable target per load-bearing category; (10) a traceable chain (no orphan feature; every goal has a feature; metrics tie to goals; stories have AC); (11) dependencies named; (12) amend integrity when amending. The companion `reviewing-prd` skill asserts the same 12-condition bar, so author and reviewer stay aligned.

## Output

A **comprehensive PRD** that meets the plannability bar, written into the template tool's section structure. The abstract consumer is the downstream planning stage (which derives milestones/tasks) and a reviewer (which asserts the same bar). The skill supplies the *content quality*; the template tool owns the *structure*.

## Key guarantees

- **Composes, never restates** — structure comes from the template tool; this skill is the method.
- **Never fabricates evidence** — no invented statistics or citations; honest flagged assumptions instead.
- **Plannable or not done** — won't hand off a PRD an engineer can't derive milestones from.
- **Elaborates the idea** — content traces to the given idea, never generic boilerplate.
- **Measurable, unambiguous** — metrics have targets + methods; vague adjectives are replaced with benchmarks.
- **Amends, doesn't rewrite** — on a change to an existing PRD, edits in place + versions + changelogs; never silently regenerates.

## Limitations

- "Comprehensive" sets the output ambition; the skill keeps it proportional — a thin idea collapses sections it doesn't need (completeness of decisions, not word count).
- It authors the PRD; deciding *which* documents a project needs is a separate discovery concern, and the section structure is owned by a template skill (e.g. `content-template-gateway`).
- It is produce-side; judging a finished PRD is a separate review skill.

## License

MIT © 2026 Bhushan Modi.
