# Producing one extract record

ONE mechanism, read from ONE platform's own corpus, in ONE `.md` file: the YAML frontmatter and the
markdown analysis, never split and never deeply nested.

The shape is deliberately bounded — six top-level keys, one nesting level under `finding`, no
free-form maps. A component-scale payload (a full manifest key list, a policy-clause table) goes in
the BODY, not into a new frontmatter branch.

## Name the file by DERIVING it

```
uv run --no-project python -c "import sys; sys.path.insert(0,'scripts'); \
  import validate_platform_ecosystem_prior_art as V; print(V.record_filename('<your item id>'))"
```

The id is `<platform_id>__<angle>`, and both halves are restated inside `finding` — the gate checks
that a record does not disagree with itself, because every lens groups on `platform_id`. On a
revise round, RENAME the existing file; a second file under a new name is a stray the frozen queue
reports as a row nobody wrote.

## `as_of` and `volatility` are one mechanism, not two fields

`as_of` is **when the fact was true**, never when the file was written. `volatility` is what makes
that actionable: it tells a later reader which records rot first.

| value | what it means | how fast it rots |
| --- | --- | --- |
| `contractual` | revenue share, fee thresholds, billing rails | months |
| `policy` | review rules, enforcement posture | with regulation |
| `technical-reference` | manifest keys, API surfaces | per release |
| `historical` | a completed migration timeline | never |

Without `volatility`, every record looks equally fresh and a report inherits a stale contractual
number in silence. The synthesis gate refuses a decision resting on a contractual record more than
90 days older than the index, unless the row carries a staleness marker.

## `corpus.version: retrieved-only` is an explicit value, not a fallback

Use it when the page states no date, states an implausible one, or contradicts itself. Three pages
verified on this corpus are each one of those: one shows two conflicting dates on the same page,
one shows a footer date years before the thing it documents existed, and one carries no date at all
while describing itself as a living document.

Writing a date you inferred, or silently using `retrieved_at` as though it were the page's own, is
the failure this value prevents. Where a platform publishes its dates elsewhere, take the date from
there and say so in the body.

## `evidence_quote` is the receipt, and it is structural

A short verbatim quote. It is in the schema so that a record **cannot** assert a revenue-share
percentage without carrying the sentence it came from. A paraphrase is not a receipt: the
convergence lens groups on what platforms independently STATE, and a paraphrase makes two different
statements look identical.

## `enumeration_count` — a number, or null

An integer on an enumerating record, null on every other. The surface-size lens computes minimum,
median and maximum on it, and the recommendation it produces is the MINIMUM surface any comparable
platform shipped. "Many contribution points" is not a number, and the gate refuses a count carried
by a record whose angle never enumerated.

## `announced_on` and `enforced_on` — a4 only

The migration-debt lens divides by the interval between them. Both are nullable and both are a4
only; the gate refuses them elsewhere and refuses an enforcement that precedes its announcement,
because a negative interval is not a short runway.

## `reversibility` is a JUDGEMENT, and it is yours to make honestly

`cheap`, `costly`, `one-way`. The gate checks only that it is present and in the enum — whether the
judgement is right is a reviewer's condition, deliberately, because it is exactly the kind of call a
deterministic check cannot make.

Ask what it would cost to undo the decision AFTER launch. A billing relationship with users is
one-way. A pricing tier is costly. A manifest key is usually cheap.

## `authority` ranks; it never cuts

`first-party-normative` is what the platform prescribes in its own normative documentation, and
convergence requires **two independent** such records agreeing. The other bands are still recorded
— the relevance bail is the only cut this survey makes.

## A bail STILL WRITES the record

`outcome: skipped` with a typed cause — `mechanism-not-present`, `touches-no-capability`,
`corpus-unreachable`, `forbidden-by-terms` — and a `detail` naming what you checked. No `finding`,
and no body is owed: the cause is the whole record.

## The body

Everything a reader needs that the frontmatter cannot hold: what the platform prescribes in
context, the receipt read alongside its page, and why the reversibility call is what it is. A record
whose body is empty has shipped its machine half alone, and the gate refuses it.

## Then run the gate

```
uv run --no-project --with pyyaml --with jsonschema python scripts/validate_platform_ecosystem_prior_art.py \
  extract extracts/extract-<stem>.md
```
