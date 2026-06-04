---
name: authoring-user-guide
description: >
  Use when authoring an end-user guide — the consumer-facing help the (typically
  non-technical) person USING a product reads to accomplish their goals: a
  getting-started tutorial, task-oriented how-to guides, conceptual explanation, an
  end-user feature/configuration reference (features, settings, CLI commands — not the
  HTTP API), and troubleshooting/FAQ. Guides the METHOD, not the outline: deriving one
  how-to per user goal from the handed-in upstreams (never inventing steps), keeping the
  four Diataxis modes distinct, and holding every step accurate to the actual product
  behavior. Composes with a separate user-guide template tool (which supplies the section
  structure) and a research capability. Assumes the handed-in upstream docs (typically a
  feature-spec + user-flows + wireframes) — never a blank page. Not for the developer-tool
  adoption narrative (a separate developer-guide), not for the HTTP/SDK endpoint catalog (a
  separate api-reference), and not for reviewing a finished user guide.
extensions:
  claude:
    when_to_use: "authoring an end-user user guide for a product from its upstream docs"
    argument-hint: "<the upstream docs (feature-spec + user-flows + wireframes) to base the guide on>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `authoring-user-guide` — SKILL.md

> **Variant:** standard · **When to use:** a producer is authoring the end-user guide
> for a product and needs the Diataxis-keyed authoring method + the usability/accuracy
> bar, composing the section structure from a separate template tool.

## Overview

This skill guides authoring an **end-user user guide**: the help a real person uses to
accomplish their goals with a product. It carries the *judgment* — how to derive one
how-to per user goal from the upstream docs instead of inventing steps, how to keep the
four Diataxis documentation modes distinct (mixing them is the most common cause of
confusing docs), how to hold every step accurate to what the product actually does — not
a section list, which comes from a template tool. The audience is the (typically
non-technical) **end user**, not a developer integrating a tool: a developer-tool's
adoption/integration narrative is a separate `authoring-developer-guide`, and the
HTTP/SDK endpoint catalog is a separate `authoring-api-reference`. This guide's
"reference" mode is the end-user **product** reference (features, settings, CLI
commands), not the API. The guide sits downstream of the product/behavior docs it
describes, and is checked against a usability/accuracy bar by `reviewing-user-guide`.

## When to activate

- Authoring an end-user / customer-facing user guide, help center, or product manual for
  a product, given its upstream docs (typically a feature-spec + user-flows + wireframes).
- Producing the full end-user documentation set — getting-started tutorial, task how-to
  guides, conceptual explanation, an end-user feature/config reference, troubleshooting/
  FAQ, and a glossary — so a real user can accomplish every supported goal.

**Do NOT activate when:**

- Reviewing/judging a finished user guide — that is the review-side gate
  (`reviewing-user-guide`), which asserts the same bar this skill produces to.
- Authoring the developer-tool adoption/integration/onboarding narrative for a library,
  SDK, CLI, framework, or API platform — that is `authoring-developer-guide`.
- Authoring the HTTP/SDK endpoint catalog (the per-endpoint wire contract for integrators)
  — that is `authoring-api-reference`. This skill's reference mode is the end-user product
  surface, not the API.
- Authoring the internal engineering docs (feature-spec, data-model, architecture) — the
  user guide is the external help derived from those, not the contract itself.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents
discovery determined inform this one) — and trace each how-to and section back to them.
The typical upstreams are the **feature-spec** (the behaviors the guide explains), the
**user-flows** (the task paths each how-to walks), and the **wireframes** (the screens the
steps reference); where present, also the **PRD** (what/why), the **design-system** (UI
terminology), and the **api-reference** (for a developer product). Do not assume a fixed
input: that list is method guidance, not a cap on what you receive — **never hardcode a
single narrow input.**

Be **self-contained and graceful** — produce the guide from *whatever* context you
actually receive. When an expected informing document is absent (e.g. no wireframes), proceed
on what you have and surface the gap as an **explicit assumption**; never fabricate a
feature, setting, screen, or step to fill it. And **use a research capability where one is
available** (the `deep-research` capability, else web search) to make the guide
comprehensive — grounding it in established end-user-docs practice (Diataxis, task-oriented
minimalism, a reputable docs style guide), not merely to fill the template.

## Workflow

> **Compose with the template tool first.** Before drafting, obtain the user-guide section
> structure from the content-template tool (the `content-template-gateway` capability, or
> whatever template provider is installed). It supplies the section slots — introduction/
> overview, getting-started tutorial, how-to guides, conceptual explanation, feature/config
> reference, troubleshooting/FAQ, glossary. **Never hardcode a competing outline** — this
> skill fills the template's slots with derived content; it does not redefine them. Use a
> research capability (the `deep-research` capability, else web search) to ground any docs
> conventions you are unsure of.

### Step 1: Enumerate the user goals — one how-to per goal, no orphans

List the user goals from the handed-in upstreams: from the **user-flows** when present
(each flow is a user goal/job), else from the **feature-spec / PRD**. Produce exactly **one
task-oriented how-to per goal** — every goal gets a how-to, every how-to traces back to a
goal. This is the no-orphan coverage rule, and it degrades gracefully: do not assume
user-flows was handed in; take the goals from whatever upstream actually arrived.

### Step 2: Write the getting-started tutorial as one guaranteed happy path

The tutorial is a single learn-by-doing lesson: ONE path, no choices or alternatives,
every step yields a visible result, and success is the author's responsibility. Defer the
"why" to the explanation section and push every failure branch to troubleshooting — a
tutorial that forks or fails is not a tutorial. Pick the first meaningful success the new
user can reach.

### Step 3: Write each how-to as imperative numbered steps — not a concept dump

Each how-to addresses an already-oriented user with one goal. Title it as the task
(bare-infinitive, task-based heading). Write it per established docs-style mechanics:
**numbered steps, one action per step** (split a step that runs long), **second person,
present tense, imperative/active voice**. Cover the happy path and point to troubleshooting
for failures. A how-to written as prose or as a concept explanation is the single most
common Diataxis defect — keep it steps.

### Step 4: Write the explanation with no steps, and the reference complete

- **Explanation** provides the mental model and the "why"; it contains **no steps** and
  cross-links to the how-to/reference that act on the concepts. Keep it to concepts the
  user genuinely needs, not a tour of internal architecture.
- **Feature/config reference** is neutral, factual, and **complete** over the end-user
  product surface — every feature, setting, and CLI command/shortcut. It **describes, does
  not instruct**, and its structure **mirrors the product** so the user can navigate both
  together. This is the product reference, NOT the HTTP API endpoint catalog.

### Step 5: Source troubleshooting from the known error states

Build the troubleshooting catalog from the **user-flows' error/recovery paths** and the
**feature-spec's error handling** — every known error state becomes an entry. Organize by
the user-visible **symptom** (not the internal cause); each entry is symptom -> cause ->
fix. Add an FAQ for recurring questions and a "get more help" pointer. This is where the
failure content the tutorial and how-tos deliberately omit lives.

### Step 6: Describe screens textually, reference the wireframes and design-system terms

The artifact is markdown text: describe each screen **in words and link the wireframe**
rather than embedding a screenshot. Use the **design-system's** component and term names
where one exists, so the guide's vocabulary matches the product's. Keep command/config
content in fenced snippets.

### Step 7: Trace every step to a behavior; surface gaps as assumptions

Trace each procedural step to a feature-spec behavior (or another handed-in upstream).
Where an upstream was thin or absent, state the **assumption** you made (so a reviewer can
challenge it) and list unresolved unknowns as **open questions** — never invent a feature,
setting, or step and bury it in a procedure.

### Step 8: Self-check against the usability/accuracy bar (below) before handoff

Run the quality bar. Fix every miss before handing the guide to review.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** The section structure comes from the template tool; this
  skill never ships a competing outline.
- **Derive, don't invent.** Every step traces to a handed-in upstream behavior; surface a
  missing upstream as an explicit assumption, never fabricate to fill it.
- **One how-to per goal — no orphans.** Every user goal in the handed-in upstreams has a
  how-to; goals come from the user-flows when present, else the feature-spec/PRD.
- **Keep the four Diataxis modes distinct.** Tutorial, how-to, explanation, reference are
  separate and correctly typed; never conflate them (no how-to as a concept dump, no
  explanation buried in a tutorial).
- **End-user audience + product reference.** The guide is for the end user; the reference
  is the product surface (features/settings/commands), not the HTTP/SDK API.

**Preferences (override-able):**

- Procedure mechanics: numbered steps, one action per step, second person, present tense,
  imperative voice, task-based headings.
- Task-oriented minimalism — action-first, anchored in the user's real tasks; cut anything
  that does not serve the task.
- Proportion the guide to the product's goal/feature set — neither pad nor truncate.

## Gotchas

- **How-to written as a concept dump.** It looks thorough but buries the steps the user
  came for. A how-to is imperative numbered steps; the "why" belongs in explanation.
- **Tutorial that forks or can fail.** A getting-started lesson with branches or a failure
  path is not a tutorial — it is a how-to or troubleshooting in disguise. One guaranteed
  happy path; push failures to troubleshooting.
- **Incomplete reference.** Skipping the settings/commands that "seem obvious" leaves the
  user unable to look things up. The reference must cover the whole product surface.
- **Fabricated steps from a thin upstream.** When an upstream is missing, inventing a step
  that the product may not actually do is a hidden defect. Surface the gap as an
  assumption instead.
- **Embedding screenshots.** The markdown medium has no binary assets — describe the screen
  in words and link the wireframe. Real screenshots are a future-backend concern, not this
  artifact.
- **Confusing the reference with the API catalog.** The end-user feature/config reference
  is NOT the HTTP/SDK endpoint reference (`authoring-api-reference`); do not pull endpoint
  contracts in here.

## Anti-patterns

- **"I'll bake the section list into the doc myself."** That duplicates the template and
  drifts from it. Always compose the structure from the template tool.
- **"One big walkthrough covers everything."** Collapsing tutorial + how-to + explanation
  + reference into one narrative is the #1 cause of confusing docs. Keep the modes
  distinct.
- **"The upstream didn't say, so I'll just describe what it probably does."** Silent
  invented behavior belongs in the assumptions/open-questions surface, not in a procedure.
- **"This is a developer tool, so I'll write the integration/onboarding narrative here."**
  That is `authoring-developer-guide`; this skill is the end-user product help.
- **"I'll embed the API endpoint table as the reference."** The reference is the product
  surface; the endpoint catalog is `authoring-api-reference`.

## Usability / accuracy quality bar

A user guide is **complete + usable + accurate** when ALL hold (this is the same bar the
review-side gate asserts):

1. **Goal coverage — one how-to per goal, no orphans.** Every user goal in the handed-in
   upstreams (user-flows when present, else feature-spec/PRD) has exactly one how-to; every
   how-to traces to a goal.
2. **Four Diataxis modes present AND correctly typed.** Tutorial, how-to, explanation, and
   reference are all present and not conflated — tutorial is one guaranteed path, how-to is
   imperative steps (not a concept dump), explanation has no steps, reference is neutral and
   complete.
3. **Feature/config reference complete.** Every user-facing feature, setting, and CLI
   command/shortcut is documented; the reference mirrors the product. (Product surface, not
   the HTTP API.)
4. **Steps accurate to the actual product behavior.** Every step matches a handed-in
   upstream behavior; no invented step, setting, or screen.
5. **Procedure mechanics sound.** Numbered steps, one action per step, second person,
   present tense, imperative voice, task-based headings.
6. **Troubleshooting covers the known error states.** Every error/recovery path from the
   upstreams appears as a symptom -> cause -> fix entry; recurring questions are in the FAQ;
   a "get more help" pointer exists.
7. **Usable by the target user.** A real user could accomplish every supported goal from
   the guide alone; language suits the audience; screens are described and wireframe-linked.
8. **Assumptions/gaps surfaced.** Where an upstream was absent or thin, the assumptions are
   stated (challengeable), not silently invented.

## Output

An end-user user guide in markdown, composed onto the template tool's structure: an
introduction/overview, a getting-started tutorial (one guaranteed happy path), one
task-oriented how-to per user goal (imperative numbered steps), a conceptual explanation
(no steps), an end-user feature/configuration reference (the product surface — features,
settings, CLI commands — not the HTTP API), a troubleshooting/FAQ sourced from the known
error states, a glossary, and an assumptions/open-questions surface. Screens are described
in words with wireframe links; commands/config are fenced snippets. The artifact is consumed
by the review-side gate (which judges it against the usability/accuracy bar above) and,
ultimately, by a real user accomplishing every supported goal. The method + bar are
medium-independent: a future docs-platform or screenshot-rich backend changes only the
rendering (how screens are shown), not the derivation or the bar.

## Related

- **Template provider** (`content-template-gateway` capability) — supplies the user-guide
  section structure this skill composes onto; never duplicated here.
- **Research capability** (`deep-research`, else web search) — grounds the docs conventions
  (Diataxis, minimalism, the style guide) and the derivation evidence.
- **Upstream input — the handed-in `depends_on` set.** Typically a feature-spec +
  user-flows + wireframes (plus PRD/design-system/api-reference where present). Never
  authored from a blank page.
- **`reviewing-user-guide`** — the review-side gate that asserts the same usability/accuracy
  bar; produce-side and review-side are single-sourced.
- **`authoring-developer-guide`** — the sibling for the developer-tool adoption/integration
  narrative; this skill is the end-user product help, distinct from it.
- **`authoring-api-reference`** — the sibling for the HTTP/SDK endpoint catalog; this
  skill's reference mode is the end-user product surface, distinct from it.

## Progressive disclosure

- `references/sources.md` — research provenance for the section set, the Diataxis-keyed
  authoring method, and the usability/accuracy bar. Load when verifying a claim's grounding.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k.
