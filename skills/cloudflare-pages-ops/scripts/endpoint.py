#!/usr/bin/env python3
"""Resolve one operation from the bundled Cloudflare Pages OpenAPI slice.

Usage: python3 endpoint.py <operationId>   (e.g. pages-project-create-project)
       python3 endpoint.py --list          (list operationId / METHOD / path)

The bundle is the Pages-only slice of Cloudflare's official OpenAPI (3.0.x):
the 11 `/accounts/{account_id}/pages/...` paths + their transitive $ref
closure. Finds the operation, $ref-resolves its params + request body +
success-response schema (bounded depth + cycle guard), and prints a readable
summary + a curl skeleton. Python stdlib only; no pip dependency. Every Pages
path is account-scoped and every response is the Cloudflare envelope
{success, errors, messages, result}.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "cloudflare-pages-openapi.json")
BASE = "https://api.cloudflare.com/client/v4"
MAXDEPTH = 6


def load():
    with open(SPEC) as f:
        return json.load(f)


def resolve_ref(spec, ref):
    node = spec
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def find_op(spec, opid):
    for path, item in spec.get("paths", {}).items():
        shared = (item or {}).get("parameters", []) or []
        for method, op in (item or {}).items():
            if isinstance(op, dict) and op.get("operationId") == opid:
                merged = dict(op)
                seen = {(p.get("name"), p.get("in")) for p in op.get("parameters", []) or []}
                merged["parameters"] = (op.get("parameters", []) or []) + [
                    p for p in shared if (p.get("name"), p.get("in")) not in seen
                ]
                return method.upper(), path, merged
    return None


def prop_type(ps, spec):
    if "$ref" in ps:
        return ps["$ref"].split("/")[-1]
    t = ps.get("type")
    if isinstance(t, list):
        t = "/".join(x for x in t if x != "null") or "null"
    if t == "array":
        it = ps.get("items", {}) or {}
        inner = it["$ref"].split("/")[-1] if "$ref" in it else it.get("type", "?")
        return f"array<{inner}>"
    if ps.get("enum"):
        return f"{t or 'enum'} {ps['enum']}"
    return t or "object"


def schema_lines(schema, spec, seen, depth, indent):
    pad = "  " * indent
    if depth <= 0:
        yield pad + "… (max depth — re-run on the named schema)"
        return
    if not isinstance(schema, dict):
        return
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            yield pad + f"→ {ref.split('/')[-1]} (recursive)"
            return
        yield from schema_lines(resolve_ref(spec, ref), spec, seen | {ref}, depth, indent)
        return
    for comb in ("allOf", "oneOf", "anyOf"):
        if comb in schema:
            yield pad + f"({comb}):"
            for sub in schema[comb][:8]:
                yield from schema_lines(sub, spec, seen, depth - 1, indent + 1)
            return
    t = schema.get("type")
    if t == "object" or "properties" in schema:
        req = set(schema.get("required", []))
        props = schema.get("properties", {}) or {}
        if not props:
            yield pad + "{ object }"
            return
        for name, ps in props.items():
            mark = " *" if name in req else ""
            yield pad + f"- {name}{mark}: {prop_type(ps, spec)}"
            yield from schema_lines(ps, spec, seen, depth - 1, indent + 1)
    elif t == "array":
        yield pad + "[array of]:"
        yield from schema_lines(schema.get("items", {}), spec, seen, depth - 1, indent + 1)


def list_ops(spec):
    rows = []
    for path, item in spec.get("paths", {}).items():
        for method, op in (item or {}).items():
            if isinstance(op, dict) and op.get("operationId"):
                short = path.replace("/accounts/{account_id}", "")
                rows.append((op["operationId"], method.upper(), short))
    for oid, m, p in sorted(rows):
        print(f"  {oid:42} {m:6} {p}")


def main():
    if len(sys.argv) != 2:
        print("usage: python3 endpoint.py <operationId> | --list", file=sys.stderr)
        sys.exit(2)
    spec = load()
    if sys.argv[1] == "--list":
        print("Cloudflare Pages operationIds:")
        list_ops(spec)
        return
    opid = sys.argv[1]
    found = find_op(spec, opid)
    if not found:
        print(f"operationId '{opid}' not found — scan assets/endpoint-index.md.", file=sys.stderr)
        sys.exit(1)
    method, path, op = found
    url = f"{BASE}{path}"

    print(f"operation: {opid}")
    print(f"{method} {url}")
    if op.get("summary"):
        print(f"summary: {op['summary'].strip()}")
    print('auth: -H "Authorization: Bearer $<token_env>"  (account_id from context)')

    params = op.get("parameters") or []
    if params:
        print("\nPARAMS (* = required):")
        for pr in params:
            if "$ref" in pr:
                pr = resolve_ref(spec, pr["$ref"])
            mark = " *" if pr.get("required") else ""
            sch = pr.get("schema", {}) or {}
            print(f"  - {pr.get('name')} ({pr.get('in')}){mark}: {prop_type(sch, spec)}")

    rb = op.get("requestBody", {})
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"])
    content = rb.get("content", {}) or {}
    body_ct = next(iter(content)) if content else None
    if content:
        print(f"\nREQUEST BODY ({body_ct}){' *' if rb.get('required') else ''}:")
        if body_ct == "multipart/form-data":
            print("  (binary upload — use `wrangler pages deploy <dir>`, not a curl)")
        bsch = content[body_ct].get("schema", {}) or {}
        for line in schema_lines(bsch, spec, set(), MAXDEPTH, 1):
            print(line)

    resp = op.get("responses", {}) or {}
    code = next((c for c in ("200", "201", "202", "204") if c in resp), None)
    if code and code != "204":
        r = resp[code]
        if "$ref" in r:
            r = resolve_ref(spec, r["$ref"])
        rc = r.get("content", {}) or {}
        if rc:
            ct = next(iter(rc))
            print(f"\nRESPONSE {code} ({ct}) — envelope {{success, errors, messages, result}}:")
            for line in schema_lines(rc[ct].get("schema", {}), spec, set(), 3, 1):
                print(line)

    print("\nERRORS: check `success:false` + `errors[].code/message`; 1200 req/5min.")
    print("\nCURL SKELETON:")
    if body_ct == "multipart/form-data":
        print("  (deploy is a multipart upload — use `wrangler pages deploy <dir>`, not curl)")
    json_ct = body_ct is not None and body_ct != "multipart/form-data"
    cth = ' -H "Content-Type: application/json" -d \'<json body>\'' if json_ct else ""
    print(f'  curl -sS -X {method} -H "Authorization: Bearer $<token_env>"{cth} \\')
    print(f'    "{url.replace("{account_id}", "$CLOUDFLARE_ACCOUNT_ID")}"')


if __name__ == "__main__":
    main()
