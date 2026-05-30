# atlassian-rest-ops

> Call the Atlassian Cloud REST API directly — Confluence Cloud v2 +
> Jira Cloud v3 — via `curl` (no SDK, no pip). Constructs any of the
> 800+ endpoints from a bundled OpenAPI spec via an endpoint index + a
> `$ref`-resolver, with per-API patterns (base URL, pagination, errors,
> rate limits) and the ADF / storage rich-text formats handled
> explicitly. Reads credentials from a file convention; the token value
> is read only by `curl`, never printed.

**Skill file:** [`skills/atlassian-rest-ops/SKILL.md`](../../skills/atlassian-rest-ops/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent **full-coverage** access to Confluence Cloud (v2) and Jira Cloud (v3) by calling the REST API directly — the complete API surface, including writes (e.g. creating a Confluence page). **No language SDK, no `pip` dependency:** API calls use `curl`; the only helper is a `python3` stdlib `$ref`-resolver. Confluence and Jira differ on several axes, so the skill carries **per-API** patterns rather than one generic shape.

## When to activate

- ✅ Performing a Confluence Cloud v2 operation (pages, spaces, attachments, search…).
- ✅ Performing a Jira Cloud v3 operation (issues, JQL search, comments, transitions…).
- ✅ Any write or operation you need done programmatically against the Atlassian REST API.

### When NOT to activate

- The target is Atlassian **Server / Data Center** (this skill is Cloud + API-token only).
- You only need credential setup — that's the `.service-accounts.yaml` / `.env` file convention, not this skill.

## Workflow

| Step | Role |
|---|---|
| 1 Resolve account | Read the `.service-accounts.yaml` record at the active scope → `base_url`, `email`, `token_env`. The token value stays in `.env`. |
| 2 Find endpoint | Scan `assets/endpoint-index.md` (one line per operation) for the one you need. |
| 3 Resolve shape | `python3 scripts/endpoint.py <confluence\|jira> <operationId>` → `$ref`-resolved params / request body / response + a `curl` skeleton. |
| 4 Construct + run | Apply the per-API patterns (auth, base URL, rich-text); run the `curl`. |
| 5 Handle response | Pagination + errors per API; honor Jira 429 `Retry-After`. |

## Per-API patterns

| | Confluence v2 | Jira v3 |
|---|---|---|
| Base URL | `<base_url>/wiki/api/v2/<path>` | `<base_url>/<path>` (paths include `/rest/api/3`) |
| Auth | Basic (`email:api_token`) | Basic (`email:api_token`) |
| Pagination | cursor + follow `_links.next` | `startAt`/`maxResults` (+`total`/`isLast`) or `nextPageToken` |
| Errors | inline JSON | `ErrorCollection {errorMessages, errors, status}` |
| Rich-text | `body: {representation, value}` — `value` always a string | ADF as a **raw JSON object** |
| Delete | two-stage: plain `DELETE` only trashes; `?purge=true` removes (once trashed) | standard `DELETE` |

**Rich-text gotcha:** Jira embeds ADF as a **raw object**; Confluence `atlas_doc_format` embeds the ADF JSON **stringified** inside `body.value` (`storage` = XHTML string).

## Credentials (file convention — read-only)

The skill reads, never writes, credentials:

- `<scope-root>/.service-accounts.yaml`: per-account `{name, provider, base_url, email, token_env}` (workspace OR project scope; multi-account).
- `<scope-root>/.env`: the token value under `token_env` (gitignored). Read **only** by the `curl` subprocess; never surfaced to the agent.

## Bundled assets + examples

- `assets/confluence-v2.json`, `assets/jira-v3.json` — the OpenAPI specs (queried on disk via the index + resolver, never loaded into context).
- `assets/endpoint-index.md` — **832 operations**, one line each (discovery).
- `scripts/endpoint.py` — the `$ref`-resolving lookup (python3 stdlib).
- `scripts/{create-confluence-page,list-confluence-pages,create-jira-issue,search-jira-issues}.sh` — validated example `curl`s, each with a `.validation.md` proof.

## Limitations

- **Cloud + API-token only** — no Server/Data Center; no OAuth 2.0 (3LO) in v1.
- **Spec freshness** — the bundled OpenAPI specs are a point-in-time snapshot; refresh as Atlassian evolves the API.
- **`jq` in example scripts** — used for safe JSON build/parse (optional; inline JSON if `jq` is absent). API calls themselves need only `curl`.
- **Permissions** — some operations require specific Atlassian permissions; a `4xx` is the API's response, not a skill error.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
