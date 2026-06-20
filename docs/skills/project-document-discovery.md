# project-document-discovery

Decide **which documents a software/product project needs to ship to production** — classifying the project across 10 dimensions, identifying its distinct capability areas, and producing a proportional, capability-scoped document manifest (which documents, who produces each, the order they depend on). Discovery only; never authors a document.

**Version: 2.0.0**

## Purpose

A project idea isn't enough to know what to build — the features live in the documents. Before any document is produced, something has to decide *which* documents the project actually needs, proportional to its size and capability decomposition, and *what it takes* to produce each. This skill is that decision: it turns an idea into a **three-key JSON output** (`capability_map` + `product_capabilities` + `manifest`) — the project classification, the product capability areas (the partition axis for document fan-out), and the capability-scoped document plan. It deliberately stops at discovery; authoring each document is a separate per-document skill composed with a template skill.

## When to activate

- ✅ Deciding which documents a new project needs *before* any document is produced.
- ✅ Amending an existing manifest when the project changes (new feature, pivot, compliance trigger) — use amend mode when `capability-map.yaml` and `manifest.yaml` exist.
- ✅ Producing a capability-scoped manifest that a later stage reads to produce the documents.

### When NOT to activate

- **Authoring/templating a specific document** → use a per-document authoring skill + a content/template skill.
- **Discovering the build-time engineering roster** → a separate, later analysis from finished documents.
- The project already has an agreed document set and no change is in scope.

Two modes. **Greenfield** runs Phase A (Steps 1–3) then Phase B (Steps 4–8). **Amend** (existing `capability-map.yaml` + `manifest.yaml` + a change request) runs the iteration method instead of re-deriving.

**Phase A — Classify + Identify:**

1. **Classify across 10 dimension clusters** — archetype (web-app, api-service, cli-tool, …), domain (e-commerce, fintech, healthcare, b2b-saas, …), scale (users, traffic, data volume), UI presence, security (auth, PII, compliance), data/ML, regulatory, infrastructure, team, and prior-art-triggers (Python-injected; do not populate). Produces `capability_map` JSON.
2. **Identify product capability areas** using the 4-signal algorithm (load `references/reference-architectures.md`): Signal 1 = domain reference architecture lookup; Signal 2 = pivotal domain events; Signal 3 = core domain nouns; Signal 4 = JTBD jobs. Fill the full seam contract for each area: `id`, `name`, `scope` (does AND does NOT), `owns`, fan-out flags (`has_ui`, `has_api`, `has_persistence`), `refs`, `publishes`/`consumes` (dot-notation), `entry_points`, `exit_points`, `depends_on`, `ui_complexity`.
3. **Apply sizing tests**: single-team test · single-reason-to-change test · authoring-turn test. Split any failing area; add L2 sub-capabilities if only the authoring-turn test fails. Target: 4–10 L1 areas.

**Phase B — Fan-out Manifest:**

4. **Generate shared documents** from classification flags (prd, architecture-doc always; design-system + system-wireframes if any `has_ui: true`). Load `references/document-type-catalog.md` and add domain overlay documents.
5. **Generate per-capability document entries** — for every active capability: always `feature-spec-{id}` (docs); if `has_persistence` → `data-model-{id}` (docs); if `has_api` → `api-spec-{id}` (docs); if `has_ui` → `wireframes-{id}` (**design**); if `has_ui` AND `ui_complexity` in `[complex, consumer-grade]` → `hi-fi-{id}` (**design**). Each entry has `type`, `scope`, `capabilities` field.
6. **Attach `depends_on` edges** — per catalog edges pruned to the project set, plus per-capability edges (feature-spec-{id} → prd + feature-spec of depends_on capabilities; wireframes-{id} → system-wireframes + feature-spec-{id}; hi-fi-{id} → wireframes-{id} + design-system). Verify acyclic.
7. **Research / forge-on-gap** an unrecognized document type — never guess its purpose.
8. **Self-check (the plan's definition of done)** — confirm the plan passes the **eleven-item self-check** before returning it (the `reviewing-document-discovery` gate asserts the same twelve, single-sourced): (1) proportional; (2) load-bearing present; (3) production reqs per document; (4) `depends_on` per document; (5) acyclic DAG; (6) no orphan (terminal-deliverable exception); (7) no padding; (8) open-ended preserved; (9) amend delta is change-scoped; (10) 4–10 L1 capability areas, all sizing tests pass; (11) per-capability fan-out entries match flags. Then stop.

### Iteration / amend (re-tailoring an existing plan on a change)

When handed an **existing document plan + a stated project change** (a new feature, a pivot, a new domain/compliance trigger, an archetype shift), do **not** re-derive the plan — re-tailor it for the change: identify + classify the change, **ADD / RETIRE / REVISE** only the documents the change needs, re-attach production requirements for added/revised docs, re-prune the DAG over the new set (only the affected edges, re-verify acyclic), and run the Self-check **on the delta only** (item 9). If there is no prior plan, this is greenfield — run Steps 1–6 instead.

## The seven lifecycle bands + four domain overlays

Lifecycle bands (walked proportionally): `planning` (Band 0) · `analysis/discovery` · `product/requirements` (usually load-bearing) · `design/UX` (for UI products) · `architecture/engineering` · `delivery/go-to-production` · `user-facing docs` (Band 6). On top, **domain overlays** add document sets only when a project's domain triggers them: `data/ML` · `security/compliance` · `legal/governance` · `regulated/validation`. The bundled `references/document-type-catalog.md` gives ~45 document types across these bands + overlays (each: what it is · when needed · what it feeds), a per-archetype load-bearing/skip table, the common `depends_on` edges, and an OSS-first producer-role + tooling map. The catalog is **illustrative and open-ended** — research/add a type it doesn't list.

## Output

Three-key JSON: `{capability_map, product_capabilities, manifest}`.

- `capability_map` — 10-cluster project classification (archetype, domain, scale, ui, security, data_ml, regulatory, infrastructure, team; `prior_art_triggers` is Python-injected and must not be model-provided).
- `product_capabilities` — flat list of `CapabilityRecord` objects (L1 and optional L2); model must omit `level`, `status`, `superseded_by`, `merged_into` (Python-injected).
- `manifest` — document plan: `{documents: [...], providers: [...], roles: [...], skills: [...]}`. Each document entry has `id`, `title`, `type`, `scope` (capability id or "system"), `capabilities` (`["docs"]` or `["design"]`), `archetype`, `tools`, `skills`, `depends_on`.

**Breaking from v1.x:** `manifest` is now nested under the `"manifest"` key (was the root object). Two new top-level keys added.

## Key guarantees

- **Discovery only** — decides *which* documents + *what it takes*; never authors or templates them.
- **Proportional, never a fixed taxonomy** — the set is sized to the archetype; a thin project gets few documents. (The anti-rigidity guard.)
- **Load-bearing docs preserved** — the documents that define the features are never cut to seem lean.
- **Acyclic dependencies** — direction is requirements → design → delivery → docs; each document's `depends_on` lists **every informing upstream** (explicit per catalog entry), copied into the manifest pruned to the project's set, so a producer receives the full enriching context.
- **Eleven-item self-check** — the plan's definition of done (proportional, load-bearing, reqs + `depends_on` per doc, acyclic, no orphan, no padding, open-ended preserved, delta change-scoped on amend, 4–10 L1 capability areas with sizing tests, fan-out entries match flags), single-sourced with the `reviewing-document-discovery` gate (twelve-condition bar — the reviewer adds the output-contract shape check).
- **Amend, not just greenfield** — an existing plan is re-tailored on a stated change (add/retire/revise + DAG re-prune, scoped to the delta), never re-derived from scratch.
- **OSS-first** tools/providers; research/forge-on-gap for unknown document types.

## Limitations

- Org titles vary (PM vs BA vs founder all produce PRDs) — it names *role kinds*, not fixed titles.
- The document-type catalog is illustrative + open-ended, not an authoritative or exhaustive taxonomy.
- It decides the document *set*; the depth of how to write each document is the job of a per-document authoring skill (composed with a template skill such as `content-template-gateway`).

## License

MIT © 2026 Bhushan Modi.
