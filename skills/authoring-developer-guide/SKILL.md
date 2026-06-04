---
name: authoring-developer-guide
description: >
  Use when authoring developer-tool documentation — the adoption +
  integration narrative for an SDK, library, CLI, framework, or API
  platform: the guide a developer reads to install the tool, grasp its
  model, and integrate it. Guides the producer
  through the METHOD, not the outline: organizing around developer GOALS not
  endpoints, a fast verifiable first success, core CONCEPTS before reference,
  goal-named code-centric integration recipes, an end-to-end tutorial,
  grounded production best-practices, and POINTERS into — never a copy of —
  the api-reference; full Diataxis correctly typed and kept separated, every
  code sample runnable and accurate to the actual tool, nothing fabricated.
  Composes with a separate developer-guide template tool and deep-research.
  Consumes the handed-in upstreams (typically feature-spec + api-reference +
  PRD) — never a blank page. Not the api-reference catalog (it links that),
  not the end-user user-guide, not the internal engineering docs, not
  reviewing a finished one.
extensions:
  claude:
    when_to_use: "authoring the consumer-facing adoption + integration narrative for a developer-tool product (SDK/library/CLI/framework/API platform)"
    argument-hint: "<the feature-spec + api-reference (+ PRD) to turn into a developer guide>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `authoring-developer-guide` — SKILL.md

> **Variant:** standard · **When to use:** authoring the developer-tool adoption + integration narrative — to a bar where a developer can install the tool, grasp its model, and complete the common integration scenarios from the guide alone, with runnable code, every step matching what the tool actually does.

## Overview

This skill is the *how-to* of writing a strong **developer guide** — the consumer-facing **adoption and integration narrative** for a developer-tool product (an SDK, library, CLI, framework, or API platform). It is the prose a **developer** reads to go from zero to a working integration: get to a first successful call fast, understand the tool's mental model, follow code-centric recipes for the common scenarios, build a small real thing end to end, and apply production best-practices — with pointers **out** to the exhaustive reference. It spans the full **Diataxis** quadrant (tutorial / how-to / explanation / reference) for a technical reader. This skill carries the producer's *judgment* — the research method and the quality bar — **not** the section list. It assumes two collaborators: a **developer-guide template tool** that supplies the section *structure*, and a **deep-research capability** to ground the guide in established developer-experience (DX) docs practice and Diataxis. The producer is handed the **upstream documents** the plan determined inform this guide — never a blank page. The bar to clear: a developer can install, grasp the model, and complete the common integration scenarios **from the guide alone**, with runnable code, and every step matches what the tool actually does.

## When to activate

- Authoring the adoption + integration narrative for a developer-tool product (SDK, library, CLI, framework, or API platform).
- Writing the getting-started, core-concepts, integration recipes, end-to-end tutorial, and best-practices a developer needs to integrate the tool.
- Filling a developer-guide template with researched, runnable, accurate content driven off the handed-in feature-spec and api-reference.

**Do NOT activate when:**

- Writing the exhaustive per-endpoint / per-symbol **api-reference** catalog (every parameter, type, and error) → that is a separate document. This guide **narrates and links into** the reference; it never re-lists it.
- Writing the non-technical end-user **user-guide** (product task help, no code, a different audience) → the developer guide's reader is a developer integrating the tool. The producer picks by the upstream PRD's audience.
- Writing the internal engineering docs — the **api-spec** (the wire contract), the **architecture-doc** (system design), or the **data-model** (persistence schema). Those are not consumer-facing developer docs.
- Reviewing or grading a finished developer guide → use the runtime review gate; this skill is produce-side only.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this guide) — and trace each how-to and concept back to them. Do not assume a fixed input: the typical upstreams below are method guidance, not a cap on what you receive.

- **Typical upstreams.** The **feature-spec** (the capabilities the guide teaches), the **api-reference** (the endpoints the integration recipes drive — when the tool exposes an API), and the **PRD** (the audience + the value); where present, the **user-flows** (integration scenarios) and the **architecture-doc** (auth/deployment context). **Drive the integration recipes off the handed-in api-reference** — real endpoints, real capabilities.
- **Self-contained + graceful.** Produce the guide from *whatever* context you actually receive. When an expected upstream is absent — for example a non-API library or CLI tool has **no api-reference** — proceed on what you have (build from the feature-spec + the tool's surface) and **surface the gap as an explicit assumption; never fabricate** a capability, endpoint, or code path to fill it.
- **Research for comprehensiveness.** Use a research capability (deep-research) to ground the guide in established developer-docs / DX practice and Diataxis, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tool — don't invent an outline

Get the section structure from your developer-guide template tool (comprehensive variant). Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive developer-guide structure (request/forge one, or fall back to the canonical set: overview/orientation, getting-started, core concepts, integration how-to guides, end-to-end tutorial, best-practices, api-reference pointers, versioning/migration, open questions), then proceed.

### Step 2: Load the upstreams; drive coverage off the feature-spec + api-reference

Read the handed-in documents — this is your **input, not a blank page**. The **feature-spec's** capabilities are your concept- and recipe-coverage checklist; the **api-reference's** endpoints are what the integration recipes call. Every recipe and code sample traces to a real upstream capability/endpoint — no invented APIs. Where an upstream is thin or absent (e.g. no api-reference for a non-API tool), make the gap an **explicit assumption**, never a silently-invented endpoint or capability.

### Step 3: Research to ground the guide

Use a deep-research pass to ground the guide in **established DX-docs practice** (the Stripe/Twilio/Auth0 bar — getting-started to a first call fast, runnable code, goal-organized, concepts before reference) and **full Diataxis** for a technical audience (the four modes, correctly typed and kept separated) — for *this* product, not "docs in general." **If no research capability is available, do NOT fabricate** install commands, endpoints, parameters, or error shapes — state them as explicitly-flagged assumptions to validate before publish.

### Step 4: Apply the per-section method

Fill the template's sections to this method. Collapse a section a thin tool doesn't need; size proportionally to the product.

- **Organize around developer GOALS, not endpoints.** Frame the whole guide by what the developer wants to *accomplish*. Name how-to recipes by the goal ("accept a payment", "send a message"), never by the API symbol. Lead with what you can build.
- **Overview / orientation** — state in two lines what the tool does + the problem it solves, the assumed reader + prerequisites, the 2–4 headline scenarios (each linking to its recipe), and **plainly that the exhaustive reference lives elsewhere** (this guide links into it).
- **Getting-started = a fast, verifiable first success.** The smallest complete program that makes **one real, successful call**: prerequisites → install → configure credentials → first call → **verify**. Code is **runnable + copy-pasteable**; credentials come from an **env var / config, never hardcoded**; the call shows **real value, not hello-world**. Close with the literal expected output and the 2–3 most common first-call failures with a one-line fix each. (This is Diataxis tutorial mode applied to onboarding.)
- **Core concepts BEFORE reference and before recipes.** Explain the mental model — the client/resource object, the domain nouns and how they relate, the request lifecycle (sync/async, webhooks, idempotency at the conceptual level), environments (test vs live) — so parameters and recipes have *meaning*. This is Diataxis explanation: the "why", not a parameter list.
- **Integration how-to guides = goal-named, code-centric, independently-followable recipes** for an **already-oriented** reader (Diataxis how-to — directions for a competent user, not teaching from scratch). One subsection per common scenario, each with the goal, any extra prerequisites, the focused **runnable** code (relevant lines only), the success result, and a **link into the reference** for the full option set — do not inline the catalog. Size the recipe set to the tool's real surface.
- **End-to-end tutorial = build one small real thing, start to finish** (Diataxis tutorial — a single guided lesson from empty project to a finished, runnable artifact). **Keep it separate from the section-4 lookup recipes** — mixing how-to and tutorial is the most common cause of confusing docs. Close with the expected result + where to go next.
- **Best-practices grounded in real production usage** (Diataxis explanation, not an option dump). Show the *recommended* pattern + a short snippet, deferring exhaustive options to the reference: **auth/secrets** (env or secret manager, least-privilege scopes, test vs live keys); **error handling** typed **retryable-vs-fatal** with the catch/branch pattern; **retries + idempotency** (backoff with jitter, honor retry-after, idempotency key on writes); **pagination** (the auto-iterator or cursor loop; the dropped-cursor pitfall); **rate limits** (catch 429, read `Retry-After`, else backoff+jitter); **resource hygiene** (reuse one client, pooling, timeouts).
- **API-reference pointers — link OUT, never reproduce.** State that the exhaustive per-endpoint/per-symbol catalog is the source of truth and lives in the separate api-reference; optionally map this guide's concepts/recipes to the relevant reference sections; list supporting resources (sample repo, support, status).
- **Versioning + migration** — the scheme (SemVer / date-based) + what major/minor/patch means + how to pin; the deprecation policy + timelines; link the changelog; give **per-major-jump migration notes with before/after for each breaking change** and the migrate step order.

### Step 5: Self-check against the adoptability + accuracy bar before handing off

Confirm all hold (this is the bar the runtime review gate asserts — author and gate share it so they don't drift):

1. **Goal-organized** — the guide is framed around what the developer can build/accomplish; recipes are named by goal, not endpoint.
2. **Getting-started reaches a verifiable first success** — prerequisites → install → configure credentials → one real successful call → a **verify** step with expected output; runnable, copy-pasteable, real value (not hello-world), env-var (not hardcoded) credentials.
3. **Core concepts present and BEFORE the reference/recipes** — the mental model is explained as understanding-oriented content, ahead of the recipes.
4. **Integration how-tos cover the common scenarios** in the handed-in upstreams — one goal-named, code-centric, independently-followable recipe per scenario; runnable; linking into the reference for full options.
5. **An end-to-end tutorial builds one small real thing** start to finish, kept separate from the lookup recipes (correct how-to vs tutorial typing).
6. **Best-practices grounded in real usage** — auth/secrets, retryable-vs-fatal errors, retries+idempotency+backoff, pagination, rate limits — recommended pattern + snippet, not an option dump.
7. **Diataxis modes correctly typed + separated** — tutorial / how-to / explanation / reference each in its mode; no mode bleeds into another.
8. **Links into — never duplicates — the api-reference** — the catalog is pointed to as the source of truth, not re-listed inside the guide.
9. **Code samples runnable + accurate to the actual tool/API** — every sample reflects real capabilities/endpoints from the handed-in upstreams; nothing contradicting the upstream contract.
10. **Versioning + migration stated** — scheme, deprecation policy/timelines, changelog link, per-major-jump before/after notes.
11. **Grounded, not fabricated** — capabilities/endpoints/code reflect the upstreams; gaps surfaced as explicit assumptions, not invented.

**Thin-input gate:** if a scenario the guide must teach cannot be researched or even credibly assumed into a runnable recipe, surface it as a **blocker** ("integration scenario under-defined — needs the api-reference / a product decision") rather than inventing an endpoint or code path. A guide whose first-success path and recipes are guesses is not adoptable.

## Rules

**Hard rules (never violate):**

- **Narrate + link the api-reference; never re-derive the catalog.** The developer guide is the adoption/integration narrative; the exhaustive endpoint/symbol listing is the separate api-reference. Point into it for full options — do not re-list parameters/types/errors inside the guide.
- **Getting-started reaches a verifiable first success.** A fast, runnable, copy-pasteable path to one real successful call, ending in a verify step. Credentials come from an env var / config, never hardcoded. A getting-started with no verifiable success is not done.
- **Concepts before reference.** Explain the mental model before sending the reader into recipes or the reference; parameters need meaning first.
- **Goal-organized, not endpoint-organized.** Frame the guide and name recipes by the developer's goal, not the API symbol.
- **Type the Diataxis modes correctly and keep them separated.** Getting-started/tutorial = guided lesson; how-to = task recipe for an oriented reader; explanation = concepts/best-practices; reference = the linked catalog. Don't let one mode bleed into another (no reference dumped into the tutorial, no concepts buried in a recipe).
- **Code samples runnable and accurate.** Every sample reflects the real, handed-in tool/API surface and runs; never a sample for a capability the upstreams don't show.
- **Never fabricate.** Don't invent endpoints, capabilities, install commands, or code paths to look complete. With no source, state them as explicitly-flagged assumptions to validate before publish.
- **Consume the handed-in upstreams; never a blank page, never one hardcoded input.** Trace each recipe/concept to its upstreams; drive recipes off the handed-in api-reference. When an expected upstream is absent (e.g. no api-reference for a non-API tool), build from what you have and surface the gap as an assumption.
- **Compose, don't duplicate.** Take the section structure from the template tool; this skill is the method that fills it. Do not paste a competing outline.
- **Narrative, not catalog, not end-user help, not engineering docs.** This is the developer adoption narrative — distinct from the api-reference (catalog), the user-guide (non-technical end-user help), and the internal api-spec/architecture-doc/data-model.

**Preferences (override-able):**

- "Comprehensive" sets output *ambition*; stay **proportional** — a thin CLI collapses recipes and lightens concepts; a broad API platform expands the recipes + migration notes. The bar is first-success + a correct production integration, not word count.
- Prefer multi-language code samples where the tool ships multiple SDKs; for an API, prefer curl + at least one language.
- Prefer cursor-based pagination guidance and backoff-with-jitter retries as the recommended patterns, deferring exhaustive options to the reference.

## Gotchas

- **Re-listing the api-reference inside the guide.** Pasting the endpoint/parameter catalog into the guide duplicates (and drifts from) the reference. Narrate the scenario, show the focused recipe, and link out for the full option set.
- **Hello-world getting-started.** A first call that prints "hello" demonstrates nothing. The first success must reach **real value** (a created resource, a real response) and end in a verifiable check, or the reader gains no confidence.
- **Hardcoded credentials in samples.** A sample with an inline API key teaches a security anti-pattern and won't run for the reader. Read credentials from an env var / config every time.
- **How-to and tutorial blurred together.** Turning the end-to-end tutorial into a pile of independent recipes (or a recipe into a from-scratch lesson) confuses the reader — the most common Diataxis failure. Keep section-4 recipes as lookups for an oriented reader; keep the tutorial as one guided build.
- **Reference material leaking into the tutorial.** A tutorial that stops to enumerate every flag derails into reference. Mention only what the step needs; link the rest.
- **Fabricated endpoints/capabilities when an upstream is thin.** Inventing an endpoint the api-reference doesn't list (or a capability the feature-spec doesn't name) ships a guide that doesn't match the tool. Surface the gap as an assumption instead.
- **Restating the template outline.** Re-deriving the section list inside the content (or in this skill) duplicates the template tool and drifts — fill its sections with judgment instead.

**Worked contrast — generic (looks plausible) vs adoptable** (use it to self-detect):

| Aspect | Generic (reject) | Adoptable (ship) |
|---|---|---|
| Getting-started | "Install the SDK and make a call." | "1. `pip install acme`; 2. `export ACME_KEY=...`; 3. run the 6-line snippet that creates a charge; 4. expected output: `{\"id\": \"ch_...\", \"status\": \"succeeded\"}`; if `401`, the key is wrong." |
| Concept | "The SDK has a client." | "The `Client` holds your key and connection pool — create one and reuse it; each domain noun (`Charge`, `Customer`) is a resource you act on through it." |
| Recipe | "There's a method to send messages." | "**Send an SMS** — `client.messages.create(to=..., body=...)`; returns a `Message` with a `sid`; see the reference for the full parameter set (media, scheduling)." |
| Reference | "All endpoints are documented here." | "Full per-endpoint parameters, types, and errors live in the [API reference](link) — the source of truth; this guide links into it." |
| Code accuracy | a call to an endpoint the api-reference doesn't list | every call uses an endpoint/capability the handed-in api-reference/feature-spec actually defines |

If your fill reads like the left column — true of any tool, no runnable first success, no real concepts, the catalog pasted in — it isn't done.

## Anti-patterns

- **"I'll list every endpoint so the guide is complete."** That is the api-reference's job — narrate the scenarios and link out; re-listing the catalog drifts.
- **"Hello-world is a fine first call."** It builds no confidence — reach real value and verify it.
- **"I'll hardcode the key to keep the sample short."** Teaches a security anti-pattern and won't run — read it from the environment.
- **"Recipes and the tutorial are the same thing."** They're different Diataxis modes — lookup recipes for an oriented reader vs one guided end-to-end build. Keep them separate.
- **"This is also the user-guide, so I'll write for non-technical users."** Different audience and document — the developer guide is code-centric for a developer integrating the tool.
- **"The api-reference is thin, I'll invent the endpoints."** Surface the gap as an assumption; never fabricate a capability or endpoint.
- **"Skip the research, I know how SDKs work."** The research grounds *this product's* surface, scenarios, and conventions — not docs theory.
- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it.

## Output

A **comprehensive developer guide** that meets the **Step 5 adoptability + accuracy bar** (goal-organized; getting-started reaches a verifiable first success; concepts before reference; integration how-tos cover the handed-in scenarios; an end-to-end tutorial builds a small real thing; best-practices grounded; Diataxis modes correctly typed and separated; links into — not duplicates — the api-reference; code samples runnable and accurate to the actual tool; versioning/migration stated; nothing fabricated). The artifact is **textual** — numbered setup steps + fenced install commands + fenced integration code samples (curl + at least one language where an API is involved), screens/flows described in words; the method + bar are medium-independent. The **abstract consumer** is the developer adopting and integrating the tool, and a runtime review gate (which asserts the same bar). The guide **consumes** the handed-in upstreams (typically feature-spec + api-reference + PRD) as input and **links into** the api-reference downstream. Its *structure* comes from the template tool; this skill supplies the *content quality*.

## Related

- A **developer-guide template tool** (e.g. a content/template gateway) — supplies the section structure this skill fills. Compose with it; never restate its outline.
- A **deep-research capability** — grounds the guide in established DX-docs practice (Stripe/Twilio/Auth0) and Diataxis for a technical audience.
- An **api-reference-authoring skill** — produces the exhaustive endpoint/symbol catalog this guide narrates and **links into**, never re-derives.
- A **user-guide-authoring skill** — the non-technical end-user product help; a distinct audience and document this skill is **not** (the producer picks by the PRD's audience).
- A **feature-spec** (the capabilities taught), an **api-reference** (the endpoints the recipes drive), and a **PRD** (the audience + value) — the typical *upstream* inputs; where present, **user-flows** + **architecture-doc**.
- A **runtime developer-guide review gate** — asserts the same adoptability + accuracy bar on the finished guide; author and gate share one bar so they don't drift.

## Progressive disclosure

- `references/sources.md` — research provenance for the method + quality bar (Diataxis framework; DX-docs / information-architecture practice; SDK/API documentation, error-handling, retries/idempotency, pagination, rate-limit, and versioning/migration guidance). Load only to audit where the guidance came from.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.
