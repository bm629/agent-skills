# github-cli-ops

> Perform any github.com operation **CLI-first**: prefer the `gh` CLI, and
> fall back to `gh api` (REST) — or `gh api graphql` — only where no command
> exists. Every call is authenticated **per-invocation** with `GH_TOKEN` read
> from a per-account record + gitignored `.env`; it never runs `gh auth
> switch` and never prints the token. For the REST long tail it constructs a
> `gh api` call from a bundled OpenAPI spec via an endpoint index + a
> `$ref`-resolver, and `gh secret set` handles client-side secret encryption.

**Skill file:** [`skills/github-cli-ops/SKILL.md`](../../skills/github-cli-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent full-coverage access to github.com — the ergonomic `gh`
commands where they exist, and the **complete** REST surface (1,186
operations) via `gh api` everywhere else. `gh` is the only runtime dependency:
it manages auth, hosts, pagination, output, and — critically — client-side
secret encryption, so the skill never reimplements HTTP plumbing or hand-rolls
crypto. It is the sibling of `atlassian-rest-ops` under the per-provider
service-skill pattern, but driving a first-class CLI instead of `curl`.

## When to activate

- ✅ An operation with a first-class command — issues, pull requests, repos,
  releases, labels, gists, Actions runs/workflows, Projects, secrets (`gh <cmd>`).
- ✅ A REST operation with **no** command — via `gh api <endpoint>`.
- ✅ A GraphQL-only need (e.g. Discussions) — `gh api graphql`.

### When NOT to activate

- A local/interactive `gh` action (`gh auth`, `gh browse`, `gh repo clone`,
  `gh pr checkout`, `gh config`, …) — those aren't API operations.
- GitHub Enterprise Server as a first-class need (v1 targets github.com;
  Enterprise routes via the record's `host` + `GH_HOST`/`GH_ENTERPRISE_TOKEN`
  but is untested in v1).
- Credential setup — that's the `.service-accounts.yaml` / `.env` convention.

## Workflow

| Step | Role |
|---|---|
| 1 Resolve account | Read the `provider: github` record (`token_env`, `host`); verify `GH_TOKEN="$<token_env>" gh api user`. The token value stays in `.env`. |
| 2 Decide CLI vs API | Scan `assets/cli-index.md` for a `gh` command. Prefer a command; `gh api` for the gap; `gh api graphql` for GraphQL-only. |
| 3a CLI path | Read flags live from `gh <cmd> --help`; run `GH_TOKEN="$<token_env>" gh <command> …` (`--json`/`--jq` for machine output). |
| 3b API fallback | Scan `assets/endpoint-index.md`; `python3 scripts/endpoint.py <operationId>` → `$ref`-resolved shape + a `gh api` skeleton. |
| 4 Handle response | `--jq`/`--paginate`/`--slurp`; a 4xx is usually a missing token scope, not a skill bug. |

## Auth — per-call `GH_TOKEN` (no global switch)

The account record names *which* account to act as; `gh` holds the token:

```yaml
# .service-accounts.yaml  (non-secret; token value lives in .env, gitignored)
accounts:
  - name: github-personal
    provider: github
    host: github.com
    token_env: GH_PERSONAL_TOKEN
```

Every call is `GH_TOKEN="$<token_env>" gh …`. Verified from `gh help
environment`, `GH_TOKEN` takes precedence over stored credentials
per-invocation — so the skill selects the account with **no `gh auth switch`**
and no mutation of the global active account (shared across the user's shells).
The token is read only by the `gh` subprocess; never printed.

## CLI-first vs `gh api` fallback

`gh` covers the common operations of `repos`/`issues`/`pulls`/`actions`/etc.,
but **~1/3 of the REST surface has no first-class command** — whole areas like
`teams`, `checks`, `packages`, `code-scanning`/`-security`, `dependabot`,
low-level `git` data, `reactions`, and `apps`, plus the long tail inside the
command-backed tags. For those the skill goes straight to `gh api` with the
resolver; `references/gh-api.md` lists the common gh-api-only areas.

## Bundled assets + examples

- `assets/github-openapi.json` — the GitHub REST OpenAPI spec (api.github.com,
  pinned `2026-03-10`; OpenAPI 3.0.3, 784 paths / 1,186 ops). Queried on disk,
  never loaded into context.
- `assets/endpoint-index.md` — **1,186 operations**, one line each (discovery).
- `assets/cli-index.md` — **229 `gh` commands**, one line each (discovery; flag
  detail is read live from `gh --help`).
- `scripts/endpoint.py` — the `$ref`-resolving lookup (python3 stdlib).
- `scripts/{create-issue,view-repo,set-secret,api-traffic-views,api-graphql-viewer}.sh`
  — validated example `gh`/`gh api` calls, each with a `.validation.md`.

## Limitations

- **github.com + token only** — no Enterprise Server as a v1 deliverable; no
  OAuth device flow (the token is provided).
- **`gh` is a hard dependency** — CLI-first, `gh api` fallback, and secret
  encryption all use it.
- **Spec freshness** — the bundled OpenAPI spec is a point-in-time snapshot;
  refresh + regenerate the index and re-validate the resolver as the API
  evolves.
- **Token scopes** — a `4xx` is usually a missing scope (e.g. `repo`,
  `delete_repo`, `read:org`), the API's response, not a skill error.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
