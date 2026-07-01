# Validation: md_to_adf.py

- **Method**: syntax check (`py_compile`) + functional runs over representative Markdown
- **Tools**: python3 (stdlib only), `python3 -m py_compile`
- **Date**: 2026-07-01
- **Exit codes**: py_compile: 0 · normal run: 0 (reads stdin, prints ADF JSON to stdout)

## Captured output

- `## Assessment` → `{type: heading, attrs:{level:2}, content:[{type:text, text:"Assessment"}]}`.
- GFM table (`| Dim | Verdict |` + `|---|---|` + rows) → `{type: table, content:[{type:tableRow, content:[{type:tableHeader,...}]}, {type:tableRow, content:[{type:tableCell,...}]}]}` — header row uses `tableHeader`, body rows `tableCell`, each cell wrapping a `paragraph`.
- `**pass**` → `{type:text, text:"pass", marks:[{type:strong}]}`; `` `x` `` → `marks:[{type:code}]`; `[t](u)` → `marks:[{type:link, attrs:{href:"u"}}]`.
- `- a` / `1. a` → `bulletList` / `orderedList` of `listItem` → `paragraph`.
- fenced ```` ``` ```` block → `{type:codeBlock, content:[{type:text, text:"..."}]}` (with `attrs.language` when the fence names one).
- Top-level envelope is always `{version:1, type:"doc", content:[...]}` (Jira takes the ADF as a raw object).

## Usage

```bash
python3 scripts/md_to_adf.py < comment.md            # ADF JSON on stdout
# then send it as the comment body: {"body": <adf>} to Jira addComment / issue description
```

## Caveats

- Inline marks are non-nested (a `**bold**` span is not further scanned for `` `code` `` inside it) — sufficient for the phase-comment layouts; nest-heavy Markdown degrades to plain text for the inner span.
- Empty text nodes are dropped (ADF rejects empty `text`); an empty paragraph is emitted with empty `content`.
- This is the skill's self-contained copy of the converter (the hq spine carries an independent copy — the skill cannot import it).
