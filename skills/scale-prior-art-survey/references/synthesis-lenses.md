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
| 8 | Currency | `published_date` across the backing episodes, read as a caveat on the whole area rather than folded into `confidence`. |

## `evidence[]` is episode ids, ALWAYS

Never a prose citation. Every id must RESOLVE to an episode in an extracted record, which is what
makes `--extracts` load-bearing: without it the gate says so and exits 1, and it prints
`SKIP extracts-crosscheck` rather than passing quietly.

## `lineage`

A delta run records `lineage{extends}` naming the baseline index it extends. The validator READS
it: a `delta`-mode index whose `extends` is null is refused. This is the half that reverted
silently in two shipped packages when a fix landed only on the validator side.
