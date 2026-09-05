# Conditions

Numbered `C1…Cn`, contiguously, grouped per KIND. Each names the rule that owns the other half
where one exists. **The count is derived from this file, never stated in prose.**

Exactly one `VERDICT: approve|revise`, as the LAST line of your review. `revise` requires at least
one finding NAMING its condition; `approve` with findings attached is a contradiction.

The gate runs FIRST and returns early. Nothing below re-states a schema enum or a validator rule —
if the gate can decide it, it already has, and a rule stated twice drifts with only one of them
running.

---

## Evidence, per kind

| kind | what you are handed |
| --- | --- |
| `keyword-map` | **the handed SCOPE document**, `references/source-registry.yaml`, `references/scale-vocabulary-map-guide.md` |
| `search` | the map it was produced against, `references/source-registry.yaml`, `references/angles/<angle>.md` |
| `extract` | **the SOURCE itself**, `references/load-band-thresholds.md`, `references/quality-filter.md`,
`references/absent-input-policy.md`, `references/extraction-template-guide.md` |
| `synthesis` | **the extracts directory**, the map (for `project_band`), `schemas/scale-envelope-index.schema.json` |

Every source listed here is USED by a condition below. A packet that stages a file no condition
reads is a promise nobody keeps; a condition needing a file the packet does not stage can only ever
record "unjudgeable".

---

## `keyword-map`

**C1.** The declared band at `meta.classification.scale` is a **faithful transcription** of the
handed scope's `scale.*` block, leaf for leaf. Judge it against the SCOPE, never against the map's
own prose — a fabricated band reads exactly like a real one, and every lens leans on it. The
validator owns presence and enum membership (`declared-band`); faithfulness is yours.

**C2.** Each group is populated from the scope, not from an angle's imagined results, and per the
four axes `references/scale-vocabulary-map-guide.md` names. A `named-technology` group naming
components the scope never mentions is a finding — that group is the input three angles would
otherwise take from a sibling's OUTPUT, which is the coupling the whole design forbids.

**C3.** `expansions[]` are terms the corpus actually uses, not synonyms invented to look thorough.

**C4.** `negative_terms[]` on the `system-class` and `failure-class` groups exclude the false
positives the scope's own words invite. "Saturation" also means market saturation.

**C5.** Each angle verdict FOLLOWS from the classification. Read the angle's `predicate` in
`references/source-registry.yaml` and evaluate it against the transcribed band yourself: a
`holds: false` names a deciding value that really decides it, and a `holds: true` on a conditional
angle means the predicate really fires.
The validator owns the shape of the verdict (`map-completeness`); the inference is yours.

**C6.** The probe note describes what the three checks actually returned. A note that says a
channel is open where the record says otherwise is a finding.

**C7.** Every `skipped` row's `cause` is OBSERVABLE evidence — a status code, a robots directive, a
dated refusal — and not an assumption. `no-holding-angle` is checkable against the verdicts.

**C8.** `assumptions[]` records what the author had to assume. A map that assumed something and
recorded nothing is a finding even when the assumption was reasonable.

---

## `search`

**C9.** Each candidate's `url` RESOLVES to what the row claims it is. The gate checks the field is
present (`admission`); whether it resolves is yours.

**C10.** The admission conjuncts were applied HONESTLY. A `stated_date` copied from the retrieval
date rather than the source is the failure this condition exists for — an undated claim cannot be
placed, because what ages is the hardware and managed-service generation underneath it.

**C11.** Every unadmitted row's `reason_class` is the one that actually applies, and its `reason`
says what was looked for.

**C12.** A zero is ENUMERATED or BOUNDED, and the cell says which. Look the row up in
`references/source-registry.yaml`: a zero from a row whose `complete_listing` is `false` says only
that the query did not match, and recording it as evidence of absence is a finding. A zero from a
`complete_listing: true` row IS evidence, and treating it as inconclusive wastes it.

**C13.** The `ordering` is RE-APPLIABLE by a reader with the same corpus: it names a signal every
source the angle walks actually exposes, and a tie-break. The gate checks the signal is declared
(`ordering-appliable`); whether a reader could apply it is yours.

**C14.** `hit: true`'s `dropped_note` names the ordering position reached and the first row that
fell off, and a reader could act on it.

**C15.** **`a1` only** — a candidate's recorded host posture was taken AT FETCH TIME from the host
actually reached, not copied from the registry, which would describe a host the run never visited.

---

## `extract`

**C16.** **The number is the SOURCE's number.** `measured_value` is verbatim as the source words
it. A converted, rounded or recomputed figure is a finding even when the arithmetic is right.

**C17.** The `evidence_quote` and `claim` pair: the quote SUPPORTS the claim, and the claim does
not reach past it.

**C18.** `evidence_class` fits what the source IS. A vendor's own blog post describing its own
system is not `independent-verification` however measured it is.

**C19.** **`configuration_stated: true` means the configuration is actually stated.** A benchmark
number with no disclosed configuration is not a comparable measurement, however authoritative its
host.

**C20.** **`primary_dimension` is the dimension the episode actually MEASURED** — judged from
`signal` and `metric_name` against the source, never from the source's topic. **This duty was
DEMOTED from the validator**: no signal→dimension mapping exists to decide it deterministically, so
if this condition does not carry it, nothing does.

**C21.** **`transferability` is weighable and INDEPENDENT of `confidence`.** A `reason` that
restates `level` is not a reason. A high-confidence measurement three bands above this project is
LOW transferability, and saying so is the condition working, not a finding against the source.

**C22.** **The `score` is defensible.** The validator checks presence and range
(`quality-filter`); whether a 9 is a 9 is judged here, against `references/quality-filter.md`. A
score that would have changed which records synthesis sees is worth a finding; one that would not
is not.

**C23.** `load_class` sub-keys record what the SOURCE states. A band filled in from the project's
own classification rather than from the source is a finding, and the gate cannot see it — it
re-derives only the `primary_dimension`'s sub-key, and only where a boundary is published.

**C24.** **For a dimension in `references/load-band-thresholds.md`'s `unsourced_dimensions` list,
the band is YOURS to judge and nobody else's.** No published boundary exists, so the gate skips
the re-derivation entirely: a `concurrency: extreme` on an episode measuring 300 requests per
second is not caught by anything upstream of you. Read the file, note which dimension you are
looking at, and say whether the band the producer chose is defensible against the number the
source states. Where the dimension IS sourced — `availability_target` — the gate has already
compared them and you are not re-running it.

**C25.** The four body sections `references/extraction-template-guide.md` names say something. The
gate checks presence and non-triviality; whether `## Method and configuration` actually explains
how each number was obtained — and whether `## Transferability` compares the band it was measured
at against this project's — is yours.

**C26.** A `skipped` record's `detail` is observable, in the forms
`references/absent-input-policy.md` sets out — a status code, a robots directive, a dated refusal.
"Not relevant" is not a detail. The same file governs a null where a source states no number: check
that the producer recorded the absence rather than forcing a nearest-looking enum member, which
reads as a measurement and is worse than a null.

---

## `synthesis`

**C27.** Every `evidence[]` id resolves to an episode that says what the area claims it says. The
gate checks resolution (`synthesis`); whether the episode supports the pattern is yours.

**C28.** The area's `confidence` is the WEAKEST backing class, and the weakest episode is one a
reader would agree is weakest.

**C29.** A `blocks_requirement: true` hard limit really blocks a requirement this project has. It
is the only blocker-producing lens, and a false one costs more than a missed one.

**C30.** `default_pattern` is what the episodes converged on, not what the reviewer would have
chosen.

**C31.** The `migration_trigger` names a condition someone could observe, and its `dimension` is
the axis the trigger is actually on.

**C32.** **An absence is phrased with its receipt.** `open_gap` says what was looked for and where,
not merely that something is unknown.

**C33.** The index's `project_band` EQUALS the map's `meta.classification.scale`, leaf for leaf,
and both are faithful to the scope. C1 owns the map side; this owns the equality and the index
side.
