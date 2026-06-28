# Assay demo (the previewable product)

The thing you show on stage. A cheap agent runs a finance step, silently wires the wrong amount, and Assay catches it
against the trade's real arithmetic, walks the recovery ladder, and ends correct. Plus the scoreboard.

## Run it
```bash
python3 demo/server.py
# open http://localhost:8200  and click "Run the agent"
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
| Cheap alone | 60% | cheapest | 3 |
| **Cheap + Assay** | **100%** | **74% cheaper** | **0** |
| Expensive alone | 100% | most expensive | 0 |

→ **100% reliable, 74% cheaper than the big model.** Cheap alone silently shipped 2 broken results (incl. a wrong wire).

## Next
- [P1] real-API live mode (`ASSAY_REAL=1`)
- [P1] "connect your API" wired to the team's `proxy.py`
- [P2] per-step drill-down / replay
