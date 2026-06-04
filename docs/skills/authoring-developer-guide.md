# authoring-developer-guide

Author **developer-tool documentation** — the adoption + integration narrative for an SDK, library, CLI, framework, or API platform: the guide a developer reads to install the tool, grasp its model, and integrate it. The how-to (a developer-experience method + an adoptability/accuracy bar), composed with a separate developer-guide template tool and a research capability; targets a textual markdown artifact (numbered setup steps + fenced install commands + fenced integration code samples).

## Purpose

A developer guide is what a developer reads to go from "never heard of it" to "integrated in production." This skill carries the producer's judgment — not the section list — guiding a producer to organize around developer GOALS (not endpoints), reach a fast verifiable first success, present core CONCEPTS before reference material, write goal-named code-centric integration recipes, ground production best-practices (auth, errors, retries, pagination, rate limits), and POINT into — never copy — the api-reference for the endpoint catalog. The bar to clear: a developer can install, grasp the model, and complete the common integration scenarios from the guide alone, with runnable code, every step accurate to the actual tool.

## When to activate

- Authoring the developer-facing documentation for a developer-tool product (SDK, library, CLI, framework, API platform) from its handed-in upstreams (typically a feature-spec + api-reference + PRD).
- Producing getting-started/installation, core-concepts, integration how-to guides, an end-to-end tutorial, best-practices, and api-reference pointers + versioning/migration.
- Filling a developer-guide template with researched, integration-complete, behavior-accurate developer content.

### When NOT to activate

- **The HTTP/SDK API endpoint catalog** (the published per-endpoint reference) → `authoring-api-reference` (this guide LINKS that, never re-lists it).
- **The non-technical end-user product help** → `authoring-user-guide`.
- **The internal engineering docs** (api-spec, architecture, data-model) → engineering, not consumer-facing developer docs.
- **Reviewing a finished developer guide** → `reviewing-developer-guide` (the paired acceptance gate).

## Workflow

Take the section structure from the developer-guide template tool (don't invent an outline). Read the full handed-in `depends_on` set; drive integration recipes off the handed-in api-reference (and the feature-spec capabilities). Research to ground the guide in established developer-experience (DX) docs practice (getting-started to a first call fast, runnable code, concepts before reference) and the Diataxis framework for a technical audience. Then fill each section to method: getting-started/installation (a fast, verifiable first success — install, credentials via env var, a first call, verify); core-concepts explanation (the mental model, before reference); goal-named integration how-tos (code-centric recipes, one per common scenario); an end-to-end tutorial (build a small real thing); grounded best-practices/patterns; pointers into the api-reference + versioning/migration. Keep code samples runnable and accurate to the actual tool; for a non-API tool (library/CLI) there is no api-reference upstream — build from the feature-spec + the tool surface; surface any missing-upstream gap as an explicit assumption rather than fabricating an endpoint or capability. Self-check against the adoptability/accuracy bar before handoff.

## Output

A comprehensive developer guide meeting the **adoptability/accuracy bar** (getting-started reaches a first success; concepts before reference; integration how-tos cover the handed-in scenarios; code samples runnable + accurate to the tool; links into — not duplicates — the api-reference; the Diataxis modes correctly typed; nothing fabricated). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same bar the paired `reviewing-developer-guide` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Goals, not endpoints** — organized around what a developer wants to do; a fast first success; concepts before reference.
- **Links, doesn't re-list** — points into the api-reference for the catalog rather than copying it; stays distinct from the end-user `user-guide`.
- **Accurate, runnable code** — every sample matches the actual tool/API; gaps surfaced as assumptions, never fabricated.
- **Single-sourced bar** — shared with `reviewing-developer-guide`, so produce and review don't drift.

## License

MIT © 2026 Bhushan Modi.
