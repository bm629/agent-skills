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
owed   = {(group, source) for source in your angle's sources ∩ the map's ACTIVE sources}
```

A pair in the owed set with no cell is an unexplained gap. A cell OUTSIDE the owed set is one
group's evidence filed under another angle's mechanism.

## Queries are recorded verbatim, whatever the channel

Several sources here are APIs, so a "query" is the request you issued — and, where you filtered the
response, the expression you filtered with. Both halves, or a reader cannot reproduce your number.

A paraphrase cannot be re-run, and a coverage record that cannot be re-run proves nothing.

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
`forbidden-by-terms`, and this type has already lost two channels this way.

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

**Every candidate carries its evidence.** `evidence_quote` is the load-bearing sentence VERBATIM
from the locator; `claim` is what that sentence says in your words. Where the two disagree, the
quote governs — and a claim about what a model DOES, resting on a quote about what a document
SAYS, is the recurring failure here.

**An absence is a finding, not an empty field.** "The card publishes no evaluation on any held-out
split" is evidence a decision-maker needs. An empty field is a hole they will read as an oversight.

**A result carries evaluation, split and date or it is not recorded.** A rank is a claim under a
stated protocol; `test` and `validation` are different numbers, and a leaderboard row that does not
say which is not comparable to anything.

**Authority ranks, never cuts.** A vendor benchmark is recorded with `authority:
vendor-published` and ordered below an independent one. Excluding on authority is how a survey
quietly becomes an opinion.

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
    locator: "https://huggingface.co/briaai/RMBG-1.4"
    retrieved_at: "2026-09-02"
    as_of: null
    source_claimed_modified_at: null
    source_claim_provenance: absent
    evidence_quote: >
      "RMBG v1.4 is our state-of-the-art background removal model, designed to effectively separate
      foreground from background."
    claim: >
      The card states the checkpoint is for background removal. The superlative is the card's claim
      about itself, not a measurement — a3 is where an evaluated comparison would come from.
    finding: >
      The card publishes no licence for commercial use in a form this survey can quote verbatim,
      which for a consumer photo app is the field that decides adoption.
    evaluation: null
    provenance: {arxiv_id: null, doi: null, code_url: null}
    licence: "unstated"
  - item_id: HF-facebook/detr-resnet-50
    id_class: HF
    found_by: object-detection/huggingface-hub-api
    name: facebook/detr-resnet-50
    authority: vendor-published
    locator: "https://huggingface.co/facebook/detr-resnet-50"
    retrieved_at: "2026-09-02"
    as_of: null
    source_claimed_modified_at: null
    source_claim_provenance: absent
    evidence_quote: >
      "DEtection TRansformer (DETR) model trained end-to-end on COCO 2017 object detection."
    claim: >
      The card states the checkpoint was trained on COCO for object detection. It claims nothing
      about on-device inference, which is b4's question and not this one's.
    finding: null
    evaluation: null
    provenance: {arxiv_id: "2005.12872", doi: null, code_url: null}
    licence: "apache-2.0"
unadmitted: []
notes: []
```

**Read the third cell.** `returned: 0` with no cause and no frame is CORRECT: the search ran, the
domain term reached nothing, and that zero is evidence. Omitting the cell instead would have made
it indistinguishable from a pair nobody searched.
