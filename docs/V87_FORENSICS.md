# v87 forensics checkpoint — 2026-09-28

## Starting point
v86 (sub `56648082`) live: **20 games, 14W-6L-0T, +$20.4k margin, peak 1741 → 1586.**
v85 (sub `56647395`): 30 games, 20W-8L-2T, peak 1777.
Tie bank is DEAD (0/20). Losses are NOT blowouts: 5 of 6 under $8k.

## What the replays actually show
Downloaded all 6 v86 losses (`scripts/get_replays.py`) + 2 wins, dissected with
`scripts/forensic_losses.py` (day-bucket money gap) and `scripts/step_diff.py`
(per-step divergence + biggest gap movers).

**Replay structure gotcha (cost me one wrong parse — reusables updated):**
each seat's `observation` contains BOTH farms (`farms[0]`/`farms[1]`), so read
ours as `obs["farms"][us]` and theirs as `obs["farms"][them]` from either seat.
`private` is per-seat. Animals are **PASTURE dicts with an `animal` key**, not
`["COW", ...]` tile lists.

### 5 of 6 losses are NEAR-CLONE boards
| EP | opp | diff | us herd | opp herd |
|----|-----|------|---------|----------|
| 114819623 | EPHEMORIA | -$197 | 17 | 17 |
| 114824058 | webmaking | -$363 | 17 | 17 |
| 114830027 | NoDash | -$658 | 17 | 17 |
| 114828522 | HuaLQin | -$1,050 | 23 | 23 |
| 114829868 | holyholy | -$7,812 | 16 | 17 |
| **114825517** | **Atakan Aldemir** | **-$26,366** | **15 (+10 stranded)** | **23** |

The five near-clones are coin flips against our own lineage. The field has
converged on this engine; there is no tie bank left to farm.

### The one structural loss is a REAL BUG (EP 114825517)
We requested `BUY_ANIMAL` 9 COW + 16 SHEEP = **25**, but only ever **placed 15**.
From d9 to d29, **8 SHEEP + 2 COW sat in the shed** = **$4,800 dead**.

Engine proof — `kaggriculture.py:596`:
```python
if op == "SELL" and item in PRODUCTS:
```
`PRODUCTS` excludes COW/SHEEP/GOOSE, so **animals are UNSELLABLE**. A stranded
animal is a total loss with no recovery path.

**Root cause: v85's own gate is wrong.** `_v85_space()` (build/main_v86.py:7940)
returns True on any `None` tile — bare dirt. A bare tile is NOT placement
capacity; an animal needs a PASTURE. At d20 we held 2 free pastures + 10 stuck
animals while the gate reported "space available" off 50+ bare tiles.

### Second finding: BUILD_PASTURE IS FREE
`kaggriculture.py:499-503` — no cost lookup at all, just `if tile is not None:
return`. Same game: we built **17** pastures, Atakan built **24**
(24 tiles = 23 animals + 1 free). We had **71 bare tiles** sitting unused at
game end. Pasture supply, not money, was the binding constraint.

## v87 changes (delta on exact v86 artifact)
1. **`_v85_space` fixed** — requires a real free PASTURE
   (`kind == "PASTURE"` and no `animal`). Stops dead-money animal buys.
2. **`_V87_PASTURE`** — retasks only hands whose action is already `["PASS"]`
   (zero opportunity cost) to walk to bare land and `BUILD_PASTURE`. Gated on
   `opp_total - my_total >= 2` so it only ramps when behind, capped at 2
   hands/step, steps 48-648, stops at 30 pastures.

## Things measured and DELIBERATELY not shipped
- **Sell under-ordering** (`scripts/sell_gap.py`): looks huge ($400k+ "free
  slot$") but it is the natural harvest→sell sawtooth at day boundaries
  (steps 432/456/480/528 are all hour-0). Not a leak. Rejected.
- **Hire-eats-sale-slots**: 13-20 steps/game where 10 HIREs consume all order
  slots. Same sawtooth; sells complete on adjacent steps. Rejected.
- **Shed overflow**: shed pins at 100 in every game but overflow steps are
  1-4/game and the shed drains; no measured $ loss. Rejected.

## Artifacts
- `scripts/get_replays.py` — replay download
- `scripts/forensic_losses.py` — day-bucket gap + herd/sell/hand-op report
- `scripts/step_diff.py` — first divergence + biggest gap-moving steps
- `scripts/sell_gap.py` — SELL under-ordering measurement
- `scripts/stranded.py` — shed-stranded goods/animals
- `scripts/build_v87.py`, `scripts/bench_v87.py`
