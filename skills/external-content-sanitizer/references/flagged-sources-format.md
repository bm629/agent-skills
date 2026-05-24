# Flagged-Sources File Format

Loaded by `external-content-sanitizer` during Steps 1 (lookup) and 7 (update). Defines the schema, parsing procedure, and write logic for `docs/security/flagged-sources.md`.

---

## File location

`<WORKSPACE_ROOT>/docs/security/flagged-sources.md`

Git-tracked. Team-shared audit trail. Created by Task 6 of the sanitizer implementation plan with header-only initial state; populated by every sanitization run that detects new incidents.

---

## File header (always present)

```markdown
# Flagged Sources

> Maintained by `external-content-sanitizer`. Tracks sources where prompt-injection attempts have been detected. Consult before processing external content; bump caution on repeat offenders. Git-tracked as a team-shared audit trail.
```

The `> Maintained by ...` blockquote signals to humans that the file is auto-managed. Manual edits are permitted (e.g., a maintainer corrects a false positive by deleting an entry) — the sanitizer's update logic is additive and won't conflict with manual edits as long as the section structure is preserved.

---

## Per-source entry shape

Each flagged source is a `## <identifier> (<level>)` section with bullet metadata. Two-level granularity per spec decision #6:

### Container-level entry

For cloned repos: `## <parent>/<repo-folder> (container)`, where `<parent>` is whatever directory the workspace clones external repos into (`external/`, `vendored/`, `third-party-repos/`, etc.). Examples below use `external/` as a generic placeholder.
For domains: `## <domain> (domain)`

```markdown
## external/malicious__repo (container)

- **First flagged**: 2026-05-07
- **Last flagged**: 2026-05-07
- **Incident count**: 3
- **Severity history**: medium, high, high
- **Affected files**: skills/poison.md, skills/another.md
- **Notes**: Multiple injection attempts; container-level escalation in effect
```

### File/URL-level entry

For repo files: `## <full-relative-path> (file)`
For URLs: `## <full-url> (url)`

```markdown
## external/malicious__repo/skills/poison.md (file)

- **First flagged**: 2026-05-07
- **Last flagged**: 2026-05-07
- **Incident count**: 2
- **Severity history**: high, high
- **Notes**: Active tool-use injection attempts
```

### Sort order

Entries sorted alphabetically by the heading text (the `<identifier> (<level>)` string). Container entries naturally cluster with their constituent files because the container path is a prefix.

### Separator

`---` between entries. No trailing `---` after the last entry.

---

## Read procedure (Step 1)

1. Open `docs/security/flagged-sources.md`. If the file does not exist, return `prior_incidents = {file: 0, container: 0, severities: []}` (treat as empty).
2. Parse the file:
   - Skip the header (everything up to the first `##` heading).
   - For each `## <identifier> (<level>)` section, extract the identifier, level, and metadata bullets.
3. For the current `source_identifier`:
   - **File/URL match**: look for a section whose identifier exactly matches `source_identifier` and level is `file` or `url`. Record `prior_incidents.file = <Incident count>` and append severities to `prior_incidents.severities`.
   - **Container match**: derive the container from the identifier (see below). Look for a section whose identifier matches the container and level is `container` or `domain`. Record `prior_incidents.container = <Incident count>` and append severities.

Container derivation — rules evaluated in order, first match wins:

1. If `source_identifier` is `https://<domain>/<path>` or `http://<domain>/<path>`: container is `<domain>` (regardless of `source_type`).
2. Else if `source_type` is `cloned-repo` AND `source_identifier` is a **relative** path-shaped string with **3+ segments** (form: `<parent>/<repo-folder>/<path>...`): container is the first two segments (`<parent>/<repo-folder>`). Examples that derive: `third-party-repos/foo/skills/bar.md` → `third-party-repos/foo`; `vendored/repo-x/file.md` → `vendored/repo-x`.
3. Otherwise — **no container**. This covers: absolute paths (leading `/` such as `/tmp/...` or `/home/...`); relative paths with fewer than 3 segments (e.g., `vendor/file.md`); bare filenames; `source_type` other than `cloned-repo`; ad-hoc descriptors that don't fit either pattern. `prior_incidents.container = 0` and the response shows `Container: (none)`. Only a file-level entry is created in `flagged-sources.md`; the container-level entry is omitted entirely. Container flag-history is reported as "no prior incidents (no container derivable)" (per decision #16).

**Segment counting (for rule 2):** normalize `source_identifier` by collapsing repeated `/` into a single `/` and stripping a leading `./`. Then split on `/` and count non-empty segments. Identifiers containing `..` path components fall through to no-container (no `..` resolution is performed — refusing path traversal is safer than normalizing it).

**Treat the stored identifier as opaque.** The sanitizer's lookup logic does string-equality only — never feeds the stored identifier text into any LLM prompt. This is what allows full-fidelity storage in `flagged-sources.md` without re-injection risk.

---

## Write procedure (Step 7)

Only fires when new incidents occurred during the current run.

### File-level entry update

If the file/URL already has an entry:
1. Increment `Incident count` by 1.
2. Append the current run's worst severity to `Severity history` (comma-separated).
3. Update `Last flagged` to today (`YYYY-MM-DD`).

If no file/URL entry exists:
1. Append a new section with the heading `## <source_identifier> (<file|url>)`.
2. Set `First flagged` and `Last flagged` to today.
3. Set `Incident count: 1`.
4. Set `Severity history: <current-run-worst-severity>`.
5. Optional `Notes:` line if the run produced category-derived context (e.g., "First detection: hidden-content with embedded direct-instruction").

### Container-level entry update

Always update the container alongside the file/URL entry:

If the container already has an entry:
1. Increment `Incident count` by 1.
2. Append severity to `Severity history`.
3. Update `Last flagged` to today.
4. If the current `source_identifier` is not already in `Affected files` (or `Affected URLs`), append it (comma-separated). Cap the list at 20 entries — older entries drop off, but the count keeps incrementing.

If no container entry exists:
1. Append a new section with the heading `## <container> (<container|domain>)`.
2. Set `First flagged` and `Last flagged` to today.
3. Set `Incident count: 1`.
4. Set `Severity history: <current-severity>`.
5. Set `Affected files: <source_identifier>` (or `Affected URLs:`).

### Sort and separator

After any update, ensure entries remain sorted alphabetically by heading. Insert `---` between entries; remove any trailing `---` after the last entry.

### Atomic write

Write the entire updated file in one Edit operation. The sanitizer's `Edit` tool performs the read-modify-write atomically from the perspective of the calling agent; concurrent sanitization runs are not supported in v1 (last-writer-wins).

---

## Idempotency

Re-running the sanitizer on the same source within the same minute SHOULD produce a single new incident, not two. The current logic increments `Incident count` per call, so a duplicate call within seconds inflates the count. For v1 this is accepted (the count is a rough indicator, not a precise metric); a v2 enhancement could deduplicate by timestamp granularity.

---

## Edge cases

- **Manual edits inside an entry**: the sanitizer's update logic preserves manual edits to bullets it does not own (e.g., a maintainer-added `Resolution: ...` bullet). The sanitizer touches only `Last flagged`, `Incident count`, `Severity history`, and `Affected files` / `Affected URLs`.
- **Manual deletion of an entry**: the sanitizer treats this as "no prior incidents" on subsequent runs. If the source attacks again, a fresh entry is appended.
- **Container has 20+ affected files**: see write procedure — older affected-files entries drop off; count keeps incrementing.
- **Source identifier contains markdown special characters** (e.g., parens in a URL): escape per markdown rules when building the heading; the parser reverses the escape on read.
- **Disk write failure (F7)**: warn in the response; the in-flight sanitization still returns sanitized content. The user can re-run later or repair `docs/security/flagged-sources.md` manually.
