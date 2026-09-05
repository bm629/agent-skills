"""The CALL-SITE kill sweep. Run it; it is not part of the suite.

For each `_fail` call site, suppress that ONE site at runtime and run the package suite. A site
no test notices is a branch that can be deleted with everything green — and five such sites, when
they were found, turned a real exit-1 finding into exit 0.

It is out of the suite because it runs the suite once per site: ~124 runs, several minutes. The
rule-level guard in the test module is its fast proxy and is strictly weaker — a rule is pinned
when SOME test names it, which says nothing about its other branches. Run this after any change
that adds or moves a `_fail`.

    uv run --group dev python3 skills/scale-prior-art-survey/scripts/kill_site_sweep.py

Last run: 0 survivors of 124 sites.
"""

import ast
import pathlib
import subprocess
import sys
import os

PKG = pathlib.Path(__file__).resolve().parents[1]
V = PKG / "scripts/validate_scale_prior_art.py"
orig = V.read_text()
sites = [
    (n.lineno, n.args[0].value)
    for n in ast.walk(ast.parse(orig))
    if isinstance(n, ast.Call)
    and getattr(n.func, "id", "") == "_fail"
    and n.args
    and isinstance(n.args[0], ast.Constant)
]
patched = orig.replace(
    "def _fail(rule: str, message: str, f: Findings) -> None:",
    "def _fail(rule: str, message: str, f: Findings) -> None:\n"
    "    import inspect, os\n"
    "    _k = os.environ.get('KILL_SITE')\n"
    "    if _k and inspect.currentframe().f_back.f_lineno == int(_k):\n"
    "        return",
    1,
)
V.write_text(patched)
survivors = []
try:
    for ln, rid in sites:
        env = {**os.environ, "KILL_SITE": str(ln)}
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(PKG / "scripts"),
                "-q",
                "--no-header",
                "-x",
                "-p",
                "no:cacheprovider",
                "--timeout=120",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        if r.returncode == 0:
            survivors.append((ln, rid))
finally:
    V.write_text(orig)
print("call sites:", len(sites), "| SURVIVORS:", len(survivors))
for ln, rid in survivors:
    print(f"   L{ln}  {rid}")
