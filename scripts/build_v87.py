"""Build v87: STEP-SHIM -- recover the missing `step` field on seat 1.

THE BUG (found 2026-09-28, from live v86 replays):
`observation["step"]` is declared `"shared": true` in the episode spec, so both
agents should receive it. Measured across 5,760 recorded observations from 8
live replays:

    seat 0 -> `step` present in 5760/5760 observations (100%)
    seat 1 -> `step` ABSENT  in 5760/5760 observations (100%)

It is not intermittent -- it is exactly the seat-1 agent that never gets the
field. `_v85_step()` / `_v83_step()` default to 0, so on seat 1 EVERY
step-gated feature in the shipped stack is dead all game:

    _v85_expand  (48 <= step <= 600)   expansion      -> never runs
    _v86_dump    (648 <= step <= 719)  terminal fert  -> never runs
    _v83_rescue  (step < 670)          feed rescue    -> never runs

`day` and `hour` ARE present for both seats, and `day * 24 + hour` reproduces
the step index EXACTLY (verified mean error +0.00, min 0, max 0 across every
sampled observation). turnsPerDay defaults to 24 and the season is 30 days =
720 steps, so the arithmetic is exact, not approximate.

Live cost, v86 submission 56648082, 20 games:
    seat 0 (features live)  13 games  10-3   margin +$25,663/game
    seat 1 (features dead)   7 games   4-3   margin    +$169/game

WHY LOCAL BENCHES NEVER CAUGHT THIS: the local harness supplies `step` to both
seats, so every paired A/B exercised the live path on both sides and reported
clean margins. This is the seat-asymmetry cousin of the known local-runner
seat-interleaving bias -- same root cause class (an artefact that cancels in
mirror play), different mechanism (a field the server withholds).

THE FIX: prefer `obs["step"]`, else derive `day * 24 + hour`. Applied at the
single helper every step-gated layer calls, so it revives v85/v86/v83 on
seat 1 without touching their logic. `_V83_STEP = _v85_step` repoints v83's
private copy too. Seat 0 is unaffected (the real field still wins), and a
genuine step of 0 at episode start still reads 0.

This also unblocks the orphan placer, whose window is 120..660 and which was
built and abandoned separately (scripts/build_v87_orphan_placer_abandoned.py):
it could never fire on seat 1 because the window never opened.
"""
import glob
import importlib.util
import json
import os
import tarfile

import kaggle_environments

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "main_v86.py")
OUT = os.path.join(ROOT, "build", "main_v87.py")
TAR = os.path.join(ROOT, "build", "submission_v87.tar.gz")

OLD = '''def _v85_step(obs):
    try:
        return int(obs.get("step", 0) if isinstance(obs, dict)
                   else getattr(obs, "step", 0) or 0)
    except (TypeError, AttributeError, ValueError):
        return 0'''
NEW = '''def _v85_step(obs):
    """v87: the server withholds `step` from the SEAT-1 agent (measured:
    present 5760/5760 for seat 0, absent 5760/5760 for seat 1). Defaulting to
    0 killed every step-gated feature all game on seat 1. Fall back to
    day*24+hour, which reproduces the step index exactly."""
    try:
        raw = (obs.get("step", None) if isinstance(obs, dict)
               else getattr(obs, "step", None))
        if raw is not None:
            return int(raw)
    except (TypeError, AttributeError, ValueError):
        pass
    return _v87_step_from_clock(obs)


def _v87_step_from_clock(obs):
    try:
        day = (obs.get("day", 0) if isinstance(obs, dict)
               else getattr(obs, "day", 0)) or 0
        hour = (obs.get("hour", 0) if isinstance(obs, dict)
                else getattr(obs, "hour", 0)) or 0
        return int(day) * 24 + int(hour)
    except (TypeError, AttributeError, ValueError):
        return 0'''

WRAPPER = '''

# v87 step shim (see scripts/build_v87.py). _v83_step is a private copy made
# before this point, so repoint it or the feed rescue stays dead on seat 1.
_V83_STEP = _v85_step

_V87_ON = True


_V87_PARENT = agent


def _v87_entrypoint(observation, configuration=None):
    return _V87_PARENT(observation, configuration)


agent = _v87_entrypoint
kaggle_submission_agent = _v87_entrypoint
_kaggle_submission_entrypoint = _v87_entrypoint
'''

if not os.path.exists(SRC):
    raise SystemExit(
        "build_v87.py is a DELTA builder and needs two inputs that are "
        "deliberately not published in this repo:\n"
        "  1. the previous artifact  %s\n"
        "  2. recorded live replays  rivals/replays_v86/  (~194 MB)\n"
        "This repo ships the BUILT result only: main.py IS the v87 artifact.\n"
        "To rebuild, check out the full working tree and run this script there."
        % SRC)

src = open(SRC, "r", encoding="utf-8").read().replace("\r\n", "\n")
assert "_V87_" not in src and "_v87_" not in src, "v87 markers already present"
assert src.count(OLD) == 1, "step anchor: %d" % src.count(OLD)

out = src.replace(OLD, NEW)
out = ("# v87: step shim -- the server withholds `step` from the seat-1 agent, "
       "which silently disabled every step-gated feature; see "
       "scripts/build_v87.py.\n" + out + WRAPPER)
open(OUT, "w", encoding="utf-8", newline="").write(out)
compile(out, OUT, "exec")
print("Generated {} ({:,} bytes)".format(OUT, os.path.getsize(OUT)))

spec = importlib.util.spec_from_file_location("v87_check", OUT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
for ep in ("agent", "kaggle_submission_agent", "_kaggle_submission_entrypoint"):
    assert hasattr(mod, ep), "missing entrypoint " + ep
assert mod._V87_ON is True
assert mod._V85_EXPAND_ON is True and mod._V86_DUMP_ON is True
assert mod._V83_RESCUE_ON is True
assert mod._V83_STEP is mod._v85_step, "v83 must use the shimmed step"

# --- unit 1: the shim against the REAL recorded observations ---------------
replays = sorted(glob.glob(os.path.join(ROOT, "rivals", "replays_v86", "*.json")))
assert replays, "no replays available to verify the shim against"
n_0 = n_1 = 0
for rp in replays:
    data = json.load(open(rp, encoding="utf-8"))
    steps = data["steps"]
    names = [str(x).lower() for x in (data["info"].get("TeamNames") or [])]
    us = next((i for i, x in enumerate(names) if "bassel" in x), 0)
    for t, rec in enumerate(steps):
        for seat in (0, 1):
            if seat >= len(rec) or not isinstance(rec[seat], dict):
                continue
            o = rec[seat].get("observation")
            if not isinstance(o, dict) or "farms" not in o:
                continue
            n_0 += 1 if seat == us else 0
            n_1 += 0 if seat == us else 1
            got = mod._v85_step(o)
            assert got == t, "shim wrong at t{}: got {}".format(t, got)
print("Shim verified on {} real observations (us-seat {}, opp-seat {}): each "
      "reconstructs its own step index.".format(n_0 + n_1, n_0, n_1))
assert n_1 > 0, "expected to exercise the step-less seat"

# real `step` still wins; genuine 0 still reads 0; malformed never raises
assert mod._v85_step({"step": 7, "day": 20, "hour": 5}) == 7, "prefer real step"
assert mod._v85_step({"step": 0, "day": 0, "hour": 0}) == 0
assert mod._v85_step({}) == 0 and mod._v85_step(None) == 0
assert mod._v85_step({"day": 27, "hour": 23}) == 671, "clock fallback"

# --- unit 2: the step-gated windows now REACH on a seat-1-shaped obs -------
def _obs(step, seat, tiles):
    return {"player": seat, "day": step // 24, "hour": step % 24,  # NO "step"
            "farms": [{"money": 9000.0, "tiles": tiles, "farmer": [4, 4],
                       "hands": [[4, 5], [0, 0]],
                       "unlocked_quadrants": ["NW", "NE", "SW", "SE"]},
                      {"money": 9000.0, "tiles": [[None] * 10 for _ in range(10)],
                       "farmer": [0, 0], "hands": [],
                       "unlocked_quadrants": ["NW"]}],
            "private": {"shed": {}, "seeds": {}, "inventories": [{}, {}]},
            "market": {"prices": {"WOOL": 200}, "inventory": {}},
            "town": {"unlocked_shops": []}}


grid = [[{"kind": "PLANT", "crop": "WHEAT"}] * 10 for _ in range(10)]
assert 48 <= mod._v85_step(_obs(300, 1, grid)) <= 600, "expand window on seat 1"
assert 648 <= mod._v85_step(_obs(660, 1, grid)) <= 719, "dump window on seat 1"
assert mod._v85_step(_obs(300, 1, grid)) < mod._V83_STEP_MAX, "rescue window"
print("Step-gated windows verified OPEN on seat-1-shaped observations.")

env = kaggle_environments.make("kaggriculture",
                               configuration={"episodeSteps": 10, "seed": 0},
                               debug=True)
env.run([mod.agent, mod.agent])
assert len(env.steps) >= 10
print("Smoke passed (10-step self-play + all entrypoints).")

print("Packaging {}...".format(TAR))
with tarfile.open(TAR, "w:gz") as tar:
    tar.add(OUT, arcname="main.py")
with tarfile.open(TAR) as tar:
    names = tar.getnames()
    assert names == ["main.py"], "tar contents: %s" % names
    assert tar.extractfile("main.py").read() == open(OUT, "rb").read(), "stale archive"
print("OK {} ({:,} bytes) contents={}".format(TAR, os.path.getsize(TAR), names))
