# The per-angle search output, explained

One angle's result, with the receipts that make it re-runnable.

Schema: `schemas/search-output.schema.json`. Gate:
`validate_visual_prior_art.py search <file> --keyword-map <map>`.

## Three outcomes

| `outcome` | Means | Owes |
| --- | --- | --- |
| `not_run` | The precondition did not hold | A `not_run` block with a reason. **No cells.** |
| `vacated` | The precondition held, but the applicable set came out empty | A `vacated` block. **No cells.** |
| `ran` | The angle executed | Coverage, retrieval summary, bound |

An unrun angle writing empty cells manufactures zeros that read as searches — the most damaging
thing this artifact can do, and the gate rejects it outright. `vacated` is separate because
"nothing was applicable" and "we chose not to run" are different facts, and the gate additionally
rejects a `vacated` claim when the applicable set is demonstrably non-empty.

## The applicable set

```
applicable = { (group, source) : group.type ∈ angle.applicable_group_types
                               ∧ source ∈ angle.sources ∩ map.sources.active }
```

Checked **both ways**: a missing cell is an unexplained gap; a surplus cell means the angle
worked another angle's channels, which duplicates a sibling and inflates this angle's arithmetic.

## Cell statuses

`reached` (requires `returned` + `kept`) · `unreachable` · `partial` · `rate-limited` ·
`forbidden-by-terms` · `content-withheld` · `not-attempted`. Every non-reached status requires a
`cause`.

`partial` is the catch-all for a fetch that succeeded without yielding a clean result set — a
document that rendered with sections missing, or a source that answered without honouring the
query.

**`forbidden-by-terms` versus `unreachable`** carries the most weight: the first is a decision
you made, the second a failure that happened to you. Collapsing them hides a policy choice inside
an outage report. Every screenshot gallery is `forbidden-by-terms` by construction — the modality
lock — and the gate rejects any cell naming one at all.

## Queries

Verbatim, **as run**. A paraphrase cannot be re-run. For a corpus walk the "query" is the
traversal you performed — which index you read, which pages you selected and by what criterion —
recorded precisely enough that someone else reaches the same set.

## returned, kept, and the bound

- `returned` — what the source yielded **for this group's terms**, not the size of the corpus.
  For a search engine that is the result count. **For a corpus walk it is the number of index
  entries matching this group's terms** — walking a thirty-pattern index for one group that
  matches three of them is `returned: 3`, not 30. The convention is load-bearing because
  `kept <= returned` is enforced, so two producers counting differently produce incomparable
  arithmetic.
- `kept` — distinct rows carried forward into `candidates` plus `unadmitted`. The gate enforces
  the arithmetic: **`kept` must equal the number of rows whose `found_by` names this cell.**
  It is frequently far below `returned`, and that is normal — most of a pattern index is not
  relevant to a given project's screens.
- `bound.cap` — **the registry's number for this angle**, sized to the corpus it walks. Not the
  run's to choose: the gate rejects a cap disagreeing with the registry in either direction.
  The caps genuinely differ (b3's clears WCAG's 87 success criteria; b4's is far smaller) because
  a single number cannot be right for corpora of 87, 31, 18 and a handful.
- `bound.hit` — whether it bound. If true, `dropped_note` says what was dropped, in kind; a
  declared hit with candidates *under* the cap is rejected, since a limit that did not bind must
  not be recorded as though it had.

There is **no total queue cap** anywhere. The per-angle limit is the only place coverage is
deliberately bounded, which is why it is recorded so carefully.

## retrieval_summary — the duplication IS the check

It restates the cell statuses and names every degraded source with its cause and, where one was
taken, the registry-declared `fallback_used`. Reconciling the two is how a failure laundered into
a zero is caught. A fallback other than the angle's declared one is rejected — the substitution
belongs to the registry, not the run.

## Candidates

**Admission: a named, retrievable corpus.** A convention is carried only from a corpus with a
resolvable URL and a stated release or date. Blog opinion with no upstream source is unbounded in
supply and uncitable; it goes to `unadmitted` with that reason — recorded, never silently
dropped.

**Identity is corpus-scoped**, and the gate checks the shape per class:

| `id_class` | Form |
| --- | --- |
| `aria-pattern` | `ARIA-<slug>` |
| `wcag-criterion` | `WCAG-<n>.<n>.<n>` |
| `design-system` | `DS-<system>` — **one record per SYSTEM**, its component catalog in the body |
| `deceptive-pattern` | `DP-<slug>` |
| `platform-guideline` | `HIG-<platform>-<section>` |

The design-system form is the one worth care: a record per *component* would produce ~200 records
for what is one governed system, and would push a token tree and a component catalog into flat
frontmatter that cannot hold them.

**Two fields that look alike and are not:**

- `authority` — *who says it*: `normative-standard` > `published-system` > `platform-guideline` >
  `secondary-commentary`. Ranking and dedupe input; **never a cut**.
- `prescriptivity` — *whether it binds*: `normative` or `descriptive`. A success criterion binds;
  one design system's opinion does not. Downstream must not weigh them alike.

**`corpus_version` is required on every candidate.** ARIA APG, WCAG, the design systems and the
token format all version independently, so a convention without its release is not re-checkable
later.

**`token_format`, where claimed**, states the format and version — the downstream consumer reads
DTCG, and the gate rejects a claim in another format or with no version. Wave 1 carries the
*claim*; the tokens themselves are the extract wave's.

## Notes

Vocabulary discovered mid-run, dead ends, and cross-angle leads. A lead belonging to another
angle goes here for the caller to route — chasing it duplicates another worker.

The full fixture is `scripts/fixtures/search-output.valid.yaml`.
