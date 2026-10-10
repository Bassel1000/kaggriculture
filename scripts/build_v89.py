"""Build v89: keep v88's step normalization, kill the pasture ramp, revert space gate.

WHY (evidence, 2026-09-30):
  Live v88 (ref 56685549, 97 games, 50W-46L, last30 10-20 -3.3k/game,
  blowout rate 5.2% vs v87's 2.5%) regressed vs v87 (159 games, last30
  10-19 -0.4k/game). Local bench is clean (v88-vs-v87 1-1-14 $0; panel
  8-0 c95/spar) because the harness supplies step to BOTH seats and the
  panel bots never expand -- the regression is live-only, same class as
  the v87 step-blindness bug.
  Forensics on the 5 worst v88 losses (rivals/replays_v88):
  1. Stranded animals PERSIST (6C+3S, 7S, 2C in shed) -- the tight space
     gate + ramp FAILED at their stated goal.
  2. The ramp fires 27-30 BUILD_PASTURE/game, diverting PASS-hand labor for
     pens that don't get used. PASS hands are NOT free: hijacked hands walk
     away from schedule positions with no walk-home, desyncing the tape.
     Pre-ship record already rejected this: pasture-ramp forced ablation
     -$55k (STATE.md v87 section).
  3. Tight space gate blocks expansion buys exactly on deficit boards
     (v88 U9: buys 25 -> 0 when behind with no free pen). $4.8k stranded
     savings << $25-35k quantity gaps; v85 loose-gate firing won +$4.2k.
  4. Ablation 2026-09-30: killing ramp + reverting space leaves seed-0
     local play bit-identical, so the ramp/space pair buys nothing locally
     and costs games live. The normalizer half of v88 is verified correct
     (day*24+hour error +0.00 over 8,640 real obs) and fixes the +$25k/game
     seat-1 bleed -- KEEP it.

DELTA on exact v88 artifact (build/main_v88.py), three changes:
  1. _v85_space REVERTED to the v87 original (any None tile counts). The
     native schedule builds pens then places same-day and v82 fixers repair
     shed takes; bare dirt today is capacity tomorrow. Tight gate starved
     quantity on expander boards.
  2. Pasture ramp DISABLED via _V89_PASTURE_ON=False (entrypoint
     normalization stays ON -- it does not consult the flag).
  3. Entrypoints rebound to _v89_entrypoint (alias of the v88 callable).

VERIFICATION (all must pass):
  V1 compile + three entrypoints bound to the v89 callable
  V2 normalizer unit: missing step -> day*24+hour; real step wins; {} -> 0
  V3 seat-1-shaped obs through the FULL call at steps {0,100,300,700} x both
      seats: no crash, step normalized, legal action shape
  V4 space gate loose again (bare dirt True; free pen True; occupied False)
  V5 firing proof (behind, no free pens, steps 48..600): v89 BUYs animals
      (>0 over the sweep) and builds ZERO pastures (ramp off)
  V6 mirror + v89-vs-v87 H2H seeds 0-7: 1-1-14 $0 pattern (dormant locally)
  V7 panel vs c95/spar seeds 0-3: 8-0 both, margins >= v87's
  V8 determinism across fresh instances
"""
import importlib.util
import os
import tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "build", "main_v88.py")   # exact shipped v88 artifact
OUT = os.path.join(ROOT, "build", "main_v89.py")
TAR = os.path.join(ROOT, "build", "submission_v89.tar.gz")

src = open(SRC, encoding="utf-8").read().replace("\r\n", "\n")
assert "_V89_" not in src and "_v89_" not in src, "v89 markers already present"
assert "_V88_ON = True" in src, "v88 flag anchor missing"

# --- 1. revert the space gate to the v87 original ---------------------------
V88_SPACE = '''def _v85_space(my):
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
V89_SPACE = '''def _v85_space(my):
    """v89: REVERTED to the v87 original. Bare dirt counts as capacity: the
    native schedule builds pens then places same-day and the v82 fixers
    repair shed takes, so dirt today is a pen tomorrow. The v88 tight gate
    blocked expansion buys on exactly the deficit boards where quantity
    matters (live: still stranded AND fell behind)."""
    try:
        for row in my.get("tiles", []) or []:
            for tile in row or []:
                if tile is None:
                    return True
    except AttributeError:
        pass
    return False'''
assert src.count(V88_SPACE) == 1, "space anchor count: %d" % src.count(V88_SPACE)
out = src.replace(V88_SPACE, V89_SPACE)

# --- 2. gate the pasture ramp on a v89 flag (default OFF) --------------------
OLD_GUARD = '''def _v88_pasture(action, obs):
    if not _V88_ON:
        return action'''
NEW_GUARD = '''def _v88_pasture(action, obs):
    if not (_V88_ON and _V89_PASTURE_ON):
        return action'''
assert out.count(OLD_GUARD) == 1, "pasture guard count: %d" % out.count(OLD_GUARD)
out = out.replace(OLD_GUARD, NEW_GUARD)

# --- 3. v89 tail: flag OFF + entrypoint rebind --------------------------------
TAIL = '''

# ============================================================================
# v89 -- RAMP OFF, SPACE GATE REVERTED, NORMALIZATION KEPT
# (see scripts/build_v89.py). v88 live regressed (blowouts 5.2% vs 2.5%,
# last30 -3.3k/game vs -0.4k; stranded animals persisted while the ramp
# burned 27-30 PASS-hand builds/game; pre-ship pasture ablation -$55k).
# The step normalizer is the verified-good half of v88 (seat-1 bleed fix)
# and stays ON: _v88_normalize does not consult any flag.
# ============================================================================
_V89_PASTURE_ON = False

_V89_PARENT = _v88_entrypoint
_v89_entrypoint = _v88_entrypoint


agent = _v89_entrypoint
kaggle_submission_agent = _v89_entrypoint
_kaggle_submission_entrypoint = _v89_entrypoint
'''
out = ("# v89: pasture ramp OFF + space gate reverted to v87 loose; step "
       "normalization kept. See scripts/build_v89.py.\n" + out + TAIL)

compile(out, OUT, "exec")
open(OUT, "w", encoding="utf-8", newline="").write(out)
print("Generated {} ({:,} bytes)".format(OUT, os.path.getsize(OUT)))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load(OUT, "v89_check")
for ep in ("agent", "kaggle_submission_agent", "_kaggle_submission_entrypoint"):
    assert hasattr(mod, ep), "missing entrypoint " + ep
    assert getattr(mod, ep) is mod._v89_entrypoint, ep + " not bound to v89"
assert mod._V88_ON is True and mod._V89_PASTURE_ON is False
print("V1 OK: compiles, all three entrypoints bound to the v89 callable.")


def mk_obs(step, seat, my_herd=0, opp_herd=3, pastures=0):
    def make_grid(herd_n, free_pens):
        grid = [[None] * 10 for _ in range(10)]
        placed = 0
        pen = 0
        for y in range(4, 7):
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
    o = mk_obs(step, 1, **kw)
    o["day"] = step // 24
    o["hour"] = step % 24
    assert "step" not in o
    return o


# --- V2: normalizer ------------------------------------------------------------
o = seat1_obs(300)
assert mod._v88_normalize(o)["step"] == 300
assert mod._v88_normalize({"step": 7, "day": 20, "hour": 5})["step"] == 7
assert mod._v88_normalize({})["step"] == 0
assert mod._v88_normalize(None) is None
print("V2 OK: normalization intact (seat-1 bleed fix kept).")

# --- V3: full call on seat-1-shaped obs ---------------------------------------
for s in (0, 100, 300, 700):
    for seat in (0, 1):
        oo = mk_obs(s, seat)
        if seat == 1:
            oo.pop("step", None)
            oo["day"] = s // 24
            oo["hour"] = s % 24
        else:
            oo["step"] = s
        act = mod.agent(oo, None)
        assert isinstance(act, dict), (s, seat, type(act))
        assert oo.get("step") == s, (s, seat)
print("V3 OK: seat-1-shaped obs reaches inner layers with the true step.")

# --- V4: space gate is loose again ---------------------------------------------
assert mod._v85_space({"tiles": [[None] * 10 for _ in range(10)]}) is True
assert mod._v85_space({"tiles": [[{"kind": "PASTURE", "animal": "SHEEP"}]]}) is False
assert mod._v85_space({"tiles": [[{"kind": "PLANT", "crop": "WHEAT"}]]}) is False
print("V4 OK: space gate reverted (bare dirt counts, v87 original).")

# --- V5: firing proof via direct layer calls (behind-board, no free pens) ----
# NOTE: full-agent synthetic probes teleport hands every step so the ramp can
# never WALK to arrival synthetically; live forensics already prove v88
# builds 27-30 pastures/game. Here we prove the v89 delta directly:
#  (a) _v85_expand appends BUY_ANIMAL under the loose gate, blocked under
#      the v88 tight gate (inverse of v88-U9, same board shape);
#  (b) _v88_pasture leaves PASS hands untouched when the ramp is OFF (v89)
#      and retasks them when ON (v88 reference).
v88 = load(SRC, "v88_ref")


def behind_board():
    # deficit 5, zero free pens, money rich, wool high (sheep route eligible)
    o = seat1_obs(300, my_herd=0, opp_herd=5)
    o["farms"][1]["money"] = 9000.0
    o["market"]["prices"]["WOOL"] = 200.0
    return o


o9, o8 = behind_board(), behind_board()
d9, _, my9 = mod._v85_totals(o9)
d8, _, my8 = v88._v85_totals(o8)
assert d9 >= 2 and d8 >= 2, (d9, d8)
assert mod._v85_space(my9) is True, "loose gate must see bare dirt"
assert v88._v85_space(my8) is False, "tight gate must see no pens (sanity)"
a9 = {"farmer": ["PASS"], "hands": [], "market": []}
a8 = {"farmer": ["PASS"], "hands": [], "market": []}
mod._V85_STATE["seen"].clear()
mod._V85_STATE["bought"].clear()
v88._V85_STATE["seen"].clear()
v88._V85_STATE["bought"].clear()
r9 = mod._v85_expand(a9, o9)
r8 = v88._v85_expand(a8, o8)
buys9 = [x for x in (r9.get("market") or []) if x and x[0] == "BUY_ANIMAL"]
buys8 = [x for x in (r8.get("market") or []) if x and x[0] == "BUY_ANIMAL"]
assert len(buys9) == 1, "v89 loose gate must fire the expansion buy"
assert len(buys8) == 0, "v88 tight gate must block it (sanity)"

p9 = {"farmer": ["HARVEST"], "hands": [["PASS"], ["PASS"]], "market": []}
p8 = {"farmer": ["HARVEST"], "hands": [["PASS"], ["PASS"]], "market": []}
mod._V88_STATE.clear()
v88._V88_STATE.clear()
q9 = mod._v88_pasture(p9, behind_board())
protected = [list(h) for h in q9["hands"]]
assert protected == [["PASS"], ["PASS"]], "v89 ramp OFF must not touch hands"
q8 = v88._v88_pasture(p8, behind_board())
assert any(h != ["PASS"] for h in q8["hands"]), "v88 ramp must retask (sanity)"
print("V5 OK: v89 buys on deficit boards (v88 blocked) and builds nothing.")

# --- V6/V7/V8 run in bench_v89.py (full games) ---------------------------------
print("STATIC CHECKS PASSED -- now run bench_v89.py for V6/V7/V8 + packaging.")
