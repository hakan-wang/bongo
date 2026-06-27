# Bongo demo (the previewable product)

The thing you show on stage. A cheap coding agent fixes failing tests, **fails silently**,
and Bongo catches it (by running the real tests — deterministic) and escalates only that
step to a stronger model → green. Then the cost + reliability scoreboard.

## Run it
```bash
python3 demo/server.py
# open http://localhost:8200  and click "Run the demo"
```
No dependencies (Python stdlib only). Works offline.

## What's real vs staged (be honest on stage)
- **REAL:** the verifier. `demo/scenarios.py` actually executes the candidate code and runs
  the unit tests — the green/red is genuine, deterministic ground truth. No AI judging AI.
- **PINNED:** the model outputs are staged (a known cheap-buggy version + a correct strong
  version) so the failure *always* fires live — cheap LLMs are non-deterministic, so we
  don't gamble on stage. Say this out loud; owning it reads as rigor.

## Files
- `scenarios.py` — the tasks, the real `verify()`, the reliability loop, the scoreboard. Run
  it directly (`python3 demo/scenarios.py`) to print the numbers.
- `server.py` — stdlib HTTP server: serves `index.html` + `/api/run`.
- `index.html` — the dashboard (vanilla HTML/CSS/JS).

## Current numbers (per 1,000 runs)
| | reliability | $/1k | broken shipped |
|---|---|---|---|
| Cheap alone | 67% | $2 | 2 |
| **Cheap + Bongo** | **100%** | **$15.33** | **0** |
| Expensive alone | 100% | $40 | 0 |

→ **100% reliable, 62% cheaper than the expensive model.** The cheap model alone silently
shipped 2 broken results.

## Next (see ../BUILD-PLAN.md)
- [P1] real-API live mode (`BONGO_REAL=1`)
- [P1] "connect your API" wired to the team's `proxy.py`
- [P2] per-step drill-down / replay
