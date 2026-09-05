"""The CALL-SITE kill sweep. Run it; it is not part of the suite.

For each `_fail` call site, suppress that ONE site at runtime and run the package suite. A site
no test notices is a branch that can be deleted with everything green — and five such sites, when
they were found, turned a real exit-1 finding into exit 0.

It is out of the suite because it runs the suite once per site. The rule-level guard in the test
module is its fast proxy and is strictly weaker: a rule is pinned when SOME test names it, which
says nothing about its other branches. Run this after any change that adds or moves a `_fail`.

    uv run --group dev python3 skills/scale-prior-art-survey/scripts/kill_site_sweep.py

TWO BUGS ITS FIRST VERSION HAD, both of which made `SURVIVORS: 0` unconditional:

- it passed `--timeout=120` to pytest, which is not installed, so every run exited 4 and the
  `returncode == 0` test was never true;
- it derived the site line numbers from the UNPATCHED source while its own patch inserted four
  lines above them, so `KILL_SITE` never matched a real call site.

A sweep that cannot report a survivor is worse than no sweep, because its output is quoted. The
line numbers are derived from the PATCHED source now, and the run is a plain pytest invocation.

AND IT SWEEPS A COPY. The first version patched the shipped validator in place and restored it in
a `finally`; a run killed before the restore left the patch — an env-var early return inside
`_fail` — in the file, and it was committed. No `finally` survives a SIGKILL. A copy needs none.
"""

import ast
import os
import pathlib
import subprocess
import sys

PKG = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = PKG / "scripts" / "validate_scale_prior_art.py"

#: Inserted at the top of `_fail`. Its own line count is what the first version got wrong.
PATCH = (
    "def _fail(rule: str, message: str, f: Findings) -> None:\n"
    "    import inspect\n"
    "    import os\n"
    "\n"
    "    _k = os.environ.get('KILL_SITE')\n"
    "    if _k and inspect.currentframe().f_back.f_lineno == int(_k):\n"
    "        return\n"
)
ANCHOR = "def _fail(rule: str, message: str, f: Findings) -> None:\n"


def call_sites(source: str) -> list[tuple[int, str]]:
    """Every `_fail` call site as (lineno, rule id), derived from the source it will RUN."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", "") == "_fail"
            and node.args
            and isinstance(node.args[0], ast.Constant)
        ):
            out.append((node.lineno, node.args[0].value))
    return sorted(out)


def sweep() -> list[tuple[int, str]]:
    """Sweep a COPY of the package. The shipped file is never written to.

    The first version patched the validator in place and restored it in a `finally`. A run killed
    before the restore left the patch — an env-var early return inside `_fail` — in the shipped
    file, and it was committed. No `finally` survives a `SIGKILL`; a copy needs no `finally`.
    """
    import shutil
    import tempfile

    original = VALIDATOR.read_text()
    patched = original.replace(ANCHOR, PATCH, 1)
    survivors = []
    with tempfile.TemporaryDirectory() as td:
        work = pathlib.Path(td) / "pkg"
        shutil.copytree(PKG, work)
        (work / "scripts" / "validate_scale_prior_art.py").write_text(patched)
        # Sites from the PATCHED text: the frame reports the line the interpreter is running.
        for lineno, rule in call_sites(patched):
            env = {**os.environ, "KILL_SITE": str(lineno)}
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(work / "scripts"),
                    "-q",
                    "--no-header",
                    "-x",
                    "-p",
                    "no:cacheprovider",
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            if result.returncode == 0:
                survivors.append((lineno, rule))
    return survivors


def main() -> int:
    found = sweep()
    print(
        f"call sites: {len(call_sites(VALIDATOR.read_text().replace(ANCHOR, PATCH, 1)))}"
    )
    print(f"SURVIVORS: {len(found)}")
    for lineno, rule in found:
        print(f"   L{lineno}  {rule}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
