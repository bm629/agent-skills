"""The four rules, decided against the enumerator in `trigger_integrity`.

Three FAIL and one REPORTS. The reporting one is deliberate: a dead (trigger-leg, predicate-leg)
pair is sometimes a real defect and sometimes an angle deliberately scoped to one cohort, and the
two are logically indistinguishable — measured, three of five plausible `scale` angles hit it and
all three were legitimate. A rule that cannot decide should say so rather than fail correct work.

Nothing here runs inside a portable skill or a validator's `main()`. It is author-time, because a
false positive at dispatch time parks every ticket in a live survey.
"""

from __future__ import annotations

from dataclasses import dataclass

from trigger_integrity import (
    OPS,
    assignments,
    axioms_hold,
    fields_of,
    free_atoms,
    holds,
)

#: rule id -> the defect that earned it. Playbook #47: no defect, no rule.
RULES = {
    "axioms-unsatisfiable": "a contradictory axiom set reports every angle as always-firing",
    "predicate-not-expressible": "three shipped angles predicate on an enum-less array; a "
    "property-less object or a typo'd field cannot be decided at all",
    "angle-always-fires": "visual b3 (L-2) and user_research b2 (L-3) restate their own type "
    "trigger, both while closing a fail-closed hole",
    "leg-never-fires": "user_research b5 (L-4) carries a leg dead against trigger leg 1",
}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    angle: str
    message: str

    def __str__(self) -> str:
        return f"{'FAIL' if self.severity == 'fail' else 'REPORT'} {self.rule}: {self.message}"


def _expressible(atom: dict, specs: dict) -> bool:
    spec = specs.get(atom["field"])
    if spec is None:
        return False
    if spec.enumerable:
        return True
    # A `contains` over an enum-less array becomes a free boolean: deliberate, conservative, and
    # documented. Extending that to EVERY non-enumerable field would silently weaken all four
    # rules — a typo'd field name included — so everything else is refused.
    return atom["op"] == "contains" and spec.is_array


def _satisfiable(dnfs: list, specs: dict, axioms: list, negate=None) -> dict | None:
    """First assignment satisfying every DNF in `dnfs` (and falsifying `negate`), or None."""
    all_dnfs = [*dnfs] + ([negate] if negate else [])
    # Axiom atoms are wrapped as a one-conjunction DNF so they travel through the same
    # field/free-variable collectors as everything else.
    axiom_dnf = [[a for ax in axioms or [] for a in ax["when"] + ax["then"]]]
    frees = free_atoms(specs, *all_dnfs, axiom_dnf)
    fields = fields_of(*all_dnfs, axiom_dnf)
    for assignment, free in assignments(fields, specs, frees):
        if axioms_hold(axioms, assignment, free):
            continue
        if not all(holds(d, assignment, free) for d in dnfs):
            continue
        if negate is not None and holds(negate, assignment, free):
            continue
        return {**assignment, **{str(k): v for k, v in free.items()}}
    return None


def check_angle(trigger: list, angle: dict, specs: dict, axioms: list) -> list[Finding]:
    """Every finding for one conditional angle, in the order the rules must run."""
    aid = angle.get("id", "?")
    predicate = angle.get("predicate") or []

    # 1. The axiom set must admit at least one world. Otherwise every entailment below is
    #    vacuously true and the gate reports everything, which is worse than reporting nothing.
    if axioms and _satisfiable([], specs, axioms) is None:
        return [
            Finding(
                "axioms-unsatisfiable",
                "fail",
                aid,
                "the coherence axiom set admits no assignment, so every angle would report as "
                "always-firing; fix the axioms before reading any other finding",
            )
        ]

    # 2. Refuse what cannot be decided, rather than guessing a truth value for it.
    bad = [a for conj in predicate for a in conj if not _expressible(a, specs)]
    if bad:
        return [
            Finding(
                "predicate-not-expressible",
                "fail",
                aid,
                f"angle {aid!r} predicates on "
                + ", ".join(sorted({f"{a['field']!r} with op {a['op']!r}" for a in bad}))
                + " — no finite domain, so the trigger cannot be decided. If the field carries "
                "no computable value, fold the coverage into an always-on angle and record the "
                "platform gap rather than shipping an untriggerable angle",
            )
        ]

    out: list[Finding] = []

    # 3. Entailment. Guarded on the trigger being satisfiable at all, so an unsatisfiable
    #    trigger does not masquerade as every angle always-firing.
    if (
        _satisfiable([trigger], specs, axioms) is not None
        and _satisfiable([trigger], specs, axioms, negate=predicate) is None
    ):
        out.append(
            Finding(
                "angle-always-fires",
                "fail",
                aid,
                f"angle {aid!r} is entailed by its own type-level trigger: no capability map "
                "satisfies the trigger without also satisfying this predicate, so the angle "
                "fires for every project the survey runs on. It is unconditional — declare it "
                "`trigger: always` and drop the anchor, or narrow the predicate",
            )
        )

    # 4. Pairwise deadness. Reports; a `leg_scope` note acknowledges it.
    if not angle.get("leg_scope"):
        dead = [
            (i, j)
            for i, tleg in enumerate(trigger)
            for j, pleg in enumerate(predicate)
            if _satisfiable([[tleg], [pleg]], specs, axioms) is None
        ]
        if dead:
            every = len(dead) == len(trigger) * len(predicate)
            head = (
                f"angle {aid!r} can never fire — every (trigger-leg, predicate-leg) pair is "
                f"unsatisfiable"
                if every
                else f"angle {aid!r} has dead (trigger-leg, predicate-leg) pairs {dead}"
            )
            out.append(
                Finding(
                    "leg-never-fires",
                    "report",
                    aid,
                    head + ". If the angle is deliberately scoped to one trigger cohort, record "
                    "a one-line `leg_scope:` justification; otherwise the leg is dead weight. "
                    "This rule cannot tell the two apart, which is why it reports",
                )
            )
    return out


#: Ops that take a `values` list, and those that must not carry one. Written as a pair because a
#: one-directional check on a two-directional property reads as covered and is not (#34).
_NEEDS_VALUES = frozenset({"in", "not_in", "eq", "neq", "contains"})
_FORBIDS_VALUES = OPS - _NEEDS_VALUES


def _wf(rule: str, angle: str, message: str, severity: str = "fail") -> Finding:
    return Finding(rule, severity, angle, message)


def check_wellformed(registry: dict) -> list[Finding]:
    """Registry SHAPE, checked before anything tries to decide entailment from it.

    Decidability is a separate concern and belongs to `predicate-not-expressible`: one rule
    firing for two unrelated reasons tells the author neither.

    Returns:
        Findings. A single `registry-out-of-scope` finding at severity `skip` means the registry
        declares no `type_trigger.predicate` — `code` has no `angles:` block at all and
        `security` uses prose scope predicates by a recorded decision, so both are skipped with
        a reason rather than crashed on.
    """
    if not (registry.get("type_trigger") or {}).get("predicate"):
        return [
            _wf(
                "registry-out-of-scope",
                "-",
                "no `type_trigger.predicate` declared, so trigger integrity cannot be decided "
                "for this registry; skipped deliberately rather than failed",
                severity="skip",
            )
        ]

    out: list[Finding] = []
    for angle in registry.get("angles") or []:
        aid = angle.get("id", "?")
        conditional = angle.get("trigger") == "conditional"
        predicate = angle.get("predicate")

        if conditional and not predicate:
            out.append(_wf("predicate-missing", aid, f"angle {aid!r} is conditional with no `predicate`"))
        if not conditional and predicate:
            out.append(
                _wf(
                    "predicate-only-on-conditional",
                    aid,
                    f"angle {aid!r} is always-on but declares a `predicate`",
                )
            )

        scope = angle.get("leg_scope")
        if scope is not None and (
            not isinstance(scope, list)
            or not scope
            or not all(isinstance(s, str) and s.strip() for s in scope)
        ):
            out.append(
                _wf(
                    "leg-scope-shape",
                    aid,
                    f"angle {aid!r} `leg_scope` must be a non-empty list of non-empty strings; an "
                    "empty justification silences the rule while recording nothing",
                )
            )

        if not predicate:
            continue
        if not all(isinstance(c, list) for c in predicate):
            out.append(
                _wf(
                    "predicate-shape",
                    aid,
                    f"angle {aid!r} `predicate` must be a list of conjunctions (a list of lists of "
                    "atoms); a bare atom list is a common mis-nesting",
                )
            )
            continue
        for atom in (a for conj in predicate for a in conj):
            if "field" not in atom:
                out.append(_wf("atom-field-required", aid, f"angle {aid!r} has an atom with no `field`"))
                continue
            op = atom.get("op")
            if op not in OPS:
                out.append(
                    _wf("atom-unknown-op", aid, f"angle {aid!r} atom on {atom['field']!r} has unknown op {op!r}")
                )
                continue
            has = bool(atom.get("values"))
            if op in _NEEDS_VALUES and not has:
                out.append(
                    _wf("atom-values-required", aid, f"angle {aid!r}: op {op!r} on {atom['field']!r} needs `values`")
                )
            if op in _FORBIDS_VALUES and has:
                out.append(
                    _wf(
                        "atom-values-forbidden",
                        aid,
                        f"angle {aid!r}: op {op!r} on {atom['field']!r} takes no `values`; the ones "
                        "given would be silently ignored",
                    )
                )
    return out
