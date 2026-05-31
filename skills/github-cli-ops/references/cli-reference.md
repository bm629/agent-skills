# CLI-first path — `github-cli-ops`

The preferred path. `gh`'s high-level commands are ergonomic, validated, and handle
things raw REST does not (notably secret encryption).

## Decision rule

1. Scan `assets/cli-index.md` for a `gh` command matching the operation.
2. **A command exists →** use it (this path).
3. **No command →** fall to `gh api` ([`gh-api.md`](gh-api.md)).
4. **GraphQL-only need (e.g. Discussions) →** `gh api graphql`.

Many operations exist in both surfaces; the rule resolves the overlap toward the CLI.

## Finding the command + its flags

- **Discovery:** `assets/cli-index.md` is one line per command (`gh <path> — <summary>`).
  It is a *map*, not full docs.
- **Exact flags:** read them **live** from the installed `gh`:
  `GH_TOKEN="$<token_env>" gh <command> --help` (no token needed for `--help`, but
  it is harmless). Live help is always current with the user's `gh` version — the
  reason the full manual is not bundled.

## Structured output

Most read commands support machine-readable output:

```bash
GH_TOKEN="$TOK" gh repo view OWNER/REPO --json name,visibility,defaultBranchRef
GH_TOKEN="$TOK" gh pr list --repo OWNER/REPO --json number,title,state --jq '.[] | select(.state=="OPEN")'
GH_TOKEN="$TOK" gh issue view 42 --repo OWNER/REPO --json title,body,labels
```

- `--json <fields>` emits JSON; run `gh <cmd> --json` with no value to list the
  available fields.
- `--jq <expr>` slices it (built-in jq; no external `jq` needed).
- `--template` is the Go-template alternative.

## Secrets — `gh secret set` (client-side encryption)

`gh secret set` encrypts the value locally before sending it (verified from its help:
*"Secret values are locally encrypted before being sent to GitHub"*). This is why
CLI-first beats REST-direct: you never fetch the repo public key or libsodium-encrypt
by hand.

```bash
GH_TOKEN="$TOK" gh secret set MYSECRET --repo OWNER/REPO --body "$VALUE"
GH_TOKEN="$TOK" gh secret set MYSECRET --repo OWNER/REPO < value.txt   # from stdin/file
GH_TOKEN="$TOK" gh secret set MYSECRET --org MYORG --visibility all     # org-level
GH_TOKEN="$TOK" gh secret list --repo OWNER/REPO                        # verify (names only)
```

- Levels: repository (default), `--env`, `--org`, `--user`; app via `--app
  {actions|codespaces|dependabot}`.
- Secret **values** are never readable back (only names/metadata via `gh secret list`).

## Common command shapes

```bash
GH_TOKEN="$TOK" gh issue create --repo OWNER/REPO --title "T" --body "B" [--label bug]
GH_TOKEN="$TOK" gh pr create   --repo OWNER/REPO --title "T" --body "B" --base main --head feature
GH_TOKEN="$TOK" gh release create v1.0.0 --repo OWNER/REPO --notes "…" [./asset.zip]
GH_TOKEN="$TOK" gh repo create OWNER/NAME --private --description "…"
GH_TOKEN="$TOK" gh run list --repo OWNER/REPO --json databaseId,status,conclusion
```

Always confirm exact flags via `gh <cmd> --help` before running — flags evolve with
the `gh` version.
