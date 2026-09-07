# The quality filter — 0-10, RANKING ONLY, never a cut

`score` orders a corpus. It never removes anything from one.

**The sole cut in this survey is the relevance bail**: an artifact that serves none of the scope's
capabilities is recorded as `skipped` with that cause. Everything else is extracted and scored
honestly, including the abandoned, the toy and the superseded — a `discard` verdict later is a
judgement about fit, made once, with the whole corpus visible. A filter that cut here would make
that judgement invisibly, ten times, on evidence nobody could see.

Ten signals per kind. Count the ones the record can actually evidence.

## `model`

1. **Reproducibility** — weights, config and code actually retrievable, not merely announced.
2. **Evaluation transparency** — third-party measured rather than vendor self-reported.
3. **Licence clarity** — a named licence whose use restrictions are stated.
4. **Card completeness** — intended use, out-of-scope use and limitations all present.
5. **Maintenance** — a recent `last_modified`, versioned releases, a stated deprecation policy.
6. **Adoption** — ONE signal among ten, deliberately de-emphasised. A low-download model can score
   high, and often should: download counts measure fashion at least as much as fitness.
7. **Serving maturity** — a measured latency or throughput figure with someone's name on it.
8. **Safety or bias evaluation reported at all** — its absence is the signal, not its result.
9. **Provenance** — a named producer plus a paper or DOI.
10. **Operational track record** — evidence of the thing running somewhere that is not a demo.

## `dataset`

Every signal here maps to a field a real standard already defines, so the score is checkable
against the record rather than felt.

1. **Licence clarity.**
2. **`croissant_present`** — the Hub emits one for every Hub dataset, so its ABSENCE is a signal.
3. **Documented collection process.**
4. **Annotation protocol, platform and annotators-per-item** — the single best predictor of label
   quality, which is why all three are carried rather than summarised.
5. **Size and defined splits.**
6. **Documented bias and limitations.**
7. **PII and consent posture** — `unstated` scores below `no`, because silence is not a negative.
8. **Versioning and a maintenance plan.**
9. **Accessible without an authentication wall.**
10. **Citation and adoption** — again ONE signal among ten.

## `benchmark`

1. **Protocol specified.**
2. **A public, versioned harness.**
3. **Contamination controls.**
4. **A held-out or private split.**
5. **Reproducible results** — someone other than the authors has re-run it.
6. **Breadth against our capability** — does it exercise what we need, or a neighbour of it?
7. **Leaderboard recency.**
8. **Independence from the vendors it ranks.**
9. **Metric appropriateness.**
10. **Submission volume.**

**Score an archived harness low on principle.** A benchmark whose harness stopped moving stopped
tracking the field, and its ranking ages into a claim about a world that has changed.

## Bands — guidance, not arithmetic

**8-10** adoptable today: licence clear, independently measured, maintained.
**5-7** solid with gaps.
**2-4** reference only.
**0-1** abandoned, toy or superseded — extracted and scored honestly, never dropped.

## A leaderboard rank is not a quality signal at all

It is a measurement, and whether that measurement is valid for OUR capability is a separate
question asked once, at synthesis, by the yardstick lens. Folding a rank into `score` answers it
silently and in the wrong place.
