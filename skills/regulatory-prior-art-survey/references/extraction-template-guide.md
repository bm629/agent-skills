# Producing one extract record

ONE instrument, deep-read into its obligations, in ONE `.md` file: YAML frontmatter plus the
markdown body. The frontmatter stays FLAT — nested machine structure means the record wants to be
JSON, and this one is meant to be read.

**Throughout this survey, `requirement` means a LEGAL OBLIGATION — never a product requirement.**
The word is overloaded across engineering documents, and reading it the other way grades the wrong
thing.

## Name the file by DERIVING it

```
uv run --no-project python -c "import sys; sys.path.insert(0,'scripts'); \
  import validate_regulatory_prior_art as V; print(V.record_filename('<your instrument id>'))"
```

The seven id prefixes are `CELEX-`, `CFR-`, `USC-`, `NIST-`, `ISO-`, `STD-` and `WEB-`.

**A candidate is never given an id it did not read.** Where an instrument has no registry
identifier, `WEB-` is the honest fallback. **Inventing a registry number is the single worst thing
this survey can do** — it produces a citation that resolves, to the wrong law.

Note what is a FIELD and not a filename: an `eli` URI contains slashes, and a `cfr_citation`
contains spaces and dots. Both are stored; neither names the file.

## Two dates, and they are different facts

`as_of` is **the date the TEXT was true** — the consolidation date. `retrieved_at` is when you
fetched it. Collapsing them makes a five-year-stale consolidation look current, which is the whole
reason the currency lens exists.

`in_force_date` and `applies_from_date` are also different, and the difference is load-bearing:
staged application is common, and an instrument that binds in fourteen months is an **architecture
constraint now** and a **compliance obligation later**. The report distinguishes them, so the record
must.

## `applies_because` names why it binds THIS product

"Healthcare products must comply with the health-privacy statute" is true of a category and
establishes nothing about this one. What binds is a scope condition: what the product does, with
whose data, in which jurisdiction. Write that, and put the sentence it rests on in
`scoping_evidence`.

## `verbatim_anchor` is SHORT

A quoted phrase, never the whole provision. The whole provision is a licence problem and is not
extraction.

## `stated_standard` may be NULL, and often should be

"Appropriate", "reasonable" and "state of the art" are **not specifications**. Reproducing them as
though they were is how an instrument that deliberately declined to specify becomes a requirement
this survey invented. A null here is a fact the conflict lens reads.

## `text_retrievable: paywalled` is a legitimate terminal state

A record may name the instrument, set `paywalled`, and carry **no quoted requirement at all**.
*"This standard applies here and its text costs money to read"* is a genuine finding an
architecture document needs.

**Never paraphrase a paywalled clause.** The gate refuses a verbatim anchor on a text recorded as
unreachable, and paraphrasing one is the fabrication failure this type must not have.

## `dimension` is a CLOSED enum, and each member declares its comparator

| dimension | unit | ordered? | "stricter" means |
| --- | --- | --- | --- |
| `encryption_strength` | algorithm + key bits | yes | more bits within one algorithm class |
| `retention_floor` | ISO-8601 duration | yes | LONGER |
| `erasure_deadline` | ISO-8601 duration | yes | SHORTER |
| `breach_notification_deadline` | ISO-8601 duration | yes | SHORTER |
| `audit_log_retention` | ISO-8601 duration | yes | LONGER |
| `consent_basis` | enum | **no** | not comparable — a CONFLICT, never a merge |
| `residency_constraint` | jurisdiction set | **no** | not comparable — a CONFLICT, never a merge |

Durations are stored ISO-8601 (`P7D`, `P6Y`, `PT72H`), which removes the unit-parsing step
entirely — it is what lets hours be compared against years. A duration on a dimension not measured
in one is refused: it is a value in a unit that dimension has no comparator for.

**A dimension marked not-comparable NEVER merges.** Two obligations disagreeing there go to the
conflict section. Resolving them to a "stricter" value invents an ordering the law does not have.

## Requirement ids extend their instrument

`<instrument_id>#r<N>`, minted after the read. The prefix is how synthesis groups by instrument, so
an id that does not extend its own instrument's orphans the requirement from every group it belongs
to. The gate refuses a mismatch.

## Ambiguity is declared, not resolved

`interpretation_confidence` is `clear`, `uncertain` or `ambiguous`. **`ambiguous` implies
`requires_counsel: true`, and the gate checks it.** An obligation this survey could not read
unambiguously is precisely the one it must not settle on its own.

## `control_ids` are OSCAL lowercase-dotted

`at-2.2`, never the prose casing `AT-2(2)`. Both spellings are real and refer to the same control,
so mixing them silently splits a merge group in two.

## A bail STILL WRITES the record

`outcome: skipped` with a typed cause — `out-of-scope`, `superseded`, `not-retrievable`,
`duplicate-of`, `not-an-instrument` — and a detail naming what you checked.

## The four body sections, fixed and in order

`## Scope and applicability` · `## Requirements` · `## What this does not establish` ·
`## Retrieval and limits`

**The third matters more here than anywhere.** An obligation to protect data does not establish
which algorithm. A maximum fine does not establish likely exposure. An instrument applying to a
sector does not establish that it applies to this product's role within it. Write what your reading
does NOT support, because the next reader will otherwise assume it does.

## Then run the gate

```
uv run --no-project --with pyyaml --with jsonschema python scripts/validate_regulatory_prior_art.py \
  extract extracts/extract-<stem>.md
```

## The fields not covered above, each with what it is for

`short_name` is the working name a reader recognises; `source_url` is where you read the text.
`out_of_unit_count` and `out_of_unit_criterion` record how many obligations you deliberately left
out of unit and the rule you applied — a count with no criterion is a number nobody can check.
`duration_value` carries the ISO-8601 duration for a timing obligation and null everywhere else.

The frozen queue's own rows carry `frozen_at` and, per row, `location` and `found_by_angle`: where
the instrument was found and which angles admitted it, comma-joined because every spawn param is a
string.
