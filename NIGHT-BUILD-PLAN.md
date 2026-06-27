# NIGHT-BUILD-PLAN.md — Ship Plumbline by 13:00 Paris (Sun Jun 28)

**Scope line (24h deadline):** Re-skin the existing engine onto the finance money-shot, make the recovery ladder + honesty case VISIBLE, rename to Plumbline everywhere, cut the <=5 min video. **Zero new core engine on the critical path.** Reuse `demo/scenarios.py`, `demo/server.py`, `index.html`, `demo/gateway.py`, `demo/real_proof.py`.

---

## P0 — Must ship (the video cannot exist without these)

### 1. Rename to Plumbline [~20 min] [HARD DEPENDENCY for video + deck]
- [ ] 1.1 Wordmark on `index.html` header (swap "Plumbline")
- [ ] 1.2 Slide 1 title + logo
- [ ] 1.3 Find/replace "Plumbline" across README, dashboard, deck
- [ ] 1.4 10-min trademark clearance check (USPTO/EUIPO software class); if crowded → **Plumbline**
- [ ] 1.5 VERIFY: grep repo for "Plumbline" returns only changelog/history

### 2. Finance money-shot scenario (the cold-open artifact) [~90 min]
- [ ] 2.1 Add finance task to `TASKS` in `demo/scenarios.py`: input = fixed synthetic trade ticket / 10-K excerpt with **hardcoded ground truth** `{revenue, net_debt, counterparty, notional, currency}` + `settle_trade(amount, ccy, account)` tool call
- [ ] 2.2 Plant the silent bug in `cheap_code` output: sign-flipped `net_debt` OR 10x `notional` OR wrong `currency` — looks clean, fails arithmetic
- [ ] 2.3 Wire the deterministic check reusing **existing registry unchanged**: `tool-args` + `json-schema` + `schema-from-example` + a hardcoded **arithmetic equality** check (`notional*price == cash`, `amount == ticket_amount`)
- [ ] 2.4 `strong_code` = correct extraction (the escalation target)
- [ ] 2.5 VERIFY: `python3 demo/scenarios.py` → finance step red on cheap, green after escalate, scoreboard updates

### 3. Make the recovery LADDER visible on screen [~75 min] [Agentic Depth: 8→13]
- [ ] 3.1 **Rung 1 — retry-cheap-with-guidance**: feed verifier's failure reason back to cheap model BEFORE spending frontier money (surface this step in the trace)
- [ ] 3.2 **Rung 2 — cross-provider escalate** only if retry still fails (Mistral → Anthropic)
- [ ] 3.3 **Rung 3 — Tripwire kill-switch**: fire on a deliberately runaway/looping step (budget/loop halt)
- [ ] 3.4 Show ALL THREE outcomes in one run on the dashboard
- [ ] 3.5 VERIFY: each rung renders a distinct badge/state in `index.html`

### 4. The honesty-boundary case [~30 min] [non-negotiable insurance]
- [ ] 4.1 Add one open-ended step with no deterministic ground truth
- [ ] 4.2 Plumbline flags **"can't deterministically verify — low-confidence, NOT auto-passed"**
- [ ] 4.3 VERIFY: it does NOT turn green; it renders an amber "flagged" state

### 5. Animated agent-trace "flight recorder" [~60 min]
- [ ] 5.1 Horizontal step 1..N timeline, each node = model used + verdict (reuse `steps[]` trace already produced)
- [ ] 5.2 Broken step glows red with the exact failing assertion; escalation badge pops; flips green
- [ ] 5.3 VERIFY: renders for the finance scenario end to end

### 6. On-screen overlays [~40 min]
- [ ] 6.1 "COST OF SHIPPING THIS BUG: $X" counter on the finance catch
- [ ] 6.2 Live escalation-rate counter ("47 cheap / 3 escalated") — pre-empts #1 objection
- [ ] 6.3 Cost-per-COMPLETED-task line (not per-token); scoreboard cheap 67% → Plumbline 100%, ~62% cheaper — as RECEIPTS at the end only

### 7. Record + cut the video [~90 min] [GATEKEEPER]
- [ ] 7.1 Single-take finance catch, cold-open in first 10s (no logo intro)
- [ ] 7.2 ~15s coding red→green pytest cutaway as mechanism shot
- [ ] 7.3 Moat sentence on screen at the cross-provider hop
- [ ] 7.4 Honesty case shown
- [ ] 7.5 Receipts (cost/escalation counters) at close
- [ ] 7.6 base_url drop-in as closing 15s
- [ ] 7.7 VERIFY: total <=5 min, zero blacklisted buzzwords in first 20s

### 8. README + repo hygiene [~30 min] [submission requirement]
- [ ] 8.1 What it does / how it works / install+run (reuse QUICKSTART)
- [ ] 8.2 `python3 demo/scenarios.py` and dashboard run instructions verified clean-clone
- [ ] 8.3 Public GitHub repo, Plumbline name, screenshot of the catch

---

## P1 — Strong polish (do if P0 done with >3h margin)

- [ ] 9. **base_url drop-in proof** [~30 min]: film 2-line change on a real OSS agent using existing `demo/gateway.py`; agent now catches+escalates a failure it used to ship
- [ ] 10. **Reliability-per-dollar leaderboard** [~45 min]: each provider row = accuracy %, $, composite score; Plumbline row on top beats every model on BOTH axes (reuse scoreboard data)
- [ ] 11. **real_proof.py live cross-provider** [~30 min]: run `demo/real_proof.py` with real keys (has `--mock` fallback) for one genuinely-live escalation clip
- [ ] 12. **"Break it yourself" failure injector** [~60 min]: buttons to inject failure class (hallucinated field / wrong tool arg / schema drift / off-by-one); anti-"staged demo" move

---

## P2 — Bonus (only if hours to spare; never on critical path)

- [ ] 13. **Swarm lane (mechanism beat)** [~90 min]: parallel asyncio fan-out of same step to 3-4 cheap models, reality elects winner via the existing verifier; 4-lane animation. **In-demo mechanism only, never headline.**
- [ ] 14. Polish wordmark/favicon, deck transitions

---

## Loop / verify discipline (run after EVERY P0 item)
1. `python3 demo/scenarios.py` — scoreboard fires, finance step red→green
2. Open dashboard — ladder + honesty case + trace render
3. grep for "Plumbline" — none in shipped assets
4. Time the video segment — first 10s = the wrong-number catch, no jargon
5. Clean-clone test before submit: fresh checkout → install → run → demo fires

## Critical-path order (do in this sequence)
Rename (1) → Finance scenario (2) → Recovery ladder (3) → Honesty case (4) → Trace UI (5) → Overlays (6) → Record video (7) → README (8). P1/P2 only after the video is in the can.
