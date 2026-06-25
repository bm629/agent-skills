---
name: project-document-discovery
description: >
  Use when deciding which documents a software or product project needs to produce — classifies
  across 10 dimensions, identifies product capability areas (4-signal algorithm), and produces a
  proportional, capability-scoped manifest with all five sections populated (documents, roles,
  skills, tools, capabilities). Re-tailors when the project changes (amend). Covers the full
  SDLC universe (seven lifecycle bands + four domain overlays). Returns a three-key JSON payload;
  caller writes two files from it (capability-map.yaml + manifest.yaml) — never assumes scope_root.
  Discovery only: decides which documents and what it takes to produce them, not how to author
  them. Keywords: document discovery, documentation plan, SDLC documents, document manifest,
  capability map, proportional docs, manifest completeness.

extensions:
  claude:
    when_to_use: "Deciding the set of documents a project needs (a capability-scoped document manifest) from an idea, before producing any. Also for amending an existing manifest when the project changes."
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}

version: "3.2.0"

forge:
  status: reviewed
  forged: 2026-06-03
  reviewed: 2026-06-21
---

# `project-document-discovery` — SKILL.md

> **Variant:** standard · **When to use:** invoked to turn a project idea into a proportional, capability-scoped plan of the documents the project needs; returns a three-key JSON (capability_map + product_capabilities + manifest); control passes back to the caller.

## Overview

Given a software/product project idea, this skill decides **which documents the project needs to ship to production**, and **what it takes to produce each** — the producer role, the tools/providers, the skills, and which other documents it depends on. It is **discovery only**: it picks the *set* and describes *how each will be produced*, never how to author a document (that is a separate per-document authoring skill). The guiding discipline is **proportionality** — the document set is sized to the project.

The skill runs as two explicit internal phases within a single model invocation:

- **Phase A — Classify + Identify:** classify the project across 10 dimension clusters → identify the product's distinct capability areas (4-signal algorithm + sizing tests) → produce `capability_map` JSON and `product_capabilities` list.
- **Phase B — Fan-out Manifest:** drive shared-document selection from classification flags → generate per-capability document entries from the capability list (fan-out rules) → attach DAG edges → self-check.

Output: three-key JSON `{capability_map, product_capabilities, manifest}`.

## When to activate

- ✅ Deciding which documents a new project needs *before* any document is produced (greenfield).
- ✅ Amending a document plan for a project change (new feature, pivot, new compliance trigger, archetype shift) — use amend mode when `capability-map.yaml` and `manifest.yaml` already exist.
- ✅ Producing a capability-scoped manifest that a later stage reads to produce the documents.

**Do NOT activate when:**

- **Authoring or templating a specific document** — use a per-document authoring skill + a content/template skill.
- **Discovering the build-time engineering roster** — that is a separate, later analysis from the finished documents.
- The project already has an agreed document set and no change is in scope.

## Workflow

Two modes: **Greenfield** runs Phase A (Steps 1–3) then Phase B (Steps 4–9) in order. **Amend** (existing `capability-map.yaml` + `manifest.yaml` + a change request) runs the **Iteration / amend** method below instead of re-deriving.

---

### Phase A — Classify + Identify

#### Step 1: Classify the project across 10 dimension clusters

Read `idea.md`. Classify the project across all 10 dimension clusters and produce a `capability_map` JSON object. Each cluster is a top-level key:

| Cluster key | What to classify |
|---|---|
| `archetype` | Project archetype — primary (web-app, api-service, cli-tool, data-pipeline, mobile-app, library/sdk, …) and any secondary types |
| `domain` | Business domain — primary (e-commerce, fintech/neobank, healthcare, b2b-saas, marketplace, developer-platform, …) and sub-domain |
| `scale` | Expected users (< 100 / 100–10k / 10k–1m / > 1m), traffic pattern (steady / bursty / batch / realtime), data volume |
| `ui` | Has UI (yes/no), UI types (web / mobile / desktop / cli / email / embedded), consumer-facing (yes/no) |
| `security` | Auth required (yes/no), auth type (jwt / oauth2 / api-key / session / mtls), PII involved, compliance requirements |
| `data_ml` | Has data pipeline, has ML model, data stores (relational / document / timeseries / graph / vector / blob / cache / search) |
| `regulatory` | Regulatory applies (yes/no), specific frameworks (GDPR / HIPAA / PCI-DSS / SOX / ISO 27001 / FedRAMP) |
| `infrastructure` | Deployment target (cloud / on-premise / hybrid / edge / serverless), cloud providers, containerized |
| `team` | Team size (solo / small / medium / large), engineering maturity (startup / growing / mature / enterprise) |
| `prior_art_triggers` | **Leave empty — Python-injected from the classification flags.** Do not populate. |

The `capability_map` object is **model-provided** for clusters 1–9; `prior_art_triggers` is **Python-injected** (omit it in your output).

**Field-value conventions (single-sourced with the schemas + the deterministic validator):**

- **Kept enums — emit the token VERBATIM: exact characters, no added spaces.** `scale.expected_users` is exactly one of `<100` / `100-10k` / `10k-1m` / `>1m` — write `<100`, never `< 100`. Emit the exact tokens likewise for `traffic_pattern`, `data_volume`, `ui.ui_types` (`web`/`mobile`/`desktop`/`cli`/`email`/`embedded`/`voice`/`wearable`/`ar-vr`/`tv`), `subdomain`, `ui_complexity`, `deployment_target`, `data_stores`, `team_size`, `engineering_maturity`.
- **Open fields — prefer a recommended-vocab token; free-text is allowed when none fits:**
  - `security.auth_type`: `jwt`, `oauth2`, `openid-connect`, `api-key`, `session`, `mtls`, `saml`, `ldap`, `basic`, `webauthn/passkey`.
  - `security.compliance_requirements` — standards/certifications the system is built to MEET (distinct from `regulatory.frameworks`, the governing bodies/laws by jurisdiction): `gdpr`, `hipaa`, `pci-dss`, `sox`, `iso27001`, `fedramp`, `soc2`, `ccpa`, `nist`, `glba`, `ferpa`, … (e.g. `sebi` for an Indian securities system).
  - `infrastructure.cloud_provider`: `aws`, `gcp`, `azure`, `cloudflare`, `fly`, `railway`, `render`, `digitalocean`, `vercel`, `netlify`, `heroku`, `oracle`, `alibaba`, `ibm`, `linode`, `supabase`, `hetzner`, `vultr`, `self-hosted`, …
- **Lengths are soft — no field hard-fails on length.** Keep `scope` concise (1–3 sentences) and `notes` under ~2000 chars as guidance, not a gate.

---

#### Step 2: Identify the product's distinct capability areas

**Load `references/reference-architectures.md` at the start of this step** (progressive disclosure — same pattern as `document-type-catalog.md` in Phase B). It contains the 4-signal algorithm, the reference architecture table (10 domains × canonical L1 capability areas), the three sizing tests, seam contract filling guidance, and capability count guidance.

Apply the 4-signal identification algorithm from the reference file in order:

1. **Signal 1 — Domain reference architecture** (highest confidence): look up `domain.primary` in the reference architecture table; adopt + trim the canonical decomposition. If the domain is novel, proceed to Signals 2–4.
2. **Signal 2 — Pivotal domain events**: extract the major state transitions from `idea.md` (e.g. "Order Placed"). Each is a boundary — the area to the left owns what happens before, the area to the right owns what happens after.
3. **Signal 3 — Core domain nouns**: extract primary nouns and group into entity clusters. Each cluster → the capability area that custodies those entities.
4. **Signal 4 — Jobs-to-be-done**: map user jobs from `idea.md`. Each distinct job cluster → a capability area.

For each identified capability area, fill the full seam contract (all required fields + all optional fields present in `idea.md`):
- **Required:** `id` (kebab-case unique), `name`, `scope` (concise, 1–3 sentences: does AND does NOT — the negative clause is required), `owns` (may be empty for ownerless capabilities: pure-UI / gateway / analytics / orchestration), `has_ui`, `has_api`, `has_persistence`
- **Optional:** `subdomain` (core / supporting / generic), `parent`, `refs` (dot-notation: `{capability-id}.{entity-name}`), `publishes` / `consumes` (dot-notation: `{capability-id}.{event-name}`), `entry_points`, `exit_points`, `depends_on`, `ui_complexity` (simple / moderate / complex / consumer-grade), `notes`
- **Must omit:** `level`, `status`, `superseded_by`, `merged_into` — Python-injected.

Consult the seam contract filling guide in `references/reference-architectures.md` for dot-notation conventions and per-flag guidance.

---

#### Step 3: Apply capability count check and sizing tests

Apply all three sizing tests (from the reference file) to every L1 candidate:
1. **Single-team test**: one cross-functional team can own it end-to-end.
2. **Single-reason-to-change test**: the capability changes for exactly ONE business reason.
3. **Authoring-turn test**: the scope statement requires no "and" connecting two unrelated concerns.

**If a candidate fails any test:** split it. **If it fails Test 3 only:** add an L2 sub-capability (`parent: {l1-id}`) rather than a full split.

**Capability count target:** 4–10 L1 areas. Below 4 = under-decomposed; above 10 = over-decomposed (merge strongly-coupled areas or add L2 sub-capabilities instead of more L1s).

---

### Phase B — Fan-out Manifest

#### Step 4: Generate shared document entries

Read the `capability_map` from Phase A. Generate shared documents based on classification flags:

| Document | Condition | Producer | Type |
|---|---|---|---|
| `prd` | Always | idea-strategist | prd |
| `architecture-doc` | Always | systems-architect | architecture-doc |
| `design-system` | Any capability has `has_ui: true` | ux-designer | design-system |
| `system-wireframes` | Any capability has `has_ui: true` | ux-designer | wireframes |

Load `references/document-type-catalog.md` at the start of this step. Add any domain overlay documents the classification flags trigger:
- `regulatory.applies: true` → add legal-governance overlay documents
- `data_ml.has_data_pipeline: true` → add data/ML overlay documents
- `security.pii_involved: true` + compliance requirements → add security/compliance documents

---

#### Step 5: Generate per-capability document entries (fan-out rules)

For **every active capability area** in `product_capabilities` (status == active or no status field), generate the per-capability document entries:

| Fan-out rule | Condition | Document id | Type | capability |
|---|---|---|---|---|
| Feature spec | Always | `feature-spec-{id}` | feature-spec | docs |
| Data model | `has_persistence: true` | `data-model-{id}` | data-model | docs |
| API spec | `has_api: true` | `api-spec-{id}` | api-spec | docs |
| Wireframes | `has_ui: true` | `wireframes-{id}` | wireframes | **design** |
| Hi-fi | `has_ui: true` AND `ui_complexity` in `["complex", "consumer-grade"]` | `hi-fi-{id}` | hi-fi | **design** |

Set the `scope` field on each document entry to the capability's `id` (for per-capability entries) or `"system"` (for shared entries: prd, architecture-doc, design-system, system-wireframes).

Each manifest entry must include: `id`, `title`, `type`, `scope`, `capability` (scalar string: `"docs"` for text documents, `"design"` for wireframes/hi-fi), `archetype` (producer role), `role` (role id — `document-author` for engineer/strategist, `designer` for designer), `depends_on` (to be filled in Step 6), `skills` (skill ids for this document type — from `references/manifest-schema.md` Section 4).

---

#### Step 6: Set `depends_on` edges (the production DAG)

Attach `depends_on` for every document entry. Take each type's canonical edges from `references/document-type-catalog.md`, then **prune to the documents actually in this project's set** (drop edges to absent documents).

**Per-capability document DAG edges** (applies in addition to catalog edges):

| Document | `depends_on` edges |
|---|---|
| `feature-spec-{id}` | `[prd] + [feature-spec-{d} for d in cap.depends_on]` |
| `data-model-{id}` | `[feature-spec-{id}]` |
| `api-spec-{id}` | `[feature-spec-{id}]` + `[data-model-{id}]` if has_persistence |
| `wireframes-{id}` | `[system-wireframes, feature-spec-{id}]` |
| `hi-fi-{id}` | `[wireframes-{id}, design-system]` + cross-capability hi-fi edges from cap.depends_on |
| `system-wireframes` | `[design-system]` |
| `design-system` | `[prd, architecture-doc]` |

**Verify the assembled (pruned) graph is acyclic** — catalog edges are pre-verified acyclic; pruning cannot introduce a cycle; this is a safety check.

---

#### Step 7: Research / forge-on-gap the unknowns

For a document type, archetype, or domain you don't recognize, **research it** (or forge a skill for it) before placing it — never guess its purpose, producer, or dependencies.

---

#### Step 8: Populate manifest meta-sections

Load `references/manifest-schema.md`. Derive and populate all five meta-sections from the assembled document set. Do not leave any section as `[]`.

**`capabilities:`** — copy verbatim from `references/manifest-schema.md` Section 2:
- Always include the `docs` capability entry.
- Include the `design` capability entry only when `ui.has_ui: true` from Phase A.
- Do NOT include any other capability (auth, ci, vcs, storage, etc.) — those are build-level, outside discovery scope.
- `selected_provider: null`, `account: null`, `status: "unassigned"` on every entry.

**`roles:`** — derive from document archetypes:
- If any document has `archetype: "engineer"` or `archetype: "strategist"` → include the `document-author` role (full definition from `references/manifest-schema.md` Section 3).
- If any document has `archetype: "designer"` → include the `designer` role (full definition from `references/manifest-schema.md` Section 3).

**`skills:`** — take the union of all `skills` arrays across every document entry, then add:
- `deep-research` (category: research) — always
- `external-content-sanitizer` (category: utility) — always

Deduplicate. For each skill: set `version: null` and `source: null` (discovery time; approval gate resolves versions). Derive `category` from the id using the naming convention in `references/manifest-schema.md` Section 1 — prefer a recommended-vocab value (`authoring`, `reviewing`, `research`, `orchestration`, `utility`, `ops`, `testing`, `reference/library`), free-text allowed when none fits. Likewise `tool.type` prefers `web-search`, `file-read`, `file-write`, `code-exec`, `api-call`, `browser`, `mcp`, `database`, `shell`, `messaging`, `email`, `queue`.

**`tools:`** — derive from the document set using `references/manifest-schema.md` Section 5:
- `file-read` and `file-write` — always.
- `web-search` — if any text document type is in the set.
- `browser` — if any design document type (wireframes, hi-fi, design-system, user-flows) is in the set.

**`amendments:`** — always `[]` on greenfield output.

---

#### Step 9: Self-check (the definition of done for the document plan)

Before returning the output, confirm the plan passes all fourteen items:

1. **Proportional** — no over-selection and no under-selection for the project's size/risk.
2. **Load-bearing present** — PRD / feature specs (for UI products, design docs) are in the set.
3. **Production reqs per document** — every document has producer role + tools/providers + skills.
4. **`depends_on` per document** — every document carries its pruned `depends_on`.
5. **Acyclic DAG** — the assembled (pruned) graph has no cycle.
6. **No orphan** — every intermediate document feeds another or is fed by one; leaf deliverables (LICENSE, CHANGELOG, SECURITY.md, README) with `depends_on: []` are exempt.
7. **No padding** — no document the project won't use.
8. **Open-ended preserved** — unrecognized types are researched/forged, not guessed.
9. **(Amend only) the delta is change-scoped** — only changed/added documents + their DAG edges were touched.
10. **Capability areas: 4–10 L1 areas identified**; each passes all three sizing tests.
11. **Per-capability entries: every active capability has `feature-spec-{id}`**; fan-out flags (has_ui, has_api, has_persistence) match the per-capability document entries actually produced.
12. **Manifest output structure** — the returned JSON has a `"manifest"` key (not a root-level document list); each document entry has `type` and `scope` fields.
13. **Meta-sections populated:** `capabilities:` contains `docs` (always) and `design` (if `ui.has_ui: true`); no build-level capability present. `roles:`, `skills:`, `tools:`, and `amendments:` are present — none empty. All skill entries have `version: null` and `source: null`.
14. **`capability` scalar on all document entries:** every document entry has `capability: "docs"` or `capability: "design"` (string scalar), not `capabilities: [...]` (array).

Fix any failed item before returning.

---

### Iteration / amend (re-tailoring an existing plan on a change)

When handed **existing `capability-map.yaml` + existing `manifest.yaml` + a change request**, classify the delta and apply it — do NOT re-derive the plan.

**Amend receives both files as context** — the full existing capability state AND the existing document manifest, not just the change request. This lets the delta target only what needs updating.

**Change-type taxonomy:**

| Type | Description | Structural change | Human gate |
|---|---|---|---|
| T1 | FIELD_ADD: new optional field on existing record | No | No |
| T2 | FIELD_UPDATE: non-identity field update on existing record | No | No |
| T3 | RECORD_ADD: new capability area added to the list | No | No |
| T4 | CAPABILITY_SPLIT: one area becomes two | Yes | **Yes** |
| T5 | CAPABILITY_MERGE: two areas become one | Yes | **Yes** |

**Additive-only invariant (T2 forbidden mutations):** `id` and `name` may not change; `owns` items may not be removed; `has_ui`, `has_api`, `has_persistence` may not go `true → false`; list fields (`refs`, `publishes`, `consumes`, `entry_points`, `exit_points`, `depends_on`) are append-only.

**Two-prompt dispatch:**

1. **Prompt A — Classify:** receives existing `capability-map.yaml` + existing `manifest.yaml` + change request text → returns `{change_type: T1|T2|T3|T4|T5, capabilities_affected: [...], reason, confidence}`.
2. **[GATE]** If `change_type in {T4, T5}` OR `confidence != "high"`: surface to human for confirmation before continuing.
3. **Prompt B — Act:** receives affected capability records + change request → returns `{records: [updated/new CapabilityRecord, ...]}`. Model must omit `level`, `status`, `superseded_by`, `merged_into` — Python-injected.

**Document impact routing per type:** T1 = no fan-out change; T2 = amend feature-spec-{id} (+ add new doc entries if a fan-out flag changed false→true); T3 = add full document set for new capability + amend prd; T4/T5 = supersede old documents, add full sets for new capabilities, amend prd, cascade to capabilities with old ID in `depends_on`/`consumes`/`refs`.

## Rules

**Hard rules (never violate):**

- **Discovery only.** Decide *which* documents and *what it takes* to produce them. Never author or template a document.
- **Proportional, never a fixed taxonomy.** Size the set to the archetype; a thin project gets few documents.
- **Keep the load-bearing documents.** PRD / feature specs (and UI design docs) are never cut to seem lean.
- **Dependencies form a DAG.** Direction is requirements → design → delivery → docs; no cycles.
- **OSS-first tools/providers** (oss → free → paid); local/self-hostable preferred.
- **Research/forge-on-gap an unknown type;** never invent its purpose.
- **Additive-only amend.** In amend mode, do not change identity fields, remove entities, or downgrade fan-out flags. Use T4/T5 (with human gate) for structural changes.

**Preferences (override-able):**

- Group the chosen set by lifecycle band.
- Name the producer as a role kind; use `archetype × domain` where the consumer uses that model.
- For volatile detail (API endpoints, schemas), prefer **generate-and-link** over duplicating in prose.

## Gotchas

- **Heavy fixed taxonomy on a small project.** Cause: skipping Step 1 archetype classification. Fix: classify first, size to it.
- **Cutting load-bearing docs to look lean.** Cause: omitting PRD/feature-spec. Fix: keep the load-bearing band; trim optional bands.
- **Drifting into authoring.** Cause: listing a document's sections. Fix: stop at *which* document + *what it takes*.
- **Cyclic dependencies.** Cause: PRD `depends_on` architecture. Fix: requirements → design → delivery → docs only.
- **Over 10 L1 capabilities.** Cause: treating every noun as a separate area. Fix: merge strongly-coupled areas; add L2 sub-capabilities instead of more L1s.
- **Forgetting the negative clause in `scope`.** Cause: only writing what a capability does. Fix: every `scope` must end with "does NOT…" — it defines the boundary.

## Anti-patterns

- **"Every project needs the full SDLC document set."** No — proportional to the archetype.
- **"While deciding the set, I'll also outline how to write each one."** That is authoring; out of scope.
- **"I don't recognize this document type, I'll guess."** Research or forge-on-gap instead.
- **"Skip the PRD, we'll figure out features in code."** Features must be defined in documents first.
- **"Add a few more documents to be safe."** Padding; stop once the proportional set is complete.
- **"Amend by re-running discovery from scratch."** Amend re-tailors the delta only; do not re-derive.

## Output

**The skill returns one three-key JSON object. The skill does NOT write files. The caller writes two files from this object:**
- `<scope_root>/capability-map.yaml` — from keys `capability_map` + `product_capabilities`
- `<scope_root>/manifest.yaml` — from key `manifest` (all five sections)

`scope_root` is caller-supplied context. The skill never assumes or derives it.

Three-key JSON object returned:

```json
{
  "capability_map": {
    "archetype": { "primary": "web-app", "secondary": ["api-service"] },
    "domain": { "primary": "e-commerce" },
    "scale": { "expected_users": "10k-1m", "traffic_pattern": "bursty" },
    "ui": { "has_ui": true, "ui_types": ["web"], "consumer_facing": true },
    "security": { "auth_required": true, "auth_type": ["jwt"], "pii_involved": true },
    "data_ml": { "has_data_pipeline": false, "has_ml_model": false },
    "regulatory": { "applies": true, "frameworks": ["gdpr", "pci-dss"] },
    "infrastructure": { "deployment_target": "cloud", "cloud_provider": ["aws"] },
    "team": { "team_size": "small", "engineering_maturity": "growing" }
  },
  "product_capabilities": [
    {
      "id": "catalog",
      "name": "Catalog",
      "scope": "Manages product listings, variants, and pricing; does NOT handle inventory or fulfillment.",
      "subdomain": "core",
      "owns": ["product", "variant", "price"],
      "has_ui": true,
      "has_api": true,
      "has_persistence": true,
      "ui_complexity": "consumer-grade"
    }
  ],
  "manifest": {
    "version": 1,
    "generated_at": "<ISO-8601>",
    "schema": "manifest/v1",
    "documents": [
      {
        "id": "prd",
        "title": "Product Requirements Document",
        "type": "prd",
        "scope": "system",
        "capability": "docs",
        "archetype": "strategist",
        "role": "document-author",
        "skills": ["authoring-prd", "deep-research"],
        "depends_on": [],
        "account": null,
        "status": "active"
      },
      {
        "id": "feature-spec-catalog",
        "title": "Feature Spec: Catalog",
        "type": "feature-spec",
        "scope": "catalog",
        "capability": "docs",
        "archetype": "engineer",
        "role": "document-author",
        "skills": ["authoring-feature-spec", "deep-research"],
        "depends_on": ["prd"],
        "account": null,
        "status": "active"
      },
      {
        "id": "wireframes-catalog",
        "title": "Wireframes: Catalog",
        "type": "wireframes",
        "scope": "catalog",
        "capability": "design",
        "archetype": "designer",
        "role": "designer",
        "skills": ["authoring-wireframes"],
        "depends_on": ["system-wireframes", "feature-spec-catalog"],
        "account": null,
        "status": "active"
      },
      {
        "id": "hi-fi-catalog",
        "title": "Hi-fi: Catalog",
        "type": "hi-fi",
        "scope": "catalog",
        "capability": "design",
        "archetype": "designer",
        "role": "designer",
        "skills": ["authoring-hi-fi"],
        "depends_on": ["wireframes-catalog", "design-system"],
        "account": null,
        "status": "active"
      }
    ],
    "roles": [
      {
        "id": "document-author",
        "name": "Document Author",
        "goal": "Produce high-quality, evidence-grounded project documents.",
        "persona": "Senior technical writer and engineer with deep domain expertise. Grounds every claim in research or existing project artifacts. Writes for the next engineer, not for the original author.",
        "skills": ["deep-research", "external-content-sanitizer"],
        "tools": ["web-search", "file-read", "file-write"],
        "model": "claude-sonnet-4-6"
      },
      {
        "id": "designer",
        "name": "Designer",
        "goal": "Produce structural, buildable design artifacts grounded in UX research.",
        "persona": "Senior product designer with UX research and interaction-design expertise. Produces design artifacts that engineering can implement directly. Grounds visual decisions in user research and established design systems.",
        "skills": ["deep-research", "external-content-sanitizer"],
        "tools": ["web-search", "file-read", "file-write", "browser"],
        "model": "claude-sonnet-4-6"
      }
    ],
    "skills": [
      { "id": "authoring-prd", "version": null, "source": null, "category": "authoring" },
      { "id": "authoring-feature-spec", "version": null, "source": null, "category": "authoring" },
      { "id": "authoring-wireframes", "version": null, "source": null, "category": "authoring" },
      { "id": "authoring-hi-fi", "version": null, "source": null, "category": "authoring" },
      { "id": "deep-research", "version": null, "source": null, "category": "research" },
      { "id": "external-content-sanitizer", "version": null, "source": null, "category": "utility" }
    ],
    "tools": [
      { "id": "file-read", "name": "File Read", "type": "file-read", "access": "read-only", "credential_key": null, "auth_type": null },
      { "id": "file-write", "name": "File Write", "type": "file-write", "access": "read-write", "credential_key": null, "auth_type": null },
      { "id": "web-search", "name": "Web Search", "type": "web-search", "access": "read-only", "credential_key": null, "auth_type": null },
      { "id": "browser", "name": "Browser", "type": "browser", "access": "read-only", "credential_key": null, "auth_type": null }
    ],
    "capabilities": [
      {
        "id": "docs",
        "name": "Document Storage",
        "description": "Stores and retrieves text documents produced by the pipeline.",
        "required": true,
        "available_providers": [
          { "id": "local-docs", "name": "Local Docs Backend", "tier": "open-source", "supported": true },
          { "id": "github-docs", "name": "GitHub (docs folder)", "tier": "free", "supported": true },
          { "id": "confluence", "name": "Confluence", "tier": "paid", "supported": false },
          { "id": "notion", "name": "Notion", "tier": "paid", "supported": false }
        ],
        "selected_provider": null,
        "account": null,
        "status": "unassigned"
      },
      {
        "id": "design",
        "name": "Design Tool",
        "description": "Produces and hosts wireframes, hi-fi mockups, and design systems.",
        "required": true,
        "available_providers": [
          { "id": "penpot", "name": "Penpot", "tier": "open-source", "supported": true },
          { "id": "figma", "name": "Figma", "tier": "paid", "supported": false }
        ],
        "selected_provider": null,
        "account": null,
        "status": "unassigned"
      }
    ],
    "amendments": []
  }
}
```

Breaking change from v2.0.0: `manifest.providers` renamed to `manifest.capabilities` (populated, not `[]`); document entries use `capability` scalar (not `capabilities` array); `manifest.roles`, `manifest.skills`, `manifest.tools` are populated from the document set; `manifest.amendments: []` added; `version`/`generated_at`/`schema` headers added.

## Related

- A content/template skill (e.g. `content-template-gateway`) — the **authoring-time** counterpart. Composes with this skill: this one picks the *set*, that one templates *each*.
- A research skill (e.g. `deep-research`) — for researching an unfamiliar document type (Step 7).
- `reviewing-document-discovery` — the dedicated reviewer that gate-checks the output of this skill (self-check items 1–14 single-sourced 1:1 with reviewer conditions 1–14).
- [`references/document-type-catalog.md`](references/document-type-catalog.md) — the document-type universe, per-archetype proportionality table, and typical dependency edges. Load at Phase B Step 4.
- [`references/reference-architectures.md`](references/reference-architectures.md) — 4-signal algorithm, reference architecture table, sizing tests, seam contract filling guide. Load at Phase A Step 2.

## Progressive disclosure

- `references/reference-architectures.md` — 4-signal capability identification algorithm, 10-domain reference architecture table, three sizing tests, seam contract filling guidance. **Load at Phase A Step 2** (identifying capability areas).
- `references/document-type-catalog.md` — the seven-band + four-overlay catalog (name + when-needed + what-it-feeds per type), the per-archetype load-bearing/skip table, and the common `depends_on` edges. **Load at Phase B Step 4** (selecting the document set / domain overlays).
- `references/manifest-schema.md` — self-contained reference for Step 8: provider catalog for `docs`/`design`, role definitions, document-type-to-skill map, document-to-tool map. **Load at Phase B Step 8** (populating meta-sections).
- `references/sources.md` — research provenance for the catalog and the proportionality/dependency guidance. Load only if auditing where the guidance comes from.
- `schemas/capability-map.schema.json` — JSON Schema 2020-12 validator for `capability-map.yaml`. IDE YAML validation reference; runtime validation is Python-side in hq-core.
- `schemas/manifest.schema.json` — JSON Schema 2020-12 validator for `manifest.yaml` (documents[] + the five meta-sections). Single-sourced with `references/manifest-schema.md` and the §Output contract. IDE YAML validation + the deterministic discovery-qa gate; semantic checks (uniqueness, referential integrity, acyclicity, cross-file scope) stay algorithmic.
- `scripts/validate.py` — the deterministic gate: `python scripts/validate.py <capability-map.yaml> <manifest.yaml>` runs JSON Schema validation of both files plus the algorithmic checks (uniqueness, within-file + cross-file referential integrity, `depends_on` acyclicity, ISO-8601 `generated_at`, kept-enum whitespace normalization). Exit 0 = pass; exit 1 + one `FAIL <rule>: …` line per violation. Read-only (never rewrites the files). Requires `pyyaml` + `jsonschema`. Run it after producing the two files and fix every reported failure before treating discovery as complete. See `scripts/validate.py.validation.md`.

## Body budget

- `description` ≤ 1,024 chars (leads with "Use when …").
- Body soft limit: ~1,000 lines / ~10K tokens. Production-grade comprehensive coverage is the target; this is a soft limit, not a hard cap.

## Changelog

- **3.2.0** (2026-06-25) — additive. Schema relaxation + deterministic validator. Both schemas: hard `maxLength` caps dropped → soft guidance in descriptions; the evolving-real-world enums opened to free-text + recommended vocab (`compliance_requirements`, `cloud_provider`, `auth_type`, `skill.category`, `tool.type`); `ui_types` expanded but stays closed (+`voice`/`wearable`/`ar-vr`/`tv`); `owns` `minItems` 1 → 0. Bounded conceptual taxonomies (incl. `expected_users`) stay hard enums; id patterns + structure stay hard. New `scripts/validate.py` (+ `.validation.md`, `test_validate.py`): the deterministic gate — JSON Schema validation of both files plus uniqueness, within-/cross-file referential integrity, `depends_on` acyclicity, ISO-8601, and kept-enum whitespace normalization. SKILL.md gains verbatim-emission guidance for kept enums, recommended-vocab for opened fields, and soft-limit notes. Backward-compatible: every previously-valid document stays valid.
- **3.1.0** (2026-06-25) — additive. New `schemas/manifest.schema.json` (JSON Schema 2020-12), parity with `capability-map.schema.json`, single-sourced with `references/manifest-schema.md` + the §Output contract — `documents[]` plus the five meta-sections. Gives `manifest.yaml` IDE YAML validation and a machine-validatable contract for the deterministic discovery-qa gate. No method/output change.
- **3.0.0** (2026-06-21) — BREAKING. Phase B gains Step 8: populates all five manifest meta-sections (`capabilities:`, `roles:`, `skills:`, `tools:`, `amendments: []`) from the assembled document set using `references/manifest-schema.md`. Document entries: `capabilities: [...]` (array) → `capability: "..."` (scalar string). Manifest output: `providers:` key renamed to `capabilities:` (populated with `docs` + `design` when `has_ui: true`; no build-level capabilities). Output contract explicit: skill returns one three-key JSON object, does NOT write files, caller writes `capability-map.yaml` + `manifest.yaml` to `scope_root`. Self-check extended with items 12 (manifest output structure), 13 (meta-sections populated), and 14 (`capability` scalar). New reference: `references/manifest-schema.md`.
- **2.0.0** (2026-06-21) — BREAKING restructure. Two-phase internal workflow: Phase A (classify project across 10 dimensions + identify product capability areas via 4-signal algorithm); Phase B (fan-out manifest — per-capability document entries with scope + capabilities fields). Output contract changed: three-key JSON `{capability_map, product_capabilities, manifest}` where `manifest` is now nested (was root). Fan-out rules added: feature-spec always; data-model/api-spec/wireframes/hi-fi per flags; wireframes+hi-fi use `design` capability. Amend method updated: receives both `capability-map.yaml` AND `manifest.yaml`; two-prompt pipeline (Prompt A classify T1–T5 → gate T4/T5 → Prompt B produce records); additive-only invariant explicit. Self-check extended: items 10 (4–10 L1 areas, sizing tests) and 11 (per-capability fan-out entries match flags). New reference file `references/reference-architectures.md` loaded at Phase A Step 2. New schema file `schemas/capability-map.schema.json`. Body budget soft limit raised to ~1,000 lines / ~10K tokens.
- **1.3.0** (2026-06-15) — production-grade redesign (additive). Explicit Self-check (nine-item definition of done). Added Iteration / amend method. Named proportionality method (ISO 15289 tailoring + ROI). Re-grounded on ISO/IEC/IEEE 15289 + 12207.
- **1.2.0 / 1.1.0** — catalog expansion (Band 0 + Band 6 + four domain overlays; 5 → 7 lifecycle bands).
- **1.0.0** (2026-06-03) — initial reviewed release.
