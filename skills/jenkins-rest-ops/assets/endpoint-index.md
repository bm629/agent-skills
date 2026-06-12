# Jenkins CORE Remote Access endpoint index

The authoritative CORE-path table for this skill, grounded on the official Jenkins Remote Access API docs (jenkins.io + the Jenkins wiki). Jenkins is **path-addressed** REST (not RPC, not operationId-based): the same path template serves every job. Paths are relative to `<base_url>`. Reads are GET (auth only); writes are POST (auth; a crumb only as a fallback — see `references/patterns.md`).

For the subset that the bundled (unofficial) `swaggy-jenkins` OpenAPI also describes, `python3 scripts/endpoint.py <operationId>` prints its request/response schema. This index is the primary navigation; swaggy-jenkins is a partial cross-check (it omits `buildWithParameters`, `consoleText`, arbitrary `job/<n>/<build>/api/json`, copy/stop/doDelete-on-build).

## Conventions

- **Nested folders / multibranch:** repeat the `job/` segment per level — `job/<folder>/job/<name>/...`.
- **URL-encode** job names with spaces/specials (`My Job` → `My%20Job`).
- **Shape responses:** `?tree=field[sub,sub]` (select fields — preferred), `?depth=N` (recurse — inflates payloads fast), `?pretty=true`. `api/json` / `api/xml` (`?xpath=`) / `api/python` are the same data in different serializations.

## Trigger a build (async — returns a queue item, not a build)

- `POST job/<name>/build` — trigger, no parameters. → `201` + `Location: <base_url>/queue/item/<id>/`.
- `POST job/<name>/buildWithParameters` — trigger with params as form data (`--data NAME=value`, repeatable). → `201` + queue-item `Location`.

## Poll the queue item → build

- `GET queue/item/<id>/api/json` — poll until `.executable.number` / `.executable.url` appears (build started). While waiting: `.why`, `.blocked`, `.buildable`, `.stuck`; dropped: `.cancelled: true`. The queue item is ephemeral (~5 min post-completion) — capture `.executable.url` promptly.

## Read build status + console

- `GET job/<name>/<buildNumber>/api/json` — `result` (SUCCESS/FAILURE/UNSTABLE/ABORTED/`null` while building), `building`, `duration` (ms), `number`, `url`, `timestamp`.
- `GET job/<name>/lastBuild/api/json` — same shape for the latest build (also `lastSuccessfulBuild`, `lastFailedBuild`, `lastCompletedBuild`).
- `GET job/<name>/<buildNumber>/consoleText` — full plaintext console log.
- `GET job/<name>/<buildNumber>/logText/progressiveText?start=<offset>` — streaming chunk from `<offset>`; response headers `X-Text-Size` (next offset) + `X-More-Data: true` (more to come). Loop with `X-Text-Size` as the next `start`.

## List / inspect

- `GET api/json` — root: `jobs[]` + system/view info.
- `GET job/<name>/api/json` — job detail (builds list, `last*` pointers, health, params).
- `GET view/<name>/api/json` — a view's contents.
- `GET queue/api/json` — the whole build queue.
- `GET computer/api/json` — nodes / executors.

## Job CRUD (CORE)

- `POST createItem?name=<name>` — create; body = a `config.xml`, `Content-Type: application/xml` (use `--data-binary @config.xml`).
- `POST createItem?name=<new>&mode=copy&from=<src>` — copy an existing job.
- `GET job/<name>/config.xml` / `POST job/<name>/config.xml` — read / update a job's config XML.
- `POST job/<name>/doDelete` — delete a job.
- `POST job/<name>/enable` · `POST job/<name>/disable` — enable / disable a job.

## Build management

- `POST job/<name>/<buildNumber>/stop` — stop a running build (`lastBuild/stop` for the latest).
- `POST job/<name>/<buildNumber>/doDelete` — delete a build's record.

## CSRF crumb (fallback only — see patterns.md)

- `GET crumbIssuer/api/json` — `{crumbRequestField (default "Jenkins-Crumb"), crumb}`. With API-token auth the crumb is **exempt** (Jenkins 2.96/2.107+); fetch + attach only on a `403 No valid crumb`. A `404` here means CSRF is disabled — skip the header.
