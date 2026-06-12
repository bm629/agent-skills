#!/usr/bin/env python3
"""Resolve one operation from the bundled (UNOFFICIAL) swaggy-jenkins OpenAPI.

Usage: python3 endpoint.py <operationId>   (e.g. postJobBuild, getQueueItem)
       python3 endpoint.py --list          (list the CORE operationIds)

Jenkins has NO official OpenAPI (JENKINS-35808); this resolves the community
`swaggy-jenkins` description bundled in assets/, which covers only a SUBSET of
the CORE surface (it omits buildWithParameters, consoleText, arbitrary
job/<n>/<build>/api/json, copy/stop/doDelete-on-build). The authoritative CORE
path table is assets/endpoint-index.md — use this resolver as a schema
cross-check for the ops it does cover. Python stdlib only; no pip dependency.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "swaggy-jenkins-openapi.json")
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
        for method, op in (item or {}).items():
            if isinstance(op, dict) and op.get("operationId") == opid:
                return method.upper(), path, op
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
        yield pad + "… (max depth)"
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


def list_core(spec):
    for path, item in spec.get("paths", {}).items():
        if "/blue/" in path:
            continue
        for method, op in (item or {}).items():
            if method in ("get", "post", "put", "delete", "patch"):
                print(f"  {op.get('operationId', '(none)'):26} {method.upper():5} {path}")


def main():
    if len(sys.argv) != 2:
        print("usage: python3 endpoint.py <operationId> | --list", file=sys.stderr)
        sys.exit(2)
    spec = load()
    if sys.argv[1] == "--list":
        print("CORE swaggy-jenkins operationIds (unofficial subset):")
        list_core(spec)
        return
    opid = sys.argv[1]
    found = find_op(spec, opid)
    if not found:
        print(f"operationId '{opid}' not in the bundled swaggy-jenkins spec.", file=sys.stderr)
        print("Run --list, or use the authoritative assets/endpoint-index.md.", file=sys.stderr)
        sys.exit(1)
    method, path, op = found

    print(f"operation: {opid}  (source: UNOFFICIAL swaggy-jenkins)")
    print(f"{method} <base_url>{path}")
    if op.get("summary"):
        print(f"summary: {op['summary'].strip()}")
    print('auth: -u "$username:$<token_env>"  (crumb only as a 403 fallback)')

    params = []
    for pr in (op.get("parameters") or []):
        if "$ref" in pr:
            pr = resolve_ref(spec, pr["$ref"])
        params.append(pr)
    if params:
        print("\nPARAMS (* = required):")
        for pr in params:
            mark = " *" if pr.get("required") else ""
            ptype = prop_type(pr.get("schema", {}) or {}, spec)
            print(f"  - {pr.get('name')} ({pr.get('in')}){mark}: {ptype}")

    rb = op.get("requestBody", {})
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"])
    content = rb.get("content", {}) or {}
    if content:
        ct = next(iter(content))
        print(f"\nREQUEST BODY ({ct}):")
        for line in schema_lines(content[ct].get("schema", {}), spec, set(), MAXDEPTH, 1):
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
            print(f"\nRESPONSE {code} ({ct}):")
            for line in schema_lines(rc[ct].get("schema", {}), spec, set(), 3, 1):
                print(line)

    print("\nNOTE: swaggy-jenkins is unofficial + partial; see assets/endpoint-index.md.")
    print("\nCURL SKELETON:")
    body = ' --data-binary @config.xml' if content else ""
    print(f'  curl -sS -u "$username:$<token_env>" -X {method} \\')
    print(f'    "$base_url{path}"{body}')


if __name__ == "__main__":
    main()
