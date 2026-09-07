# Writing the synthesis report

`ml-option-register.yaml` is the machine half and the handoff index; `report.md` is what a human
reads beside it. The survey ships both and no third file.

## The sections are FIXED, in this order

1. **Survey scope.** What was surveyed and how: the capabilities, the angles that ran, the sources
   reached, and the date.
2. **Coverage and absence** *(second on purpose — it is what a reader checks before trusting the
   rest)*. Per angle: ran, vacated or not run, each non-`ran` outcome with its cause; then every
   zero, phrased as what did not surface across what was searched, with any frozen or archived
   corpus flagged as historical.
3. **The ladder, per capability.** The chosen rung, the records it rests on, and **every descent
   above it with the record that failed and why**. This is the spine, and a section that states a
   rung without its descents has removed the only part a reader can argue with.
4. **Yardstick validity.** Per capability: the benchmark, what it measures, the delta to our
   capability, and its contamination state. A rung resting on a benchmark that measures something
   else is a rung resting on nothing, and this section is where that becomes visible.
5. **Licence and use restrictions.** The composition across models AND datasets, with anything that
   blocks use called out regardless of how good the artifact is.
6. **Cost and serving envelope.** The collective figure, naming the capabilities it covers and the
   volume it assumes.
7. **Realistic accuracy expectation.** Per capability: the metric, the benchmark, the population it
   was measured on, and the user-visible consequence. Every figure carries the record it came from.
8. **Governance-documentation gap** *(only where that angle ran)*. Where it did not, the section
   says so in one sentence and stops.
9. **Amendments changelog** *(delta runs)*. One dated entry per run: what changed, what was added,
   and what a prior run claimed that this one corrects.

## What does not go in the report

**No architecture, and no infrastructure specification.** The survey reports what exists and what
it would cost; choosing what to build is the downstream document's job, working from the register.

**No re-scoring and no recomputation.** `score`, `rung` and every metric are the register's. A
figure restated differently in prose leaves a reader with two answers and no way to tell which is
current — and a metric converted, pooled or rounded in the report is a number that no longer traces
to any record.

## Grounding

Every figure carries the extract record id it came from, and every claim carries its date. A model
that was state of the art in the spring is a historical claim by the autumn, and an undated
sentence about this corpus is a sentence that will be read as current long after it stopped being
true.
