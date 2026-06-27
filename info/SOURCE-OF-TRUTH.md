# Plumbline — Source of Truth (canonical)

> **This is the single canonical doc. If anything elsewhere conflicts with this, this wins.**
> Primary source = **Håkan** (founder, most current context). Older docs that describe a
> different/earlier idea are superseded — see "Document status" at the bottom.
> Working name "Plumbline" is a placeholder; we'll pick a real name later.
> _Living doc — updated as Håkan adds clarity. Last merged from: Håkan's direction +
> Michelle's build + team docs + ongoing research._

---

## 1. One line

**Run the cheap model. Plumbline makes it reliable, and cuts your bill.**

## 2. The core insight

Today developers pay for the expensive model (e.g. Gemini 3.5 Pro) because they can't
trust the cheap one (e.g. Gemini Flash). The cheap model is 10–50× cheaper but makes
more mistakes — and worse, **when it makes a mistake, nobody knows** (it fails silently:
a confident, well-formatted, wrong answer; nothing crashes).

Plumbline sits between an app and the LLM API, **watches every step** of a multi-step agent,
**catches** the cheap model's bad steps, and **corrects** them. Result: a cheap model
performs like an expensive one. You stop overpaying for reliability you can get another way.

## 3. What Plumbline is

A drop-in layer — **one line: change the `base_url`, keep your own API key.** It is:

1. **Vendor-independent / cross-model.** Works across Gemini, OpenAI, Anthropic, and
   open/Chinese models. *This is also the answer to "why won't a big LLM company build it":
   a model maker only ever improves its OWN model — it will never tell you "use the
   competitor's cheaper model." Plumbline sits above all of them.* (A QRT advisor confirmed
   this is exactly why he'd use it.)
2. **Runtime, in the loop.** It watches and fixes **while the agent runs** — not just a
   dashboard after the fact. That live catch-and-fix is the magic.
3. **Multi-agent / multi-API.** It can watch many agents and many APIs at once.

## 4. Main feature — the reliability loop (watch → verify → correct → learn)

For each step of a multi-step workflow Plumbline:
- **Traces** the step (input, output, tool calls, tokens, cost, latency).
- **Verifies** it — cheaply detects whether the step went wrong (see §6, the hard core).
- **Intervenes** on a bad step — retry the cheap model with guidance, supply missing
  context, or **escalate that one step** to a stronger model. (Implemented in
  `reliability.py`: cheap → retry cheap → strong-fallback; cost units cheap=1, strong=50.)
- **Learns** — remembers the failure so it's caught faster next time (the growing
  reliability/failure database is the long-term moat).

## 5. Side feature — cost + comparison

Because Plumbline sees every step and its quality, it can:
- Tell you where you're **overpaying** ("you're using Pro where Flash + Plumbline would do").
- **Score reliability across providers** as it gathers data, and recommend a cheaper or
  better model for a given job. (e.g. "Model X is only 20% reliable here — don't use it";
  "Flash is 60% alone but 95% with Plumbline".)
- The team's `proxy.py` already does a cost layer (caching → ~70% bill cut in the demo).

## 6. The hard technical core (this is what makes or breaks Plumbline)

"Watch every step and catch the bad ones" only works if Plumbline can tell a step is wrong
**cheaply, without already knowing the answer.** The bet: **verification is cheaper than
generation.** How Plumbline knows depends on the step type:

- **Verifiable steps (START HERE):** code (run the test), structured output (validate the
  schema), tool calls (did it return valid data), math (recompute), retrieval (does the
  cited source actually exist). Here the check is **deterministic and bulletproof — no AI
  judging AI.** (This deterministic, "check against reality not another AI's opinion"
  principle is a core team insight and is the right thing to lead with.)
- **Fuzzy steps (harder):** "is this the best video clip" has no clean right answer. Even
  here, the *checkable* parts (valid format, timestamps that exist, count/length
  constraints) can be guarded deterministically; pure taste is the frontier — say so honestly.

**Strategy:** lead with verifiable steps and structured/deterministic checks. The team's
open lean — **start the demo on a CODE agent** (right/wrong is auto-checkable = a
bulletproof live demo) — is consistent with this.

## 7. Who needs it (audience)

Any startup or team that put an LLM API inside their product, especially with **multi-step
agent workflows** (analyze → reason → act). They all face the same tradeoff:
cheap-and-unreliable vs expensive-and-safe. **Plumbline removes the tradeoff.** Nobody can
afford to run Opus/Gemini-Pro on their customer-support bot — but a cheaper bot makes
mistakes. Without Plumbline it just fails. With Plumbline: save money AND stay reliable.

## 8. Objections, answered

- **Won't a big LLM company / lab build it?** Only for their own model. Plumbline is
  independent and cross-model. (QRT advisor confirmed.)
- **Does it die when models get perfect?** No. It's about the cost/reliability tradeoff
  and making the cheap option safe — which always matters. Framed as the **proof /
  reliability / trust layer**, it lasts. Receipts: OpenAI is *deprecating* its own Evals
  platform (shutdown Nov 2026) and pointing to third-party tools; Anthropic endorses
  third-party evals and says they get *harder* as models improve; the EU AI Act mandates
  **independent** assessment (~Aug 2026). You can't grade your own homework. (Datadog
  thrives even though AWS ships CloudWatch.)
- **Crowded space?** The eval/observability incumbents (LangSmith, Arize, Datadog,
  Braintrust) and YC cos (Coval, Chronicle, Respan, Arga, Roark, Raindrop, Baserun) mostly
  **measure / test your OWN agent before shipping** (passive). Plumbline is a **runtime layer
  that catches and corrects in production, across models, and cuts cost** — different lane.
  The cost gateways/routers (OpenRouter, Portkey, LiteLLM, Helicone, Cloudflare AI Gateway)
  route/cache/track spend but **don't actively fix the cheap model's mistakes**. (Research
  doc `info/competitors-and-differentiation.md` covers this in detail.)

## 9. Differentiation, in one stage line

> **"Everyone else tells you your agent failed. Plumbline catches it and fixes it — on a
> cheaper model — across every provider, and shows you the cheapest model that still does
> the job."**

## 10. Pitch ammo (data points — analyst/industry estimates, treat as direction)

- AI agents market: ~**$8B (2025) → ~$52B by 2030** (~46% CAGR, MarketsandMarkets).
- Retrieval is the dominant failure point; naive RAG fetches wrong context a large share of
  the time; a majority of RAG *failures* originate at retrieval.
- ~**37% gap** between agent lab-benchmark scores and real-deployment performance.
- A UC Berkeley team built an agent that **scored 100% on top coding benchmarks while
  solving zero tasks** (faked success) — the market just learned it can't trust its own evals.
- (Re-verify fast-changing figures near the event. Full table in `docs/early-writeup.md`.)

## 11. Business model (from GTM.md)

- **Pay-from-savings:** Plumbline takes ~**20% of the AI spend it saves you**. Save you
  nothing → you pay nothing. Easiest yes, instant ROI, no buyer risk.
- **Free / open core** (drop-in proxy, basic caching) drives adoption + pleases OSS judges.
- **Team** (~$40/dev/mo) for dashboards/history/controls; **Enterprise** self-hosted.

## 12. Team & roles

- **Håkan** — GTM / sales / pitch (owns the live pitch; warm outreach; LOIs; the room).
- **Michelle** — demo + pitch + design (demo story, dashboard look, deck, rehearsal).
- **Tech 1** — engine (reliability core, real API integration, recovery).
- **Tech 2** — surface (proxy + dashboard, bulletproof live demo).

## 13. What's built so far

- `proxy.py` — OpenAI-compatible cost proxy + caching (~70% bill cut, mock mode).
- `reliability.py` — real step-runner: deterministic checkers + cheap→retry→strong cascade.
- `reliability_demo.py`, `dashboard.html`, `demo_traffic.py`.

## 14. Open decisions (need Håkan)

1. Lead promise wording: "make cheap models reliable" vs "cut your bill". *Recommended:
   combined — "run cheap, stay reliable," show cost as the proof.*
2. First demo domain: **code agent** (auto-verifiable, bulletproof) vs general. *Team leans
   code; research is checking a more judge-resonant universal example — see §15.*
3. On a bad step: alert / retry / escalate to strong model? *Recommended: retry then escalate.*
4. In-the-loop fix vs after-the-fact dashboard? *Recommended: in-the-loop (the magic).*

## 15. The demo example (in progress)

**Brolly** (Håkan's video-editing agent: analyze → reason about best clips → cut/assemble,
on the Gemini API) is a fine *internal* example but most judges won't know it, and taste is
hard to verify. We're researching the best **universal-yet-judge-resonant** example (code
agent / support-RAG / data-extraction / quant-document-extraction) tied to what the judge
companies actually run — see `info/demo-example-choice.md` (coming) and the judge-API-usage
research. **Decision:** use the example that the whole room understands instantly AND where
a cheap model's failure is cheaply checkable.

## 16. Demo target (36h)

A multi-step agent runs on a CHEAP model, makes a mistake, **Plumbline catches it live and
corrects it**, and the dashboard shows: **same quality as the expensive model, a fraction
of the cost.** Headline: *"Pro-level reliability at Flash-level price."*

---

## Document status (read me)

- ✅ **Canonical / current:** this file, plus `VISION.md`, `PLAN.md`, `GTM.md`,
  `reliability.py`, `proxy.py`.
- 📚 **Background research (current):** the `info/` folder (judges, competitors, technical
  playbook, model landscape, positioning, wow-metric, pitch) — being filled by research.
- ⚠️ **Superseded (kept for the valuable data only):** `docs/early-writeup.md` and
  `docs/hackathon-context.md` describe an **earlier idea** — a standalone "verifier / proof
  layer that catches agents faking success." That deterministic-verification insight now
  lives inside Plumbline as the **VERIFY** step (§6), but Plumbline's headline is **cheap-model
  reliability + cost**, not a standalone fakery-catcher. Use those old docs only for their
  market figures and competitor list.
