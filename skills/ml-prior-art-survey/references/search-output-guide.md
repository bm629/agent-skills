# Writing one angle's search output

You are ONE child of a survey, running ONE assignment. You never run the whole survey and never
read another angle's output.

## The coverage grid is the product

Not the candidates. The grid is what makes "no such model exists" distinguishable from "nobody
looked", and downstream that distinction is the whole value of the survey.

**One cell per owed (group × source) pair.** The owed set is DERIVED, never every group against
every source:

```
types  = your angle's applicable_group_types
groups = the map's groups whose type is in `types`
owed   = {(g, s) for g in groups
                 for s in your angle's OWN sources ∩ the map's ACTIVE sources}
```

A pair in the owed set with no cell is an unexplained gap. A cell OUTSIDE the owed set is one
group's evidence filed under another angle's mechanism.

## Queries are recorded verbatim, whatever the channel

Several sources here are APIs, so a "query" is the request you issued — and, where you filtered the
response, the expression you filtered with. Both halves, or a reader cannot reproduce your number.

A paraphrase cannot be re-run, and a coverage record that cannot be re-run proves nothing.

**A `not-attempted` cell still owes a `queries` entry**, and the convention is to record what you
WOULD have run, marked as not run:

```yaml
queries: ["(not attempted) would have been https://huggingface.co/models?search=support+ticket"]
```

That is not a paraphrase — it is the request, plus the fact that it was not issued. It matters most
where a source permits no request that fits your axis at all: Zenodo takes ids and DOIs and forbids
site search, so an a2 term-axis cell records the request it could not legitimately make and the
cause that says so. Fabricating a runnable-looking query there would be worse than the gap.

## The two counts, and why both need a frame

`returned` counts ITEMS the source gave you, under the frame `count_frame` states. `kept` counts
candidate ROWS you carried forward into `candidates` **plus** `unadmitted`.

They are different units on purpose. Forty models returned can produce two candidate rows; the
count of things inside one row lives in that row.

**`count_frame` is required whenever `returned` is above zero.** This corpus yields several
defensible counts for one page — first page or all pages, deduplicated by repo or by name, MV3
keys only or every key — and a count whose frame is missing cannot be re-derived by anyone.

**`kept` must EQUAL** the candidates naming that cell plus the `unadmitted` rows naming it. That is
an equality, not a direction: counting only candidates would score a row you found and dropped
without recording as correct, which is precisely what `unadmitted` exists to prevent.

## Statuses, and the two this corpus actually produces

`gated` is new in this type and is its characteristic failure: a source that answered last month and
now demands a key. The fetch COMPLETED and was refused — it is neither `unreachable` nor
`forbidden-by-terms`. This type lost one channel to gating and one to a redirect — two losses,
and recording the redirect as `gated` would erase the difference.

`rate-limited` is a normal operating condition for the shared academic pools, not an outage and
never a searched zero.

`superseded` is a 301 to a live replacement: the fetch SUCCEEDED, and recording it as `unreachable`
hides that the corpus is moving under the survey.

Every non-`reached` cell owes a cause with OBSERVABLE evidence — an HTTP status, a redirect target,
the error body. "Could not access" is not a cause.

## Candidates are ADOPTABLE artifacts

A model, a dataset, a benchmark, a hosted endpoint. Not a paper, not a vendor, not a research
direction: if it cannot be adopted, it is not a candidate. A paper's identifier belongs in
`provenance.arxiv_id`, on the artifact it introduced.

**Every candidate carries its evidence.** `evidence_quote` is the load-bearing sentence **or field
value** VERBATIM from the locator; `claim` is what it says in your words. Where the two disagree,
the quote governs — and a claim about what a model DOES, resting on a quote about what a document
SAYS, is the recurring failure here.

**On an API angle the `locator` is the API resolution, not the rendered page.** `evidence_quote`
is verbatim FROM THE LOCATOR, so the two have to name the same document: quoting
`pipeline_tag: image-segmentation` against a `huggingface.co/<repo>` locator claims the rendered
page said it, which is not where you read it. Record the URL you actually fetched. The repo is
still identified — `item_id` and `name` carry it — and every card resolution is a query, so it
appears in the cell's `queries` alongside the listing that found the repo.

**A field value is a first-class warrant, not a fallback.** Most of this corpus is read through
APIs, and an API returns fields rather than prose: `a1` requires the Hub card be resolved with
`?full=true`, whose response carries `tags`, `cardData`, `model-index`, `library_name` and
`pipeline_tag` and **no prose field whatsoever**. Demanding a sentence there would demand a Pages
fetch the angle forbids. Quote the field as `key: value` so a reader can re-resolve it, and let
`claim` say what it establishes.

**A cell records its own sanitization only where the fetch departed from the map's.** The map
already carries a posture per source, established at wave 0. `coverage[].sanitization` is an
OVERRIDE for the cell where this angle's fetch differed — a model card that embedded a note
addressed to an agent, a sanitizer that could not run on one response — and it takes the same
shape and the same four statuses as the map's, because one posture recorded two ways teaches a
producer to write whichever the nearest example used. Every status but `clean` owes a `cause`.
Absence is not a gap: it means the map's posture held.

**An absence is a finding, not an empty field.** "The card publishes no evaluation on any held-out
split" is evidence a decision-maker needs. An empty field is a hole they will read as an oversight.

**A result carries its evaluation and its split, always.** A rank is a claim under a stated
protocol; `test` and `validation` are different numbers, and a leaderboard row that does not say
which is not comparable to anything. **The date is recorded where the table gives one and `null`
where it does not** — an undated result is still evidence, and dropping it would discard the
measured comparison this angle exists to find.

**Authority ranks, never cuts.** A vendor benchmark is recorded with `authority:
vendor-published` and ordered below an independent one. Excluding on authority is how a survey
quietly becomes an opinion.

**The six values, so that two runs pick the same one.** Authority is about WHO stands behind the
claim you quoted, never about who published the artifact:

| value | the claim is made by |
| --- | --- |
| `independent-benchmark` | a third party who evaluated the artifact and has no stake in it — a leaderboard, an evaluation harness |
| `peer-reviewed` | a venue that reviewed it before publication; the DOI or arXiv id goes in `provenance` |
| `vendor-published` | the ORGANISATION that produced the artifact — a company, a lab, a funded project |
| `self-reported` | the INDIVIDUAL who uploaded it, about their own work. **A community Hub upload under a personal namespace is this**, and it is the commonest value in this corpus |
| `community-reported` | someone other than the author who is also not an independent evaluator — a downstream user's report, a forum measurement |
| `unattributed` | the page carries the claim with no identifiable author at all |

The split that matters and is easy to miss: `vendor-published` and `self-reported` are the same
posture at different scale — both are the author speaking about their own artifact — and the line
between them is organisation versus individual, not credibility. Neither is a reason to exclude.

## Worked example

An a1 output for the vocabulary map in `ml-task-vocabulary-map-guide.md` — the photo-app scope, not
the one `SKILL.md` uses.

```yaml
schema_version: 1
meta:
  angle_id: a1
  retrieved_at: "2026-09-02"
  revision: 1
outcome: ran
coverage:
  - group_id: object-detection
    source_id: huggingface-hub-api
    queries:
      - "GET /api/models?pipeline_tag=object-detection&sort=downloads&direction=-1&limit=40"
      - "GET /api/models/facebook/detr-resnet-50?full=true"
    timestamp: "2026-09-02"
    status: reached
    returned: 40
    count_frame: "models returned by the API for this pipeline_tag, first page at limit=40"
    kept: 1
    cause: null
    fallback_used: null
  - group_id: image-segmentation
    source_id: huggingface-hub-api
    queries:
      - "GET /api/models?pipeline_tag=image-segmentation&sort=downloads&direction=-1&limit=40"
      - "GET /api/models/briaai/RMBG-1.4?full=true"
    timestamp: "2026-09-02"
    status: reached
    returned: 40
    count_frame: "models returned by the API for this pipeline_tag, first page at limit=40"
    kept: 1
    cause: null
    fallback_used: null
  - group_id: on-device-photo
    source_id: huggingface-hub-api
    queries:
      - "GET /api/models?search=on-device+photo&limit=40"
    timestamp: "2026-09-02"
    status: reached
    returned: 0
    count_frame: null
    kept: 0
    cause: null
    fallback_used: null
retrieval_summary:
  status_counts: {reached: 3}
  degraded_sources: []
bound: {cap: 40, hit: false, ordering: "downloads within the pipeline_tag, then recency of the last commit", dropped_note: null, ordering_deviation: null}
candidates:
  - item_id: HF-briaai/RMBG-1.4
    id_class: HF
    found_by: image-segmentation/huggingface-hub-api
    name: briaai/RMBG-1.4
    authority: vendor-published
    locator: "https://huggingface.co/api/models/briaai/RMBG-1.4?full=true"
    retrieved_at: "2026-09-02"
    as_of: null
    source_claimed_modified_at: "2025-07-06"
    source_claim_provenance: api-field
    evidence_quote: >
      pipeline_tag: image-segmentation; tags: ["image-segmentation", "remove background",
      "background-removal", "vision"]
    claim: >
      The repo declares itself an image-segmentation checkpoint and tags itself for background
      removal. Those are the uploader's own labels, not a measurement — a3 is where an evaluated
      comparison would come from.
    finding: >
      `cardData.license` is the uninformative value `other`, so the card publishes no commercial
      terms this survey can quote, which for a consumer photo app is the field that decides
      adoption. `model-index` is empty: no metric on any split.
    evaluation: null
    provenance: {arxiv_id: null, doi: null, code_url: null}
    licence: "other"
  - item_id: HF-facebook/detr-resnet-50
    id_class: HF
    found_by: object-detection/huggingface-hub-api
    name: facebook/detr-resnet-50
    authority: vendor-published
    locator: "https://huggingface.co/api/models/facebook/detr-resnet-50?full=true"
    retrieved_at: "2026-09-02"
    as_of: null
    source_claimed_modified_at: "2024-04-10"
    source_claim_provenance: api-field
    evidence_quote: >
      pipeline_tag: object-detection; cardData.datasets: ["coco"]; cardData.license: apache-2.0
    claim: >
      The repo declares itself an object-detection checkpoint trained on COCO, under Apache-2.0. It
      declares nothing about on-device inference, which is b4's question and not this one's.
    finding: >
      `model-index` is empty — the repo names its training corpus but publishes no metric on any
      split, so nothing here is comparable to another candidate.
    evaluation: null
    provenance: {arxiv_id: "2005.12872", doi: null, code_url: null}
    licence: "apache-2.0"
unadmitted: []
notes: []
```

**Read the third cell.** `returned: 0` with no cause and no frame is CORRECT: the search ran, the
domain term reached nothing, and that zero is evidence. Omitting the cell instead would have made
it indistinguishable from a pair nobody searched.
