# project-document-discovery

Decide **which documents a software/product project needs to ship to production**, and **what it takes to produce each** — from a project idea. Discovery only: it picks the *set* and describes *how each will be produced* (producer role, tools, dependencies), never how to author a document.

## Purpose

A project idea isn't enough to know what to build — the features live in the documents. Before any document is produced, something has to decide *which* documents the project actually needs, proportional to its size, and *what it takes* to produce each. This skill is that decision: it turns an idea into a **document plan** (a manifest) — the document set, each document's producer role + OSS-first tooling + skills, and the inter-document dependency graph — keyed to the project's archetype so a thin CLI tool gets a handful of documents and a UI product gets many. It deliberately stops at discovery; authoring each document is a separate per-document skill composed with a template skill.

## When to activate

- ✅ Deciding which documents a new project needs *before* any document is produced.
- ✅ Producing a "document plan" / manifest that a later stage reads to produce the documents (and later to plan the build).
- ✅ Sizing a documentation set proportionally (a lean MVP vs a full product).

### When NOT to activate

- **Authoring/templating a specific document** (writing the PRD, drafting the architecture doc) → use a per-document authoring skill + a content/template skill.
- **Discovering the build-time engineering roster** (what it takes to *build the product*) → a separate, later analysis done from the finished documents.
- The project already has an agreed document set.

Two modes. **Greenfield** (a fresh idea, no prior plan) runs Steps 1–6 in order. **Amend** (an existing plan + a stated project change) runs the iteration method instead of re-deriving (see below).

1. **Classify the project archetype** — CLI tool · library/SDK · API service · web app · mobile app · data pipeline · … (open-ended; research an unfamiliar kind). This sets how large/design-heavy the set should be.
2. **Select a proportional document set** from the seven-band + four-overlay catalog (`references/document-type-catalog.md`) using the per-archetype load-bearing/skip table — take the load-bearing docs, add the bands the project needs, add any domain overlay it triggers, skip what it doesn't.
3. **Attach each document's production requirements** — producer role (e.g. product strategist → PRD, UX designer → wireframes, systems architect → architecture), tools/providers (OSS-first: Penpot, C4/arc42, OpenAPI, Markdown-in-repo), and skills.
4. **Attach dependencies** — each document's `depends_on`, flowing requirements → design → delivery; verify the graph is **acyclic**.
5. **Research / forge-on-gap** an unrecognized document type or domain — never guess its purpose.
6. **Self-check (the plan's definition of done)** — confirm the plan passes the **nine-item self-check** before returning it (the `reviewing-document-discovery` gate asserts the same nine, single-sourced): (1) proportional to the archetype; (2) load-bearing docs present; (3) production reqs per document; (4) `depends_on` per document; (5) acyclic DAG; (6) no orphan — with the terminal-deliverable exception (a shippable leaf like LICENSE/README with `depends_on: []` is not an orphan); (7) no padding; (8) open-ended preserved (an unrecognized type researched/forged, not guessed); (9) on an amend, the delta is change-scoped. Then stop; don't pad.

### Iteration / amend (re-tailoring an existing plan on a change)

When handed an **existing document plan + a stated project change** (a new feature, a pivot, a new domain/compliance trigger, an archetype shift), do **not** re-derive the plan — re-tailor it for the change: identify + classify the change, **ADD / RETIRE / REVISE** only the documents the change needs, re-attach production requirements for added/revised docs, re-prune the DAG over the new set (only the affected edges, re-verify acyclic), and run the Self-check **on the delta only** (item 9). If there is no prior plan, this is greenfield — run Steps 1–6 instead.

## The seven lifecycle bands + four domain overlays

Lifecycle bands (walked proportionally): `planning` (Band 0) · `analysis/discovery` · `product/requirements` (usually load-bearing) · `design/UX` (for UI products) · `architecture/engineering` · `delivery/go-to-production` · `user-facing docs` (Band 6). On top, **domain overlays** add document sets only when a project's domain triggers them: `data/ML` · `security/compliance` · `legal/governance` · `regulated/validation`. The bundled `references/document-type-catalog.md` gives ~45 document types across these bands + overlays (each: what it is · when needed · what it feeds), a per-archetype load-bearing/skip table, the common `depends_on` edges, and an OSS-first producer-role + tooling map. The catalog is **illustrative and open-ended** — research/add a type it doesn't list.

## Output

A **document plan** (decision knowledge, not a fixed schema): a list of documents, each with *what it is*, its *producer role*, *tools/providers*, *skills*, and `depends_on` — proportional to the project and forming an acyclic dependency graph. Serialization belongs to the consumer; the skill decides the *content*. The abstract consumer is the next stage that produces the documents (and later reads them to plan the build).

## Key guarantees

- **Discovery only** — decides *which* documents + *what it takes*; never authors or templates them.
- **Proportional, never a fixed taxonomy** — the set is sized to the archetype; a thin project gets few documents. (The anti-rigidity guard.)
- **Load-bearing docs preserved** — the documents that define the features are never cut to seem lean.
- **Acyclic dependencies** — direction is requirements → design → delivery → docs; each document's `depends_on` lists **every informing upstream** (explicit per catalog entry), copied into the manifest pruned to the project's set, so a producer receives the full enriching context.
- **Nine-item self-check** — the plan has an explicit definition of done (proportional, load-bearing, reqs + `depends_on` per doc, acyclic, no orphan, no padding, open-ended preserved, delta change-scoped on an amend), single-sourced with the `reviewing-document-discovery` gate.
- **Amend, not just greenfield** — an existing plan is re-tailored on a stated change (add/retire/revise + DAG re-prune, scoped to the delta), never re-derived from scratch.
- **OSS-first** tools/providers; research/forge-on-gap for unknown document types.

## Limitations

- Org titles vary (PM vs BA vs founder all produce PRDs) — it names *role kinds*, not fixed titles.
- The document-type catalog is illustrative + open-ended, not an authoritative or exhaustive taxonomy.
- It decides the document *set*; the depth of how to write each document is the job of a per-document authoring skill (composed with a template skill such as `content-template-gateway`).

## License

MIT © 2026 Bhushan Modi.
