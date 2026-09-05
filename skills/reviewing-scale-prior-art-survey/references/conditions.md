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

**Paths below marked `producer:` live in the PRODUCER package**, not in this one. They are
staged into the packet beside the artifact; `references/conditions.md`, `references/sources.md`
and `references/fixtures/` are this package's own. Without the distinction a reviewer reads
every path as twin-relative, finds it absent, and records the condition "unjudgeable" — which is
what nine of the conditions below would then be.

| kind | what you are handed |
| --- | --- |
| `keyword-map` | **the handed SCOPE document**, `producer: references/source-registry.yaml`, `producer: references/scale-vocabulary-map-guide.md`, `references/sources.md` |
| `search` | the map it was produced against, `producer: references/source-registry.yaml`, `producer: references/angles/<angle>.md` |
| `extract` | **the SOURCE itself** (staged as `references/fixtures/source-*.md`), `producer: references/load-band-thresholds.md`, `producer: references/quality-filter.md`, `producer: references/absent-input-policy.md`, `producer: references/extraction-template-guide.md` |
| `synthesis` | **the extracts directory**, the map (for `project_band`), the extracted records themselves |

Every source listed here is USED by a condition below. A packet that stages a file no condition
reads is a promise nobody keeps; a condition needing a file the packet does not stage can only ever
record "unjudgeable".

---

## Every kind

Read this group whatever kind you were handed. It is the one duty that does not belong to a
single artifact shape.

**C1 — The result is PROPORTIONATE, and a small honest result is CORRECT.** An enumerated zero
is evidence. A four-cell grid over a four-child run is the floor working, not a corpus
half-walked. Do not raise a finding whose substance is "this seems thin" — a reviewer who treats
a small number as a defect teaches the next producer to pad, and padding is the failure this
whole type is built against. If you believe a result is too small, name the specific query, cell
or source you would have expected and why; if you cannot name one, there is no finding.

---

## `keyword-map`

**C2 — The declared band at `meta.classification.scale` is a faithful transcription of the
handed scope's `scale.*` block, leaf for leaf.** Judge it against the SCOPE, never against the
map's own prose — a fabricated band reads exactly like a real one, and every lens leans on it.
The validator owns presence and enum membership (`declared-band`); faithfulness is yours.

**C3 — Each group is populated from the scope, not from an angle's imagined results, and per the
four axes `producer: references/scale-vocabulary-map-guide.md` names.** A `named-technology`
group naming components the scope never mentions is a finding — that group is the input three
angles would otherwise take from a sibling's OUTPUT, which is the coupling the whole design
forbids.

**C4 — `expansions[]` are terms the corpus actually uses, not synonyms invented to look
thorough.**

**C5 — `negative_terms[]` on the `system-class` and `failure-class` groups exclude the false
positives the scope's own words invite.** "Saturation" also means market saturation.

**C6 — Each angle verdict FOLLOWS from the classification.** Read the angle's `predicate` in
`producer: references/source-registry.yaml` and evaluate it against the transcribed band
yourself: a `holds: false` names a deciding value that really decides it, and a `holds: true` on
a conditional angle means the predicate really fires. The validator owns the shape of the
verdict (`map-completeness`); the inference is yours.

**C7 — The probe note describes what the three checks actually returned.** Count the checks the
note claims against the three the guide defines, then read each claim against the row it is
about: a note reporting a read of a row whose own `sanitization.status` is `not-fetched` is
asserting a request that did not happen, and it is a finding whether or not that row's
`access_status` says the channel is open. Reachability and having-been-read are different
claims, and the note is the only place the second one is made.

**C8 — Every `skipped` row's `cause` is OBSERVABLE evidence — a status code, a robots directive,
a dated refusal — and not an assumption.** `no-holding-angle` is checkable against the verdicts.

**C9 — An ACTIVE row's `sanitization.status` of `clean` asserts a read this run actually
performed.** The wave-0 probe makes three checks, so most active rows were never opened and
`not-fetched` is their honest posture; `clean` on a row the probe never touched claims a read
that did not happen, and no rule can see it — the posture is a report about an event outside the
artifact. This is separable from C8, which owns whether a SKIPPED row's `cause` is observable: a
row can carry an impeccable cause and still, on the other side of the ledger, assert a read that
never happened, and a blind reviewer caught exactly that with no condition to name.

**C10 — `scope_guard` is internally consistent with the groups.** Every `shared_terms[]` entry
names a term BOTH its groups actually carry and an `owner` that is one of them — a term declared
shared with a group that does not have it de-duplicates a query that was never going to run
twice. Every `absent_types[]` axis really has no group, and every one carries its reason in
`excluded[]`.

**C11 — `assumptions[]` records what the author had to assume.** A map that assumed something
and recorded nothing is a finding even when the assumption was reasonable.

**C12 — An ACTIVE row's `as_of` and `access_status` say what THIS run established, or the map
records that they do not.** `references/sources.md` makes the date load-bearing — "a row whose
`as_of` is older than the corpus it claims to describe is a row nobody probed" — and the wave-0
probe makes only three checks. A map that restamps every active row with the run's date while
carrying `sanitization: not-fetched` on most of them has inherited a posture and dated it as its
own; the honest form records the inheritance in `assumptions[]`, and this condition is where the
map side of that claim is guarded at all.

---

## `search`

**C13 — Each candidate's `url` RESOLVES to what the row claims it is.** The gate checks the
field is present (`admission`); whether it resolves is yours.

**C14 — The admission conjuncts were applied HONESTLY.** A `stated_date` copied from the
retrieval date rather than the source is the failure this condition exists for — an undated
claim cannot be placed, because what ages is the hardware and managed-service generation
underneath it.

**C15 — Admission is RECORDED in both directions.** Every unadmitted row's `reason_class` is the
one that actually applies and its `reason` says what was looked for — and, the other way,
nothing that belongs in `unadmitted[]` is sitting in `candidates[]`. That second half is the
failure mode `duplicate-of` and `superseded` exist for: two candidates carrying the same quote,
the same claim or the same stated date across DIFFERENT hosts is the tell, because independent
bodies do not publish the same sentence on the same day, and admitting all of them triples a
queue from what is on its face one result.

**C16 — A zero is read against the ROW, not against the cell.** Look the row up in `producer:
references/source-registry.yaml`: a zero from a `complete_listing: false` row says only that the
query did not match, and recording it as evidence of absence is a finding. A zero from a
`complete_listing: true` row IS evidence — a complete walk that did not find the term — and
treating it as inconclusive WASTES the strongest result a search can produce. The cell does not
restate which reading applies, and asking it to would put a second copy of a registry fact where
it can drift; your job is to check the producer read it the right way round.

**C17 — The `ordering` is RE-APPLIABLE by a reader with the same corpus: it names a signal every
source the angle walks actually exposes, and a tie-break.** The registry declares the signal and
the build asserts it is total across the sources the angle walks; whether a READER with the same
corpus could apply it is yours.

**C18 — `bound.cap` is the registry's value TRANSCRIBED VERBATIM.** Look the angle up in
`producer: references/source-registry.yaml` and compare. The gate compares them too, so this is
the one condition that overlaps a rule deliberately: a widened cap changes nothing downstream
when the corpus is small, so it survives every count-based check and is caught only by someone
reading both numbers. An author does not widen their own cap.

**C19 — `hit: true`'s `dropped_note` names the ordering position reached and the first row that
fell off, and a reader could act on it.**

**C20 — The terms actually QUERIED are the group's, and every declared term left unqueried is
accounted for.** `expansion_cap` is a maximum, so a run may query fewer terms than a group
carries and be right to; what it may not do is drop one silently. Read each cell's `queries[]`
against its group in the map: the `canonical` AND every `expansion` that appears in no cell of
the grid needs a reason in `notes[]` or `assumptions[]`, and a term the scope makes interesting
— a component it names as evaluated and rejected, say — needs a better one than the rest. The
canonical is in scope because a blind reviewer had to reason its way past an unqueried one that
this condition, scoped to expansions, could not reach. The gate owns the other half
(`coverage-grid-5`): that every query names SOME term the group declares. Which terms were left
out, and whether that was defensible, is yours.

**C21 — `a1` only — a candidate's recorded host posture was taken AT FETCH TIME from the host
actually reached, not copied from the registry, which would describe a host the run never
visited.**

---

## `extract`

**C22 — The number is the SOURCE's number.** `measured_value` is verbatim as the source words
it. A converted, rounded or recomputed figure is a finding even when the arithmetic is right.

**C23 — The episode's `claim` does not reach past the evidence behind it.** The quote lives on
the upstream SEARCH candidate, not on the episode — `producer:
references/extraction-template-guide.md`'s episode field list carries no `evidence_quote` — so
read the candidate that admitted this source, or the body's `## Method and configuration`, and
ask whether the claim asserts more than either supports. A claim that names a threshold the
evidence never states is the case this exists for, and it is the one that propagates: the
index's hard limits and migration trigger are built from claims.

**C24 — `evidence_class` fits what the source IS.** A vendor's own blog post describing its own
system is not `independent-verification` however measured it is.

**C25 — Every recorded fact ABOUT THE SOURCE is one the source states, or the field is null.**
`technology`, `license`, `consistency_model`, `system_name` and `published_date` are assertions
about the source, not judgements about the episode, and each is checkable by reading it. A null
is the honest value where the source is silent — the absent-input policy says so — and a
plausible value invented to fill the field is the failure this exists for. A blind run grounded
two of them in one record and could file neither: an engine named on both episodes of a source
that fixes its query set across every engine and names none, and a licence the source never
mentions. `claim` was the one field the conditions covered, which is why it is the one field a
producer composes carefully.

**C26 — `configuration_stated: true` means the configuration is actually stated.** A benchmark
number with no disclosed configuration is not a comparable measurement, however authoritative
its host.

**C27 — `primary_dimension` is the dimension the episode actually MEASURED — judged from
`signal` and `metric_name` against the source, never from the source's topic.** This duty was
DEMOTED from the validator: no signal→dimension mapping exists to decide it deterministically,
so if this condition does not carry it, nothing does.

**C28 — `transferability` is weighable and INDEPENDENT of `confidence`.** A `reason` that
restates `level` is not a reason. A high-confidence measurement three bands above this project
is LOW transferability, and saying so is the condition working, not a finding against the
source.

**C29 — The episode's `confidence` is defensible against the four facts the derivation reads —
`evidence_class`, whether `measured_value` is present, `configuration_stated`, and whether
`load_class` is fully stated.** The gate re-derives it and refuses a disagreement, so a value
that DISAGREES never reaches you. What reaches you is a value that agrees with the table and is
still wrong because one of the four facts is mis-recorded: a measured, configuration-disclosed
benchmark episode recorded as `narrative-only` derives `very-low` legally. Read the source, not
the table.

**C30 — The `score` is defensible against the ten signals.** The validator checks presence and
range (`quality-filter`); whether a 9 is a 9 is judged here. Count the ten signals in `producer:
references/quality-filter.md` against the source yourself. File a finding when the COUNT is
wrong: name the signals the source satisfies and the ones it does not, and say which way the
count moves. The threshold is not "would this have changed what synthesis sees" — `score` is
written after the queue is fixed, nothing truncates the extracts directory, and the filter ranks
rather than cuts, so no score could ever change it. A condition whose own threshold its design
forbids is unfilable. AND the count is consistent with the record's own fields: a score counting
`the system named` in a record whose every episode carries `technology: null` is a contradiction
inside one document, and reading it is the whole check. Two blind runs counted this same cell
differently before the signal spelled out that it is a conjunction.

**C31 — The episode's `cause_class` is a FAILURE MODE, not the map's field of the same name.**
Two levels, two vocabularies, disjoint members — and the gate checks membership, not meaning. An
episode recording `saturation` where the source describes a quota exhaustion is legal and wrong,
and so is one recording a plausible-looking member for a phenomenon the source never names.
Judge it against what the source says failed.

**C32 — `load_class` sub-keys record what the SOURCE states.** A band filled in from the
project's own classification rather than from the source is a finding, and the gate cannot see
it — it re-derives only the `primary_dimension`'s sub-key, and only where a boundary is
published.

**C33 — For a dimension in `producer: references/load-band-thresholds.md`'s
`unsourced_dimensions` list, the band is YOURS to judge and nobody else's.** No published
boundary exists, so the gate skips the re-derivation entirely: a `concurrency: extreme` on an
episode measuring 300 requests per second is not caught by anything upstream of you. Read the
file, note which dimension you are looking at, and say whether the band the producer chose is
defensible against the number the source states. Where the dimension IS sourced —
`availability_target` — the gate has already compared them and you are not re-running it.

**C34 — The four body sections `producer: references/extraction-template-guide.md` names say
something.** The gate checks presence and non-triviality; whether `## Method and configuration`
actually explains how each number was obtained — and whether `## Transferability` compares the
band it was measured at against this project's — is yours.

**C35 — A `skipped` record's `detail` is observable, in the forms `producer:
references/absent-input-policy.md` sets out — a status code, a robots directive, a dated
refusal.** "Not relevant" is not a detail. The same file governs a null where a source states no
number: check that the producer recorded the absence rather than forcing a nearest-looking enum
member, which reads as a measurement and is worse than a null.

---

## `synthesis`

**C36 — Every `evidence[]` id resolves to an episode that says what the area claims it says.**
The gate checks resolution (`synthesis`); whether the episode supports the pattern is yours.

**C37 — The area's `confidence` is the WEAKEST backing class, and the weakest episode is one a
reader would agree is weakest.**

**C38 — Each `failure_modes[]` entry lists EVERY episode carrying its `cause_class`, not just
one.** Lens 3 groups by the field, so an entry citing the narrative episode while omitting the
measured one with the same class tells a reader the failure mode rests on an unmeasured aside.
Completeness is the test; C36 owns whether a listed id supports the claim.

**C39 — A `blocks_requirement: true` hard limit really blocks a requirement this project has.**
It is the only blocker-producing lens, and a false one costs more than a missed one.

**C40 — `default_pattern` is what the episodes converged on, not what the reviewer would have
chosen.**

**C41 — The `migration_trigger` names a condition someone could observe, and its `dimension` is
the axis the trigger is actually on.**

**C42 — An absence is phrased with its receipt.** `open_gap` says what was looked for and where,
not merely that something is unknown.

**C43 — The index's `project_band` EQUALS the map's `meta.classification.scale`, leaf for leaf,
and both are faithful to the scope.** C2 owns the map side; this owns the equality and the index
side.

**C44 — Every gap the backing EXTRACTS state reaches the index.** An extract's `##
Transferability` section and its episodes' `transferability.reason` are where a band that does
NOT carry gets written down, and the index is the only document an ADR is written against. A
limit stated in an extract and absent from `open_gap`, `hard_limits[]` or `failure_modes[]` is a
limit the reader will never meet: a blind run found the calibration extract saying "the
concurrency band does not carry at all — the source says every figure in the round is
single-client, while this project's scope declares `moderate`", and the index carrying nothing
about concurrency outside `project_band`. Read every staged extract's transferability prose and
ask, for each limit, where in the index it lands.
