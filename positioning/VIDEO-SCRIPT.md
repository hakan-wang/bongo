# VIDEO-SCRIPT.md — Assay demo (≤5 min, wow-first, zero buzzwords)

> ⚠️ **Every number here must equal `python3 demo/scenarios.py` output. Re-run it before recording.**
> Current truth: notional should be **$985,000** (10,000 units × $98.50); the cheap model wires
> **$9,850,000** (10× slip) → an **$8,865,000 over-wire**. Cheap **60%** → Assay **100%**, **74% cheaper**,
> **2 of 5** verifiable steps escalated. Cross-provider = **Mistral → Anthropic**.

**Golden rule:** the first 10 seconds decide whether they keep watching. Cold-open on the wrong
number that moves money. No logo intro, no "we're a team of 4." Cost is receipts, never the headline.

---

### BEAT 0 — Cold open: the silent disaster (0:00–0:12)
- **On-screen:** a finance agent. A cheap model reads a trade ticket (10,000 units @ $98.50),
  computes the notional, and emits `settle_trade(amount=9,850,000, ccy=USD)`. Green **"200 OK — submitted."** Looks clean.
- **VO:** *"This agent just queued a wire on a cheap model. The notional should be nine-hundred-eighty-five thousand. It computed nine-point-eight-five **million** — off by ten-x. Nothing errored."*
- **Cut to:** the true value ($985,000) flashing next to the wrong one. Counter: **"COST OF SHIPPING THIS BUG: $8,865,000."**

### BEAT 1 — Name the trap (0:12–0:40)
- **On-screen:** split — *"Cheap model: silently wrong, no error"* vs *"Frontier on every step: 20× the bill."*
- **VO:** *"Cheap models fail like this — confidently, silently, no exception thrown. The fix everyone reaches for is to run the expensive model on every step. That's twenty times the cost to dodge a problem on a handful of steps. We do neither. You keep your model. We catch it against reality."*
- **On-screen wordmark:** **Assay.**

### BEAT 2 — The catch, live (0:40–2:00)
- **On-screen:** the same trade, now through Assay — a 3-step chain: **extract → compute → wire.**
- **VO:** *"Same agent, same cheap model — but every step is now checked against reality. Not another AI's opinion. We re-run the actual arithmetic."*
- **Action:** the **compute** step glows **RED** — the exact verifier line shows:
  `amount 9,850,000 != units × price = 985,000 (10x the true notional)`. Assay pinpoints *that one step* — **before** step 3 wires it.
- **VO:** *"There. Assay recomputed units-times-price, caught the exact step, and stopped it before the wire."*

### BEAT 3 — Mechanism inoculation: red→green pytest (2:00–2:15)
- **On-screen (~15s cutaway):** real `pytest`-style output on a coding step — failing assertions in red, then green after the fix.
- **VO:** *"This is what 'checked against reality' means — we run the real test. Red turns green. No model grading another model."*

### BEAT 4 — The recovery ladder + why-not-X (2:15–3:30)
- **VO:** *"Now we recover — and we don't just throw money at it."*
- **Rung 1:** *"First we retry the cheap model with the failure reason fed back in."* (trace shows the retry — still wrong currency)
- **Rung 2:** retry still wrong → **escalate only that step, cross-provider, Mistral → Anthropic.** Re-verify → **GREEN.**
  - **On-screen:** *"Anthropic's model can't tell you to use Mistral. Only an independent layer does."*
- **Why-not-X card (4 logos, one disqualifier each):**
  - **Routers (OpenRouter)** — retry only on hard errors, never a wrong-but-200 answer.
  - **Observability (Datadog)** — tells you *after* the fact.
  - **Guardrails (Portkey)** — verify but won't regenerate.
  - **Future AGI** — regenerates the whole request, not the one step; no cross-provider reliability-data moat.
  - **VO:** *"Everyone else routes, watches, or blocks. We catch the wrong step and fix only it, live, across providers."*
- **Rung 3 (honesty case):** a later open-ended step has no ground truth → Assay renders **amber: "Can't deterministically verify — flagged low-confidence. Not auto-passed."**
  - **VO:** *"And when we can't vouch for a step, we say so. We never rubber-stamp."*

### BEAT 5 — Receipts (3:30–4:15)
- **On-screen:** the scoreboard. Cheap-alone **60%**. Assay **100%**. Escalation counter: **"3 stayed cheap, 2 escalated (2 of 5)."** Cost: **74% cheaper than frontier-on-every-step.**
- **VO:** *"Cheap model alone: sixty percent correct — and you'd never know which forty percent was wrong. With Assay: a hundred percent, because reality checked every step. Three steps stayed cheap; we only paid for the strong model on the two that needed it. Seventy-four percent cheaper than running frontier everywhere — but cost was never the point. Correctness was."*

### BEAT 6 — Drop-in + close + ask (4:15–4:55)
- **On-screen:** a real agent. A two-line `base_url` swap. The agent now catches + escalates a failure it used to ship.
- **VO:** *"Two lines. Point your agent at Assay, keep your own model and keys, and it stops shipping silently-wrong steps."*
- **Ask:** *"If you ship agents that move money or data, we want three design partners."* (contact/url on screen)
- **Final frame:** **Assay** wordmark + *"Keep your model — we verify it against reality."*

---

## Timing budget
| Beat | Time | Purpose / rubric |
|---|---|---|
| 0 Cold open | 0:12 | Problem Clarity, gatekeeper hook |
| 1 Trap | 0:28 | Problem Clarity, anti-router |
| 2 Catch (the chain) | 1:20 | Demo + Agentic Depth (per-step, cascade prevented) |
| 3 Pytest | 0:15 | Differentiation (ground truth, not an LLM) |
| 4 Ladder + why-not-X | 1:15 | **Agentic Depth** + **Differentiation** (competitors named) |
| 5 Receipts | 0:45 | Pricing proof, cost-as-receipts |
| 6 Drop-in + ask | 0:40 | GTM/adoption + close on moat+ask |
| **Total** | **~4:55** | under 5:00 |

## Buzzword guard
First 20s contain: *wire, wrong number, off by 10×, caught* — and NOTHING from the blacklist
(no "reliability layer," "observability," "eval," "swarm," "router," "cut your bill"). Watch the
first 20s for jargon before recording.

## Production notes
- The trade scenario is **staged to fire** (cheap LLMs are non-deterministic) — the **verification is real**.
  Capture Beat 3's red→green from `python3 demo/real_proof.py roman_to_int` with both keys set
  (re-run until the cheap model fails so the escalation fires) — that cutaway is the **un-pinned** proof.
- Say the honesty out loud once: *"the trade run is staged to fire; the check that catches it is real and, here, un-pinned."*
