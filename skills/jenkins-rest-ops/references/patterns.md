# Jenkins REST patterns — async builds, the crumb, paths

Jenkins is **path-addressed** REST: append `api/json` (or `api/xml` / `api/python`) to almost any object's URL to read it; POST to action paths to write. Five patterns cover the CORE surface.

## 1. The async-build trap (the #1 mistake)

A build trigger does **not** return a build — it returns a **queue item**:

1. `POST job/<name>/build` (or `buildWithParameters` with `--data K=V`) → **HTTP 201** + a `Location:` header = the queue item, e.g. `<base_url>/queue/item/<id>/`.
2. **Poll** `GET queue/item/<id>/api/json` until `.executable.number` / `.executable.url` appears — only then has the build started (it may sit in the queue: quiet period, blocked, no free executor — see `.why`). `.cancelled: true` means it was dropped.
3. *Then* read the build at `.executable.url` (`job/<name>/<number>/api/json`).

Do not assume the build started immediately or guess the build number. The queue item is **ephemeral** (~5 min after the build ends) — capture `.executable.url` promptly. `scripts/trigger-build.sh` + `scripts/poll-queue-item.sh` implement this. (Note: the bundled `swaggy-jenkins` `getQueueItem` schema omits `.executable` — trust the official `.executable.number`/`.url` the scripts use, not the resolver here.)

## 2. The CSRF crumb — token auth is exempt; crumb is a fallback

Since Jenkins **2.96 weekly / 2.107 LTS**, a request authenticated with an **API token over HTTP Basic auth is exempt from the CSRF crumb** (jenkins.io Remote Access API; CloudBees / JENKINS-22474). So with token auth you normally **POST without any crumb**.

Only when a POST returns **`403 No valid crumb was included in the request`** (old Jenkins, or password auth) do you need one:

1. `GET crumbIssuer/api/json` → `{crumbRequestField (default "Jenkins-Crumb"), crumb}`.
2. Re-send the POST with header `Jenkins-Crumb: <crumb>` (use the returned `crumbRequestField` name). When a crumb is required via cookie-session auth it is session-scoped — but with token auth the crumb is moot.
3. If `crumbIssuer/api/json` **404s**, CSRF is disabled — skip the header.

`scripts/crumb.sh` prints the `field:value` header line and exits cleanly (printing nothing) on 404/empty. Attach only on a 403.

## 3. Paths, folders, and response shaping

- **Nested folders / multibranch:** repeat the `job/` segment per level — `job/<folder>/job/<name>/...`.
- **URL-encode** job names with spaces/specials (`My Job` → `My%20Job`).
- **`?tree=field[sub,sub]`** selects fields (preferred — small responses); **`?depth=N`** recurses (inflates payloads fast — use sparingly); **`?pretty=true`** pretty-prints.
- `api/json` / `api/xml` (supports `?xpath=` + `?exclude=`) / `api/python` are the **same data** in different serializations.

## 4. Build status + console

- `job/<name>/<n>/api/json` → `result` (SUCCESS / FAILURE / UNSTABLE / ABORTED / **`null` while building**), `building`, `duration` (ms). `lastBuild`, `lastSuccessfulBuild`, `lastFailedBuild`, `lastCompletedBuild` are aliases for the build number.
- `job/<name>/<n>/consoleText` → full plaintext log. `…/logText/progressiveText?start=<offset>` streams from `<offset>`, returning `X-Text-Size` (next offset) + `X-More-Data: true` (more to come) headers — loop with `X-Text-Size` as the next `start`.

## 5. Job CRUD + the config.xml content-type

- Create: `POST createItem?name=<name>` with the body = a `config.xml` and **`Content-Type: application/xml`** (use `--data-binary @config.xml` so the XML is not form-mangled). Copy: `createItem?name=<new>&mode=copy&from=<src>`.
- Read/update config: `GET`/`POST job/<name>/config.xml`. Delete: `POST job/<name>/doDelete`. Enable/disable: `POST job/<name>/enable` / `…/disable`. Build mgmt: `POST job/<name>/<n>/stop`, `…/doDelete`.

## Grounding caveat — no official OpenAPI

Jenkins ships **no official OpenAPI** (JENKINS-35808). The bundled `assets/swaggy-jenkins-openapi.json` is the community **unofficial** description (flagged in `sources.md`); it is **partial** (omits `buildWithParameters`, `consoleText`, arbitrary `job/<n>/<build>/api/json`, copy/stop/doDelete-on-build) and models a few ops oddly (e.g. its `postJobBuild` invents a required `json` query param the official trigger does not need). The **authoritative** CORE path table is `assets/endpoint-index.md`, grounded on the official Remote Access API docs; treat the resolver (`scripts/endpoint.py`) as a schema cross-check only. The CORE API is plugin-independent — plugin-contributed endpoints vary per install and are out of scope.
