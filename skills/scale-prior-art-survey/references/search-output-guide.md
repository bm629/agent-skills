# One angle's search output (wave 1)

The 2-D coverage grid, the candidates, the bound and the retrieval summary.

## `outcome`

If the map recorded `holds: false` for your angle, `outcome` is `not_run` with a
`not_run{map_verdict}` block quoting the map's reason, and **nothing else** — no cells, no
candidates, no bound. Stop there.

## The owed grid is derived from THREE terms

1. the map's `groups[]` **of your angle's applicable types**,
2. crossed with **your angle's own `sources`**,
3. **intersected with the map's ACTIVE sources**.

All three. Dropping the first owes cells against axes the angle does not search, each recordable
with an honest-looking zero. Dropping the second owes cells against every registry row. Dropping
the third owes a cell against a channel this run recorded as dead.

For the calibration fixture's `b5`: 2 applicable groups × 5 sources = **10 cells**.

## Each cell

`group_id`, `source_id`, `queries[]` VERBATIM (including any filter expression), `timestamp` and
`status` — **five fields, reached or not**. A cell that was refused still says which query against
which source was refused, and when.

A REACHED cell records `returned` and `kept`, and a non-zero `returned` records a `count_frame`
saying what was counted — a count is unre-derivable without it. It also records
`sanitization{status, cause}`: the subject is the CELL, not the map row it cites, so a reached
cell's own status is never `not-fetched`.

**A cell that was NOT reached records an observable `cause` and NO count.** A zero and an absence
are different claims and the grid must keep them apart.

## Admission

A candidate enters the extract queue only on **both** conjuncts: a resolvable `url` AND a
`stated_date` — a publication date, a benchmark result date, a documentation version, or an
incident date.

The dating conjunct is sharper here than for any sibling. A scale claim without a date is not
re-checkable, because what ages is not the argument but the **hardware and managed-service
generation** underneath it. A 2016 result on spinning disks is not wrong; it is un-transferable,
and an undated one cannot even be placed.

A source failing either conjunct is UNADMITTED with its `reason_class` — `no-resolvable-url`,
`no-stated-date`, `out-of-scope-for-this-angle`, `duplicate-of` or `superseded` — never silently
dropped.

**Every candidate and every unadmitted row carries `found_by`**, the `group/source` cell key it
came from, because `kept` == |candidates citing the cell| + |unadmitted citing the cell| and
without it on candidates the first term is not computable.

## `bound`

`cap` transcribed VERBATIM from the registry, `hit`, `ordering`, `dropped_note`,
`ordering_deviation`.

`hit: true` owes a `dropped_note` a reader could RE-APPLY: name the ordering position reached and
the FIRST row that fell off. "The rest were dropped" is not re-appliable. An `ordering` deviating
from the registry's owes an `ordering_deviation` saying why.

## `retrieval_summary`

Derived from the FINISHED coverage list, never counted as you go.
