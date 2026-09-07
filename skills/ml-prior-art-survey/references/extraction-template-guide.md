# Producing one extract record

One admitted artifact, deep-read, in two files: the record `extract-<stem>.yaml` and its companion
`extract-<stem>.md`. Both derive from ONE stem, and the stem comes from `record_filename`.

## Name the file by DERIVING it, never by writing the id out

```
uv run --no-project python -c "import sys; sys.path.insert(0,'scripts'); \
  import validate_ml_prior_art as V; print(V.record_filename('<your item id>'))"
```

`record_filename` returns an id unchanged when it is already filename-safe and does not already
look like a hashed stem, and otherwise returns a sanitized prefix joined to a 12-hex digest of the
WHOLE id. Two worked examples, one of each branch:

| item id | stem |
| --- | --- |
| `BENCH-mmlu-pro` | `BENCH-mmlu-pro` |
| `HF-meta-llama/Llama-3.1-8B-Instruct` | `HF-meta-llama-Llama-3.1-8B-Instruct--<12 hex>` |

**Most names here will carry a digest, and that is correct.** `HF-`, `HFD-` and `DOI-` ids
essentially always contain a slash, so the sanitizing branch is the ordinary case in this survey
rather than a corner. A slash written into a filename becomes a directory, and the record lands
where nothing looks.

On a revise round, **RENAME** the existing file. A second file under a new name is a stray the
cross-check reports.

## The seven prefixes

`HF-` a Hub model · `HFD-` a Hub dataset · `API-` a hosted vendor model · `OPENML-D-` / `-T-` /
`-F-` an OpenML dataset, task or flow · `DOI-` a DOI deposit · `BENCH-` a benchmark, on a slug we
mint · `WEB-` anything with a resolvable locator and no registry identity.

**A paper is never a record.** An artifact's paper travels on the artifact's row, in
`provenance.arxiv_id` or `provenance.doi`. A model's code lives in `provenance.code_url` and a
benchmark's harness in `benchmark.harness_url` — neither gets a row of its own.

**A minted `BENCH-` slug may not contain `--`.** The schema enforces it with a pattern rather than
asking you to remember: a slug carrying `--` would hand the filename helper's identity branch the
one input its guard exists to catch.

## The spine every record carries

`schema_version`, `meta{item_id, as_of, revision, found_by}`, `outcome`, and `provenance` — all
three of `arxiv_id`, `doi` and `code_url`, explicitly null where the artifact has none.

`as_of` is **the point in time the fact was true**, never the time you wrote it down.

`found_by` is the comma-joined angle list you were handed, carried verbatim. It is the
corroboration signal, and every spawn parameter is a string.

An **extracted** record additionally owes `kind`, `authority` and `score`, and exactly one payload
matching its `kind`. The schema leaves those optional because a skipped record has none of them;
a rule requires them the moment `outcome` is `extracted`.

## Bail honestly — and a bail STILL WRITES the record

A `skipped` record carries `skipped{cause, detail}` and no payload. The causes are typed:
`serves-no-scope-capability`, `no-resolvable-locator`, `access-gated`, `unreachable`, `superseded`,
`duplicate-of`. The `detail` names what you actually checked.

A queue row that produced no file at all is indistinguishable from a spawn that never ran, which is
the defect this rule exists for.

## Borrowed fields, and who owns each

Where a standard already names a field, this record uses that name so the two can join. Read the
owner's definition before deciding a value is wrong.

| block | owner |
| --- | --- |
| `model.task` | the Hub's `pipeline_tag` vocabulary, VERBATIM |
| `model.library_name`, `base_model`, `base_model_relation`, `license_*` | Hub model-card metadata |
| `model.downloads`, `likes`, `last_modified` | the Hub API's `downloads`, `likes`, `lastModified` |
| `model.results[]` | Hub eval-results plus `model-index` |
| `model.considerations` | CycloneDX 1.6 `modelCard.considerations` |
| `model.governance` | the SPDX 3.0.1 AI profile |
| `dataset.name`, `description` | schema.org `Dataset` |
| `dataset.size_reported`, `rows`, `modality` | the SPDX Dataset profile |
| `dataset.splits_defined` | Croissant `cr:Split` |
| `dataset.provenance_block`, `annotation`, `known_bias`, `limitations`, `intended_use_cases`, `pii_or_consent_noted` | Croissant RAI, plus the SPDX Dataset profile |

**Where `croissant_present` is true, the dataset blocks above are READ, not authored.** The record
transcribes what the Croissant file states. Composing a plausible collection process for a dataset
whose Croissant record says something else is a fabrication with a standard's name on it.

`model.serving`, `model.cost`, `model.availability`, `params_reported`, `context_window`,
`artifact_formats`, and the benchmark payload's `harness` and `harness_version` are **ours** —
nothing supplies them. Harness identity in particular is what no standard carries, and an
evaluation whose harness is unnamed is not reproducible.

## Numbers travel as the source words them

`params_reported` is a string because `7B`, `7 billion` and `6.74e9` are three different
statements and only the source's own is evidence. `results[].value` is a string for the same
reason. Never convert, round, recompute or pool — the lens downstream is forbidden from doing it
too, and the record is where that discipline starts.

`results[].reported_by` is `third-party`, `vendor` or `unstated`. The second rung of the adoption
ladder requires `third-party`, so this field decides an outcome and guessing it decides one wrongly.

Every point-in-time figure carries its own date: `results[].as_of`, `cost.as_of`.

## Three-state fields, and why they are not booleans

`dataset.pii_or_consent_noted` is `yes | no | unstated`. `benchmark.held_out_split` and
`contamination_noted` are the same three. A boolean asserts a fact about the artifact wherever the
truth is that its documentation is silent — and turning your own unread page into a finding about
someone else's work is the failure the third state prevents.

## The companion body — seven headings, fixed

`## What it is` · `## Fit to our capabilities` · `## Evidence` · `## Licence and use restrictions`
· `## Cost and serving` · `## Risks and limitations` · `## Verdict rationale`

The gate checks that all seven are PRESENT. Whether the verdict follows from the findings is a
reviewer's judgement, and deliberately not the gate's: the gate needs no scope input, which is what
keeps it runnable anywhere.

A skipped record owes no body. It has stated its cause, and there is nothing to write seven
sections about.

## Then run the gate

```
uv run --no-project --with pyyaml --with jsonschema python scripts/validate_ml_prior_art.py \
  extract extract-<stem>.yaml
```
