#!/usr/bin/env python3
"""Resolve one operation from the bundled Netlify OpenAPI (Swagger 2.0).

Usage: python3 endpoint.py <operationId>   (e.g. createSiteDeploy, updateSite)
       python3 endpoint.py --list          (list operationId / METHOD / path)

Finds the operation by operationId, $ref-resolves its parameters + body schema
+ success-response schema (bounded depth + cycle guard) against the bundled
spec, and prints a readable summary + a curl skeleton. The spec is Swagger 2.0
(refs point at #/definitions; body params carry a `schema`). Python stdlib
only; no pip dependency. Most ops are also callable via the CLI escape hatch:
`netlify api <operationId> --data '<json>'`.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "netlify-openapi.json")
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
                # Swagger 2.0: path-level params apply to every method (op-level wins on name+in).
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
            for sub in schema[comb]:
                yield from schema_lines(sub, spec, seen, depth, indent)
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
                rows.append((op["operationId"], method.upper(), path))
    for oid, m, p in sorted(rows):
        print(f"  {oid:28} {m:6} {p}")


def main():
    if len(sys.argv) != 2:
        print("usage: python3 endpoint.py <operationId> | --list", file=sys.stderr)
        sys.exit(2)
    spec = load()
    if sys.argv[1] == "--list":
        print("Netlify operationIds (also via `netlify api <operationId> --data ...`):")
        list_ops(spec)
        return
    opid = sys.argv[1]
    found = find_op(spec, opid)
    if not found:
        print(f"operationId '{opid}' not found — scan assets/endpoint-index.md.", file=sys.stderr)
        sys.exit(1)
    method, path, op = found
    base = spec.get("basePath", "")
    host = spec.get("host", "api.netlify.com")
    url = f"https://{host}{base}{path}"

    print(f"operation: {opid}")
    print(f"{method} {url}")
    if op.get("summary"):
        print(f"summary: {op['summary'].strip()}")
    print('auth: -H "Authorization: Bearer $<token_env>"')

    params = [pr for pr in (op.get("parameters") or []) if pr.get("in") != "body"]
    if params:
        print("\nPARAMS (* = required):")
        for pr in params:
            mark = " *" if pr.get("required") else ""
            print(f"  - {pr.get('name')} ({pr.get('in')}){mark}: {pr.get('type', 'string')}")

    body = next((pr for pr in (op.get("parameters") or []) if pr.get("in") == "body"), None)
    if body:
        print(f"\nREQUEST BODY ({body.get('name', 'body')}{' *' if body.get('required') else ''}):")
        for line in schema_lines(body.get("schema", {}) or {}, spec, set(), MAXDEPTH, 1):
            print(line)

    resp = op.get("responses", {}) or {}
    code = next((c for c in ("200", "201", "202", "204") if c in resp), None)
    if code and code != "204" and resp[code].get("schema"):
        print(f"\nRESPONSE {code}:")
        for line in schema_lines(resp[code]["schema"], spec, set(), 3, 1):
            print(line)

    print("\nERRORS: non-2xx; limits 500/min, deploys 3/min·100/day (honor X-RateLimit-*).")
    print("\nCALL OPTIONS:")
    print(f"  CLI:  netlify api {opid} --data '<json>'")
    cth = ' -H "Content-Type: application/json" -d \'<json body>\'' if body else ""
    print(f'  REST: curl -sS -X {method} -H "Authorization: Bearer $<token_env>"{cth} \\')
    print(f'          "{url}"')


if __name__ == "__main__":
    main()
