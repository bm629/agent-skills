# Planted defects

Each fixture here **passes the deterministic gate** and is nonetheless wrong. That is the point: a
gate demonstrating only approve-on-good proves nothing about the judgment half. These exist to
prove the reviewing skill's conditions actually bite.

Every one was verified to exit 0 through the validator before being committed. If a change to the
validator ever makes one of these FAIL the gate, re-read rather than re-fix — either the defect
became mechanically detectable (move the check into the gate and retire the fixture) or the gate
grew a false positive.

**No fixture names its own defect.** The bodies carry no marker comments — a fixture that
announces its answer cannot test a blind reviewer.

| Fixture | Passes gate | Must be caught by | The defect |
| --- | --- | --- | --- |
| `search-output.failure-as-zero.yaml` | yes | **C13**, trigger 2 | The throttled cell rewritten as `reached, returned: 0` with a plausible selection added — but `retrieval_summary.degraded_sources` still records `nngroup` as `rate-limited` with its HTTP 429 cause, while every `nngroup` cell now claims `reached`. The gate does not compare those two records in that direction, so it passes; the summary and the cells state incompatible facts about the same source. |
| `search-output.abstract-as-full-text.yaml` | yes | **C18 + C19** | An admission whose `full_text_url` points at the article's summary anchor rather than its full text, and whose `method_stated` is the article's TOPIC ("self-service checkout usability") rather than a study design. Both fields are present and non-empty, which is all a shape check can ask. |
| `search-output.selection-omits-remainder.yaml` | yes | **C17** | A crawl-delayed cell whose `selection` records only what was shortlisted and fetched, and never what was identified and deliberately not fetched. The gate requires a selection to exist, not that it be complete — and without the un-fetched remainder a reader cannot tell a narrow corpus from a truncated one. |

## Why these three

They cover the three ways this artifact fails while looking healthy:

1. **A failure laundered into a zero** — the only defect that actively misleads rather than merely
   omitting, and the one the whole survey exists to prevent. Here it takes the form specific to
   this type: a shared-pool throttle is indistinguishable from an empty result set.

   **This fixture launders ONE record and not the others, deliberately.** An earlier version
   also emptied `degraded_sources` to match, and a blind reviewer correctly APPROVED it — a
   thoroughly laundered zero is internally coherent, and no review confined to the artifact,
   its schemas, the registry and the map can catch it. That is a property of the evidence set,
   not a reviewer failure, and planting a defect no correct reviewer could find tests nothing.
   What is testable, and what real laundering looks like, is a producer who edits the cell and
   forgets the summary they already wrote. The unreachable case is recorded as a stated limit in
   `conditions.md` under C13 rather than pretended away, and the cheapest mechanical route to it
   is closed by `counts-only-when-retrieved`.
2. **An abstract admitted as a full read, with a topic standing in for a method** — both conjuncts
   of this survey's admission rule broken at once, and neither visible to a shape check. The
   record that follows would read exactly like one grounded in the method section.
3. **A selection that records only its successes** — the half-truth. Every fetched item is
   accounted for and the un-fetched remainder simply does not appear, so the coverage looks
   exhaustive for a source that was in fact sampled.

## What is deliberately NOT planted here

The wave-2 defects — an unsupported `certainty`, a high-certainty finding from an unrelated domain
carried with an unexamined transferability claim. **Neither is expressible in a wave-1 artifact**:
the search-output schema has no field for either, and a fixture cannot plant a defect the shape
forbids. They belong to the extract wave's fixtures, and are recorded here so their absence reads
as a design decision rather than an oversight.
