# Assay

**Catch the silently-wrong step — against reality, not another AI's opinion.**

**▶ Live demo (no install, runs in your browser): https://assay-demo.vercel.app**

Your agent's cheap model can confidently produce a wrong number — a 10× notional, a flipped
sign, the wrong currency — and **nothing errors**. It returns HTTP 200 and the bad value flows
straight into a wire, a trade, a database. Assay sits in your agent's loop, **checks every
step against reality** (it runs the test; it does the arithmetic), **catches the silently-wrong
step**, pinpoints it, and **fixes only that step** with a recovery ladder:

1. **Retry** the cheap model with the failure reason (cheapest fix)
2. **Escalate** only that step to a stronger model **on a different provider**
3. **Kill-switch** a runaway/looping step before it burns budget
4. When a step has **no ground truth**, Assay is honest — it **flags it low-confidence**, it does not fake a green.

You keep your model. You keep your price. You stop shipping wrong answers.

> **Not a router.** Routers (OpenRouter, etc.) pick a model *for* you and lock it. Assay keeps
> the model **you** chose and verifies it, per step, in the loop. The moat: **deterministic
> ground-truth verification + per-step pinpoint + cross-provider escalation** — the one thing a
> single model lab structurally won't ship (Anthropic will never escalate your failed step to Mistral).

## Why not X?

|  | cross-provider | runtime / in-loop | per-step correctness | active fix |
|---|:---:|:---:|:---:|:---:|
| Routers — OpenRouter, Vercel AI Gateway | ✓ | ✕ | ✕ | ✕ — pick a model up front; retry only on hard errors, never a wrong-but-200 answer |
| Observability — Datadog, Arize | ✓ | tells you *after* | ✓ | ✕ — reports the failure, doesn't fix it |
| Guardrails — Portkey | ✕ | ✓ | ✓ | ✕ — verifies but won't regenerate |
| Eval — Raindrop, Galileo | ✓ | offline | ✓ | ✕ — fixes offline / canned override |
| **Assay** | **✓** | **✓** | **✓** | **✓ — catches the wrong step and fixes only it, live, across providers** |

The loop is copyable in a month; the **cross-provider per-(model × task) reliability data that compounds with traffic** is not.

**Track:** Software for Agents · **Paris Builds** (Unaite × Y Combinator).

---

## Run it (30 seconds, no keys, offline)

Requires only Python 3 (standard library — no `pip install`).

```bash
python3 demo/server.py
# open http://localhost:8200  and click "Run the agent"
```

A cheap agent runs 7 steps. The **left** (no safety net) silently wires the wrong amount and
ships broken work. The **right** (same cheap model + Assay) catches the wrong number against
the trade's real arithmetic, walks the recovery ladder, and ends correct. Then the scoreboard:

| | reliability | cost | result |
|---|---|---|---|
| Cheap model alone | **60%** | cheapest | shipped 2 broken (incl. a wrong wire) |
| **Cheap + Assay** | **100%** | **74% cheaper than the big model** | 0 broken |
| Expensive model alone | 100% | most expensive | right but overkill |

Assay paid the frontier premium on **only 2 of 5** steps. Print the numbers yourself:
```bash
python3 demo/scenarios.py
```

## How it works

- **`demo/scenarios.py`** — the engine. Real deterministic checkers (`run-tests` executes code +
  unit tests; `finance` **recomputes** the notional from the source figures, `units × price`; `json-schema`), the
  catch → recovery-ladder loop, the kill-switch, the honest low-confidence flag, and the scoreboard.
  Model outputs are **pinned** so the demo is reproducible; **the verification is real** (we say so out loud).
- **`demo/server.py` + `demo/index.html`** — the dashboard you see (vanilla HTML/CSS/JS, no deps).
- **`demo/gateway.py`** — the wired *"point your `base_url` at Assay"* path: an OpenAI-compatible
  endpoint that verifies each step and escalates failures cross-provider. Mock by default; set
  `ASSAY_REAL=1` + keys for real calls.
- **`demo/real_proof.py`** — one genuinely-real Mistral→Anthropic escalation (needs keys; `--mock` to dry-run).

## Connect your own agent (one line, keep your key)
```python
client = OpenAI(base_url="http://localhost:8129/v1", api_key=YOUR_KEY)  # the only change
```
See **[`QUICKSTART.md`](QUICKSTART.md)**.

## Repo map
- **[`positioning/`](positioning/)** — `POSITIONING.md`, the **`VIDEO-SCRIPT.md`** (≤5 min), `PITCH-DECK.md`.
- `reliability.py`, `proxy.py` — the original reliability loop + cost/caching proxy.

## Honest status
The on-stage demo's model outputs are **pinned** (deterministic → it always fires); the
**verification is real**. `demo/real_proof.py` is the un-pinned, genuinely-real cross-provider
proof. Pointing Assay at an arbitrary production workflow end-to-end is the next milestone.

## License
MIT — see [LICENSE](LICENSE).
