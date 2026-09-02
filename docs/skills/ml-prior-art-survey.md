# `ml-prior-art-survey`

Survey the published ML artifact corpus — models, datasets, benchmarks, hosted endpoints — before
deciding whether to call an API, fine-tune, or train from scratch.

**Wave 1 only.** Two kinds: the ML task vocabulary map, and one search angle's output. The extract
and synthesis waves are not in it, and nothing here produces a recommendation — it produces a
searched, recorded corpus that a later wave turns into one.

## The organising idea

The evidence for this decision is unusually public. Model cards, dataset sheets, leaderboards and
vendor pricing are all published, versioned, and almost never gathered before the architecture is
chosen. Teams rediscover by accident what four vendors wrote down.

The problem is not access. It is that **an option that does not exist and a search that never ran
look identical downstream** — and this corpus makes that failure especially easy, because it moves
faster than any sibling's. The lead source this survey was designed around is gone: its leaderboard
corpus now redirects to an unrelated feed. A second channel was open at design time and returns 401
today. A survey that does not record its own retrieval is worthless six months later.

So the coverage grid is the product. Every query recorded as it was run, a zero written down rather
than omitted, and a `count_frame` on every count — because one Hub query yields a different number
by page size, by dedup rule, and by whether variants count as one model or several.

## Two procedures

**Procedure 1 — the ML task vocabulary map.** Built before any searching, over **eight axes**:
`ml-task` (the HuggingFace `pipeline_tag`), `modality`, `domain-term`, `benchmark`, `dataset`,
`method`, `runtime-format` and `harm-category`. Each angle declares which axes it searches, and
that is what makes the coverage grid derivable.

`pipeline_tag` is a **borrowed vocabulary and is marked borrowed**. A task the Hub does not name is
recorded with the Hub's nearest tag AND the domain term, never invented — the corpus is indexed by
the Hub's words, and a term the index has never seen returns an empty set that looks exactly like
an absent capability.

The map also gives every one of the nine angles a verdict. `holds` is the precondition evaluated
over **the scope**, not over the corpus — and an always-on angle can never be false, because it has
no precondition to fail.

**Procedure 2 — one search angle.** Nine angles, five always-on:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 model-registry enumeration | always | 40 |
| a2 dataset and training-corpus enumeration | always | 30 |
| a3 leaderboard and evaluation-result retrieval | always | 25 |
| a4 literature and preprint recency walk | always | 30 |
| a5 hosted-inference catalogue and pricing | always | 20 |
| b1 training and fine-tuning cost | `ml_involvement in {fine-tunes, trains-from-scratch, multi-model}` | 20 |
| b2 safety and responsible-AI evaluation | `regulatory.applies` OR `eu_ai_act.risk_level in {unacceptable, high}` | 20 |
| b3 serving-performance evidence | `real_time in {near, hard}` OR `concurrency in {high, extreme}` OR `availability_target in {99.99, 99.999}` | 20 |
| b4 on-device and constrained-runtime | `geo_distribution = edge` OR `archetype.primary in {mobile-app, embedded-iot, desktop-app, browser-extension}` | 20 |

## The coverage grid is 2-D, and its owed set is derived

```
groups = the map's groups whose type is in the angle's applicable_group_types
owed   = {(g, s) for g in groups for s in the angle's OWN sources ∩ the map's ACTIVE sources}
```

Three terms, not two. Dropping the angle's own source list turns a12-cell grid into a 72-cell one,
and a1 would owe a cell for every source in the registry rather than the three it declares.

`returned` counts ITEMS under a stated frame; `kept` counts candidate ROWS carried into
`candidates` **plus** `unadmitted`, per cell. That equality is what makes a row found and dropped
*without* a record impossible — which is the entire purpose of the `unadmitted` list.

## A rank is not a quality signal

It is a claim under a stated evaluation, on a stated split, at a stated date. The benchmark and the
split are required; `test` and `validation` are different numbers and a table that does not say
which cannot be compared to anything. Where the table publishes no date, `measured_on: null` is the
honest record — an undated result is still evidence, and discarding it would throw away the measured
comparison this survey exists to gather.

**Authority ranks, never cuts.** A vendor's own benchmark is recorded with `authority:
vendor-published` and ordered below an independent one, never excluded for being a vendor's. Using
authority as a filter is how a survey quietly becomes an opinion.

## An adoptable artifact, or it is not a record

A model, a dataset, a benchmark, a hosted endpoint. **Not a paper** — a paper cannot be adopted, and
its identifier belongs in `provenance.arxiv_id` on the artifact it introduced. **Not a regulation**
either: the instruments b2 cites are provenance for why a harm axis is in scope, and filing one as a
candidate is the category error that angle is most prone to.

## The deterministic gate

`scripts/validate_ml_prior_art.py` checks shape across 40 rules and exits 0 clean, 1 the artifact
has findings, 2 it could not be used at all. The exit-2 class is load-bearing: a malformed registry,
a missing dependency, an unusable `--keyword-map`, or an artifact naming an angle that does not
exist are all faults in the invocation or the package, and reporting them as exit 1 sends an author
off to edit a file that is fine.

It needs `pyyaml` and `jsonschema`:

```
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_ml_prior_art.py keyword-map <your map>
```

One limitation stated rather than papered over: `holds` cannot be fully machine-checked, because the
map records the scope as prose and `assumptions` rather than as the structured fields the registry's
predicate is written against. The deterministic half ships — always-on verdicts, completeness,
uniqueness, unknown angles — and the judgement half stays a reviewer condition.

## Companion

[`reviewing-ml-prior-art-survey`](reviewing-ml-prior-art-survey.md) — the judgement half of the same
gate.
