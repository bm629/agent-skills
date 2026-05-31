# API fallback — `gh api` — `github-cli-ops`

Use only when no first-class `gh` command exists for the operation. `gh api` makes an
authenticated HTTP request to the REST API (v3) or, with `graphql`, to GraphQL (v4).
It inherits auth, base URL, and the `Accept` header from `gh` — so per-call
`GH_TOKEN` still applies and nothing else needs configuring.

## Common gh-api-only areas

About **a third** of the REST surface has **no** first-class `gh` command — for these,
go straight to `gh api` (don't bother scanning `cli-index.md` for a command that does
not exist):

- **Whole areas, no command:** `teams` (there is no `gh team`), `checks` (check
  runs/suites), `packages`, `code-scanning`, `code-security`, `secret-scanning`,
  `dependabot`, `security-advisories`, `apps`, `migrations`, `reactions`,
  `interactions`, low-level **git data** (blobs / trees / refs / commits / tags),
  `billing`, `oidc`, `classroom`, `dependency-graph`, enterprise-team management, and
  the small utility endpoints (`meta`, `markdown`, `emojis`, `gitignore`, `rate-limit`).
- **Partial-coverage areas** (a command exists but covers only the common ops — the
  long tail is `gh api`): `repos` (e.g. traffic, contents, many settings), `actions`,
  `orgs`, `users`, `codespaces`, `activity` (events / feeds / notifications).

When unsure whether a command exists, a quick `gh <area> --help` (or its absence from
`cli-index.md`) confirms it.

## Find → resolve → construct

1. **Find:** scan `assets/endpoint-index.md` (one line per op:
   `METHOD path — summary (operationId)`) for the operation. Never load the multi-MB
   spec into context.
2. **Resolve the shape:** `python3 scripts/endpoint.py <operationId>` dereferences that
   one operation from `assets/github-openapi.json` (`$ref`-resolved) and prints the
   method, path, params, request/response schema, and a `gh api` skeleton.
3. **Construct** the call with the flags below.

## Flags (from `gh api --help`)

| Flag | Use |
|---|---|
| `<endpoint>` | path like `repos/{owner}/{repo}/issues`, or `graphql` |
| `-X, --method` | HTTP method (default GET; auto-POST once any field is added) |
| `-f, --raw-field key=value` | **string** parameter |
| `-F, --field key=value` | typed parameter: `true`/`false`/`null`/ints → JSON types; `@file` reads a file (`@-` = stdin); `{owner}`/`{repo}`/`{branch}` placeholders fill from the repo |
| `--input <file>` | pre-built JSON body (`-` = stdin); fields then go in the query string |
| `-H, --header key:value` | extra header (e.g. a custom `Accept`) |
| `--paginate` | fetch all pages (follows `Link`); `--slurp` wraps pages into one array |
| `-q, --jq <expr>` | slice the response with built-in jq |
| `-t, --template` | Go-template output |
| `--hostname <host>` | target a non-default host (Enterprise) |
| `-i/--include`, `--verbose`, `--silent` | response headers / full trace / suppress body |

Nested params: `key[subkey]=value`; arrays: repeat `key[]=v1 key[]=v2` (empty array: `key[]`).

## Examples

```bash
# Read with no first-class command (repo traffic):
GH_TOKEN="$TOK" gh api repos/{owner}/{repo}/traffic/views --jq '.count'

# Mutating call (PATCH) with typed + string fields:
GH_TOKEN="$TOK" gh api -X PATCH repos/{owner}/{repo} -f description='new' -F has_issues=true

# GET with query params (use -X GET so fields don't flip it to POST):
GH_TOKEN="$TOK" gh api -X GET search/issues -f q='repo:cli/cli is:open'

# Pre-built JSON body from a file:
GH_TOKEN="$TOK" gh api repos/{owner}/{repo}/rulesets --input ruleset.json

# Paginate a large collection into one array:
GH_TOKEN="$TOK" gh api --paginate --slurp repos/{owner}/{repo}/issues
```

## GraphQL (`gh api graphql`)

For GraphQL-only surfaces (e.g. Discussions). Pass the query as `-f query='…'`; any
other `-f`/`-F` become GraphQL variables.

```bash
GH_TOKEN="$TOK" gh api graphql -f query='{ viewer { login } }'

# Paginated GraphQL needs $endCursor + pageInfo in the query:
GH_TOKEN="$TOK" gh api graphql --paginate -f query='
  query($endCursor: String) {
    viewer { repositories(first: 100, after: $endCursor) {
      nodes { nameWithOwner }
      pageInfo { hasNextPage endCursor }
    } }
  }'
```

## Errors & scopes

- A non-zero exit / HTTP 4xx is the API's answer. Read the JSON error body
  (`--include`/`--verbose` to see status + headers).
- **403/404 on a valid call** is usually a missing **token scope** (e.g. `repo`,
  `delete_repo`, `read:org`, `admin:org`, `workflow`). Mint a properly-scoped token
  (see [`auth.md`](auth.md)); do not retry blindly.
- **422** = validation (bad/missing field) — re-resolve the schema (Step 3b).
- Rate limits surface as 403 with `X-RateLimit-Remaining: 0` (or 429) + a reset header;
  back off until reset.
