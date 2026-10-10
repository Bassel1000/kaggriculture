# Kaggriculture

> A production Kaggle agent for a two-player, 720-turn farming-economy simulation.

**Current release: v89** · **Submission entrypoint: [`main.py`](main.py)** · **License: Apache-2.0**

Kaggriculture is a single-file competition agent backed by a replay-driven research workflow. The agent reads the live game state each turn, executes a schedule/economy policy, and adds narrowly-scoped safeguards where live evidence shows a real failure mode. The repository contains the current submission artifact, the release builders, a repeatable benchmark harness, and the forensic notes behind the most consequential decisions.

## What is in this release

v89 keeps the valuable part of v88: **full step normalization**. The Kaggle server can omit `observation["step"]` for seat 1, so v89 derives it exactly as `day * 24 + hour` before any policy layer runs. This prevents step-gated logic from silently being disabled on that seat.

It intentionally removes v88's automatic pasture ramp and restores the earlier expansion-space rule. Live replay analysis showed the ramp consuming otherwise scheduled worker actions while failing to eliminate stranded-animal outcomes; the tighter space gate also prevented expansion on deficit boards. The v89 builder documents the measurements and tests the change directly.

## Quick start

```bash
python -m pip install -r requirements.txt
python -m py_compile main.py
python scripts/build_v89.py
```

`main.py` is the Kaggle submission source. It exports the three compatible entrypoints `agent`, `kaggle_submission_agent`, and `_kaggle_submission_entrypoint`, all pointing to the same v89 callable.

The builder regenerates `build/main_v89.py` from the exact v88 artifact and runs focused static and synthetic checks. Full head-to-head and panel runs are kept separate because they require the local competition engine and opponent fixtures.

## Repository map

```text
main.py                   Current v89 submission artifact
scripts/build_v89.py      Reproducible v89 delta builder and focused checks
scripts/submit_v89.py     Optional Kaggle submission helper
scripts/bench_panel.py    Shared two-seat match runner
scripts/bench_v87.py      Previous release benchmark harness
build/main_v88.py         Frozen parent artifact for the v89 builder
docs/VERSION_HISTORY.md   Release-by-release progress and evidence
docs/V87_FORENSICS.md     Replay evidence behind the v87/v88/v89 work
rivals/                   Small, versioned benchmark opponents and fixtures
```

Large replay collections, datasets, generated submission archives, local virtual environments, and the private experiment archive are deliberately ignored. They are useful for research but are neither required to inspect the release nor suitable for a public source repository.

## Validation philosophy

Local score alone is not treated as proof. Each release is evaluated with:

- Both seats for each pairing, then a seat-debiased comparison.
- Replay forensics to locate the first divergence and economic cause.
- Targeted synthetic checks for the exact bug or behavior being changed.
- Deterministic packaging and callable-entrypoint checks.

Local benchmark outputs describe the tested fixtures; they are not a claim of current Kaggle leaderboard rank. See the version history for the distinction between local results and live observations.

## Release progress

| Release | Focus | Outcome |
| --- | --- | --- |
| v72 | Portfolio/schedule frontier | Established a strong schedule-based baseline and exact local mirror behavior. |
| v85–v86 | Expansion and terminal economics | Added quantity-matching expansion and terminal fertilizer handling. |
| v87 | Seat-1 step bug | Detected that the server withheld `step` for seat 1; added an initial compatibility shim. |
| v88 | Full normalization + pasture ramp | Normalized `step` at the true entrypoint; live results rejected the added ramp. |
| **v89** | Keep the fix, remove the regression | Retains normalization while disabling the ramp and restoring the loose expansion gate. |

For the detailed timeline, methodology, measurements, and release rationale, read [`docs/VERSION_HISTORY.md`](docs/VERSION_HISTORY.md).

## Attribution and license

The agent is an Apache-2.0 derivative that preserves the relevant upstream attribution notices inline in [`main.py`](main.py). See [`LICENSE.txt`](LICENSE.txt) for the full license text. This repository is published so the current artifact and the reasoning around it can be audited; please preserve the notices when redistributing derivatives.
