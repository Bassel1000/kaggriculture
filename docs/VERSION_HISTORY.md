# Kaggriculture release history

This is the decision log for the public agent. It records the evidence that changed the shipped policy, separates local benchmarks from live observations, and deliberately includes reversions: an experiment that looked sensible but lost in live play is not treated as progress.

## How to read the numbers

- **Local** means the versioned harness and opponent fixtures in this project. Pairings are run from both seats and compared as a seat-debiased mean.
- **Live** means observations from submitted competition games and downloaded replays. These are operational signals, not a statement of leaderboard rank.
- A mirror tie is useful for deterministic regression detection; it does not prove that a policy is stronger against the field.

## Timeline

| Version | Date | Change | Evidence and decision |
| --- | --- | --- | --- |
| v72 | 2026-09-11 | Moved from an experimental reactive architecture to a schedule/portfolio baseline derived from the observed frontier. | The recorded local panel reached 24–0 with eight exact mirror ties. This became the base for later release wrappers. |
| v85 | 2026-09 | Added a financed quantity-matching expansion wrapper. | Aimed to close persistent herd/composition deficits while retaining the proven schedule core. |
| v86 | 2026-09 | Relaxed late tomato gates and added terminal fertilizer liquidation. | Live observations suggested a strong but narrow edge; later replay work showed a capacity failure still remained. |
| v87 | 2026-09-28 | Added a seat-1 `step` compatibility shim. | Across recorded observations, seat 0 received `step` while seat 1 did not. Step-gated behavior therefore defaulted off on seat 1. The fallback `day * 24 + hour` was verified to reproduce the step exactly. |
| v88 | 2026-09-29 | Normalized `step` at the actual entrypoint and added a deficit-gated pasture ramp. | The full normalization addressed remaining direct step reads. The ramp was plausible in local fixtures, but live v88 performance regressed: the recorded 97-game sample was 50–46, with the final 30 games at about −$3.3k/game and a 5.2% blowout rate. |
| **v89** | **2026-09-30** | **Kept full normalization; disabled the pasture ramp; restored the v87 loose expansion-space gate.** | **Replay forensics found 27–30 ramp builds per game consuming scheduled worker actions, while stranded animals persisted. The tight gate also blocked expansion buys on deficit boards. A pre-ship ramp ablation was about −$55k. v89 retains the verified seat-1 correction and removes the live-only regression.** |

## The current design: v89

The v89 policy has two layers:

1. The inherited schedule/economy agent supplies the baseline farming policy.
2. Thin release wrappers correct observed failure modes without rewriting that proven baseline.

The important v89 invariant is established before the inherited agent runs:

```python
if observation.get("step") is missing:
    observation["step"] = observation["day"] * 24 + observation["hour"]
```

This is intentionally an exact reconstruction, not a heuristic. It preserves a server-supplied valid step and only fills a missing or invalid one.

The pasture-ramp path remains in the codebase only as a disabled v88 experiment so the v89 delta is auditable. `_V89_PASTURE_ON = False` is the release configuration. The build script also verifies that the v89 callable is bound to every supported Kaggle entrypoint.

## Reproducibility checkpoints

Run the focused v89 builder from the repository root:

```bash
python scripts/build_v89.py
```

It regenerates `build/main_v89.py` from the frozen v88 parent and verifies:

1. The file compiles and all supported entrypoints point to the v89 callable.
2. Missing seat-1 steps reconstruct correctly, while valid server steps win.
3. Synthetic seat-1-shaped observations reach the full agent safely.
4. The v89 expansion-space behavior matches the intended loose gate.
5. The ramp is disabled while deficit-board expansion remains available.

The full-game mirror, head-to-head, and opponent-panel checks are intentionally separate from this builder because they depend on local engine/replay fixtures that are not published in this trimmed source release.

## Related evidence

- [`V87_FORENSICS.md`](V87_FORENSICS.md) contains the replay-level diagnosis that led to the capacity and seat-visibility investigations.
- [`../scripts/build_v89.py`](../scripts/build_v89.py) is the executable v89 release note: its header gives the exact v88 regression and ablation data.
- [`../bench_v87.json`](../bench_v87.json) preserves the earlier public panel baseline for comparison.

## What comes next

The next change should be driven by a reproducible discrepancy between local and live behavior, not by a broad policy rewrite. Any candidate should preserve the seat-1 normalization invariant, run both seats, and include a focused test that fails before the proposed change and passes after it.
