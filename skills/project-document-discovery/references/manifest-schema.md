# Manifest schema reference

Self-contained reference for `project-document-discovery` Step 8 — populating all five
`manifest.yaml` meta-sections. Do not read any external file; everything needed is here.

---

## 1. Section schemas (key fields only)

### `capabilities:` entry

```yaml
- id: "docs" | "design"          # closed for doc-production scope
  name: string                   # display label
  description: string            # one sentence
  required: true                 # always true for doc-production capabilities
  available_providers: [...]     # see Section 2 — copy verbatim
  selected_provider: null        # always null at discovery time
  account: null                  # always null at discovery time
  status: "unassigned"           # always unassigned at discovery time
```

### `roles:` entry

A role is a pure, task-agnostic persona. It carries NO `skills` or `tools` — those
are task mechanics resolved from the document entry + top-level sections at dispatch
time, not persona attributes.

```yaml
- id: string
  name: string
  goal: string
  persona: string
  model: string
```

### document-entry `roles:` (in the `documents:` section)

Every document names exactly TWO role ids in `[author, reviewer]` order:

```yaml
roles: [document-author, document-reviewer]   # engineer / strategist archetypes
roles: [designer, design-reviewer]            # designer archetype
```

The order is fixed and validator-enforced (archetype → pair). The document's
`skills:` array likewise carries BOTH the authoring and reviewing skill for its
type (Section 4).

### `skills:` entry

```yaml
- id: string                     # must match skill SKILL.md name: exactly
  version: null                  # always null at discovery time
  source: null                   # always null at discovery time
  category: "authoring" | "reviewing" | "research" | "orchestration" | "utility"
  purpose: string                # optional one-line note
```

Category derivation from id: `authoring-*` → authoring; `reviewing-*` → reviewing;
`deep-research` → research; `external-content-sanitizer` → utility;
`project-document-discovery` / `reviewing-document-discovery` → orchestration.

### `tools:` entry

```yaml
- id: string
  name: string
  type: "web-search" | "file-read" | "file-write" | "code-exec" | "api-call" | "browser" | "mcp"
  access: "read-only" | "read-write"
  credential_key: null
  auth_type: null
```

### `amendments:` — always `[]` on greenfield output.

---

## 2. Provider catalog (advisory — copy verbatim; user may select any provider)

The lists below are starting points. `selected_provider` is always `null` at discovery
time. Users may name any provider supporting the capability, even one not listed here.

### `docs` capability

```yaml
- id: docs
  name: "Document Storage"
  description: "Stores and retrieves text documents produced by the pipeline."
  required: true
  available_providers:
    - id: local-docs
      name: "Local Docs Backend"
      tier: open-source
      supported: true
      credential_type: none
    - id: github-docs
      name: "GitHub (docs folder)"
      tier: free
      supported: true
      registration_url: https://github.com/settings/tokens
      credential_type: pat
    - id: confluence
      name: "Confluence"
      tier: paid
      supported: false
      registration_url: https://developer.atlassian.com/console/myapps/
      credential_type: api-key
    - id: notion
      name: "Notion"
      tier: paid
      supported: false
      registration_url: https://www.notion.so/my-integrations
      credential_type: api-key
  selected_provider: null
  account: null
  status: unassigned
```

### `design` capability

```yaml
- id: design
  name: "Design Tool"
  description: "Produces and hosts wireframes, hi-fi mockups, and design systems."
  required: true
  available_providers:
    - id: penpot
      name: "Penpot"
      tier: open-source
      supported: true
      registration_url: https://design.penpot.app
      credential_type: api-key
    - id: figma
      name: "Figma"
      tier: paid
      supported: false
      registration_url: https://www.figma.com/developers/api
      credential_type: oauth2
  selected_provider: null
  account: null
  status: unassigned
```

---

## 3. Role definitions (copy verbatim; do not improvise field values)

Include the pair for each archetype present in the document set:
- Any document with `archetype: engineer` or `strategist` → include BOTH `document-author` and `document-reviewer`.
- Any document with `archetype: designer` → include BOTH `designer` and `design-reviewer`.

Roles are pure personas — no `skills`/`tools` fields.

### `document-author` (for archetype: engineer or strategist)

```yaml
- id: document-author
  name: "Document Author"
  goal: "Produce high-quality, evidence-grounded project documents."
  persona: >
    Senior technical writer and engineer with deep domain expertise.
    Grounds every claim in research or existing project artifacts.
    Writes for the next engineer, not for the original author.
  model: claude-sonnet-4-6
```

### `document-reviewer` (for archetype: engineer or strategist)

```yaml
- id: document-reviewer
  name: "Document Reviewer"
  goal: "Gate-check project documents against their acceptance bar before they are approved."
  persona: >
    Senior staff engineer acting as an adversarial reviewer.
    Judges a document against its type's acceptance bar, hunting gaps,
    unstated assumptions, and unverifiable claims. Grounds every finding
    in evidence and never rewrites the document under review.
  model: claude-sonnet-4-6
```

### `designer` (for archetype: designer)

```yaml
- id: designer
  name: "Designer"
  goal: "Produce structural, buildable design artifacts grounded in UX research."
  persona: >
    Senior product designer with UX research and interaction-design expertise.
    Produces design artifacts that engineering can implement directly.
    Grounds visual decisions in user research and established design systems.
  model: claude-sonnet-4-6
```

### `design-reviewer` (for archetype: designer)

```yaml
- id: design-reviewer
  name: "Design Reviewer"
  goal: "Gate-check design artifacts for buildability, coverage, and accessibility before they are approved."
  persona: >
    Senior product-design lead acting as an adversarial reviewer.
    Judges a design artifact against its type's buildability and
    accessibility bar, hunting missing states, unbuildable ambiguity, and
    unguarded flows. Grounds every finding in established UX practice and
    never redesigns the artifact under review.
  model: claude-sonnet-4-6
```

---

## 4. Document-type-to-skill map

Each document type maps to BOTH an authoring and a reviewing skill. Both land in TWO places:
1. On the document entry's own `skills:` array (e.g. `skills: [authoring-prd, reviewing-prd]`) — so a consumer dispatching either the author or reviewer pass resolves the skill from the entry.
2. In the top-level `manifest.skills:` registry (deduplicated across documents), plus `deep-research` and `external-content-sanitizer` always. `version: null`, `source: null` for every entry.

| Document type | Authoring skill | Reviewing skill |
|---|---|---|
| `prd` | `authoring-prd` | `reviewing-prd` |
| `feature-spec` | `authoring-feature-spec` | `reviewing-feature-spec` |
| `architecture-doc` | `authoring-architecture-doc` | `reviewing-architecture-doc` |
| `data-model` | `authoring-data-model` | `reviewing-data-model` |
| `api-spec` | `authoring-api-spec` | `reviewing-api-spec` |
| `technical-design` | `authoring-technical-design` | `reviewing-technical-design` |
| `release-runbook` | `authoring-release-runbook` | `reviewing-release-runbook` |
| `wireframes` | `authoring-wireframes` | `reviewing-wireframes` |
| `user-flows` | `authoring-user-flows` | `reviewing-user-flows` |
| `design-system` | `authoring-design-system` | `reviewing-design-system` |
| `hi-fi` | `authoring-hi-fi` | `reviewing-hi-fi` |
| `model-card` | `authoring-model-card` | `reviewing-model-card` |
| `eval-plan` | `authoring-eval-plan` | `reviewing-eval-plan` |

**Note — `model-card` / `eval-plan` skills are not yet built.** They use the prefix
convention (`authoring-{type}`) matching every row above; list them in `manifest.skills`
with `version: null`, `source: null`. The approval/produce-docs gate forges them on first
use (forge-on-gap) — discovery only lists them.

**For types not in this table:** list them as `id: <type>-authoring` / `id: <type>-reviewing`
as a best-effort placeholder; the approval gate will catch missing skills and trigger forging.

**Always include regardless of document set:**
- `deep-research` (category: research)
- `external-content-sanitizer` (category: utility)

---

## 5. Document-to-tool map

Derive `manifest.tools:` from the document types in the set.

| Condition | Tools to include |
|---|---|
| Always (every project) | `file-read`, `file-write` |
| Any text document type is in the set | `web-search` |
| Any design document type is in the set (`wireframes`, `hi-fi`, `design-system`, `user-flows`) | `browser` |

**Text document types** (trigger `web-search`): prd, feature-spec, architecture-doc,
technical-design, data-model, api-spec, release-runbook, user-research-brief,
competitive-landscape-report, and any other non-design document.

**Tool field values for the four standard tools:**

```yaml
tools:
  - id: file-read
    name: "File Read"
    type: file-read
    access: read-only
    credential_key: null
    auth_type: null

  - id: file-write
    name: "File Write"
    type: file-write
    access: read-write
    credential_key: null
    auth_type: null

  - id: web-search
    name: "Web Search"
    type: web-search
    access: read-only
    credential_key: null
    auth_type: null

  - id: browser
    name: "Browser"
    type: browser
    access: read-only
    credential_key: null
    auth_type: null
```
