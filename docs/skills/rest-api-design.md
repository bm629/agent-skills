# rest-api-design

> The **design discipline** for a REST/HTTP API and its contract — the layer
> ABOVE any web framework. Turns domain nouns into a consistent, evolvable HTTP
> surface: resource/URL modeling, method + status-code choice, one error model
> (RFC 9457 problem+json by default), a success/pagination envelope, a
> versioning/auth/rate-limit stance, and the rendering of all of it as an
> OpenAPI 3.1 contract. It produces the decisions and the contract, **not** the
> handler code — `fastapi` and `pydantic-v2` own the implementation.

**Skill file:** [`skills/rest-api-design/SKILL.md`](../../skills/rest-api-design/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the opinionated defaults a senior engineer applies when shaping
an HTTP API, so the surface is consistent and the contract is publishable
before any handler is written. Examples are Python/FastAPI + Pydantic v2
flavored, but every decision is language-agnostic. It is the sibling-above of
`fastapi` (framework mechanics) and `pydantic-v2` (schema modeling): it
references them and does not duplicate them, and it hands off deep OpenAPI
authoring / linting / SDK codegen to dedicated tooling.

## When to activate

- ✅ Designing a new API surface from a set of domain entities.
- ✅ Choosing the status code for an outcome — 400 vs 422, 401 vs 403, PUT vs PATCH.
- ✅ Defining or fixing the error model, the success envelope, or the pagination scheme.
- ✅ Deciding a versioning, auth, or rate-limiting stance.
- ✅ Turning an agreed design into an OpenAPI 3.1 contract.

### When NOT to activate

- Writing the FastAPI handler/router/DI code for an already-designed endpoint → `fastapi`.
- Modeling the request/response data classes in depth → `pydantic-v2`.
- Authoring/linting a large OpenAPI doc or running SDK codegen → a dedicated OpenAPI concern.
- Designing a GraphQL or gRPC surface → out of scope (REST/HTTP only).

## Workflow

Seven ordered steps, each with an opinionated default (deviate only with a reason):

| Step | Decision |
|---|---|
| 1 Resources | nouns not verbs; plural + consistent collections; cap nesting at 2 levels; opaque IDs |
| 2 Methods | RFC 9110 semantics; PUT replaces / PATCH merges; `Idempotency-Key` for retryable POST |
| 3 Status codes | match the outcome; **422** for validation, **400** for parse failures; never 200-with-error |
| 4 Error model | **one** model, **RFC 9457 problem+json** default (`type`/`title`/`status`/`detail`/`instance` + `errors[]`) |
| 5 Success + pagination | one envelope (`data` + `pagination`/`meta` + `links`); **cursor/keyset default**, enforced max page size |
| 6 Versioning / auth / rate limit | URL-path version, major-only; Bearer/JWT or API-key; **429 + `Retry-After`** baseline |
| 7 Contract | OpenAPI **3.1** (JSON Schema 2020-12; `type: [...,"null"]` not `nullable`); one worked contract |

## Hard rules it enforces

- One error model for the whole API — RFC 9457 problem+json as the default, served as `application/problem+json`; never mix two shapes.
- Never return 2xx with an error in the body — the status code is the contract.
- Resources are nouns; collections plural + consistent.
- Every collection endpoint is paginated with an enforced max page size.
- Always HTTPS; auth declared in the contract (`securitySchemes` + `security`).
- PUT is full-replace, PATCH is partial — never conflated.
- OpenAPI **3.1** for the contract; nullability via a `"null"` type member.

## Progressive disclosure (`references/`)

- `references/error-model.md` — RFC 9457 member-by-member, the `errors` validation array, the `about:blank` default, 404 + 422 examples, the FastAPI exception-handler pattern, and the non-standard `{error:{...}}` alternative.
- `references/contract-patterns.md` — the success envelope, the cursor-vs-offset decision table with both response shapes, the versioning lifecycle (Deprecation/Sunset/410), auth schemes, rate-limit headers.
- `references/openapi-mapping.md` — the design→OpenAPI-3.1 element mapping, 3.1-vs-3.0 notes, and one complete worked contract with problem+json responses + a security scheme.
- `references/sources.md` — research provenance.

## Limitations

- **Design + contract only** — handler/router code is `fastapi`'s job; schema modeling is `pydantic-v2`'s.
- **REST/HTTP only** — GraphQL and gRPC are out of scope.
- **One worked contract, not an authoring toolchain** — deep OpenAPI authoring, linting, mock servers, and SDK codegen are handed off.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
