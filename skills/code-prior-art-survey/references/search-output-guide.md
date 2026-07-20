# Search-output guide — the contract explained

The authoritative contract is `schemas/search-output.schema.json`; the worked
example is `scripts/fixtures/search-output.valid.yaml` (an a3
registries-and-dependents run; validator exit 0 against the keyword-map
fixture). On any disagreement, the schema wins.

## `meta` — self-description

`project`, `request` (optional), `angle_id` (a1..a9), `searched_at`
(ISO-8601, quoted), and `keyword_map_revision` — the revision of the map this
run executed. The validator cross-checks it against the supplied map: an
output produced against a stale map fails (`revision_mismatch`).

## `coverage` — proof of work

One cell per (keyword group × source) pair actually worked:

```yaml
- group_id: kw-tech-mean-reversion
  source: npm
  queries: ["npm search: mean reversion"]
  searched_at: "2026-07-17T11:48:05Z"
  result_count: 0          # zero-hits are REQUIRED cells, not omissions
```

A source you could NOT reach is not a zero — type the cell:

```yaml
- group_id: kw-tech-mean-reversion
  source: npm
  queries: ["npm search: mean reversion"]
  searched_at: "2026-07-17T11:48:05Z"   # when the LAST attempt was made
  result_count: 0
  status: unreachable                    # searched (default) | partial | unreachable
  cause: "503 Service Unavailable, 3 attempts over 155s"
```

- `status`: omit it (or `searched`) for a normal cell — that is what keeps
  every pre-existing record valid. `unreachable` = nothing was retrieved, so
  `result_count` MUST be 0. `partial` = the source returned some results and
  then cut you off (a rate limit mid-pass); `result_count` is then a FLOOR,
  not a total.
- `cause`: REQUIRED on `partial` and `unreachable`, and rejected on a normal
  cell. Record the status or error as seen, plus the attempt count. A bare
  `"429"` is fine; the validator accepts any cause carrying a digit, or ten-
  plus characters of prose where no numeric status exists.
- Try the source's registry `fallbacks` BEFORE typing a cell `unreachable`.
  Otherwise the label becomes the cheap exit from a slow source, and coverage
  shrinks while still looking complete.

**Why typed rather than omitted:** the coverage matrix must stay COMPLETE — one
cell per applicable (group × source). An unreachable source recorded as a zero
claims work that did not happen; omitted entirely, it fails the completeness
gate. The typed cell is the only honest option that also validates.

- `queries`: the exact strings as run — what makes the search reproducible
  rather than claimed. Cell ANNOTATIONS (counting conventions, filters
  applied by eye, "already covered via X" notes) ride as one extra string
  in `queries` prefixed `note:` — the schema has no note field by design,
  and this keeps annotations reproducible alongside the queries.
- Completeness is machine-checked: the validator computes every applicable
  pair (map groups whose type the registry marks for your angle's sources ×
  the map's `sources.active`) and fails on any missing cell
  (`coverage_missing`).
- Extra cells beyond the applicable set are allowed (more work than
  contracted), but their `group_id`/`source` must still exist in the map/
  registry (`unknown_group` / `unknown_source`).

## `candidates` — dedup-honest records

```yaml
- id: github__freqtrade__freqtrade     # canonical <host>__<owner>__<name>
  repo: https://github.com/freqtrade/freqtrade
  host: github
  name: freqtrade
  description: "Free, open source crypto trading bot"   # the repo's OWN words
  language: Python
  flags: {is_fork: false, fork_of: null, is_mirror: false, archived: false}
  package: {registry: pypi, name: freqtrade}            # when registry-found
  signals: {stars: 27400, last_commit: "2026-07-11", license: GPL-3.0,
            downloads: 412000, as_of: "2026-07-17T11:14:55Z"}
  found_by: {group_ids: [kw-dom-trading-bot], sources: [pypi]}
  relevance: full trading bot covering backtesting + live execution  # YOUR judgment
```

- `id` threads every later stage (screening, extraction, rollups) — same
  repo, same id, forever. Lowercase host; owner/name verbatim. Platforms
  with no owner segment (a SourceForge project, a Zenodo record) repeat the
  project/record slug: `sourceforge__<project>__<project>`,
  `zenodo__<record-id>__<slug>` — three segments always.
- `description` is data (theirs); `relevance` is judgment (yours, grounded in
  the caller's scope). Keep both.
- `flags` let downstream dedup prefer ultimate parents — a fork is not an
  independent finding. Unknown values may be null; the keys themselves are
  required.
- `signals.as_of` is the query time (signals decay). Candidate ids unique per
  file (validator-enforced); `found_by.group_ids` must exist in the map.

## `notes` — the escape valves

`vocabulary_discoveries` (terms the map lacks — never improvised into
searches; `seen_at` = WHERE the term was seen, free text like "pypi package
descriptions", not a timestamp), `dead_ends`, `unreachable_sources`.
These make honest narrowing visible and feed the caller's follow-up
decisions.

`unreachable_sources` is the human-readable SUMMARY, not the machine record —
the typed cells are that. List a source here if and only if EVERY one of its
cells is `unreachable`, by its registry id (`npm`, not "the npm website"); the
validator checks both directions and rejects a prose name it cannot match. A
`partial` source was reached, so it never belongs here.

## Validation

```bash
python <package>/scripts/validate_prior_art.py search <output-file> \
  --keyword-map <map-file>
```

Fix every FAIL; hand off only at exit 0.
