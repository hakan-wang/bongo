# Assay — The Model Landscape Cheat Sheet (mid-2026)

> **What this doc is for.** Assay's whole pitch is "run the *cheap* model, Assay makes it
> reliable." This page is the receipts behind that sentence: **which models are cheap,
> which are expensive, how big the price gap actually is, and which cheap/open models are
> already "almost as good"** — i.e. the best candidates to run as Assay's default
> ("backstop") model in a demo.
>
> Read this alongside [`SOURCE-OF-TRUTH.md`](./SOURCE-OF-TRUTH.md) (the canonical idea) and
> [`reliability.py`](../reliability.py) (where the cheap→strong cascade actually lives).
>
> ⚠️ **VERIFY NEAR EVENT.** Model names and prices churned *monthly* in the year leading to
> mid-2026 (Opus went 4.5 → 4.6 → 4.7 → 4.8; Gemini 2.5 → 3 → 3.1 → 3.5; GPT-5 → 5.4 → 5.5;
> DeepSeek V3 → V4). **Treat every number below as a snapshot to re-check the morning of the
> pitch, not a constant.** The *shape* of the argument (a ~30–100× price gap, cheap models
> within ~5–10 points of frontier) is stable; the exact suffixes and cents are not. In Assay
> itself, the model list should be **config, not code.**

---

## 1. The one thing to remember

There are **three tiers** of model, and the gap between the cheapest and the most expensive
is roughly **30× to 100× on price** — while on many real tasks the cheap model is only
**~5–10 quality points behind** the frontier.

**That gap is the entire business.** Assay's job: run in the cheap tier, catch the cheap
model's mistakes, and escalate *only the bad step* to the expensive tier. The cost story in
[`reliability.py`](../reliability.py) bakes this in as `COST = {"cheap": 1, "strong": 50}` —
a deliberately conservative ~50× spread that matches the real market below.

---

## 2. The three tiers (mid-2026 snapshot — *verify near event*)

Prices are **USD per 1 million tokens, input / output**. "Intelligence" is the rough
position on the Artificial Analysis Intelligence Index (a blended benchmark score, ~0–65
scale); treat as directional, not gospel.

### Tier A — Frontier (expensive, what people *over*-pay for)

| Model | Price in / out (per 1M tok) | Intelligence (approx) |
|---|---|---|
| Claude Opus 4.8 | $5 / $25 | ~61 (top) |
| GPT-5.5 | $5 / $30 | ~60 |
| Gemini 3.1 Pro | $2 / $12 | ~57 |
| Grok 4.3 | ~$3 / ~$15 | ~53 |

### Tier B — Mid (the "safe default" many teams reach for)

| Model | Price in / out (per 1M tok) | Notes |
|---|---|---|
| GPT-5.4 | $2.50 / $15 | workhorse |
| Claude Sonnet 4.6 | $3 / $15 | workhorse |
| Gemini 3.5 Flash | $1.50 / $9 | fast |

### Tier C — Cheap closed (Assay's home turf)

| Model | Price in / out (per 1M tok) | Notes |
|---|---|---|
| Claude Haiku 4.5 | $1 / $5 | cheap Anthropic |
| GPT-5.4-mini | $0.75 / $4.50 | |
| GPT-5.4-nano | $0.20 / $1.25 | ~25× cheaper than GPT-5.5 |
| Gemini 3.1 Flash-Lite | $0.25 / $1.50 | ~8× cheaper than 3.1 Pro on input |

### Tier D — Cheap / open weight (best backstop candidates — see §4)

| Model | Price in / out (per 1M tok) | Notes |
|---|---|---|
| DeepSeek V4-Flash | $0.14 / $0.28 | rock-bottom; ~Sonnet-level intelligence |
| DeepSeek V4-Pro | $0.44 / $0.87 (first-party) | list price elsewhere ~$1.74 / $3.48 |
| Mistral Large 3 | $0.50 / $1.50 | 675B sparse MoE, **Apache 2.0**, 256K ctx |
| Mistral Medium 3.5 | $1.50 / $7.50 | open weights (Modified-MIT) |
| GLM-5.2 | ~$ low (open weight) | strongest *open-weight* on the index (~51) |
| Kimi K2.6 / Qwen 3.5–3.6 | ~$ low | strong tool-calling; Qwen runs on a single GPU |

> **Source quality:** Anthropic / Google / OpenAI / DeepSeek prices come from primary vendor
> docs and are high-confidence (at the time gathered). Intelligence scores and open-weight
> specs (GLM-5.2, Kimi, Qwen sizes) come from aggregators and wobble a few points
> source-to-source. ⚠️ **Verify near event.**

---

## 3. The price ratios that go on a slide

These are the lines that make a judge feel the gap. (Pick one or two — don't drown them.)

- **DeepSeek V4-Flash vs Claude Opus 4.8:** ~**35× cheaper input** ($0.14 vs $5),
  ~**90× cheaper output** ($0.28 vs $25).
- **Gemini 3.1 Flash-Lite vs Gemini 3.1 Pro:** ~**8× cheaper input** ($0.25 vs $2),
  ~**12× cheaper** vs the older 2.5 Pro.
- **GPT-5.4-nano vs GPT-5.5:** ~**25× cheaper in**, ~**24× cheaper out**.
- **The cascade math (matches `reliability.py`):** if Assay keeps ~90% of steps on the cheap
  model and escalates ~10% to the strong one, you pay frontier prices on a *sliver* of the
  workload, not all of it. That is the "Pro-level reliability at Flash-level price"
  headline in `SOURCE-OF-TRUTH.md` §16.

> **Honesty note for the room:** quote **cost-per-completed-task**, not raw per-token price.
> Anthropic's newer tokenizer (Opus 4.7+) can emit up to ~35% more tokens for the same text,
> so a naive $/token comparison can mislead. Assay's cost dashboard should normalize on
> *task*, not tokens — this is also a feature, not just a caveat.

---

## 4. Which cheap/open models are "almost as good" (best backstop candidates)

These are the models worth running as Assay's **default generator** in a demo — cheap, but
close enough to frontier that Assay only has to catch a small tail of mistakes.

| Candidate | Why it's a strong backstop | Watch-outs |
|---|---|---|
| **DeepSeek V4-Flash** | ~Sonnet-4.6-level intelligence (~47 on the index) at **$0.14/$0.28**. The single most dramatic price/quality story. | Hosted; verify first-party vs promo pricing — V4-Pro's $0.44/$0.87 may revert to ~$1.74/$3.48. |
| **Gemini 3.1 Flash-Lite** | Same family as the Pro most teams already use → trivial swap; ~8–12× cheaper. Great for the "you're paying Pro for Flash work" demo. | Closed; no logprob/hidden-state access for fancy verifiers (use deterministic checks). |
| **GPT-5.4-mini / nano** | Trail frontier by only ~3–5 points on coding/GPQA; nano is ~25× cheaper. | nano degrades on the hardest reasoning — exactly the tail Assay catches. |
| **Mistral Large 3** | **Apache 2.0**, self-hostable, 256K context, $0.50/$1.50. Pleases the OSS judges and matters for the EU/sovereignty angle. | Slightly behind the very top on the index. |
| **GLM-5.2 / Qwen 3.5–3.6** | Best *open-weight* intelligence (GLM ~51); strong tool-calling; Qwen fits a single GPU. | Specs vary by source; "random Chinese model" reliability is exactly what Assay's per-model reliability score is for. |

**Rule of thumb for the demo:** pick a backstop where the failure is *cheaply checkable*
(code, structured output, tool calls) — see `SOURCE-OF-TRUTH.md` §6. **DeepSeek V4-Flash**
(most dramatic price gap) or **Gemini 3.1 Flash-Lite** (cleanest swap from a Pro most people
run) are the two best demo picks.

---

## 5. Why this *strengthens* Assay (the cross-provider moat)

No single lab spans this whole table. Anthropic will never tell you "use DeepSeek for this
step"; Google won't route you to GPT-5.4-nano. **Assay sits above all of them** and
arbitrages step-by-step:

- Run cheap (Flash-Lite / V4-Flash / Haiku) by default.
- Escalate **only the bad step** to whichever strong model (Opus 4.8 / GPT-5.5 / Gemini 3.1
  Pro) is best for it.
- Build a **cross-provider reliability database** — "Model X is 20% reliable on *this* task,
  don't use it; Flash is 60% alone but 95% with Assay" — which is the long-term moat
  (`SOURCE-OF-TRUTH.md` §5, §8).

This is the concrete, pricing-backed version of the "why won't a lab build it" answer.

---

## 6. The bet this table rests on

The reason a cheap model + Assay can match an expensive one is the team's core bet:
**verification is cheaper than generation** (`SOURCE-OF-TRUTH.md` §6). Two anchors worth
knowing:

- **Weaver (Stanford, NeurIPS 2025):** a distilled **400M** verifier retained **98.7%** of
  a full verifier ensemble's accuracy at a **~99.97% compute cut** — i.e. checking a step
  can be almost free compared to generating it.
- **Asymmetric verification in agent loops:** on a search benchmark, *verifying* an answer
  cost ~**4× fewer** tool calls than *generating* it (≈18 vs ≈75).

⚠️ **Bounded, not universal.** This holds for **checkable** steps (code, schema, tool calls,
math, retrieval) and in the **cheap-generator** regime — which is exactly Assay's lane. It
gets weaker on open-ended/"taste" steps and on frontier-model outputs. Demo on the checkable
stuff; say the boundary out loud.

---

## 7. TL;DR for a non-technical teammate

- Cheap models cost **~30–100× less** than the expensive ones.
- On most real work they're only **a little** worse — they just fail **silently** on a small
  fraction of steps.
- Assay runs the cheap one, **catches that small fraction**, and only pays for the expensive
  model **on the steps that need it**.
- That's how you get **"Pro-level reliability at Flash-level price."**
- ⚠️ **All specific model names and prices here go stale fast — re-check them right before
  any pitch.**
