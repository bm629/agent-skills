# Extract output guide (frontmatter fields)

`schemas/extract-output.schema.json` is authoritative; this guide explains it. Where the two
disagree, the schema wins and this file is the bug.

The frontmatter is deliberately machine-small and diffable. Anything long — the component
catalog, the token block, the quoted evidence — lives in the body (see
`extraction-template-guide.md`), so a schema change never becomes a migration of prose.

## Always present

| Field | Meaning |
|---|---|
| `schema_version` | `1`. |
| `meta.item_id` | The frozen queue row's canonical id this record answers, verbatim. The filename is derived from it, not equal to it. |
| `meta.as_of` | When the corpus was read. A convention statement without a date silently means something else a year later. |
| `meta.revision` | 1 on first write; incremented when a review round rewrites the record. |
| `outcome` | `extracted` or `skipped`. |

`extracted` requires `convention` and forbids `skipped`; `skipped` requires `skipped` and forbids
`convention`. The schema enforces both directions, so a record cannot claim a result and a bail at
once.

## `skipped` — the bail

| Field | Meaning |
|---|---|
| `skipped.cause` | `touches-no-capability` (the L-6 relevance bail — requires confidence; uncertainty keeps the source), `corpus-unreachable` (a retrieval failure, never a finding of absence), `not-a-convention`, `forbidden-by-terms`. |
| `skipped.detail` | Why, in your own terms, ≥10 characters. A bare cause code is a verdict without evidence. |

`corpus-unreachable` and `touches-no-capability` are different claims and downstream reads them
differently: the first says the corpus was not seen, the second says it was seen and does not
bind. Collapsing them loses the distinction the whole survey is built on.

## `convention` — the extracted record

| Field | Meaning |
|---|---|
| `id` | Canonical convention id. |
| `id_class` | `aria-pattern`, `wcag-criterion`, `design-system`, `deceptive-pattern`, `platform-guideline`. |
| `name` | Human name as the corpus gives it. |
| `corpus.name` / `corpus.version` / `corpus.url` / `corpus.retrieved_at` | The admission rule: a named, retrievable corpus with a resolvable URL and a stated version or date. A convention asserted by a listicle with no upstream source is an unadmitted candidate in the search output — it never becomes a record. |
| `authority` | `normative-standard` > `published-system` > `platform-guideline` > `secondary-commentary`. Recorded, never a cut: downstream must not weigh a listicle against a W3C recommendation, and a normative source disagreeing with an opinionated one must survive into the register. |
| `prescriptivity` | `normative` (the corpus says you must) or `descriptive` (the corpus reports what is done). |
| `statement` | One line: what the convention requires, in the corpus's terms. Set out properly in `## Statement`. |
| `governs` | The component or interaction pattern it governs. |
| `applicability.applies` / `applicability.basis` | Whether it binds this project, and the capability-map field or archetype fact the verdict rests on. `applies: false` with a basis is a real result and stays in the register. |
| `tokens_in_body` | True when the body carries a ` ```dtcg ` block. Only design-system records carry one. |
| `i18n.bidi` / `i18n.notes` | Internationalization is a FIELD on these records, not its own angle. |

## `notes`

Cross-angle leads and observations that are not this record's convention. A lead belongs here,
never as a second record — the unit is one convention source.
