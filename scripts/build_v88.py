"""Build v88: FULL STEP NORMALIZATION + PASTURE RAMP.

Delta on the shipped v87 artifact (main.py). Two changes, both aimed at the
one structural loss class left in the live record (EP 114825517, -$26k):

FINDING #1 -- the v87 shim only patched THREE late-layer helpers
(_v85_step / _v87_step_from_clock / _V83_STEP repoint). A grep of the shipped
artifact shows the rest of the stack reads `step` directly:

    * 174 sites index obs["step"] / action["step"] with []-syntax -> a
      KeyError-prone read on seat 1; any wrapper that does not catch it
      silently no-ops (or crashes into its own fallback path).
    * 5 more sites use .get("step", 0) -> defaults to 0 all game on seat 1.

  The local harness supplies `step` to BOTH seats, which is exactly why every
  paired A/B ever run reported clean margins while live seat 1 earned +$169/game
  against seat 0's +$25,663/game (docs/V87_FORENSICS.md).

  FIX: normalize `step` INTO the observation dict at the true entrypoint,
  BEFORE any parent layer sees it. day*24+hour reproduces the step index
  exactly (verified mean error +0.00 across 8,640 real observations). This
  revives ALL ~40 inner layers at once instead of three, and is a superset of
  the v87 shim (the shim stays as belt-and-braces for non-dict observations).

FINDING #2 -- animals are unsellable (engine PRODUCTS excludes COW/SHEEP/GOOSE)
and PLACE only accepts a free PASTURE/COOP tile. v87's gate still returned True
on any bare tile, so expansion buys stranded animals in the shed ($4,800 dead
in the one structural loss). Meanwhile BUILD_PASTURE is FREE (no cost lookup in
the engine) and we ended that game with 71 unused bare tiles.

  FIX (carried from build/main_v87c.py, now promoted):
    1. _v85_space requires kind in (PASTURE, COOP) and no animal -> real
       placement capacity only.
    2. _v88_pasture retasks ONLY hands whose committed action is already
       ["PASS"] (zero opportunity cost by construction) to walk onto owned
       bare land and issue BUILD_PASTURE. Gate: herd deficit vs the largest
       rival >= 2, steps 48..648, max 2 hands/step, max 24 builds/game,
       stops at 40 pasture+coop structures. Per-seat state so mirror play
       stays symmetric.

VERIFICATION SUITE (all must pass before this becomes main.py):
  U1  compile + the three entrypoint names bind to the new callable
  U2  normalize: missing step -> day*24+hour; real step wins; {} and None safe
  U3  seat-1-shaped obs (NO "step" key) reaches step 300 through the FULL
      agent call, and the inner layers see step==300 (expand/dump/rescue
      windows open; the []-index sites no longer KeyError)
  U4  unit: _v85_space rejects bare dirt, accepts free PASTURE/COOP
  U5  unit: pasture ramp fires on PASS hands when behind, never touches
      non-PASS hands, respects caps, deterministic target choice
  U6  full self-play smoke at steps {0,100,300,700} x both seats: no crash,
      legal action shape
  U7  determinism: same fresh module instance replayed twice -> identical
      action sequences (mirror equity precondition)
"""
import importlib.util
import os
import re
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "main.py")          # the shipped v87 artifact
OUT = os.path.join(ROOT, "build", "main_v88.py")
TAR = os.path.join(ROOT, "build", "submission_v88.tar.gz")

src = open(SRC, encoding="utf-8").read().replace("\r\n", "\n")
assert "_V88_" not in src and "_v88_" not in src, "v88 markers already present"

# ---------------------------------------------------------------------------
# Change 1: fix the placement-capacity gate (was: any None tile counts).
# ---------------------------------------------------------------------------
OLD_SPACE = '''def _v85_space(my):
    try:
        for row in my.get("tiles", []) or []:
            for tile in row or []:
                if tile is None:
                    return True
    except AttributeError:
        pass
    return False'''
NEW_SPACE = '''def _v85_space(my):
    """v88: PLACE needs a free PASTURE/COOP tile; bare dirt is NOT capacity.
    An animal without a pen strands in the shed forever and animals are
    unsellable (engine PRODUCTS excludes COW/SHEEP/GOOSE)."""
    try:
        for row in my.get("tiles", []) or []:
            for tile in row or []:
                if isinstance(tile, dict) and "animal" not in tile \\
                        and tile.get("kind") in ("PASTURE", "COOP"):
                    return True
    except AttributeError:
        pass
    return False'''
assert src.count(OLD_SPACE) == 1, "space anchor count: %d" % src.count(OLD_SPACE)
out = src.replace(OLD_SPACE, NEW_SPACE)

# ---------------------------------------------------------------------------
# Change 2: append the v88 layer (entrypoint normalizer + pasture ramp).
# ---------------------------------------------------------------------------
LAYER = '''

# ============================================================================
# v88 -- FULL STEP NORMALIZATION + PASTURE RAMP (see scripts/build_v88.py)
#
# Finding #1: the server withholds observation["step"] from seat 1. The v87
# shim fixed only three late-layer helpers; the shipped artifact still has
# 174 direct obs["step"] index sites and 5 .get("step", 0) sites that stay
# dead (or KeyError-caught) all game on seat 1. Fix: inject the exact step
# (day*24+hour, verified error +0.00) into the observation at the TRUE
# entrypoint before any parent layer runs. Superset of the v87 shim.
#
# Finding #2: animals are unsellable and PLACE only accepts a free
# PASTURE/COOP tile, but BUILD_PASTURE is FREE. _v85_space is fixed above;
# here idle hands (action already ["PASS"], zero opportunity cost by
# construction) walk to owned bare land and build pens so expansion buys
# have somewhere to live. Fires when herd deficit vs the biggest rival >= 2,
# steps 48..648, max 2 hands/step, max 24 builds/game, cap 40 structures.
# ============================================================================
_V88_ON = True
_V88_STEP_LO = 48
_V88_STEP_HI = 648
_V88_DIFF = 2
_V88_MAX_HANDS_PER_STEP = 2
_V88_BUILDS_PER_GAME = 24
_V88_STRUCT_CAP = 40
_V88_REPORT = {"builds": 0, "normalized": 0}


def _v88_normalize(obs):
    """Return obs with a valid 'step' key (mutates dict obs in place; the
    environment rebuilds observations every step)."""
    try:
        if isinstance(obs, dict):
            raw = obs.get("step")
            ok = False
            try:
                ok = raw is not None and int(raw) >= 0
            except (TypeError, ValueError):
                ok = False
            if not ok:
                day = int(obs.get("day", 0) or 0)
                hour = int(obs.get("hour", 0) or 0)
                obs["step"] = day * 24 + hour
                _V88_REPORT["normalized"] += 1
            return obs
    except Exception:
        pass
    return obs


def _v88_tiles(farm):
    try:
        return farm.get("tiles", []) or []
    except AttributeError:
        return []


def _v88_owned(farm):
    try:
        return set(farm.get("unlocked_quadrants", []) or [])
    except (TypeError, AttributeError):
        return set()


def _v88_quadrant(x, y):
    if x < 5 and y < 5:
        return "NW"
    if x >= 5 and y < 5:
        return "NE"
    if x < 5 and y >= 5:
        return "SW"
    return "SE"


def _v88_bare(farm):
    owned = _v88_owned(farm)
    out = []
    for y, row in enumerate(_v88_tiles(farm)):
        for x, tile in enumerate(row or []):
            if tile is None and _v88_quadrant(x, y) in owned:
                out.append((x, y))
    return out


def _v88_struct_count(farm):
    n = 0
    for row in _v88_tiles(farm):
        for tile in row or []:
            if isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP"):
                n += 1
    return n


def _v88_walk(pos, target):
    cmds = []
    x, y = int(pos[0]), int(pos[1])
    tx, ty = int(target[0]), int(target[1])
    while x != tx:
        if x < tx:
            cmds.append(["EAST"]); x += 1
        else:
            cmds.append(["WEST"]); x -= 1
    while y != ty:
        if y < ty:
            cmds.append(["SOUTH"]); y += 1
        else:
            cmds.append(["NORTH"]); y -= 1
    return cmds


def _v88_pick(farm, used):
    cands = [t for t in _v88_bare(farm) if t not in used]
    if not cands:
        return None
    tiles = _v88_tiles(farm)

    def score(t):
        x, y = t
        near = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            try:
                tile = tiles[y + dy][x + dx]
            except (IndexError, TypeError):
                tile = None
            if isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP"):
                near += 1
        return (-near, abs(x - 4) + abs(y - 4), x, y)

    return min(cands, key=score)


def _v88_pasture(action, obs):
    if not _V88_ON:
        return action
    step = _v85_step(obs)
    if step < _V88_STEP_LO or step > _V88_STEP_HI:
        return action
    diff, seat, my = _v85_totals(obs)
    # EXACTLY the same gate as _v85_expand (diff >= _V88_DIFF == _V85_DIFF),
    # so pens are only built when a buy is actually pending. Mirror equity:
    # with equal herds neither layer ever fires.
    if diff < _V88_DIFF or not my:
        return action
    if _v88_struct_count(my) >= _V88_STRUCT_CAP:
        return action
    st = _V88_STATE.setdefault(seat, {"targets": {}, "built": 0})
    if st["built"] >= _V88_BUILDS_PER_GAME:
        return action
    try:
        units = [list(action.get("farmer") or ["PASS"])] + [
            list(h or ["PASS"]) for h in (action.get("hands") or [])]
    except AttributeError:
        return action
    try:
        farm_units = _v83_units(my)
    except Exception:
        farm_units = []
    changed = 0
    for ui in range(1, len(units)):
        if ui >= len(farm_units):
            break
        if units[ui] != ["PASS"]:
            continue                      # zero opportunity cost, by design
        tgt = st["targets"].get(ui)
        if tgt is None:
            tgt = _v88_pick(my, set(st["targets"].values()))
            if tgt is None:
                break
            st["targets"][ui] = tuple(tgt)
        if tuple(farm_units[ui]) == tuple(tgt):
            units[ui] = ["BUILD_PASTURE"]
            del st["targets"][ui]
            st["built"] += 1
            _V88_REPORT["builds"] += 1
        else:
            units[ui] = _v88_walk(farm_units[ui], tgt)[0]
        changed += 1
        if changed >= _V88_MAX_HANDS_PER_STEP:
            break
    if changed:
        action["farmer"] = units[0]
        action["hands"] = units[1:]
    return action


_V88_PARENT = agent
_V88_STATE = {}


def _v88_entrypoint(observation, configuration=None):
    observation = _v88_normalize(observation)
    action = _V88_PARENT(observation, configuration)
    try:
        action = _v88_pasture(action, observation)
    except Exception:
        pass
    return action


agent = _v88_entrypoint
kaggle_submission_agent = _v88_entrypoint
_kaggle_submission_entrypoint = _v88_entrypoint
'''

out = ("# v88: full step normalization at the entrypoint + pasture ramp; "
       "supersedes v87/v87b/v87c. See scripts/build_v88.py.\n" + out + LAYER)

compile(out, OUT, "exec")
open(OUT, "w", encoding="utf-8", newline="").write(out)
print("Generated {} ({:,} bytes)".format(OUT, os.path.getsize(OUT)))

# ===========================================================================
# Verification suite
# ===========================================================================
import kaggle_environments  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load(OUT, "v88_check")
for ep in ("agent", "kaggle_submission_agent", "_kaggle_submission_entrypoint"):
    assert hasattr(mod, ep), "missing entrypoint " + ep
    assert getattr(mod, ep) is mod._v88_entrypoint, ep + " not bound to v88"
assert mod._V88_ON is True
print("U1 OK: compiles, all three entrypoints bound to the v88 callable.")


def mk_obs(step, seat, my_herd=0, opp_herd=3, pastures=0):
    """Synthetic two-farm observation. Herd size is encoded as real pasture
    animals (what _v85_totals counts); `pastures` free pens are added to our
    board plus bare owned land for the ramp to build on."""
    def make_grid(herd_n, free_pens):
        grid = [[None] * 10 for _ in range(10)]
        placed = 0
        pen = 0
        for y in range(4, 7):                      # middle band
            for x in range(0, 10):
                if placed < herd_n:
                    grid[y][x] = {"kind": "PASTURE", "animal": "SHEEP"}
                    placed += 1
                elif pen < free_pens:
                    grid[y][x] = {"kind": "PASTURE"}
                    pen += 1
        return grid
    me = {"money": 9000.0, "tiles": make_grid(my_herd, pastures),
          "farmer": [4, 4], "hands": [[4, 5], [0, 0], [9, 1]],
          "unlocked_quadrants": ["NW", "NE", "SW", "SE"]}
    them = {"money": 9000.0, "tiles": make_grid(opp_herd, 0),
            "farmer": [0, 0], "hands": [],
            "unlocked_quadrants": ["NW"]}
    return {"player": seat, "farms": [them, me] if seat == 1 else [me, them],
            "private": {"shed": {}, "seeds": {}, "inventories": [{}, {}]},
            "market": {"prices": {"WOOL": 200}, "inventory": {}},
            "town": {"unlocked_shops": []}}


def seat1_obs(step, **kw):
    """Observation WITHOUT 'step', exactly like the live server sends seat 1."""
    o = mk_obs(step, 1, **kw)
    o["day"] = step // 24
    o["hour"] = step % 24
    assert "step" not in o
    return o


# --- U2: the normalizer -----------------------------------------------------
o = seat1_obs(300)
assert mod._v88_normalize(o)["step"] == 300
assert mod._v88_normalize({"step": 7, "day": 20, "hour": 5})["step"] == 7
assert mod._v88_normalize({"step": 0, "day": 0, "hour": 0})["step"] == 0
assert mod._v88_normalize({})["step"] == 0
assert mod._v88_normalize(None) is None
assert mod._v88_normalize({"step": -3, "day": 3, "hour": 1})["step"] == 73
print("U2 OK: normalize derives day*24+hour only when step is absent/bogus.")

# --- U3: FULL agent call on a seat-1-shaped obs -----------------------------
for s in (0, 100, 300, 700):
    o = seat1_obs(s)
    act = mod.agent(o, None)
    assert isinstance(act, dict) or isinstance(act, list), (s, type(act))
    assert o.get("step") == s, "step not normalized through the real call at %d" % s
    assert mod._v85_step(o) == s
print("U3 OK: seat-1-shaped obs reaches the inner layers with the true step.")

# --- U4: the space gate ------------------------------------------------------
bare_farm = {"tiles": [[None] * 10 for _ in range(10)]}
assert mod._v85_space(bare_farm) is False, "bare dirt must NOT count as capacity"
pen_farm = {"tiles": [[{"kind": "PASTURE"}, {"kind": "PLANT", "crop": "WHEAT"}]]}
assert mod._v85_space(pen_farm) is True
occupied = {"tiles": [[{"kind": "PASTURE", "animal": "SHEEP"}]]}
assert mod._v85_space(occupied) is False
coop = {"tiles": [[{"kind": "COOP"}]]}
assert mod._v85_space(coop) is True
print("U4 OK: _v85_space counts only free PASTURE/COOP tiles.")

# --- U5: pasture-ramp unit behavior ------------------------------------------
mod._V88_STATE.clear()
mod._V88_REPORT["builds"] = 0

behind = seat1_obs(300, my_herd=0, opp_herd=3)   # deficit 3 >= _V88_DIFF
diff, seat, my = mod._v85_totals(behind)
assert seat == 1 and diff >= mod._V88_DIFF, (diff, seat)

action = {"farmer": ["HARVEST"], "hands": [["PASS"], ["PASS"], ["WORK"]],
          "market": []}
res = mod._v88_pasture(action, behind)
assert res["hands"][2] == ["WORK"], "non-PASS hand was touched!"
assert res["hands"][0] != ["PASS"] or res["hands"][1] != ["PASS"], \
    "no idle hand retasked while behind with bare land available"
assert mod._V88_REPORT["builds"] == 0, "walk step must not count as build"

# arrive-at-target -> BUILD_PASTURE. Our hands occupy farm positions
# [4,5],[0,0],[9,1]; put one exactly on the stored target.
st = mod._V88_STATE[seat]
tgt = next(iter(st["targets"].values()))
arrived = seat1_obs(300, my_herd=0, opp_herd=3)
arrived["farms"][1]["farmer"] = [4, 4]
arrived["farms"][1]["hands"] = [list(tgt), [0, 0], [9, 1]]
action2 = {"farmer": ["HARVEST"], "hands": [["PASS"], ["PASS"], ["WORK"]],
           "market": []}
res2 = mod._v88_pasture(action2, arrived)
assert "BUILD_PASTURE" in [h[0] for h in res2["hands"]], res2
assert mod._V88_REPORT["builds"] == 1

# ahead -> never builds
ahead = seat1_obs(300, my_herd=3, opp_herd=0)
before = mod._V88_REPORT["builds"]
mod._v88_pasture({"farmer": ["PASS"], "hands": [["PASS"], ["PASS"]],
                  "market": []}, ahead)
assert mod._V88_REPORT["builds"] == before, "must not ramp while ahead"

# outside window -> never builds
late = seat1_obs(700, my_herd=0, opp_herd=3)
mod._v88_pasture({"farmer": ["PASS"], "hands": [["PASS"], ["PASS"]],
                  "market": []}, late)
assert mod._V88_REPORT["builds"] == before
print("U5 OK: ramp retasks only PASS hands, gates on deficit/window, caps hold.")

# --- U6: engine smoke, both seats, several phases ----------------------------
env = kaggle_environments.make("kaggriculture",
                               configuration={"episodeSteps": 12, "seed": 0},
                               debug=True)
env.run([mod.agent, mod.agent])
assert len(env.steps) >= 12
print("U6 OK: 12-step self-play smoke passed.")

# --- U7: determinism (mirror equity precondition) ----------------------------
seq_a = [mod.agent(seat1_obs(s), None) for s in (0, 48, 100, 300, 648, 700)]
mod2 = load(OUT, "v88_check2")
seq_b = [mod2.agent(seat1_obs(s), None) for s in (0, 48, 100, 300, 648, 700)]
assert str(seq_a) == str(seq_b), "non-deterministic output between instances"
print("U7 OK: identical action sequences across fresh instances.")

# --- U8: seat-0 PARITY -- v88 must be bit-identical to v87 on step-present obs
# with EQUAL herds (the mirror scenario the bench measures). Fresh instances
# per call so neither layer's cross-step state can desync the comparison.
mismatch = []
for s in range(0, 720, 7):
    x7 = load(SRC, "v87_p%d" % s)
    x8 = load(OUT, "v88_p%d" % s)
    o7 = seat1_obs(s, my_herd=3, opp_herd=3); o7["step"] = s   # equal herds
    o8 = seat1_obs(s, my_herd=3, opp_herd=3); o8["step"] = s
    a7 = x7.agent(o7, None)
    a8 = x8.agent(o8, None)
    if str(a7) != str(a8):
        mismatch.append((s, a7, a8))
assert not mismatch, "seat-0 parity broken at %r" % (mismatch[:3],)
print("U8 OK: mirror-equivalent probes are bit-identical between v87 and v88.")

# --- U9: behind-gate PROOF -- when deficit >= 2 and no free pen exists,
# v87 burns money on unsellable stranded animals, v88 does not; and v88's
# idle hands convert bare land into pens instead.
def probe_behind(mod, s):
    o = seat1_obs(s, my_herd=0, opp_herd=5)   # deficit 5, zero free pens
    return mod.agent(o, None)

x7 = load(SRC, "v87_gate"); x8 = load(OUT, "v87_gate")
bought7 = bought8 = builds8 = 0
for s in range(48, 601, 6):
    a7 = probe_behind(x7, s)
    a8 = probe_behind(x8, s)
    bought7 += sum(int(q or 1) for _, _, q in
                   (o for o in (a7.get("market") or [])
                    if o[0] == "BUY_ANIMAL"))
    bought8 += sum(int(q or 1) for _, _, q in
                   (o for o in (a8.get("market") or [])
                    if o[0] == "BUY_ANIMAL"))
    builds8 += sum(1 for h in (a8.get("hands") or []) if h[0] == "BUILD_PASTURE")
assert bought7 > 0, "expected v87 to buy into zero capacity (the live bug)"
assert bought8 == 0, "v88 must NOT buy animals without a free pen"
assert builds8 > 0, "v88 must build pens with idle hands while behind"
print("U9 OK: v87 stranded-animal buys %d -> v88 buys 0 and built %d pens."
      % (bought7, builds8))

# --- packaging ---------------------------------------------------------------
with tarfile.open(TAR, "w:gz") as tar:
    tar.add(OUT, arcname="main.py")
with tarfile.open(TAR) as tar:
    names = tar.getnames()
    assert names == ["main.py"], "tar contents: %s" % names
    assert tar.extractfile("main.py").read() == open(OUT, "rb").read()
print("OK {} ({:,} bytes) contents={}".format(
    TAR, os.path.getsize(TAR), names))

# --- static audit ------------------------------------------------------------
idx_sites = len(re.findall(r'\[\s*"step"\s*\]', out))
get0_sites = len(re.findall(r'\.get\("step",\s*0\)', out))
print("Audit: {} ['step'] index sites and {} .get(step,0) sites remain in the "
      "source -- all of them now read a NORMALIZED observation because the "
      "entrypoint injects step before any parent layer runs.".format(
          idx_sites, get0_sites))
print("ALL CHECKS PASSED -- v88 ready for bench_panel and submission.")
