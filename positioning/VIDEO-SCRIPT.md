# VIDEO-SCRIPT.md — Plumbline demo (<=5 min, wow-first, zero buzzwords)

**Golden rule:** The first 10 seconds decide whether they watch the rest. Cold-open on the wrong number that moves money. No logo intro, no "we're a team of 4." Cost is receipts, never the headline. Mechanism shot inoculates the "checker is just an LLM" objection.

---

### BEAT 0 — Cold open: the silent disaster (0:00–0:12)
- **On-screen:** A finance agent UI. A cheap model reads a trade ticket, extracts numbers, emits `settle_trade(amount=$12,400,000, ccy=USD, account=…)`. Green "200 OK — submitted." Everything looks clean and confident.
- **VO:** "This agent just read a trade ticket on a cheap model and queued a wire. Notional should've been one-point-two-four million. It typed twelve-point-four. Off by 10x. Nothing errored."
- **Cut to:** the planted ground-truth value flashing next to the wrong one. Counter: **"COST OF SHIPPING THIS BUG: $11.2M."**

### BEAT 1 — Name the trap (0:12–0:40)
- **On-screen:** split — "Cheap model: silently wrong, no error" vs "Frontier-on-every-step: 20x the bill."
- **VO:** "Cheap models fail like this — confidently, silently, no exception thrown. The fix everyone reaches for is to run the expensive model on every step. That's twenty times the cost to dodge a problem on five percent of steps. We do neither. You keep your model. We catch it against reality."
- **On-screen wordmark:** **Plumbline.**

### BEAT 2 — The catch, live (0:40–2:10)
- **On-screen:** same trade ticket, now through Plumbline. Horizontal agent trace, step by step.
- **VO:** "Same agent, same cheap model — but every step is now checked against ground truth. Not another AI's opinion. The actual arithmetic and schema."
- **Action:** the extraction step glows **RED** — exact failing assertion shown: `notional * price != cash`. The trace pinpoints *that one step*.
- **VO:** "There. Plumbline caught the exact step, before the wire."

### BEAT 3 — Mechanism inoculation: red→green pytest (2:10–2:25)
- **On-screen (~15s cutaway):** real `pytest` output, failing assertions in red, then green after the fix.
- **VO:** "This is what 'checked against reality' means — we run the actual tests. Watch red turn green. No model grading another model."

### BEAT 4 — The recovery ladder (2:25–3:25)
- **VO:** "Now we recover — and we don't just throw money at it."
- **Rung 1:** "First we retry the cheap model with the failure reason fed back in." (trace shows retry)
- **Rung 2:** retry still wrong → **escalate only that step, cross-provider, Mistral → Anthropic.** Re-verify → **GREEN.**
  - **On-screen sentence:** *"Anthropic's model can't tell you to use Mistral. Mistral can't escalate to Anthropic. Only an independent layer does."*
- **Rung 3 (honesty case):** a later open-ended step has no ground truth. Plumbline renders **amber: "Can't deterministically verify — flagged low-confidence. Not auto-passed."**
  - **VO:** "And when we can't vouch for a step, we say so. We never rubber-stamp."

### BEAT 5 — Receipts (3:25–4:15)
- **On-screen:** scoreboard. Cheap-alone **60%** correct. Plumbline **100%**. Escalation counter: **"47 steps stayed cheap, 3 escalated."** Cost: **78% cheaper than frontier-on-every-step.**
- **VO:** "Cheap model alone: sixty-seven percent correct — and you'd never know which third was wrong. With Plumbline: a hundred percent, because reality checked every step. Forty-seven steps stayed cheap; we only paid for the strong model on the three that needed it. Sixty-two percent cheaper than running frontier everywhere — but cost was never the point. Correctness was."

### BEAT 6 — Drop-in + close (4:15–4:55)
- **On-screen:** a real OSS agent. Two-line `base_url` swap. Same agent now catches + escalates a failure it used to ship.
- **VO:** "Two lines. Point your agent at Plumbline, keep your own model and keys, and it stops shipping silently-wrong steps. Plumbline — the independent reliability layer that catches your agent's bad steps against reality, and fixes only the step that broke."
- **Final frame:** Plumbline wordmark + one line: *"Keep your model. We verify it against reality."*

---

## Timing budget
| Beat | Time | Purpose / rubric |
|---|---|---|
| 0 Cold open | 0:12 | Problem Clarity, gatekeeper hook |
| 1 Trap | 0:28 | Problem Clarity, anti-router |
| 2 Catch | 1:30 | Demo, per-step pinpoint |
| 3 Pytest | 0:15 | Differentiation (ground truth, not LLM) |
| 4 Ladder | 1:00 | **Agentic Depth** (recover + edge case) |
| 5 Receipts | 0:50 | Pricing proof, cost-as-receipts |
| 6 Drop-in | 0:40 | GTM/adoption, close |
| **Total** | **~4:55** | under 5:00 |

## Buzzword guard
First 20s contain: wire, wrong number, off by 10x, caught — and NOTHING from the blacklist (no "reliability layer," "observability," "eval," "swarm," "router," "cut your bill"). Reviewer must watch the first 20s muted-of-jargon before recording.
