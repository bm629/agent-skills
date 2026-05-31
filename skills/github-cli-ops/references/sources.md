# Sources & provenance — `github-cli-ops`

Synthesized 2026-05-31. Facts grounded in authoritative primary sources (the `gh`
manual itself + GitHub's official OpenAPI description + the verified spec analysis),
paraphrased — not copied. Research note: for this domain the authoritative source is
`gh`'s own manual (trusted, version-matched tool output), so synthesis was grounded
there rather than web-only search; the key auth/encryption claims are verified from
`gh`'s own help output.

## Primary sources

- **`gh` CLI manual, v2.92.0** (`gh help <topic>` / `gh <cmd> --help`), gathered as
  229 pages. Load-bearing facts:
  - `gh help environment` — `GH_TOKEN`/`GITHUB_TOKEN` *"takes precedence over
    previously stored credentials"*, per-invocation; `GH_ENTERPRISE_TOKEN` for
    Enterprise hosts; `GH_HOST` to pick a host. → the per-call auth model (no
    `gh auth switch`).
  - `gh api --help` — the full flag set (`-X`, `-f`/`-F` with magic typing, `-H`,
    `--paginate`/`--slurp`, `-q/--jq`, `--input`, `--hostname`, `graphql` + variables,
    `$endCursor` pagination). Auto-POST when a field is added.
  - `gh secret set --help` — *"Secret values are locally encrypted before being sent
    to GitHub"* → secrets via `gh secret set`, no hand-rolled libsodium.

- **GitHub REST OpenAPI description** — `github/rest-api-description`,
  `descriptions/api.github.com/api.github.com.2026-03-10.json` (OpenAPI 3.0.3, 784
  paths / 1,186 operations / 47 tags). Bundled as `assets/github-openapi.json` in
  augmentation. Verified parity facts: REST covers every API operation the CLI
  exposes, including **Projects v2** (`projectsV2` REST paths exist in this version);
  Discussions are GraphQL-only.

## Structural model

- The established per-provider service-skill pattern (frontmatter shape, 10 sections,
  endpoint index + `$ref`-resolver, the "added during augmentation" asset convention,
  honest-secret handling). Used as a structural model only; all content here is
  GitHub-specific.

## Scope at synthesis time

- github.com Cloud (v1). Enterprise Server routes via `host`/`GH_HOST`/
  `GH_ENTERPRISE_TOKEN` but was not validated.
- Bundled spec is a point-in-time snapshot (`2026-03-10`); refresh + re-pin as GitHub
  evolves the API, and regenerate the indexes + re-validate the resolver then.
