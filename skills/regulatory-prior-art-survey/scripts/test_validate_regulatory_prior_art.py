"""Tests for the regulatory prior-art gate.

Every rule gets a negative test that FIRES it and a mirror that passes at the boundary. A negative
test alone proves a rule can fire; it does not prove the rule is not firing on everything, and a
membership check that fires on everything passes its negative test and fails nothing else.
"""

from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "validate_regulatory_prior_art.py"
FIXTURES = HERE / "fixtures"
PACKAGE = HERE.parent
REVIEWER = PACKAGE.parent / "reviewing-regulatory-prior-art-survey"


def _load():
    spec = importlib.util.spec_from_file_location("validate_regulatory_prior_art", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


V = _load()


def _rules(findings: list[str]) -> list[str]:
    """The rule ids out of `FAIL <rule>: <message>` lines."""
    return [f.split(":", 1)[0].removeprefix("FAIL ").strip() for f in findings]


@pytest.fixture
def registry() -> dict:
    return yaml.safe_load((PACKAGE / "references" / "source-registry.yaml").read_text())


@pytest.fixture
def valid_map() -> dict:
    return yaml.safe_load((FIXTURES / "regulatory-scope-map.valid.yaml").read_text())


@pytest.fixture
def valid_search() -> dict:
    return yaml.safe_load((FIXTURES / "search-output.valid.yaml").read_text())


class TestRegistryIntegrity:
    """Exit 2, before any artifact is read. These are faults in the PACKAGE, and reporting one as
    exit 1 sends an author off to edit an artifact that is fine."""

    def test_the_shipped_registry_is_clean(self, registry):
        assert V.registry_failures(registry) == []

    @pytest.mark.parametrize("shape", [[], "a string", None, 3])
    def test_a_registry_that_is_not_a_mapping_is_caught(self, shape):
        assert "not-a-mapping" in _rules(V.registry_failures(shape))

    def test_an_angle_with_no_id_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0].pop("id")
        assert "angle-id-required" in _rules(V.registry_failures(doc))

    def test_an_unknown_trigger_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0]["trigger"] = "sometimes"
        assert "trigger-must-be-known" in _rules(V.registry_failures(doc))

    def test_a_conditional_angle_with_no_anchor_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a.pop("trigger_anchor")
        assert "anchor-required" in _rules(V.registry_failures(doc))

    def test_an_always_on_angle_carrying_an_anchor_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "always")
        a["trigger_anchor"] = ["regulatory.applies"]
        assert "anchor-only-on-conditional" in _rules(V.registry_failures(doc))

    def test_an_anchor_on_an_optional_field_is_caught(self, registry):
        """An anchor rooted on an OPTIONAL classification field fails closed for every map that
        omits it — silently, and for exactly the products that needed the angle."""
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a["trigger_anchor"] = ["data_ml.eu_ai_act.risk_level"]
        assert "anchor-must-be-required" in _rules(V.registry_failures(doc))

    def test_an_anchor_that_is_not_a_list_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        a = next(x for x in doc["angles"] if x["trigger"] == "conditional")
        a["trigger_anchor"] = "business.platform.type"
        assert "anchor-must-be-a-list" in _rules(V.registry_failures(doc))

    def test_an_angle_naming_an_unknown_source_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        doc["angles"][0]["sources"] = ["not-a-real-row"]
        assert "angle-source-unknown" in _rules(V.registry_failures(doc))

    def test_an_angle_whose_fallback_is_outside_its_own_sources_is_caught(self, registry):
        """A fallback the angle cannot reach is a route on paper only."""
        doc = copy.deepcopy(registry)
        a = doc["angles"][0]
        a["fallback"] = next(s["id"] for s in doc["sources"] if s["id"] not in a["sources"])
        assert "angle-fallback-unreachable" in _rules(V.registry_failures(doc))

    def test_a_null_terminal_with_no_rationale_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if s.get("fallback") is None)
        row.pop("fallback_rationale")
        assert "terminal-needs-rationale" in _rules(V.registry_failures(doc))

    def test_a_fallback_cycle_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        term = next(s for s in doc["sources"] if s.get("fallback") is None)
        term["fallback"] = next(
            s["id"] for s in doc["sources"] if s.get("fallback") == term["id"]
        )
        assert "fallback-cycle" in _rules(V.registry_failures(doc))

    def test_a_self_fallback_is_a_terminal_not_a_cycle(self, registry):
        """MIRROR at the boundary. A sibling registry uses a self-fallback to mean 'there is no
        second channel', documented in its own preamble. Reading it as a cycle would report ten
        false defects there; this package uses `null` and both must read as terminal."""
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if s.get("fallback") is None)
        row["fallback"] = row["id"]
        assert "fallback-cycle" not in _rules(V.registry_failures(doc))


class TestProbeMethodShape:
    """`probe_method` is a REGISTRY field, so a wrong-shaped one is exit 2 — not exit 1 beside the
    artifact rules. Grouping it with those would have left its exit code undecided."""

    def test_the_registry_wide_default_is_required(self, registry):
        doc = copy.deepcopy(registry)
        doc.pop("probe_default")
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    @pytest.mark.parametrize("bad", ["yes", 3, [], {"headers": {}}])
    def test_a_default_missing_its_method_is_caught(self, bad, registry):
        doc = copy.deepcopy(registry)
        doc["probe_default"] = bad
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_override_missing_its_method_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if "probe_method" in s)
        row["probe_method"] = {"headers": {"Accept": "text/html"}}
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_override_with_non_string_headers_is_caught(self, registry):
        doc = copy.deepcopy(registry)
        row = next(s for s in doc["sources"] if "probe_method" in s)
        row["probe_method"] = {"method": "GET", "headers": {"Accept": 5}}
        assert "probe-method-shape" in _rules(V.registry_failures(doc))

    def test_a_row_with_no_override_is_legal(self, registry):
        """MIRROR: the field is an OVERRIDE. Requiring it on every row would put the same three
        lines on nineteen of them, which a reader learns to skip."""
        doc = copy.deepcopy(registry)
        for s in doc["sources"]:
            s.pop("probe_method", None)
        assert "probe-method-shape" not in _rules(V.registry_failures(doc))


class TestTheExitContract:
    """Run through `main()`, because a subcommand reachable only in tests is a subcommand that
    does not ship."""

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=HERE, check=False,
        )

    def test_a_clean_map_exits_0(self):
        r = self._cli("keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml"))
        assert r.returncode == 0, r.stdout + r.stderr

    def test_a_missing_file_exits_2(self, tmp_path):
        r = self._cli("keyword-map", str(tmp_path / "nope.yaml"))
        assert r.returncode == 2
        assert "FAIL input:" in r.stdout + r.stderr

    def test_unparseable_yaml_exits_2(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("a: [1, 2\n  b: {\n")
        r = self._cli("keyword-map", str(bad))
        assert r.returncode == 2

    def test_an_unreadable_registry_exits_2(self, tmp_path, monkeypatch):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map",
             str(FIXTURES / "regulatory-scope-map.valid.yaml")],
            capture_output=True, text=True, cwd=HERE, check=False,
            env={**__import__("os").environ, "REGULATORY_REGISTRY_OVERRIDE": str(tmp_path / "gone.yaml")},
        )
        assert r.returncode == 2
        assert "registry-unreadable" in r.stdout + r.stderr

    def test_a_missing_dependency_exits_2_with_the_invocation_and_no_traceback(self, tmp_path):
        """The guard must be NON-RAISING at import: the shared root guard `exec_module`s this
        file, and a raising import turns that test into an ERROR rather than a run."""
        stub = tmp_path / "yaml.py"
        stub.write_text("raise ModuleNotFoundError('No module named yaml', name='yaml')\n")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "keyword-map",
             str(FIXTURES / "regulatory-scope-map.valid.yaml")],
            capture_output=True, text=True, cwd=HERE, check=False,
            env={**__import__("os").environ, "PYTHONPATH": str(tmp_path)},
        )
        out = r.stdout + r.stderr
        assert r.returncode == 2, out
        assert "FAIL dependency-missing:" in out
        assert "Traceback" not in out
        assert "--with pyyaml" in out, "the message must carry the working invocation"

    def test_both_subcommands_are_reachable_through_main(self):
        for args in (["keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml")],
                     ["search", str(FIXTURES / "search-output.valid.yaml"),
                      "--keyword-map", str(FIXTURES / "regulatory-scope-map.valid.yaml")]):
            r = self._cli(*args)
            assert r.returncode in (0, 1), f"{args} -> {r.returncode}: {r.stdout}{r.stderr}"
            assert "no such subcommand" not in (r.stdout + r.stderr).lower()

    def test_the_exported_constant_exists(self):
        """The shared root guard SKIPS its constant check without this, and a silent skip is a
        green test checking nothing."""
        assert isinstance(V.REQUIRED_CAPABILITY_FIELDS, tuple)
        assert "regulatory.applies" in V.REQUIRED_CAPABILITY_FIELDS
