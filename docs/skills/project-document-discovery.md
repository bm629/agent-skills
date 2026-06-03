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

## Workflow

1. **Classify the project archetype** — CLI tool · library/SDK · API service · web app · mobile app · data pipeline · … (open-ended; research an unfamiliar kind). This sets how large/design-heavy the set should be.
2. **Select a proportional document set** from the five-band catalog (`references/document-type-catalog.md`) using the per-archetype load-bearing/skip table — take the load-bearing docs, add the bands the project needs, skip what it doesn't.
3. **Attach each document's production requirements** — producer role (e.g. product strategist → PRD, UX designer → wireframes, systems architect → architecture), tools/providers (OSS-first: Penpot, C4/arc42, OpenAPI, Markdown-in-repo), and skills.
4. **Attach dependencies** — each document's `depends_on`, flowing requirements → design → delivery; verify the graph is **acyclic**.
5. **Research / forge-on-gap** an unrecognized document type or domain — never guess its purpose.
6. **Re-check and stop** — proportional? load-bearing docs present? acyclic? Then stop; don't pad.

## The five lifecycle bands

`analysis/discovery` · `product/requirements` (usually load-bearing) · `design/UX` (for UI products) · `architecture/engineering` · `delivery/go-to-production`. The bundled `references/document-type-catalog.md` gives ~30 document types across these bands (each: what it is · when needed · what it feeds), a per-archetype load-bearing/skip table, the common `depends_on` edges, and an OSS-first producer-role + tooling map. The catalog is **illustrative and open-ended** — research/add a type it doesn't list.

## Output

A **document plan** (decision knowledge, not a fixed schema): a list of documents, each with *what it is*, its *producer role*, *tools/providers*, *skills*, and `depends_on` — proportional to the project and forming an acyclic dependency graph. Serialization belongs to the consumer; the skill decides the *content*. The abstract consumer is the next stage that produces the documents (and later reads them to plan the build).

## Key guarantees

- **Discovery only** — decides *which* documents + *what it takes*; never authors or templates them.
- **Proportional, never a fixed taxonomy** — the set is sized to the archetype; a thin project gets few documents. (The anti-rigidity guard.)
- **Load-bearing docs preserved** — the documents that define the features are never cut to seem lean.
- **Acyclic dependencies** — direction is requirements → design → delivery.
- **OSS-first** tools/providers; research/forge-on-gap for unknown document types.

## Limitations

- Org titles vary (PM vs BA vs founder all produce PRDs) — it names *role kinds*, not fixed titles.
- The document-type catalog is illustrative + open-ended, not an authoritative or exhaustive taxonomy.
- It decides the document *set*; the depth of how to write each document is the job of a per-document authoring skill (composed with a template skill such as `content-template-gateway`).

## License

MIT © 2026 Bhushan Modi.
