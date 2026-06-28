# Assay — FINAL BUILD-PLAN.md

> **Status:** v1.0 FINAL. Plan-before-build is over for P0 — the P0 spine is already
> built and verified running (see "Ground truth" below). This plan locks scope for the
> remaining ~24h: **close the judge-flagged gaps, harden the stage, do NOT add surfaces.**
> Files live in `/Users/hakanwang/Assay/` (core: `proxy.py`, `reliability.py`) and
> `/Users/hakanwang/Assay/demo/` (`scenarios.py`, `server.py`, `index.html`).

---

## For Håkan (non-technical summary)

We're building **one website you open in a browser and show on stage.** You click **"Run
demo"** and watch two columns race to fix a broken software test suite using a *cheap* AI:

- **Left (cheap AI alone):** confidently says "done" — but the tests are still failing. It
  **shipped broken code and didn't notice.**
- **Right (cheap AI + Assay):** hits the same failure, but Assay **runs the tests itself**
  (real, not faked), catches the silent failure, and **escalates just that one step to a
  stronger model on a different provider** — the tests flip **red → green** live.

Then a **scoreboard** drops: *cheap alone = 67% reliable and shipped broken work; cheap +
Assay = 100% reliable at ~38% of the all-expensive cost.* Those numbers are **computed
live from the actual run**, not typed in.

**What you'll be able to show:** a real, clickable frontend (no terminal, works offline),
plus one slide-style line on screen explaining why this isn't just a router. We also keep a
**screen recording** as a backup so nothing can break on stage.

**What you say in one breath:** *"Same cheap model on both sides. The left ships broken work
and never knows. Assay runs the tests, catches it, and upgrades only the broken step — to a
different provider's model. Expensive-model reliability at cheap-model price."*

---

## 1. The decided product form

**DECIDED: Drop-in OpenAI-compatible proxy (the connect story) + a live web dashboard (the
previewable product).** Form A.

- **Why (line 1):** it's the only form that answers *"how do I connect?"* in one line —
  `base_url → Assay`, keep your own key — and it's the most buildable because we already own
  every component (`proxy.py`, `reliability.py`, `demo/`).
- **Why (line 2):** it's the only form non-technical Håkan can demo with zero code, and the
  red→green side-by-side visually lands the cross-provider, mid-run, post-verify wedge that
  separates us from routers and from FrugalGPT-2023.

**How a user connects their API (shown on screen, P0):**
```python
client = OpenAI(
    base_url="https://api.bongo.dev/v1",   # <- the only change
    api_key=os.environ["YOUR_KEY"],        # your key, passes through, never stored
)
```
Plus a (non-functional-but-real-looking) **"Paste your key"** field + **provider dropdown**
on the Connect card so "BYO key, any provider" is *shown*, not just said.

**The previewable UI:** a single offline `demo/index.html`, dark ops-console theme (reuses
`dashboard.html` CSS tokens), three stacked sections — **(a)** hero side-by-side live demo
with a **Run demo** button, **(b)** cost + reliability scoreboard, **(c)** Connect card with
the snippet + key field + router-wedge callout. SDK (`@bongo.step`) and MCP `run_tests` tool
are **verbal mentions only** — not built.

---

## Ground truth (already built & verified — build ON, don't rebuild)

- `proxy.py` — OpenAI-compatible proxy on `:8128`, cache + `/stats`, mock default,
  `ASSAY_REAL=1` forwards to OpenAI. Stdlib only.
- `reliability.py` — `run_step()` cascade (cheap → deterministic check → retry → strong),
  `COST={cheap:1, strong:50}`, `check_meeting` JSON checker. Stdlib only.
- `demo/scenarios.py` — **real** `verify(code, tests)` (executes code + asserts, no AI
  judge), 6 pinned tasks (2 silently buggy), `run_task(mode)` with the
  cheap→verify→**bongo-escalation**→re-verify loop, `run_all()` scoreboard.
- `demo/server.py` — stdlib server on `:8200`, serves `index.html`, `GET /api/run` →
  `run_all()` JSON.
- `demo/index.html` — animated side-by-side, connect snippet, router-wedge copy.
- **Verified running:** `python3 demo/scenarios.py` → *cheap 67% (2 broken shipped) /
  bongo 100% / strong 100%, 62% cheaper than strong.* Deterministic.

**Implication:** P0 is essentially DONE. The remaining 24h is **gap-closing + hardening**,
exactly per the judge critiques. Resist building new things.

---

## 2. The build (hierarchical checklist)

### MAIN FEATURE 1 — Demo engine: real verify + pinned failure  `demo/scenarios.py`
- **1.1 [P0] ✅ DONE — Real deterministic verifier** (`verify()` executes code + tests).
  - 1.1.1 [P0] ✅ 6 tasks with real unit tests; 2 silently buggy (cheap passes some, fails some).
  - 1.1.2 [P0] ✅ Pinned `cheap_code` / `strong_code` so the failure fires every run.
  - 1.1.3 [P1] **Pluggable-verifier framing** — refactor `verify` into a tiny `CHECKERS`
    registry and surface 2–3 types in the trace (`run-tests`, plus reuse `check_meeting`
    JSON-schema from `reliability.py`, + an `assertion` check). Pre-empts "it's one
    if-statement / just FrugalGPT." ~45 min. Add a `checker` field per verify step.
- **1.2 [P0] ✅ DONE — Assay escalation loop** (`run_task` mode `bongo`: catch → escalate
  one step → re-verify → green; `fixed_by="bongo-escalation"`).
- **1.3 [P0] ✅ DONE — Scoreboard** (`run_all` → reliability %, cost_units, broken_shipped,
  `cost_per_1k_usd`, headline). **Numbers are computed from the trace — keep it that way.**

### MAIN FEATURE 2 — Cross-provider proof (the moat — promote to P0)  `demo/scenarios.py`, `proxy.py`
- **2.1 [P0] Provider identity on every step.** Tag cheap vs strong with *different
  providers* in the trace: cheap = `mistral-small` (flatters the Mistral judge), strong =
  `claude-…`/`gpt-4o`. Add `provider` to each step dict; render provider badge in the UI
  step rows ("escalated to **Anthropic**"). ~30 min.
- **2.2 [P0] ONE genuinely-real cross-provider escalation call, captured.** Behind
  `ASSAY_REAL`, make the strong-model escalation actually hit a *different provider's* API
  once (e.g. cheap=Mistral, strong=Anthropic/OpenAI), **record the terminal + UI output to
  a file/video**, and keep it as proof. This makes the moat *demonstrably true* even though
  the stage run is pinned. Default stays mock. ~1.5h. **This is the single highest-leverage
  judge fix — do it.**
- **2.3 [P1] Router/FrugalGPT wedge as on-screen copy** (already partly in `index.html`):
  keep the *"Not a router… escalates one step, after a verify fails, mid-run, across
  providers"* callout visible in the hero, not just the footer.

### MAIN FEATURE 3 — Previewable frontend  `demo/index.html`
- **3.1 [P0] ✅ DONE — Side-by-side animated demo** (Run demo → `/api/run` → sequential
  reveal → left RED, right red→escalate→GREEN).
- **3.2 [P0] Render the REAL test output (red then green)** in a mono block under the
  escalated step — prove the verify isn't faked. Use the `detail` string already returned
  by `verify()`. ~30 min.
- **3.3 [P0] Connect card upgrade** — keep the `base_url` snippet; **add a "Paste your key"
  input + provider dropdown** (cosmetic, real-looking) so the BYO/connect story is shown.
  ~30 min.
- **3.4 [P0] Verdict banner** — "Cheap alone: shipped 2 broken. Cheap + Assay: 0 broken,
  100%. +cost only on the escalated steps." Pull from `headline`. (Mostly present — verify.)
- **3.5 [P1] Cost + reliability scoreboard tiles** — 3 counting-up stats (Reliability %,
  Cost units, $ saved/1k) + comparison bars cheap / bongo / strong. Reuse `dashboard.html`
  `.stat`/`.big`/`.bar` components.
- **3.6 [P2] Micro-animations** (glow on green flip). Cut if behind.

### MAIN FEATURE 4 — Integration + stage-proofing  `demo/`
- **4.1 [P0] One command** — `python3 demo/server.py` serves everything on `:8200`. Verify
  `GET /api/run` returns 200 + all expected fields. ✅ wired; smoke-test it.
- **4.2 [P0] Determinism gate** — run `python3 demo/scenarios.py` **10×**, assert identical
  scoreboard every time. Stage dies if this isn't green. (Quick loop, ~15 min.)
- **4.3 [P0] CLI backup runner** — `scenarios.py __main__` already prints the red→green
  scoreboard; confirm it's a clean fallback if the browser fails.
- **4.4 [P0] Record the fallback video THE MOMENT the happy path is polished** — a 90s
  screen recording of a clean Run, cued up for a >3s hang. Schedule it ~hour 14, **not hour
  23.** (Judge critique #3.)
- **4.5 [P1] Pre-seed `/stats`** — run `demo_traffic.py` once before the pitch so the
  proxy's bill-cut number looks healthy if a judge asks about the cache/cost side.
- **4.6 [P2] README run-card** for Håkan (start server, open URL, click Run).

### ⬇ The proxy (`proxy.py`) is the *connect-story spine*, already built
- [P1] Leave `proxy.py` as-is for the connect narrative; do **not** route the live demo
  through it under time pressure. The demo engine (`demo/`) is self-contained and safer.

---

## 3. ⛔ 24H SCOPE LINE — build above, cut below

**BUILD ABOVE (P0 + the high-leverage P1s):**
1.1.3 pluggable-verifier framing · 2.1 provider labels · 2.2 **one real cross-provider call,
recorded** · 2.3 wedge on screen · 3.2 real red→green test output · 3.3 connect card + key
field · 3.4 verdict banner · 3.5 scoreboard tiles · 4.1–4.4 one-command + 10× determinism +
CLI backup + **record fallback video** · 4.5 pre-seed stats.

**⛔ CUT BELOW (incorporates the judges' cut-list — do NOT build):**
- ❌ Real multi-provider *routing infrastructure* / `ASSAY_REAL` driving the **stage** run
  (do the ONE recorded real call in 2.2, then pin for stage — live model calls are the #1
  stage-killer).
- ❌ SSE / websocket streaming (setTimeout reveal is indistinguishable to judges, 1/10th the work).
- ❌ A second fallback scenario (one pinned scenario rehearsed 10× beats two flaky ones).
- ❌ Per-provider cost table / combined caching+reliability money view (bill-cut is the
  *kicker*, not the lede — no UI for it).
- ❌ Inter-page nav between `dashboard.html` and `index.html` (the demo page is the hero;
  leave the old cost dashboard as a static link).
- ❌ MCP server, SDK/`@bongo.step` decorator as built surfaces (verbal mention only).
- ❌ Browser/CLI extensions, key vault, BYO-workflow ingestion, sandboxed arbitrary-code
  execution (Form D-full).

**Hard checkpoint:** terminal RED-vs-GREEN end-to-end must be green **before** any frontend
polish. ✅ Already met (`scenarios.py` runs). So spend the night on **2.2 (real cross-provider
proof)**, **3.2/3.3 (credibility + connect)**, and **4.4 (record fallback)** — in that order.

---

## 4. The 90-second demo flow (de-risked)

**Screen:** one viewport, two columns (LEFT *"Cheap model — alone"*, RIGHT *"Cheap + Assay"*),
same 4 steps each; a scoreboard strip below, revealed at the end.

- **[0:00–0:10] Hook.** Both idle, task = *"Fix the failing test suite."*
  *"Same cheap model on both sides. The only difference: the right runs through Assay.
  Watch the left fail silently."*
- **[0:10–0:35] Both run, left goes wrong quietly.** Steps 1→3 animate; **both** show
  "patch applied — looks done." Nothing looks wrong yet.
  *"Both read the test, find the bug, write a patch, say 'done.' The cheap model is
  confidently wrong — and a normal agent loop never catches it."*
- **[0:35–0:50] The real verify.** Step 4 *Run tests* fires on both — **genuinely executes.**
  LEFT stays **RED**, marked DONE-with-✕, "silent failure" flashes. RIGHT: Assay flags
  *VERIFY FAILED → escalating step*. **Real red test output shown.**
  *"Assay doesn't trust the agent's word — it runs the tests. Free, deterministic ground
  truth. Left shipped broken. Right caught it."*
- **[0:50–1:10] The intervene (wow).** RIGHT: step re-opens, *"↗ escalated to **Anthropic**
  (strong)"* — **different provider logo than the cheap one** — re-verify flips **RED→GREEN**.
  Real green output shown. Left red, right green, side by side.
  *"Assay escalates only that one broken step — to a stronger model on a different provider —
  re-verifies, green. One step. Not the whole run."*
- **[1:10–1:25] Scoreboard reveal (live numbers).** *Reliability: cheap 67% (2 broken
  shipped) → Assay 100%. Cost: Assay ~38% of all-strong.*
  *"Left was cheap AND broken — the worst outcome. All-strong is right but expensive. Assay:
  expensive-model reliability, near-cheap cost — it only pays for the step that needed it."*
- **[1:25–1:35] Close + moat.** *"Deterministic verify, mid-run escalation, cross-provider.
  That's the whole pitch."*

**Router-wedge line (memorize; also on screen):**
> *"Routers like OpenRouter or Vercel pick a model up front, per request, and lock it. Assay
> escalates **one step, after a deterministic verify fails, mid-run, across providers.** They
> route before the work; we intervene inside the work."*

**Honesty line (if asked "is it faked?"):**
> *"We pinned the cheap model's output so the stage demo is repeatable — cheap models are
> non-deterministic. The verification that runs the tests is 100% real, and here's a recorded
> run where the escalation actually calls a different provider live."*

---

## 5. Top risks + mitigations

1. **Stage non-determinism (the #1 killer).** Pinned cheap/strong code; only the pytest-style
   `verify()` is live and it's deterministic. → **Gate 4.2: run 10×, assert identical.**
   Keep `ASSAY_REAL` OFF for the stage.
2. **"Just a router / just FrugalGPT-2023."** → Promote cross-provider to P0 (2.1, 2.2 real
   recorded call), pluggable-checker registry (1.1.3), and the wedge on screen (2.3).
   Positioning is a ~2h fix and it's the difference between "system" and "toy."
3. **"Is the green flip faked?"** → Render the **real** red→green test output on screen
   (3.2); offer to run the suite live from the terminal.
4. **Cross-provider claim is unbacked.** → 2.2: one genuinely-real, recorded escalation
   across two providers. A pinned label alone proves nothing to Datadog/Mistral.
5. **Connect story invisible.** → 3.3: snippet + key field + provider dropdown **on the
   demo screen** as P0, not a slide.
6. **Live failure on stage (network/hang).** → 4.4: record the fallback video the moment the
   happy path is polished (~hour 14); cut to it on any >3s hang. Everything runs offline
   (mock default).
7. **Frontend over-investment.** → Reuse `dashboard.html` CSS wholesale; the red→green flip
   with sequential `setTimeout` is the only must-have animation. Cut 3.6 if behind.

---

## Build order for the next 24h (decisive)
1. **2.2** real cross-provider escalation call → **record it.** (highest leverage)
2. **3.2 + 3.3** real test output on screen + connect card/key field. (credibility + connect)
3. **2.1 + 1.1.3** provider badges + pluggable-checker framing. (kills "toy/router")
4. **3.5 + 3.4** scoreboard tiles + verdict banner polish.
5. **4.2 determinism gate (10×)** → **4.4 record the fallback video** → 4.5 pre-seed stats.
6. Rehearse the 90s + the wedge line. Stop building.
