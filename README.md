# Kaggriculture Agent

Agent for the **Kaggle Kaggriculture Simulation Competition** — a 2-player,
720-turn farming economy simulation. Ships the current production agent plus
the benchmark harness used to gate every version.

**Current version: v87** (step shim).

## Layout

```
main.py                 the agent — this is the submission artifact
bench_v87.json          recorded benchmark results for this version
scripts/build_v87.py    delta builder + verification suite for v87
scripts/bench_v87.py    the version's benchmark run
scripts/bench_panel.py  shared match runner (loads the engine, runs both seats)
rivals/                 opponent agents used as the regression panel
docs/V87_FORENSICS.md   evidence behind this version's changes
```

`main.py` is the whole submission: the Kaggle archive is this single file
renamed. It exposes three entrypoints — `agent`,
`kaggle_submission_agent`, and `_kaggle_submission_entrypoint` — all bound to
the same callable.

## Install

```bash
pip install -r requirements.txt
```

## Benchmark

```bash
python scripts/bench_v87.py
```

Every pairing runs **both seats** and reports the seat-debiased mean. That
matters: the local runner has a seat-interleaving bias on divergent agents, so
single-seat numbers are not valid comparisons.

The `v87 vs v86` block is skipped automatically unless
`build/main_v86.py` is present — the repo ships only the current artifact.

### v87 results (8 seeds, both seats)

| Matchup | Record | Avg margin |
|---|---|---|
| vs Mirror (self) | 1-1-14 | $0 |
| vs v86 (previous) | 1-1-14 | $0 |
| vs C95 kernel | 8-0 | +$38,781 |
| vs Sheep-spar | 8-0 | +$46,467 |

## What v87 fixes

The episode spec declares `observation["step"]` as `"shared": true`, but the
server withholds it from the **seat-1** agent. Measured across 5,760 recorded
observations from 8 live replays: seat 0 has the field 5760/5760, seat 1 has it
**0/5760**. Not intermittent.

Because every step-gated feature read `step` and defaulted to `0`, the whole
stack ran dead all game on seat 1 — `_v85_expand` (window 48-600),
`_v86_dump` (648-719), `_v83_rescue` (step < 670). Live cost on submission
`56648082`, 20 games:

```
seat 0 (features live)  13 games  10-3   +$25,663/game
seat 1 (features dead)   7 games   4-3      +$169/game
```

Local benches never caught it because the harness supplies `step` to both
seats, so every paired A/B exercised the live path on both sides.

The fix prefers the real `obs["step"]`, else derives `day * 24 + hour`, which
reproduces the step index exactly — verified on 8,640 real observations with
mean error `+0.00`. Seat 0 is bit-identical; no other logic changed.

## License

Apache-2.0 — see `LICENSE.txt`. The agent carries upstream attribution
notices for Apache-2.0 derivations (thomastschinkel, yhay81, tetsutani,
prvsiyan, destbreso, aurax7, Dmitrii Gluzdov, Ahmed Berat Ozer and others);
those notices are preserved inline in `main.py`.

Private repository. Not for redistribution.
