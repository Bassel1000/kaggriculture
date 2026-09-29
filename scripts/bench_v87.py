"""Bench v87: pasture-ramp + fixed placement gate.

Discipline (see the kaggle-sim-competitions skill):
- mirror first: v87 must not break exact-tie equity vs itself
- then v87 vs v86 on the SAME seeds: the delta is what we are buying
- then the standing panel (C95, sheep-spar) for regressions
- every pairing runs BOTH seats; report the seat-debiased mean
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from bench_panel import run_match, load_agent  # noqa: E402

print("Loading agents...", flush=True)
v87 = load_agent(ROOT / "main.py", "v87")
# Optional A/B baseline: only present when the previous build is checked out
# alongside this one. Skipped cleanly so the repo benches standalone.
V86 = ROOT / "build" / "main_v86.py"
v86 = load_agent(V86, "v86") if V86.exists() else None
c95 = load_agent(ROOT / "rivals" / "kernels" / "c95_main.py", "c95")
spar = load_agent(ROOT / "rivals" / "sheep_spar.py", "spar")

out = {}
SEEDS = 8

print("\n--- 1. Mirror v87 vs v87 (tie equity) ---", flush=True)
res = run_match(v87, v87, "v87", "v87mirror", seeds=SEEDS)
print("vs Mirror: avg %.0f vs %.0f | Margin: %+.0f | W-L-T: %d-%d-%d"
      % (res["avg_a"], res["avg_b"], res["avg_margin"],
         res["wins"][0], res["wins"][1], res["ties"]), flush=True)
out["mirror"] = res

print("\n--- 2. v87 vs v86 (the delta) ---", flush=True)
if v86 is None:
    print("skipped: build/main_v86.py not present in this checkout", flush=True)
else:
    res = run_match(v87, v86, "v87", "v86", seeds=SEEDS)
    print("vs v86:    avg %.0f vs %.0f | Margin: %+.0f | W-L-T: %d-%d-%d"
          % (res["avg_a"], res["avg_b"], res["avg_margin"],
             res["wins"][0], res["wins"][1], res["ties"]), flush=True)
    out["v86"] = res

print("\n--- 3. vs C95 ---", flush=True)
res = run_match(v87, c95, "v87", "c95", seeds=4)
print("vs C95:    avg %.0f vs %.0f | Margin: %+.0f | W-L-T: %d-%d-%d"
      % (res["avg_a"], res["avg_b"], res["avg_margin"],
         res["wins"][0], res["wins"][1], res["ties"]), flush=True)
out["c95"] = res

print("\n--- 4. vs Sheep Spar (expander board) ---", flush=True)
res = run_match(v87, spar, "v87", "spar", seeds=4)
print("vs Spar:   avg %.0f vs %.0f | Margin: %+.0f | W-L-T: %d-%d-%d"
      % (res["avg_a"], res["avg_b"], res["avg_margin"],
         res["wins"][0], res["wins"][1], res["ties"]), flush=True)
out["spar"] = res

json.dump(out, open(ROOT / "bench_v87.json", "w"), indent=1)
print("\nWrote bench_v87.json", flush=True)
