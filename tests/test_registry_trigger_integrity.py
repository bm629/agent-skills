"""E2 — ONE guard over every prior-art registry, derived from what is on disk.

Playbook #46's discipline, applied where the files live: a sixth type is covered the moment its
registry exists, rather than when someone remembers to extend a list. The alternative — a copy
per skill — is how the path-frame invariant ended up with three implementations of three
different strengths, and it is how L-1 shipped.

It runs here rather than inside any validator's `main()` because a registry is static: only an
author can violate these, and a false positive at dispatch time parks every ticket in a live
survey. Author-time is strictly the cheaper place to be wrong.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest
import yaml
from trigger_integrity import load_field_specs
from trigger_rules import check_angle, check_wellformed

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPECS = load_field_specs()

#: The documented alias. `business.platform` is a required OBJECT and `business.platform.type`
#: is the required enum leaf inside it; both are genuinely required paths and both may anchor.
_ALIAS = {"business.platform"}


def _registries() -> list[pathlib.Path]:
    return [
        p
        for pkg in sorted(ROOT.glob("skills/*-prior-art-survey"))
        if not pkg.name.startswith("reviewing-")
        for p in [pkg / "references" / "source-registry.yaml"]
        if p.exists()
    ]


def _load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text())


def _validator(pkg: pathlib.Path):
    """Load a package's validator module by path, or None if it has none yet.

    A package can legitimately have a registry and no validator: C1 authors the registry and C2
    authors the validator, so mid-build that state is correct rather than broken. Returning None
    lets the caller SKIP with a stated reason. It previously raised StopIteration, which failed
    the suite for a package that was simply half-built — an error where a skip belongs.

    The skip is safe only because it is not the last line of defence: the ship gate (spec EC7)
    requires this guard to have RUN for the package, not merely not-failed, so a finished package
    cannot slip through on the same branch.
    """
    found = sorted(pkg.glob("scripts/validate_*.py"))
    if not found:
        return None
    src = found[0]
    spec = importlib.util.spec_from_file_location(f"_v_{pkg.name}", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_IDS = [p.parts[-3] for p in _registries()]


def test_the_guard_actually_found_some_registries():
    """A glob that silently matches nothing is a green test that checks nothing."""
    assert len(_registries()) >= 3


@pytest.mark.parametrize("path", _registries(), ids=_IDS)
def test_registry_is_well_formed(path: pathlib.Path):
    found = [f for f in check_wellformed(_load(path)) if f.severity != "skip"]
    assert not found, "\n".join(str(f) for f in found)


@pytest.mark.parametrize("path", _registries(), ids=_IDS)
def test_no_angle_always_fires_or_is_dead(path: pathlib.Path):
    """Both directions, over every conditional angle.

    A `report` finding is not advisory — the author must respond, and recording a one-line
    `leg_scope:` IS a valid response. The severity says the rule cannot decide which of the two
    it is looking at, not that it can be ignored.
    """
    reg = _load(path)
    if any(f.severity == "skip" for f in check_wellformed(reg)):
        pytest.skip(f"{path.parts[-3]}: no type_trigger.predicate — out of scope by design")
    trigger = reg["type_trigger"]["predicate"]
    axioms = reg.get("coherence_axioms") or []
    found = [
        f
        for a in reg["angles"]
        if a.get("trigger") == "conditional"
        for f in check_angle(trigger, a, SPECS, axioms)
    ]
    assert not found, "\n".join(str(f) for f in found)


@pytest.mark.parametrize("path", _registries(), ids=_IDS)
def test_the_required_field_constant_matches_the_schema(path: pathlib.Path):
    """C-4 — derived, not transcribed. A hand-maintained copy of this set is what shipped as
    L-1, and a test pinning it to a second hardcoded list would just be a third copy."""
    pkg = path.parents[1]
    mod = _validator(pkg)
    if mod is None:
        pytest.skip(f"{pkg.name}: registry authored, validator not yet — mid-build, not a defect")
    shipped = getattr(mod, "REQUIRED_CAPABILITY_FIELDS", None)
    if shipped is None:
        pytest.skip(f"{pkg.name}: predates the anchor gate, no constant to check")
    derived = {
        p
        for p, s in SPECS.items()
        if s.required and not p.startswith("prior_art_triggers.")
    }
    assert derived <= set(shipped), f"missing from {pkg.name}: {sorted(derived - set(shipped))}"
    assert set(shipped) - derived <= _ALIAS, (
        f"{pkg.name} carries fields the schema does not mark required: "
        f"{sorted(set(shipped) - derived - _ALIAS)}"
    )
