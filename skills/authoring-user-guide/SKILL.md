---
name: authoring-user-guide
description: >
  Use when authoring an end-user product guide — the consumer-facing help a typically
  non-technical person reads to accomplish goals with a product: a getting-started tutorial,
  task how-to guides, conceptual explanation, an end-user feature/settings/CLI reference
  (NOT the HTTP API), troubleshooting/FAQ, and a glossary. Guides the METHOD, not the
  outline: one how-to per user goal from the handed-in upstreams (never invented), the four
  Diataxis modes kept distinct, every step accurate and named by its exact UI label, plain
  language for a non-technical reader (no unexplained jargon), an accessible and findable
  guide, and amending a published guide as a versioned staleness sweep — to a 12-condition
  usability + accuracy bar. Composes with a user-guide template tool + a research capability.
  Assumes the handed-in upstreams (feature-spec + user-flows + wireframes) — never a blank
  page. Not the developer-tool adoption guide (developer-guide), the endpoint catalog
  (api-reference), or reviewing a finished guide.
extensions:
  claude:
    when_to_use: "authoring an end-user user guide for a product from its upstream docs"
    argument-hint: "<the upstream docs (feature-spec + user-flows + wireframes) to base the guide on>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `authoring-user-guide` — SKILL.md

> **Variant:** standard · **When to use:** a producer is authoring the end-user guide
> for a product and needs the Diataxis-keyed authoring method + the usability/accuracy
> bar (incl. plain language, accessibility, findability, and amend), composing the section
> structure from a separate template tool.

## Overview

This skill guides authoring an **end-user user guide**: the help a real person uses to
accomplish their goals with a product. It carries the *judgment* — how to derive one
how-to per user goal from the upstream docs instead of inventing steps, how to keep the
four Diataxis documentation modes distinct (mixing them is the most common cause of
confusing docs), how to hold every step accurate to what the product actually does and
named by its **exact UI label**, how to write in **plain language** a non-technical reader
can follow, how to keep the guide **accessible** and **findable**, and how to **amend** a
published guide when the product moves — not a section list, which comes from a template
tool. The audience is the (typically non-technical) **end user**, not a developer
integrating a tool: a developer-tool's adoption/integration narrative is a separate
`authoring-developer-guide`, and the HTTP/SDK endpoint catalog is a separate
`authoring-api-reference`. This guide's "reference" mode is the end-user **product**
reference (features, settings, CLI commands), not the API. The guide sits downstream of the
product/behavior docs it describes, and is checked against a usability/accuracy bar by
`reviewing-user-guide`.

## When to activate

- Authoring an end-user / customer-facing user guide, help center, or product manual for
  a product, given its upstream docs (typically a feature-spec + user-flows + wireframes).
- Producing the full end-user documentation set — getting-started tutorial, task how-to
  guides, conceptual explanation, an end-user feature/config reference, troubleshooting/
  FAQ, and a glossary — so a real user can accomplish every supported goal.
- **Amending** a published guide after an upstream change (a renamed setting, a removed/
  added feature, a changed flow, a redesigned screen) — a versioned staleness sweep.

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
steps reference); where present, also the **PRD** (what/why), the **design-system** (the UI
terminology — use its component/term names so the guide's vocabulary matches the product),
and the **api-reference** (for a developer product). Do not assume a fixed input: that list
is method guidance, not a cap on what you receive — **never hardcode a single narrow input.**

Be **self-contained and graceful** — produce the guide from *whatever* context you
actually receive. When an expected informing document is absent (e.g. no wireframes), proceed
on what you have and surface the gap as an **explicit assumption**; never fabricate a
feature, setting, screen, or step to fill it. And **use a research capability where one is
available** (the `deep-research` capability, else web search) to make the guide
comprehensive — grounding it in established end-user-docs practice (Diataxis, task-oriented
minimalism, plain-language guidelines, WCAG for textual help, a reputable docs style guide),
not merely to fill the template.

**On iteration (amend):** the flow hands in the **existing guide + a change request + the
changed upstreams**. Run Step 9 (amend), not a full rewrite — same input contract.

## Workflow

> **Compose with the template tool first.** Before drafting, obtain the user-guide section
> structure from the content-template tool (the `content-template-gateway` capability, or
> whatever template provider is installed). It supplies the section slots — introduction/
> overview, getting-started tutorial, how-to guides, conceptual explanation, feature/config
> reference, troubleshooting/FAQ, glossary, **a Versioning & Changelog / revision-history
> section** (the guide's own doc version, for amend), and an assumptions surface. **Never
> hardcode a competing outline** — this skill fills the template's slots with derived
> content; it does not redefine them. Use a research capability to ground any docs
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
tutorial that forks or fails is not a tutorial. Pick the **first meaningful success** the
new user can reach, and minimize the steps to it (fewer prerequisites/decisions between
"opened the product" and "first visible win").

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
fix, the fix in numbered steps, with the error message/code where one exists. Add an FAQ for
recurring questions and a "get more help" pointer. This is where the failure content the
tutorial and how-tos deliberately omit lives.

### Step 6: Name controls by their exact label; describe screens textually

The artifact is markdown text: describe each screen **in words and link the wireframe**
rather than embedding a screenshot. Refer to every control by its **exact UI label** as the
product shows it, and use the **design-system's** component/term names where one exists, the
same way everywhere — so a step maps to what the user sees (a step that says "click Save"
when the button reads "Apply" blocks a non-technical user). Keep command/config content in
fenced snippets.

### Step 7: Write in plain language; keep the guide accessible

- **Plain language (for the non-technical reader).** State the purpose first; prefer short
  sentences; use everyday words. **Define every product-specific term and acronym on first
  use** (and collect them in the glossary); never leave an unexplained acronym. Target a
  general-audience reading level — judged by whether a real user can follow it, not by a
  readability score.
- **Accessibility (for a textual help artifact).** Name a control by its **label**, never by
  **color alone** ("the green button") or **location alone** ("the button on the right").
  Give links **meaningful text** (the destination, not "click here"). Nest headings in order
  (no skipped levels). Write each described screen so a reader who cannot see the wireframe
  still understands it (alt-text intent). Pixel contrast / focus appearance are the rendered
  docs-site / design-system's concern, not this textual artifact.

### Step 8: Signpost the start-here; trace every step; surface gaps as assumptions

- **Findability.** Give §1 a **start-here signpost** so a first-time reader locates the
  tutorial, a task-seeker the matching how-to, a look-up the reference, and a stuck user
  troubleshooting — a reader finds their entry point without already knowing the product.
- **Accuracy.** Trace each procedural step to a feature-spec behavior (or another handed-in
  upstream). Where an upstream was thin or absent, state the **assumption** you made (so a
  reviewer can challenge it) and list unresolved unknowns as **open questions** — never
  invent a feature, setting, or step and bury it in a procedure.

### Step 9: On an amend — scope the change, sweep for staleness, re-make coherence

When handed an existing guide + a change request + the changed upstreams, **edit, don't
rewrite**:

1. **Scope** the change unit (a how-to / a reference entry / a getting-started step / a
   screen description / a troubleshooting entry / a glossary term / an explanation claim).
2. **Upstream staleness sweep (the dominant move).** For each changed/removed/renamed
   capability, find **every** guide location that referenced it — across all modes (steps,
   reference entries, screen/wireframe links, troubleshooting, glossary, explanation) — and
   re-make each accurate to the current product. A step left describing a removed/renamed
   feature is the highest-impact defect (a fabrication-by-staleness).
3. **Re-make internal coherence.** The tutorial still runs end-to-end on the new behavior;
   the modes stay typed; the reference still mirrors the product; cross-links + glossary
   intact.
4. **Version + changelog.** Bump the guide's own Doc version + add a revision-history entry
   (what changed, when, why) — distinct from the product's version and any skill semver.
5. **Mark superseded/removed.** Delete or mark a removed feature's how-to (note the
   replacement); note a renamed setting's old name once for searchers, then retire it. The
   user guide is a **leaf** — no derived doc downstream.

### Step 10: Self-check against the usability/accuracy bar (below) before handoff

Run the quality bar (the 12-condition self-check). Fix every miss before handing the guide
to review. Depth for each method lives in `references/method-depth.md`.

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
- **Plain language + accessible by construction.** Define jargon/acronyms on first use; name
  controls by their label, never by color or location alone; give links meaningful text.
- **An amend is a scoped, swept, versioned delta.** Edit the affected units, sweep every
  stale reference to a changed capability, re-make coherence, version + changelog, mark
  superseded — never a silent in-place rewrite.

**Preferences (override-able):**

- Procedure mechanics: numbered steps, one action per step, second person, present tense,
  imperative voice, task-based headings.
- Task-oriented minimalism — action-first, anchored in the user's real tasks; cut anything
  that does not serve the task (an error is a teachable moment that troubleshooting exploits).
- Proportion the guide to the product's goal/feature set — neither pad nor truncate.

## Gotchas

- **How-to written as a concept dump.** It looks thorough but buries the steps the user
  came for. A how-to is imperative numbered steps; the "why" belongs in explanation.
- **Tutorial that forks or can fail.** A getting-started lesson with branches or a failure
  path is not a tutorial — it is a how-to or troubleshooting in disguise. One guaranteed
  happy path; push failures to troubleshooting.
- **Incomplete reference.** Skipping the settings/commands that "seem obvious" leaves the
  user unable to look things up. The reference must cover the whole product surface.
- **A step that names the wrong control.** "Click Save" when the button reads "Apply"
  blocks a non-technical user — name controls by their exact product/design-system label.
- **Unexplained jargon / a bare acronym.** Accurate but unfollowable for a non-technical
  reader. Define on first use; collect in the glossary.
- **Color-/location-only instructions.** "Click the green button" / "the one on the right"
  fails a reader who can't perceive color or see the layout — name the control.
- **Fabricated steps from a thin upstream.** When an upstream is missing, inventing a step
  that the product may not actually do is a hidden defect. Surface the gap as an assumption.
- **Stale after a product change.** A step/reference/glossary entry left describing a
  removed or renamed capability is a fabrication-by-staleness — the amend's staleness sweep
  must catch every reference across every mode.
- **Embedding screenshots.** The markdown medium has no binary assets — describe the screen
  in words and link the wireframe. Real screenshots are a future-backend concern.
- **Confusing the reference with the API catalog.** The end-user feature/config reference
  is NOT the HTTP/SDK endpoint reference (`authoring-api-reference`).

## Anti-patterns

- **"I'll bake the section list into the doc myself."** That duplicates the template and
  drifts from it. Always compose the structure from the template tool.
- **"One big walkthrough covers everything."** Collapsing tutorial + how-to + explanation
  + reference into one narrative is the #1 cause of confusing docs. Keep the modes distinct.
- **"The upstream didn't say, so I'll just describe what it probably does."** Silent
  invented behavior belongs in the assumptions/open-questions surface, not in a procedure.
- **"The reader will figure out the jargon."** A non-technical reader can't — define it.
- **"The product changed; I'll just patch the one screen I remember."** Without a full
  staleness sweep, other stale references survive — sweep every mode.
- **"This is a developer tool, so I'll write the integration/onboarding narrative here."**
  That is `authoring-developer-guide`; this skill is the end-user product help.
- **"I'll embed the API endpoint table as the reference."** The reference is the product
  surface; the endpoint catalog is `authoring-api-reference`.

## Usability / accuracy quality bar

A user guide is **complete + usable + accurate** when ALL hold (this is the same 12-condition
bar the review-side gate asserts, single-sourced and numbered identically):

1. **Goal coverage — one how-to per goal, no orphans.** Every user goal in the handed-in
   upstreams (user-flows when present, else feature-spec/PRD) has exactly one how-to; every
   how-to traces to a goal.
2. **Four Diataxis modes present AND correctly typed.** Tutorial (one guaranteed path),
   how-to (imperative steps, not a concept dump), explanation (no steps), reference (neutral
   + complete) — not conflated.
3. **End-user feature/config reference complete.** Every user-facing feature, setting, and
   CLI command/shortcut is documented; the reference mirrors the product. (Product surface,
   not the HTTP API.)
4. **Steps accurate to the actual product behavior — incl. UI terminology.** Every step
   matches a handed-in upstream behavior; no invented step/setting/screen; each control is
   named by its **exact product/design-system label**. Fabrication is a hard fail.
5. **Procedure mechanics sound.** Numbered steps, one action per step, second person,
   present tense, imperative voice, task-based headings (using the exact labels).
6. **Troubleshooting covers the known error states.** Every error/recovery path from the
   upstreams appears as a symptom -> cause -> fix entry organized by user-visible symptom;
   recurring questions in the FAQ; a "get more help" pointer.
7. **Usable by the target audience.** A real (typically non-technical) user could accomplish
   every supported goal from the guide alone; prerequisites are stated; screens are described
   and wireframe-linked. *(Language comprehensibility is cond-10 — this condition is the
   accomplish-the-goal / prerequisites / screen-description outcome; do not double-judge
   jargon here.)*
8. **Assumptions/gaps surfaced.** Where an upstream was absent or thin, the assumptions are
   stated (challengeable), not silently invented.
9. **Amend is a scoped, swept, versioned delta.** On an iteration: the delta meets the bar
   on what it touched, the upstream staleness sweep is complete (no removed/renamed
   capability still referenced in any mode), internal coherence holds, the revision-history
   is updated, and superseded/removed items are marked. *(n/a on a greenfield first build.)*
10. **Plain language / readability.** Purpose-first; short sentences; every term/acronym
    defined on first use (collected in the glossary); no unexplained acronym; an audience-fit
    reading level. Judged by whether a non-technical reader can follow it, not a score.
    *(Distinct from cond-7: a jargon/readability defect is cond-10; an unfollowable-flow /
    missing-prerequisite defect is cond-7.)*
11. **Accessibility (proportional).** Meaningful link text (no bare "click here"); headings
    nest correctly; no step relies on color or location alone; described screens carry
    alt-text intent. *(n/a where there are no links/images/color cues; pixel-contrast and
    focus-appearance are the design-system's, not judged here.)*
12. **Findability / start-here.** A first-time reader can locate the start-here and their
    goal's section across the doc set. *(Distinct from cond-1 "organized by goal" and cond-2
    "modes typed" — this is whether the reader can navigate to them; trivially holds for a
    one-page guide; do not double-penalize a defect already caught by cond-1/cond-2.)*

## Output

An end-user user guide in markdown, composed onto the template tool's structure: an
introduction/overview (with a start-here signpost + plain-language/accessibility
conventions), a getting-started tutorial (one guaranteed happy path), one task-oriented
how-to per user goal (imperative numbered steps), a conceptual explanation (no steps), an
end-user feature/configuration reference (the product surface — features, settings, CLI
commands — not the HTTP API), a troubleshooting/FAQ sourced from the known error states, a
glossary, a Versioning & Changelog / revision-history section (the guide's own doc version),
and an assumptions/open-questions surface. Screens are described in words with wireframe
links; commands/config are fenced snippets; controls are named by their exact label. On an
amend, the output is a scoped versioned delta + an updated revision-history, not a rewrite.
The artifact is consumed by the review-side gate (which judges it against the 12-condition
bar above) and, ultimately, by a real user accomplishing every supported goal. The method +
bar are medium-independent: a future docs-platform or screenshot-rich backend changes only
the rendering (how screens are shown), not the derivation or the bar.

## Related

- **Template provider** (`content-template-gateway` capability) — supplies the user-guide
  section structure this skill composes onto; never duplicated here.
- **Research capability** (`deep-research`, else web search) — grounds the docs conventions
  (Diataxis, minimalism, plain language, WCAG-for-docs, the style guide) and the derivation
  evidence.
- **Upstream input — the handed-in `depends_on` set.** Typically a feature-spec +
  user-flows + wireframes (plus PRD/design-system/api-reference where present). Never
  authored from a blank page.
- **`reviewing-user-guide`** — the review-side gate that asserts the same 12-condition
  usability/accuracy bar; produce-side and review-side are single-sourced.
- **`authoring-developer-guide`** — the sibling for the developer-tool adoption/integration
  narrative; this skill is the end-user product help, distinct from it.
- **`authoring-api-reference`** — the sibling for the HTTP/SDK endpoint catalog; this
  skill's reference mode is the end-user product surface, distinct from it.

## Progressive disclosure

- `references/method-depth.md` — the depth behind the method: the plain-language/readability
  conventions, the WCAG-for-a-textual-artifact accessibility checks, the IA/start-here
  reader-journey, the UI-terminology discipline, task-oriented minimalism, and the amend
  staleness-sweep procedure. Load when authoring a section whose method you want in depth.
- `references/sources.md` — research provenance for the section set, the Diataxis-keyed
  authoring method, and the usability/accuracy bar. Load when verifying a claim's grounding.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k.

## Changelog

- **1.1.0** (2026-06-15) — production-grade restructure: single-sourced 12-condition bar
  (added cond-9 amend, cond-10 plain-language, cond-11 accessibility, cond-12 findability;
  deepened cond-4/5 with UI-terminology; migrated the jargon clause from cond-7 to cond-10);
  added Step 6 (exact-label) / Step 7 (plain-language + accessibility) / Step 8 (start-here)
  / Step 9 (amend); added `references/method-depth.md`. Additive — input contract + the bar's
  spine unchanged. (1.0.0 → 1.1.0.)
</content>
