"""Decide whether an angle's trigger is entailed by, or disjoint from, its type's trigger.

Two directions fail, and both have shipped:

* FAIL CLOSED (playbook #41) — a predicate rooted only on optional fields never fires, and
  "we did not configure it" reads identically to "it did not apply".
* FAIL OPEN (playbook #53) — a predicate that RESTATES the type-level trigger always fires,
  because a survey only runs when that trigger is true. It looks gated, gates nothing, and
  passes the non-empty-anchor assertion cleanly.

Neither is decidable by comparing per-field value sets; an earlier design tried and was unsound
both ways. The property is entailment — `trigger |= predicate` — and every field involved has a
tiny finite domain, so it is decided by enumeration rather than approximated.

This module is AUTHOR-TIME. It does not ship inside any portable skill and is not wired into a
validator's `main()`: a registry is static, only an author can violate these, and a false
positive at runtime would park every ticket in a live survey.
"""

from __future__ import annotations

import itertools
import json
import pathlib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "skills"
    / "project-document-discovery"
    / "schemas"
    / "capability-map.schema.json"
)


class _Absent:
    """A field the map omits. Distinct from every value the field could carry."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "ABSENT"


ABSENT = _Absent()

OPS = frozenset(
    {
        "in",
        "not_in",
        "eq",
        "neq",
        "is_true",
        "is_false",
        "is_absent",
        "is_present",
        "contains",
    }
)


@dataclass(frozen=True)
class FieldSpec:
    """What a capability-map field can be, for enumeration purposes.

    Attributes:
        path: Dotted path from the capability_map root.
        required: The schema requires it at every level of its chain, so it cannot be ABSENT.
        domain: Values it may take, ABSENT included when optional. Empty when not enumerable.
        enumerable: It has a finite domain. False for a bare string, an enum-less array, or one
            of the 25 property-less objects.
        is_array: Its value is a list, so `contains` is the applicable op.
    """

    path: str
    required: bool
    domain: tuple
    enumerable: bool
    is_array: bool


def _deref(node: dict, defs: dict) -> dict:
    while "$ref" in node:
        node = defs[node["$ref"].rsplit("/", 1)[-1]]
    return node


def _spec_for(path: str, node: dict, required: bool) -> FieldSpec | None:
    kind = node.get("type")
    enum = node.get("enum")
    if enum is not None:
        domain = tuple(enum)
    elif kind == "boolean":
        domain = (True, False)
    elif kind == "array":
        items = node.get("items") or {}
        return FieldSpec(path, required, (), bool(items.get("enum")), True)
    else:
        return FieldSpec(path, required, (), False, False)
    if not required:
        domain = domain + (ABSENT,)
    return FieldSpec(path, required, domain, True, False)


def load_field_specs(schema_path: pathlib.Path | None = None) -> dict[str, FieldSpec]:
    """Every addressable capability-map field, with its domain and whether it can be absent.

    Derived from the schema on every call rather than transcribed — a hand-maintained copy of
    this is exactly what shipped as a live defect (playbook #54).
    """
    schema = json.loads((schema_path or SCHEMA_PATH).read_text())
    defs = schema.get("$defs", {})
    out: dict[str, FieldSpec] = {}

    def walk(node: dict, prefix: str, parent_required: bool) -> None:
        node = _deref(node, defs)
        props = node.get("properties") or {}
        req = set(node.get("required") or ())
        for name, raw in props.items():
            child = _deref(raw, defs)
            path = f"{prefix}.{name}" if prefix else name
            is_req = parent_required and name in req
            if child.get("type") == "object":
                if child.get("properties"):
                    walk(child, path, is_req)
                else:
                    # A property-less `additionalProperties: true` object. Recorded so a
                    # predicate resting on one is REFUSED rather than silently unresolvable.
                    out[path] = FieldSpec(path, is_req, (), False, False)
                continue
            spec = _spec_for(path, child, is_req)
            if spec is not None:
                out[path] = spec

    root = _deref(schema["properties"]["capability_map"], defs)
    walk(root, "", True)
    return out


def atom_key(atom: dict) -> tuple:
    """Identity of an atom, for pinning a free variable to it."""
    return (atom["field"], atom["op"], tuple(atom.get("values") or ()))


def evaluate(atom: dict, assignment: dict, free: dict | None = None) -> bool:
    """Truth of one atom under one assignment.

    An atom whose field has no finite domain is carried as a free boolean in `free`, keyed by
    `atom_key`, so both truth values get explored rather than the atom being guessed.

    Raises:
        ValueError: The op is not one of `OPS`. Refused rather than guessed — a typo that
            evaluated to False would silently weaken whichever rule read it.
    """
    op = atom["op"]
    if op not in OPS:
        raise ValueError(f"unknown op {op!r}; expected one of {sorted(OPS)}")
    if free is not None:
        key = atom_key(atom)
        if key in free:
            return free[key]
    value = assignment[atom["field"]]
    # Order matters: is_absent is the ONE op that may be true on a missing field, and every
    # other op — negated ones included — is false. `classification-schema.md:72`.
    if op == "is_absent":
        return value is ABSENT
    if value is ABSENT:
        return False
    if op == "is_present":
        return True
    values = atom.get("values") or []
    if op == "in":
        return value in values
    if op == "not_in":
        return value not in values
    if op == "eq":
        return value == values[0]
    if op == "neq":
        return value != values[0]
    if op == "is_true":
        return value is True
    if op == "is_false":
        return value is False
    return any(v in value for v in values)  # contains


def atoms_of(dnf: Iterable[Iterable[dict]]) -> list[dict]:
    return [atom for conj in dnf for atom in conj]


def fields_of(*dnfs: Iterable[Iterable[dict]]) -> set[str]:
    return {a["field"] for dnf in dnfs for a in atoms_of(dnf)}


def free_atoms(specs: dict[str, FieldSpec], *dnfs) -> list[dict]:
    """Atoms whose field has no finite domain, and which therefore become free booleans."""
    seen: dict[tuple, dict] = {}
    for dnf in dnfs:
        for a in atoms_of(dnf):
            spec = specs.get(a["field"])
            if spec is not None and not spec.enumerable:
                seen.setdefault(atom_key(a), a)
    return list(seen.values())


def assignments(
    fields: Iterable[str], specs: dict[str, FieldSpec], frees: list[dict]
) -> Iterator[tuple[dict, dict]]:
    """Every (assignment, free-variable) pair over the enumerable fields named.

    Only the fields actually mentioned are enumerated, so the space stays small: domains are at
    most eight and a predicate names a handful of fields.
    """
    enumerable = [f for f in sorted(fields) if specs.get(f) and specs[f].enumerable]
    domains = [specs[f].domain for f in enumerable]
    keys = [atom_key(a) for a in frees]
    for combo in itertools.product(*domains) if enumerable else [()]:
        base = dict(zip(enumerable, combo))
        for truths in (
            itertools.product((True, False), repeat=len(keys)) if keys else [()]
        ):
            yield base, dict(zip(keys, truths))


def holds(dnf: Iterable[Iterable[dict]], assignment: dict, free: dict) -> bool:
    """A DNF holds when any one of its conjunctions does."""
    return any(all(evaluate(a, assignment, free) for a in conj) for conj in dnf)


def axioms_hold(axioms: list[dict], assignment: dict, free: dict) -> str | None:
    """The name of the first axiom an assignment violates, or None.

    An axiom is `{when: [atoms], then: [atoms], because: str}` — structured like every other
    predicate rather than a prose mini-language, so the same evaluator reads it.
    """
    for ax in axioms or []:
        if all(evaluate(a, assignment, free) for a in ax["when"]) and not all(
            evaluate(a, assignment, free) for a in ax["then"]
        ):
            return ax.get("because") or "axiom"
    return None
