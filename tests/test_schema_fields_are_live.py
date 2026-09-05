"""ONE guard over every prior-art schema: a top-level field is INSTRUCTED or READ, or it is dead.

`lineage` shipped in seven packages. `code` invented it and reads it; the other six inherited the
block by copy. In three of them — `visual`, `market-competitive`, `security` — no procedure step
wrote it, no rule read it, and no reviewer condition mentioned it, through every review cycle each
of those packages went through. It was found by a DERIVED sweep in an eighth package, not by any of
the reviewers who read the six.

Two things this guard is careful about, both learned from the sweep that found it:

* **The probe is structural.** `field in validator_source` is a substring test, and it read a field
  as covered the moment an unrelated failure message used the ordinary English word. It only ever
  over-reports, and never fails loudly. `.get("x")` / `["x"]` cannot be fooled that way.
* **The exemption set is asserted by EQUALITY, per package.** A subset assertion grows silently. A
  new orphan fails here and has to be argued onto the list with its reason; an orphan that gains
  prose or a rule has to leave it.

Scope, stated because a guard's scope is a claim: TOP-LEVEL properties only. That is the layer
`lineage` lived at and the layer a whole block gets copied at. Fields nested inside `$defs` are the
per-package sweep's business — `regulatory` runs one over all 94 of its own.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: `.get("x")` and `["x"]`. See the module docstring for why this is not a substring test.
READS = re.compile(r"""(?:\.get\(|\[)["']([a-z_][a-z0-9_]*)["']""")

#: Orphans that are NOT dead, with the reason each is allowed to be. Equality is asserted against
#: this, so both a new orphan and a repaired one fail until the list is updated.
#:
#: - security's `extract-output.schema.json` describes the EXTRACT wave. No type has built that wave
#:   — every shipped pair is wave 1 — so its fields are instructed by no wave-1 procedure and read
#:   by no wave-1 rule. They are pending, not dead, and deleting them would throw away a written
#:   contract the extract wave will need.
EXPECTED_ORPHANS: dict[str, set[str]] = {
    "security-prior-art-survey": {"retrieved_at", "url", "weakness_refs"},
}


def _packages() -> list[pathlib.Path]:
    """DERIVED by glob. A hand-listed set is how the ninth type ships unchecked."""
    out = [
        p
        for p in sorted((ROOT / "skills").glob("*-prior-art-survey"))
        if (p / "schemas").is_dir()
    ]
    assert len(out) >= 8, (
        f"only {len(out)} packages with schemas — the glob is wrong, not the repo"
    )
    return out


def _top_level_fields(pkg: pathlib.Path) -> set[str]:
    out: set[str] = set()
    for schema in sorted((pkg / "schemas").glob("*.schema.json")):
        out |= set(json.loads(schema.read_text()).get("properties", {}))
    return out


def _prose(pkg: pathlib.Path) -> str:
    files = [pkg / "SKILL.md", *sorted((pkg / "references").rglob("*.md"))]
    return " ".join(f.read_text() for f in files if f.exists())


def _read_by_a_rule(pkg: pathlib.Path) -> set[str]:
    src = " ".join(
        p.read_text()
        for p in sorted((pkg / "scripts").glob("*.py"))
        if not p.name.startswith("test_")
    )
    return set(READS.findall(src))


@pytest.mark.parametrize("pkg", _packages(), ids=lambda p: p.name)
def test_no_schema_field_is_instructed_nowhere_and_read_by_nothing(
    pkg: pathlib.Path,
) -> None:
    fields = _top_level_fields(pkg)
    assert len(fields) >= 15, (
        f"{pkg.name}: only {len(fields)} top-level fields — the walk is wrong"
    )
    prose, read = _prose(pkg), _read_by_a_rule(pkg)
    orphans = {f for f in fields if f not in prose and f not in read}
    assert orphans == EXPECTED_ORPHANS.get(pkg.name, set()), {
        "dead — in a schema, instructed nowhere, read by nothing": sorted(
            orphans - EXPECTED_ORPHANS.get(pkg.name, set())
        ),
        "exempted and no longer an orphan": sorted(
            EXPECTED_ORPHANS.get(pkg.name, set()) - orphans
        ),
    }


def test_the_EXEMPTIONS_name_packages_that_exist() -> None:
    """An exemption keyed on a package that was renamed is a licence nobody notices has moved."""
    names = {p.name for p in _packages()}
    assert set(EXPECTED_ORPHANS) <= names, sorted(set(EXPECTED_ORPHANS) - names)


def test_the_sweep_is_actually_looking_at_something() -> None:
    """A derived guard that finds no fields is green and worthless. Both halves of the probe are
    checked: prose that matched nothing, or a reads-regex that matched nothing, would make every
    field an orphan or none, and neither state is the repo's."""
    total = sum(len(_top_level_fields(p)) for p in _packages())
    assert total >= 150, (
        f"only {total} top-level fields across the program — the walk is wrong"
    )
    for pkg in _packages():
        assert _read_by_a_rule(pkg), (
            f"{pkg.name}: the reads-probe matched nothing at all"
        )
        assert len(_prose(pkg)) > 20_000, (
            f"{pkg.name}: the prose glob matched almost nothing"
        )
