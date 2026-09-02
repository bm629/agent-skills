# Writing the ML task vocabulary map

The map is a **search protocol**, not a glossary and not a findings document. It decides what the
nine angles will search for and which of them run at all. Nothing in it claims what a model does —
that is the search wave's, with a source attached.

## The eight axes

Every group sits on exactly one axis, and each angle declares which axes it searches. That is what
makes the coverage grid derivable: the angle's `applicable_group_types` selects the groups, the
angle's own source list selects the columns.

| axis | holds | populated by |
| --- | --- | --- |
| `ml-task` | the HuggingFace `pipeline_tag` and the capability it serves | every scope |
| `modality` | text · image · audio · tabular · time-series · graph · multimodal | every scope |
| `domain-term` | the domain's own words for the task | every scope |
| `benchmark` | benchmark and evaluation-suite names | scopes with published evaluations |
| `dataset` | dataset and training-corpus names | scopes that will train or evaluate |
| `method` | architecture and training-approach terms; model SCALE as expansions | scopes that will fine-tune or train |
| `runtime-format` | runtime, serialization format, quantization, device class | scopes that serve under a constraint |
| `harm-category` | the safety, bias and robustness axes | scopes with regulatory exposure |

An axis a searching angle needs must be either POPULATED or listed in `scope_guard.absent_types`.
An unaccounted axis is indistinguishable from one nobody thought about.

## A term sited in two groups is DECLARED, not forbidden

A term can honestly belong to two axes — `LEDGAR` is a contract corpus in its own right AND a
LexGLUE subtask — so nothing here tells you to drop one. But `canonical` and every `expansion` name
a query, and a term in two groups issues that query in two CELLS. `item_id` is unique across the
whole search output, so whatever both cells surface gets filed under one of them and is simply
missing from the other, whose `kept` then under-counts with nothing recording why.

List it in `scope_guard.shared_terms` with the groups it reaches and the `owner` that takes the
artifact. The losing cell's `unadmitted` then has somewhere to point:

```yaml
  shared_terms:
    - term: LEDGAR
      groups: [contract-corpora, lexglue]
      owner: contract-corpora
```

Matching folds case and whitespace, so `LEDGAR` and ` ledgar ` are one term. The `owner` must be
one of the groups the term actually reaches — a declaration that does not resolve reads as handled
and is worse than none.

## `pipeline_tag` is borrowed, and it is marked borrowed

`canonical` on an `ml-task` group is the HuggingFace tag verbatim, and `borrowed_from` says so. A
borrowed name that is not marked reads as ours, and then nobody re-checks it when the upstream
vocabulary moves.

**A task the Hub does not name is recorded with the Hub's NEAREST tag plus the domain term, never
invented.** An invented tag reaches nothing: the corpus is indexed by the Hub's vocabulary, and a
term the index has never seen returns an empty set that looks exactly like an absent capability.

## Expansions, caps and negative terms

`expansions` are the other ways the thing is named — vendor synonyms, domain words, and for a
`method` group its model-scale variants. A single-term query on a vocabulary axis reaches only the
corpus that already uses your word.

`expansion_cap` bounds how many any one query may carry, because an unbounded expansion set turns
one query into an unreviewable sweep.

**`ml-task`, `domain-term` and `method` groups must carry at least one expansion.** Those are the
axes where the corpus and the scope use different words, and a single-term query on one of them
reaches only the corpus that already happens to use yours. `modality` and the rest are exempt —
`text` has no synonym worth querying, and demanding one produces an invented term, which is worse
than none.

`negative_terms` are what make a hit NOT this group. Required on `domain-term` groups, which is
where the homonyms live: `transformer` reaches electrical engineering, `bert` reaches a muppet.

## The verdicts

Every registry angle gets one, including the ones that do not hold. `holds` is the precondition
evaluated over **the scope** — not "is this angle worth running", and not "does some model in the
corpus satisfy it".

**An always-on angle can never be `holds: false`.** It has no precondition to fail, so a false
verdict there is not a judgement about the scope; it is an angle being dropped with no predicate
behind it.

For a disjunctive precondition, the reason must account for the leg that DECIDES the verdict.
Establishing one leg and reporting the verdict of another is the commonest way a verdict
contradicts its own reason.

## Worked example

A different scope from the one `SKILL.md` uses, deliberately — two worked examples that read one
input two ways is how an agent ends up with the opposite map and never sees the choice.

```yaml
schema_version: 1
meta:
  retrieved_at: "2026-09-02"
  revision: 1
  scope_ref: "an on-device photo app adding subject detection and background removal, consumer, edge deployment"
groups:
  - id: object-detection
    type: ml-task
    canonical: object-detection
    borrowed_from: huggingface-pipeline-tag
    expansions: [subject detection, instance detection]
    expansion_cap: 3
    negative_terms: []
  - id: image-segmentation
    type: ml-task
    canonical: image-segmentation
    borrowed_from: huggingface-pipeline-tag
    expansions: [background removal, matting, salient object segmentation]
    expansion_cap: 4
    negative_terms: []
  - id: modality-image
    type: modality
    canonical: image
    expansions: []
    expansion_cap: 1
    negative_terms: []
  - id: on-device-photo
    type: domain-term
    canonical: on-device photo editing
    expansions: [mobile photo app, camera roll]
    expansion_cap: 3
    negative_terms: [photo printing, stock photography]
  - id: mobile-runtimes
    type: runtime-format
    canonical: coreml
    expansions: [tflite, onnx, ggml, int8 quantization]
    expansion_cap: 5
    negative_terms: []
probe:
  ran: true
  note: >
    Probed `image-segmentation` against huggingface-hub-api: 200 with a populated first page. The
    runtime-format axis returned far less, which is why b4 exists as its own angle rather than as a
    filter on a1.
scope_guard:
  excluded:
    - item: text-to-image generation
      reason: >
        The scope edits photos the user already has. A generative model would be surveyed against a
        requirement the scope does not have and would compete for a1's cap with models it can use.
  absent_types: [benchmark, dataset, method, harm-category]
angle_applicability:
  - angle_id: a1
    precondition: always applicable
    holds: true
    reason: Always-on; it has no precondition to fail, and both task groups are populated.
  # ... a2..a5 likewise, each with its own reason ...
  - angle_id: b4
    precondition: >
      scale.geo_distribution = "edge" OR archetype.primary in
      {mobile-app, embedded-iot, desktop-app, browser-extension}
    holds: true
    reason: >
      The scope declares geo_distribution = edge, which satisfies the FIRST leg on its own — so the
      verdict is decided there, and archetype.primary = mobile-app is a second reason rather than
      the deciding one.
sources:
  active:
    - id: huggingface-hub-api
      release: null
      as_of: null
      access_status: open
      sanitization:
        status: clean
    # ... every source an APPLICABLE angle declares appears here or under `skipped` ...
  skipped:
    - id: hf-croissant
      cause: "HTTP 401 — gated as of 2026-09-01; a key-less child cannot read it."
assumptions:
  - >
    "background removal" is read as image-segmentation rather than as a distinct task, because the
    Hub has no `background-removal` tag and inventing one would reach nothing.
notes: []
lineage:
  derived_from: null
  changed: []
```

Note what the b4 reason does: it names WHICH leg decided. A reason that established
`archetype.primary` and reported the verdict would leave a reader unable to tell whether the edge
declaration mattered.
