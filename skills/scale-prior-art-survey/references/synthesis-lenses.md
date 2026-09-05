# The synthesis lenses

Eight lenses over the extracted episodes, producing the scale envelope index. Each states its
formula so the index is re-derivable rather than argued.

| # | lens | the formula |
| --- | --- | --- |
| 1 | Band placement | The project's `project_band`, carried verbatim, against the band each episode was measured at. Requires the declared band; without it this lens cannot run. |
| 2 | Converged pattern | Per area, the `pattern` most episodes independently describe. Becomes `default_pattern`. |
| 3 | Failure modes | Group episodes by `cause_class`; each group becomes a `failure_modes[]` entry carrying the episode ids that evidence it. |
| 4 | Hard limits | Every `outcome_kind: limit` episode becomes a `hard_limits[]` entry. `blocks_requirement: true` makes a corpus blocker a report blocker — the only blocker-producing lens. |
| 5 | Open gaps | The question no episode answered, per area, or `null`. |
| 6 | Confidence | The **WEAKEST** class among the episodes backing `default_pattern`. Never an average: averaging lets one strong episode carry a weak one. |
| 7 | Migration trigger | The condition under which the default pattern stops holding, with the band `dimension` it is on and the episode ids that evidence it. |
| 8 | Currency | EVERY distinct `published_date` among the sources of the episodes backing the area — every evidence site, not just `evidence[]` — into `currency.dates`, EACH in the form its source carries it, with `currency.note` saying what they mean for a reader acting on this area today. The field is a MAPPING, not prose: a free-text caveat had to be pattern-matched for the dates it named, and no delimiter works for a field that admits a publication date, a benchmark result date, a documentation version and an incident date. Not "the oldest" either — there is no ordering on free text, and naming them all gives the reader the span rather than one end of it. `dates` is compared by EQUALITY, both directions. Null only where every backing source is undated. This lens had no output field for eight review cycles, which is why its formula names one now. |

## EVERY evidence site is episode ids, ALWAYS

Never a prose citation. Every id must RESOLVE to an episode in an extracted record, which is what
makes `--extracts` load-bearing: without it the gate says so and exits 1, and it prints
`SKIP extracts-crosscheck` rather than passing quietly.

**FOUR sites, not one.** The area's `evidence[]`, each `failure_modes[].evidence`, the
`migration_trigger.evidence` — and **`hard_limits[].source`**, which is an episode id despite its
name. That last one is the field lens 4 cites, lens 4 is the only blocker-producing lens, and
writing a prose citation there ("the run-3 write-up, section 4") is refused. If you want to say where in
the source it came from, the episode's own `claim` and the record's `## Method and configuration`
are the places for it.

## `lineage`

A delta run records `lineage{extends}` naming the baseline index it extends. The validator READS
it: a `delta`-mode index whose `extends` is null is refused. This is the half that reverted
silently in two shipped packages when a fix landed only on the validator side.
