---
name: authoring-developer-guide
description: >
  Use when authoring or amending developer-tool documentation — the
  adoption + integration narrative for an SDK, library, CLI, framework, or
  API platform: the guide a developer reads to install, integrate, and
  operate the tool. Guides the METHOD, not the
  outline: developer GOALS not endpoints; a signposted start-here + a fast
  verifiable first success; concepts before recipes; goal-named runnable
  recipes; an end-to-end tutorial; grounded best-practices; a troubleshooting
  path; archetype-aware emphasis (API/SDK/CLI/framework); POINTERS into —
  never a copy of — the api-reference; and amending a guide as a versioned
  delta that sweeps the tool's changes for stale samples. Full Diataxis
  correctly typed, every sample runnable + accurate to the tool, nothing
  fabricated. Composes with a template tool + deep-research. Consumes the
  handed-in feature-spec + api-reference + PRD — never a blank page. Not the
  api-reference catalog, the end-user user-guide, engineering docs, or
  reviewing one.
extensions:
  claude:
    when_to_use: "authoring or amending the consumer-facing adoption + integration narrative for a developer-tool product (SDK/library/CLI/framework/API platform)"
    argument-hint: "<the feature-spec + api-reference (+ PRD) to turn into a developer guide, or the existing guide + change request to amend>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-14
---

# `authoring-developer-guide` — SKILL.md

> **Variant:** standard · **When to use:** authoring (or amending) the developer-tool adoption + integration narrative — to a bar where a developer can install the tool, grasp its model, complete the common integration scenarios, self-serve the common errors, and operate it in production from the guide alone, with runnable code, every step matching what the tool actually does.

## Overview

This skill is the *how-to* of writing a strong **developer guide** — the consumer-facing **adoption and integration narrative** for a developer-tool product (an SDK, library, CLI, framework, or API platform). It is the prose a **developer** reads to go from zero to a working integration and on to a correct production integration: reach a first successful call fast, find their way (a signposted start-here), understand the tool's mental model, follow code-centric recipes, build a small real thing end to end, apply production best-practices, and self-serve the common errors — with pointers **out** to the exhaustive reference. It spans the full **Diataxis** quadrant (tutorial / how-to / explanation / reference) for a technical reader. This skill carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **developer-guide template tool** that supplies the section *structure*, and a **deep-research capability** to ground the guide in established developer-experience (DX) docs practice, Diataxis, and the developer-docs quality rubric (Findability / Accuracy / Relevance / Clarity / Completeness / Readability). The producer is handed the **upstream documents** the plan determined inform this guide — never a blank page. The bar to clear: a developer can install, grasp the model, complete the common integration scenarios, and recover from the common errors **from the guide alone**, with runnable code, every step matching what the tool actually does.

This skill also **amends** an existing guide (the common real operation — see Step 6): a developer guide is the most change-driven of docs because its subject (the tool) moves.

## When to activate

- Authoring the adoption + integration narrative for a developer-tool product (SDK, library, CLI, framework, or API platform).
- Writing the getting-started, core-concepts, integration recipes, end-to-end tutorial, best-practices, and troubleshooting a developer needs.
- **Amending** an existing developer guide when the tool changes (a new version, a deprecated/renamed/changed capability) or a recipe/concept needs correcting — see Step 6.
- Filling a developer-guide template with researched, runnable, accurate content driven off the handed-in feature-spec and api-reference.

**Do NOT activate when:**

- Writing the exhaustive per-endpoint / per-symbol **api-reference** catalog → a separate document. This guide **narrates and links into** the reference; it never re-lists it.
- Writing the non-technical end-user **user-guide** (product task help, no code, a different audience) → the producer picks by the upstream PRD's audience.
- Writing the internal engineering docs — the **api-spec** (the wire contract), the **architecture-doc** (system design), or the **data-model** (persistence schema).
- Reviewing or grading a finished developer guide → use `reviewing-developer-guide`; this skill is produce-side only.

## Inputs

Read **every document the plan hands you** — your `depends_on` set — and trace each how-to and concept back to them. The typical upstreams are guidance, not a fixed cap.

- **Typical upstreams.** The **feature-spec** (the capabilities the guide teaches), the **api-reference** (the endpoints the integration recipes drive — when the tool exposes an API), and the **PRD** (the audience + the value); where present, the **user-flows** (integration scenarios) and the **architecture-doc** (auth/deployment context). **Drive the recipes off the handed-in api-reference** — real endpoints, real capabilities. On an **amend**, you are also handed the **existing guide + the change request + the changed upstreams** (Step 6).
- **Self-contained + graceful.** Produce from *whatever* context you receive. When an expected upstream is absent (e.g. a non-API library/CLI has **no api-reference**), proceed on what you have and **surface the gap as an explicit assumption; never fabricate** a capability, endpoint, or code path.
- **Research for comprehensiveness.** Use `deep-research` to ground the guide in established DX-docs / Diataxis practice, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your developer-guide template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive developer-guide structure (request/forge one, or fall back to the canonical set: overview/orientation + a signposted start-here, getting-started, core concepts, integration how-to guides, end-to-end tutorial, best-practices, troubleshooting/common-errors, api-reference pointers, tool versioning/migration, a document changelog, open questions), then proceed.

### Step 2: Load the upstreams; drive coverage off the feature-spec + api-reference

Read the handed-in documents — your **input, not a blank page**. The **feature-spec's** capabilities are your concept- and recipe-coverage checklist; the **api-reference's** endpoints are what the recipes call. Every recipe and code sample traces to a real upstream capability/endpoint — no invented APIs. Where an upstream is thin or absent, make the gap an **explicit assumption**, never a silently-invented endpoint. **Identify the tool archetype** (API platform / per-language SDK / CLI / framework — a tool can be several) — it sets the emphasis throughout (Step 4).

### Step 3: Research to ground the guide

Use a deep-research pass to ground the guide in **established DX-docs practice** (the Stripe/Twilio/Auth0 bar — a first call fast, runnable code, goal-organized, concepts before reference; time-to-first-call as the intent — minimize the steps to the first verified success), **full Diataxis** (the four modes, correctly typed + separated), and the **developer-docs quality rubric** (Findability/Accuracy/Relevance/Clarity/Completeness/Readability) — for *this* product. **If no research capability is available, do NOT fabricate** install commands, endpoints, parameters, or error shapes — flag them as assumptions to validate.

### Step 4: Apply the per-section method

Fill the template's sections to this method. Collapse a section a thin tool doesn't need; size proportionally to the product and its archetype. (Depth — the rubric, IA, getting-started, concepts: `references/structure-onboarding.md`; best-practices, troubleshooting, archetypes, the amend procedure: `references/bestpractices-archetype-amend.md`.)

- **Organize around developer GOALS, not endpoints.** Frame the whole guide + name how-to recipes by what the developer wants to *accomplish* ("accept a payment"), never by the API symbol. Lead with what you can build.
- **Information architecture — a signposted start-here + a reader-journey order.** Make the entry point unmistakable (orient → first success → concepts → recipes → tutorial → best-practices → troubleshooting → reference); position auth + getting-started prominently; keep cross-links predictable; scannable headings + a focused ToC; reveal complexity gradually (common path first, edge options linked). Light accessibility for the prose: meaningful link text (never "click here"), alt text on any diagram, acronyms defined on first use, real heading hierarchy. (Findability is the rubric's first dimension; "no clear start-here" is a top abandonment driver.)
- **Overview / orientation** — what the tool does + the problem it solves (two lines), the assumed reader + prerequisites, the 2–4 headline scenarios (each linking to its recipe), the start-here path, and **plainly that the exhaustive reference lives elsewhere** (this guide links into it).
- **Getting-started = a fast, verifiable first success.** The smallest complete program that makes **one real, successful call**: prerequisites → install → configure credentials → first call → **verify**. Say **where the credential comes from** (the signup-to-key / dashboard path) and steer the first call through **test/sandbox mode** (not live). Code is **runnable + copy-pasteable**; credentials come from an **env var / config, never hardcoded**; the call shows **real value, not hello-world**. **Minimize the steps to the first verified success** (the TTFC intent). Close with the literal expected output + the 2–3 most common first-call failures (deeper ones go to troubleshooting). (Diataxis tutorial.)
- **Core concepts BEFORE reference and recipes.** Explain the mental model — the client/resource object, the domain nouns + relations, the request lifecycle (sync/async, webhooks, idempotency conceptually), environments (test vs live) — so parameters + recipes have *meaning*. (Diataxis explanation.)
- **Integration how-to guides = goal-named, code-centric, independently-followable recipes** for an **already-oriented** reader (Diataxis how-to). One subsection per common scenario, each with the goal, extra prerequisites, focused **runnable** code (relevant lines only), the success result, and a **link into the reference** for the full option set — do not inline the catalog. Size to the tool's real surface.
- **End-to-end tutorial = build one small real thing, start to finish** (Diataxis tutorial). **Keep it separate from the section-4 lookup recipes** — fusing how-to and tutorial is the most common cause of confusing docs. Close with the result + where to go next.
- **Best-practices grounded in real production usage** (Diataxis explanation, not an option dump): **auth/secrets** (env or secret manager, least-privilege scopes, test vs live keys); **error handling** typed **retryable-vs-fatal**; **retries + idempotency** (backoff with jitter, honor retry-after, idempotency key on writes); **pagination** (auto-iterator or cursor loop; the dropped-cursor pitfall); **rate limits** (429, `Retry-After`); **webhooks** where the tool emits them (signature verification, replay/dedup, ordering); **resource hygiene** (reuse one client, pooling, timeouts) — recommended pattern + a short snippet each.
- **Troubleshooting / common-errors = a self-serve path for the frequent, knowable failures** (beyond the getting-started first-call failures): group the frequent errors (auth 401/403, validation 400, rate-limit 429, not-found 404, version mismatch) as **symptom → cause → fix**; an error-code→meaning→fix table where the tool has codes; a short FAQ for recurring conceptual confusions (test vs live, async timing, idempotency). **Proportional** — a thin tool folds this into getting-started. ("No help when stuck" is a top abandonment driver.)
- **Code samples accurate to the CURRENT tool.** Every sample reflects a real capability/endpoint from the handed-in upstreams; write samples so they *can* be tested (self-contained, single-sourced from working code where possible) and **state the tool version the guide targets** so staleness is visible — the version stamp is for the amend staleness-sweep's benefit (Step 6), not a currency check the gate runs greenfield. (The CI-ing of samples is the project's pipeline, not the guide's content — but write them to be testable.)
- **API-reference pointers — link OUT, never reproduce.** State that the exhaustive catalog is the source of truth and lives in the separate api-reference; optionally map this guide's concepts/recipes to reference sections; list supporting resources (sample repo, support, status).
- **Tool versioning + migration** — the scheme (SemVer / date-based) + what major/minor/patch means + how to pin; the deprecation policy + timelines; link the changelog; **per-major-jump migration notes with before/after for each breaking change** + the migrate step order.
- **Archetype-aware emphasis (proportional).** API platform → curl + a language, auth flows, webhooks; **per-language SDK** → a first-success + recipes per supported language, client lifecycle, idiomatic patterns; **CLI** → args/flags, **exit codes**, the **stdout/stderr contract**, non-interactive/scripting use, shell completion; **framework** → scaffolding, conventions, lifecycle hooks. The bar adapts; it does not bloat every guide.

### Step 5: Self-check against the adoptability + accuracy bar before handing off

Confirm all hold (this is the bar `reviewing-developer-guide` asserts — author and gate share it 1:1 so they don't drift). Each is **proportional**: a thin tool legitimately collapses what it doesn't need.

1. **Goal-organized** — framed around what the developer can build; recipes named by goal, not endpoint.
2. **Getting-started reaches a verifiable first success** — prerequisites (incl. where the credential comes from + test/sandbox path) → install → configure credentials → one real successful call → a **verify** step with expected output; runnable, copy-pasteable, real value (not hello-world), env-var (not hardcoded) credentials; the path is short + unblocked (TTFC intent).
3. **Core concepts present and BEFORE the reference/recipes.**
4. **Integration how-tos cover the common scenarios** in the handed-in upstreams — goal-named, code-centric, independently-followable, runnable, linking into the reference.
5. **An end-to-end tutorial builds one small real thing**, kept separate from the lookup recipes.
6. **Best-practices grounded in real usage** — auth/secrets, retryable-vs-fatal errors, retries+idempotency+backoff, pagination, rate limits, webhooks (where applicable), resource hygiene — recommended pattern + snippet, not an option dump.
7. **Diataxis modes correctly typed + separated** — no mode bleeds into another.
8. **Links into — never duplicates — the api-reference.**
9. **Code samples runnable + accurate to the actual/CURRENT tool** — every sample reflects real capabilities/endpoints from the handed-in upstreams; nothing contradicting the upstream contract; the targeted tool version stated.
10. **Tool versioning + migration stated** — scheme, deprecation policy/timelines, changelog link, per-major-jump before/after notes.
11. **Grounded, not fabricated** — capabilities/endpoints/code reflect the upstreams; gaps surfaced as explicit assumptions, not invented.
12. **Amend (on iteration) is a clean delta** — edited in place, the tool's change swept for stale samples, internal coherence held, the guide's own version bumped + changelog updated, superseded content marked (Step 6). (n/a on a greenfield first build.)
13. **Troubleshooting / common-errors path present** — the frequent knowable errors are self-servable (symptom→cause→fix); proportional (folded into getting-started for a thin tool).
14. **Findable** — a first-time reader can locate the start-here + their goal's section without already knowing the API (signposted entry + reader-journey order).

**Thin-input gate:** if a scenario the guide must teach cannot be researched or even credibly assumed into a runnable recipe, surface it as a **blocker** ("integration scenario under-defined — needs the api-reference / a product decision") rather than inventing an endpoint or code path.

### Step 6: Amend an existing guide (iteration / delta)

A developer guide is the **most amend-driven** doc — its subject (the tool) moves: a new version, a deprecated/renamed endpoint, a changed signature, a new auth flow. The amend is **upstream-driven + internal**, with **no derived-doc downstream** (the guide is a leaf — the only consumer is the developer's own integration). On an amend (handed the existing guide + change request + the changed upstreams):

1. **Scope the change.** State what this delta touches (which recipes/samples/concepts/steps, for which tool version) and what is deliberately untouched.
2. **Edit in place** — change only the affected blocks; do NOT regenerate the whole guide (that loses provenance + risks breaking untouched, still-accurate samples).
3. **Run the upstream-driven staleness sweep** — find **every** guide location that referenced the changed/removed capability (samples, recipes, concepts, the getting-started call, the api-reference pointers) and re-make each accurate to the current tool. A sample left calling a removed/renamed capability is the highest-impact amend defect (a fabrication-by-staleness).
4. **Re-make internal coherence** — concepts-before-recipes still holds; the end-to-end tutorial still runs; no recipe contradicts the (possibly changed) concept section; the first-success still verifies.
5. **Version + changelog the guide document** — bump the guide's OWN version (distinct from the tool's version and the skill's semver); add a changelog row (who / when / what changed / why, e.g. "updated for SDK v3 — `Client(key=)` → `Client.from_env()`").
6. **Mark superseded/deprecated content** — with the version + the replacement, not a silent delete, so a developer still on the old version sees the path.

## Rules

**Hard rules (never violate):**

- **Narrate + link the api-reference; never re-derive the catalog.** Point into it for full options — do not re-list parameters/types/errors inside the guide.
- **Getting-started reaches a verifiable first success.** A fast, runnable, copy-pasteable path to one real successful call, ending in a verify step; credentials from an env var / config, never hardcoded; say where the credential comes from + steer through test/sandbox.
- **Concepts before reference.** Explain the mental model before recipes or the reference.
- **Goal-organized, not endpoint-organized**, with a signposted start-here.
- **Type the Diataxis modes correctly and keep them separated.** No reference dumped into the tutorial, no concepts buried in a recipe, no how-to/tutorial fusion.
- **Code samples runnable + accurate to the current tool.** Never a sample for a capability the upstreams don't show; state the targeted tool version.
- **Troubleshooting is a self-serve path, proportional** — the frequent knowable errors map to a fix; never demand a named "Troubleshooting" section on a thin tool (fold it into getting-started).
- **Amend in place + sweep for staleness.** On a tool change, find and fix every stale sample/recipe/pointer; version + changelog the guide; mark superseded content. Never regenerate the whole guide.
- **Never fabricate.** Don't invent endpoints, capabilities, install commands, or code paths. With no source, state them as explicitly-flagged assumptions.
- **Consume the handed-in upstreams; never a blank page, never one hardcoded input.** When an expected upstream is absent (e.g. no api-reference for a non-API tool), build from what you have and surface the gap as an assumption.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it.
- **Narrative, not catalog, not end-user help, not engineering docs.**

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** to the tool + its archetype — a thin CLI collapses recipes, lightens concepts, folds troubleshooting into getting-started; a broad API platform expands recipes, webhooks, troubleshooting, + migration notes. The bar is first-success + a correct production integration, not word count.
- Prefer multi-language samples where the tool ships multiple SDKs (a first-success per language); for an API, prefer curl + at least one language.
- Prefer cursor-based pagination + backoff-with-jitter retries as the recommended patterns, deferring exhaustive options to the reference.

## Gotchas

- **Re-listing the api-reference inside the guide.** Narrate the scenario, show the focused recipe, link out for the full option set.
- **Hello-world getting-started.** The first success must reach **real value** + a verifiable check, or the reader gains no confidence.
- **Hardcoded credentials in samples.** Teaches a security anti-pattern + won't run for the reader. Read from env / config every time.
- **No clear start-here.** A guide that drops the reader into endpoints with no orientation is abandoned; signpost the entry + order the journey.
- **How-to and tutorial blurred together.** The most common Diataxis failure — keep section-4 recipes as lookups, the tutorial as one guided build.
- **Reference material leaking into the tutorial.** Mention only what the step needs; link the rest.
- **Stale samples after the tool moved.** The dominant maintenance failure — on any tool change, sweep every sample/recipe for a removed/renamed capability (Step 6); a stale sample reads fine and breaks on run.
- **A troubleshooting section that lists generic debugging advice.** Make it the tool's *frequent, knowable* errors mapped to concrete fixes, not "check your logs".
- **Fabricated endpoints/capabilities when an upstream is thin.** Surface the gap as an assumption instead.
- **Restating the template outline.** Fill its sections with judgment instead.

**Worked contrast — generic (looks plausible) vs adoptable** (use it to self-detect):

| Aspect | Generic (reject) | Adoptable (ship) |
|---|---|---|
| Getting-started | "Install the SDK and make a call." | "1. `pip install acme`; 2. get a TEST key from Dashboard → API keys; 3. `export ACME_KEY=...`; 4. run the 6-line snippet that creates a charge; 5. expected: `{\"id\": \"ch_...\", \"status\": \"succeeded\"}`; if `401`, the key is wrong → see Troubleshooting." |
| Concept | "The SDK has a client." | "The `Client` holds your key + connection pool — create one and reuse it; each domain noun (`Charge`, `Customer`) is a resource you act on through it." |
| Recipe | "There's a method to send messages." | "**Send an SMS** — `client.messages.create(to=..., body=...)`; returns a `Message` with a `sid`; see the reference for the full parameter set (media, scheduling)." |
| Reference (link-not-duplicate) | the guide re-lists all 40 endpoints with parameter tables | "Full per-endpoint parameters, types, and errors live in the [API reference](link) — the source of truth; this guide links into it." |
| Troubleshooting | "If it doesn't work, debug it." | "`429 Too Many Requests` → you hit the rate limit; back off + honor `Retry-After` (see Best practices)." |
| Amend | regenerate the whole guide for SDK v3 | edit the affected samples, sweep every `Client(key=)` → `Client.from_env()`, bump the guide version + changelog, mark the v2 recipe superseded |
| Code accuracy | a call to an endpoint the api-reference doesn't list | every call uses an endpoint/capability the handed-in api-reference/feature-spec defines, for the stated tool version |

If your fill reads like the left column — true of any tool, no runnable first success, no real concepts, the catalog pasted in, no start-here, stale on the tool's current version — it isn't done.

## Anti-patterns

- **"I'll list every endpoint so the guide is complete."** That is the api-reference's job — narrate + link out.
- **"Hello-world is a fine first call."** Reach real value + verify it.
- **"I'll hardcode the key to keep the sample short."** Read it from the environment.
- **"Recipes and the tutorial are the same thing."** Different Diataxis modes — keep them separate.
- **"This is also the user-guide, so I'll write for non-technical users."** Different audience + document.
- **"The api-reference is thin, I'll invent the endpoints."** Surface the gap as an assumption.
- **"The tool shipped v3, I'll just regenerate the guide."** Amend in place + sweep for stale samples; version + changelog; mark superseded.
- **"Skip the research, I know how SDKs work."** The research grounds *this product's* surface, scenarios, + conventions.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.

## Output

A **comprehensive developer guide** that meets the **Step 5 adoptability + accuracy bar** (goal-organized + signposted start-here; getting-started reaches a verifiable first success; concepts before reference; integration how-tos cover the handed-in scenarios; an end-to-end tutorial builds a small real thing; best-practices grounded; a proportional troubleshooting path; Diataxis modes correctly typed + separated; links into — not duplicates — the api-reference; samples runnable + accurate to the current tool; tool versioning/migration stated; the guide's own version + changelog maintained on amend; nothing fabricated). The artifact is **textual** — numbered setup steps + fenced install commands + fenced integration code samples (curl + ≥1 language where an API is involved), screens/flows described in words; the method + bar are medium-independent. The **abstract consumer** is the developer adopting + integrating the tool, and `reviewing-developer-guide` (which asserts the same 14-condition bar). The guide **consumes** the handed-in upstreams (typically feature-spec + api-reference + PRD) and **links into** the api-reference downstream. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **developer-guide template tool** (e.g. `content-template-gateway`) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the guide in DX-docs practice (Stripe/Twilio/Auth0), Diataxis, and the developer-docs quality rubric.
- `reviewing-developer-guide` — the runtime gate; asserts the **same 14-condition** adoptability + accuracy bar on the finished guide; author + gate share one bar so they don't drift.
- An **api-reference-authoring skill** — produces the exhaustive endpoint/symbol catalog this guide narrates + **links into**, never re-derives.
- A **user-guide-authoring skill** — the non-technical end-user product help; a distinct audience + document this skill is **not** (the producer picks by the PRD's audience).
- A **feature-spec** (capabilities taught), an **api-reference** (endpoints the recipes drive), a **PRD** (audience + value) — the typical *upstream* inputs; where present, **user-flows** + **architecture-doc**.

## Progressive disclosure

- `references/structure-onboarding.md` — depth for the structure + onboarding angles: the developer-docs quality rubric + Diataxis modes; information architecture / start-here / reader-journey + scannability/progressive-disclosure + light accessibility; the getting-started 6-step + TTFC + credential-acquisition/sandbox; concepts-before-recipes.
- `references/bestpractices-archetype-amend.md` — depth for production + change angles: the best-practices catalog (auth/errors/retries/pagination/rate-limits/webhooks/resource-hygiene), the troubleshooting symptom→cause→fix method, the four tool-archetype overlays, the docs-as-code/freshness habit, and the amend (Step 6) staleness-sweep procedure.
- `references/sources.md` — research provenance for the method + quality bar (Diataxis; DX-docs / IA practice; the developer-docs quality rubric; SDK/API documentation, error-handling, retries/idempotency, pagination, rate-limit, troubleshooting, versioning/migration, and docs-as-code/living-docs guidance). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
</content>
