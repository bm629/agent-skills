# atlassian-rest-ops

> Call the Atlassian Cloud REST API directly — Confluence Cloud v2 +
> Jira Cloud v3 — via `curl` (no SDK, no pip). Constructs any of the
> 800+ endpoints from a bundled OpenAPI spec via an endpoint index + a
> `$ref`-resolver, with per-API patterns (base URL, pagination, errors,
> rate limits) and the ADF / storage rich-text formats handled
> explicitly. Consumes caller-injected credentials (base_url, email, and a
> token resolved by variable name); the token value is read only by `curl`,
> never printed.

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
- You only need credential setup — credentials are provided by the caller; this skill does not provision or resolve them.

## Workflow

| Step | Role |
|---|---|
| 1 Receive credentials | Consume the caller-injected `base_url`, `email`, and the token (resolved by variable name: project `.env` value if present, else the env var). The token value stays out of context. |
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

## Credentials (caller-injected — consumed, never provisioned)

The skill **consumes** caller-injected credentials; it never resolves a record or provisions anything:

- The caller injects `base_url`, `email`, and the **variable name** of the token (plus the acting capability) as context.
- The token **value** is resolved by an ordered load rule — the project-level `.env` value if that file exists and defines the var, else the environment variable of that name (project `.env` tried first; no scope-walk; project `.env`, not `.envrc`). It is read **only** by the `curl` subprocess; never surfaced to the agent.
- A `## Standalone usage (optional, not required)` appendix in the SKILL.md documents the by-hand bridge from a `.service-accounts.yaml` record + `.env` for a human running the skill manually — explicitly not a dependency.

## Bundled assets + examples

- `assets/confluence-v2.json`, `assets/jira-v3.json` — the OpenAPI specs (queried on disk via the index + resolver, never loaded into context).
- `assets/endpoint-index.md` — **832 operations**, one line each (discovery).
- `scripts/endpoint.py` — the `$ref`-resolving lookup (python3 stdlib).
- `scripts/{create-confluence-page,list-confluence-pages,create-jira-issue,search-jira-issues}.sh` — validated example `curl`s, each with a `.validation.md` proof.
- `scripts/md_to_adf.py` — a stdlib Markdown → ADF converter (headings, bold, code, links, lists, GFM tables); pipe a Markdown comment/description through it (`python3 scripts/md_to_adf.py < body.md`) to post it as native ADF instead of raw Markdown. Has a `.validation.md` proof.

## Limitations

- **Cloud + API-token only** — no Server/Data Center; no OAuth 2.0 (3LO) in v1.
- **Spec freshness** — the bundled OpenAPI specs are a point-in-time snapshot; refresh as Atlassian evolves the API.
- **`jq` in example scripts** — used for safe JSON build/parse (optional; inline JSON if `jq` is absent). API calls themselves need only `curl`.
- **Permissions** — some operations require specific Atlassian permissions; a `4xx` is the API's response, not a skill error.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
