# Error model — RFC 9457 problem+json (default)

Load when defining or fixing an API's error contract.

## The standard: RFC 9457 (obsoletes RFC 7807)

One error shape for the whole API, served with media type **`application/problem+json`**. RFC 9457 is the current standard (it obsoleted RFC 7807 in 2023; it is backward-compatible — mostly clarifications plus a problem-type registry and `errors` as a recognized extension).

### Members

| Member | Type | Meaning |
|---|---|---|
| `type` | URI string | Identifies the problem **type**. Stable, documented; SHOULD be an absolute URI. Defaults to `"about:blank"` when there is nothing beyond the status code. |
| `title` | string | Short human summary of the type, constant across occurrences (localization aside). For `about:blank`, use the HTTP status phrase (`"Not Found"`, `"Unprocessable Content"`). |
| `status` | number | The HTTP status code, duplicated in the body so the body is self-contained. |
| `detail` | string | Human-readable explanation of **this** occurrence (not the type in general). |
| `instance` | URI string | Identifies this specific occurrence — e.g. the request path, or a trace/correlation id. |
| *extensions* | any | Domain-specific extra fields. **Clients MUST ignore extensions they don't recognize** — this lets the type evolve. |

### `about:blank` rule

When a problem carries no semantics beyond its status code, omit `type` (or set `"about:blank"`) and set `title` to the status phrase. Don't invent a bespoke `type` URI for a plain 404.

### Field-level validation → the `errors` extension

RFC 9457 recognizes an `errors` array as the standard way to carry a collection of sub-problems (e.g. one per invalid field). Each entry is itself a partial problem object; a `pointer` (JSON Pointer) or a `name`/`field` identifies the offending input.

## Examples

### 404 (no extra semantics — `about:blank`)

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
```
```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "No order exists with id ord_8f3a.",
  "instance": "/v1/orders/ord_8f3a"
}
```

### 422 validation error (typed, with the `errors` array)

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json
```
```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Your request parameters did not validate.",
  "status": 422,
  "detail": "The request body has 2 invalid fields.",
  "instance": "/v1/orders",
  "errors": [
    { "detail": "must be a positive integer", "pointer": "#/quantity" },
    { "detail": "must be a valid email address", "pointer": "#/customer/email" }
  ]
}
```

## FastAPI flavor (the framework owns the wiring — see the `fastapi` skill)

Model the problem shape with `pydantic-v2` and return it from exception handlers with the right media type. The design decision this skill makes is *the shape and the media type*; the handler wiring is framework mechanics.

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

PROBLEM_JSON = "application/problem+json"

class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None

def problem_response(problem: Problem) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        media_type=PROBLEM_JSON,
        content=problem.model_dump(exclude_none=True),
    )

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError):
    errors = [
        {"detail": e["msg"], "pointer": "#/" + "/".join(str(p) for p in e["loc"][1:])}
        for e in exc.errors()
    ]
    body = {
        "type": "https://api.example.com/problems/validation-error",
        "title": "Your request parameters did not validate.",
        "status": 422,
        "detail": f"The request has {len(errors)} invalid field(s).",
        "instance": str(request.url.path),
        "errors": errors,
    }
    return JSONResponse(status_code=422, media_type=PROBLEM_JSON, content=body)
```

Mature FastAPI plugins exist that format every error as RFC 9457 automatically (search the ecosystem); evaluate one before hand-rolling. Either way the contract is the same problem+json shape.

## Alternative (only if a house style mandates it): the `{error:{...}}` envelope

Some organizations standardize on a custom envelope instead of problem+json:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "quantity", "message": "must be a positive integer" }
    ]
  },
  "meta": { "request_id": "req_abc123" }
}
```

It is consistent and machine-parseable, but **non-standard** — tooling won't recognize it the way it recognizes `application/problem+json`. Prefer problem+json for new APIs. Whichever you pick, use **one** model across the entire API and never serve both.

## Rules of thumb

- One error model, applied everywhere. No per-subsystem variation.
- Always set the real status code; never 200-with-error-body.
- `type` URIs are stable and documented — never a generic random string, never a stack trace.
- `detail` is human-readable and safe — never leak stack traces, SQL, internal paths, or secrets.
- Include a correlation id (in `instance` or an extension) so a client can quote it in a support ticket.
