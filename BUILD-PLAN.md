# Bongo — Build Plan

> **Status:** v0.1 — initial buildable plan. A judged/synthesized version from an agent
> council (product-form + UI + sub-feature decomposition + plan-judges) is being generated
> and will refine this. **Rule: plan before build.** This is the plan; building starts on
> the P0 items, which won't change.

## For Håkan (non-technical summary)

We're building a **website you can open in a browser and show on stage** ("the Bongo
dashboard"). It runs a real demo: a cheap AI coding-agent tries to fix failing tests,
**fails silently**, and Bongo **catches it and fixes it live** by escalating just that one
step to a stronger model — then shows the **cost + reliability scoreboard**. You'll be able
to click "Run" and watch it happen. Under the hood it reuses the team's `reliability.py`.

**Product form (decided for the demo):** a **drop-in proxy + web dashboard**. A user
connects by changing one line (`base_url` → Bongo) and keeping their own key; the dashboard
is what they (and the judges) see. (MCP/SDK are possible later; proxy+dashboard is the
fastest previewable, clearest "how do I connect" story for 24h. The agent council is
double-checking this.)

---

## The build (hierarchical checklist)

### MAIN FEATURE 1 — The live demo engine (the proof)  `demo/`
- [ ] **1.1 [P0] Deterministic verifier on real code** — `demo/scenarios.py`
  - [ ] 1.1.1 [P0] A set of small coding tasks, each with REAL unit tests
  - [ ] 1.1.2 [P0] `verify(code, tests)` that actually executes code + tests → pass/fail (free, deterministic = the honest "we don't use AI to judge AI")
  - [ ] 1.1.3 [P0] Pinned "cheap model" outputs (some silently buggy) + "strong model" outputs (correct) — so the failure ALWAYS fires on stage (de-risked)
- [ ] **1.2 [P0] The reliability loop** — extends `reliability.py`
  - [ ] 1.2.1 [P0] cheap gen → verify → on fail, escalate THAT step to strong → verify → pass
  - [ ] 1.2.2 [P0] Per-step trace (model used, output, verify result, action, cost)
  - [ ] 1.2.3 [P0] Three modes per task: cheap-alone / cheap+Bongo / expensive-alone
- [ ] **1.3 [P0] Cost + reliability aggregate** — cheap=1, strong=20 units, scaled "per 1,000 runs"
  - [ ] 1.3.1 [P1] Cross-provider angle: label models as different providers (e.g. cheap-open vs frontier)

### MAIN FEATURE 2 — The previewable frontend (what Håkan shows)  `demo/index.html`
- [ ] **2.1 [P0] Hero side-by-side** — "Cheap alone ❌" vs "Cheap + Bongo ✅", steps stream with green/red, escalation highlighted
- [ ] **2.2 [P0] The scoreboard panel** — cost + reliability bars; headline "100% reliable at a fraction of the big-model price"
- [ ] **2.3 [P0] "Run demo" button** + clean, modern, dependency-free styling (works offline at venue)
- [ ] **2.4 [P1] "Connect your API" section** — show the one-line proxy integration (the product story)
- [ ] **2.5 [P2] Per-step detail drill-down / replay**

### MAIN FEATURE 3 — The backend/server  `demo/server.py`
- [ ] **3.1 [P0]** stdlib HTTP server (no deps) — serves the frontend + `/api/run` returns the full demo JSON
- [ ] **3.2 [P1]** `/api/run-live` that can hit a REAL API when a key is set (`BONGO_REAL=1`), else pinned mode
- [ ] **3.3 [P2]** Wire into the team's `proxy.py` so "point your base_url at Bongo" is real end-to-end

### MAIN FEATURE 4 — Pitch surface (light, P1/P2)
- [ ] 4.1 [P1] The router-wedge line + per-judge one-liners visible in the deck (already in `info/`)
- [ ] 4.2 [P2] Pre-recorded fallback video of the demo (in case live breaks)

---

## ⛔ 24H SCOPE LINE
**Build above:** Features 1 + 2 + 3.1 (a real, de-risked, previewable side-by-side demo with
the scoreboard). **Cut/defer below:** real-API live mode (3.2), full proxy wiring (3.3),
drill-down (2.5), fallback video (4.2) — only if P0 is done and rehearsed.

## 90-second demo flow (de-risked)
1. "Every agent here runs on the cheapest model that *mostly* works." (one slide: 95%/step → 60% over 10 steps)
2. Click Run. Left (cheap alone): step fails silently → red. Right (cheap+Bongo): Bongo catches that step, escalates only it → green.
3. Reveal the scoreboard: cheap = broken, expensive = pricey, **cheap+Bongo = reliable AND cheap**.
4. Wedge line, said before a judge asks: *"Routers pick a model up-front and lock it; Bongo escalates ONE step, AFTER a verify fails, mid-run, across providers a single lab can't reach."*

## Risks + mitigations
- **Live non-determinism** → pin model outputs; the VERIFY (test run) is the only "live" thing and it's deterministic. Keep a recording.
- **"Just FrugalGPT/OpenRouter + a UI"** → lead with per-step + post-verify + cross-provider wedge; deterministic verifier, not a cheap LLM-judge.
- **Looks like a toy** → real test execution on real code = real green/red; honest cost numbers "on this workload".

## Changelog
- v0.1 — initial plan; building P0 of Features 1–3 now. (Agent-council refinement incoming.)
