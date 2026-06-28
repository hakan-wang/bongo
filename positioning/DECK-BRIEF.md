# PROMPT — Build the Assay pitch deck (read every line; the positioning is non-negotiable)

You are building the pitch deck for **Assay** for the *Paris Builds* hackathon (Unaite × Y
Combinator), track **Software for Agents**. The deck is scored on a rubric (below). Round-1 was
video-only; if we reach the top-5, this deck backs a live YC-jury pitch. **The judges are sharp
agent/infra builders from YC, Datadog, Mistral, QRT — they will catch any overclaim or any
"already-solved" example instantly.**

We ran deep, adversarial market research (8 use-case researchers + a skeptic). The findings are
below. **Most "obvious" use-cases for Assay are ALREADY SOLVED — using them on a slide loses the
deck.** Your single most important job: **build the deck only on the ONE positioning that is
genuinely real and under-served, with only verified real-world examples.**

---

## ⛔ NON-NEGOTIABLE RULES
1. **Every real-world example on a slide MUST be a genuine, verified problem from the "✅ USE"
   list below. NEVER invent an example, and NEVER use anything from the "❌ FORBIDDEN" list.**
2. **Lead with the VALUE OF THE CATCH (a silent wrong number never reaching a decision/payment),
   NOT with cost savings.** Cost is the *weakest* leg of our story — use the cost number only as
   closing "receipts," never as the headline.
3. **Name the narrowness out loud.** A sharp judge rewards "we solve ONE unowned problem" and
   punishes "Assay makes all agents reliable." Concede scope early; it buys credibility.
4. **No buzzwords** ("observability", "eval", "reliability layer", "swarm", "router") in the
   first slides — say it in plain words a non-technical person feels.

---

## WHAT ASSAY IS (honest, use this framing)
Assay is an **in-the-loop reliability layer for AI agents**. You run a (usually cheaper) model;
Assay checks each step against **deterministic ground truth** — it **re-runs the test, recomputes
the number (e.g. units × price), validates the value against the source-of-truth data** — *not
another AI's opinion*. It catches the silently-wrong step, and fixes only that step (retry the
cheap model with the failure reason → escalate just that step to a stronger model on a different
provider → kill-switch a runaway loop). When a step has **no ground truth**, it **flags it
low-confidence — it never fakes a pass.**
Tagline: **"Keep your model — Assay it."** / *"We verify each step against reality, not another AI."*

---

## ✅ THE LOCKED POSITIONING (the ONLY one — build the whole deck on this)

**Who it's for (the buyer):** Engineering teams building their **OWN agents on raw LLMs** (NOT
buying Sierra / Lorikeet / Rossum / Tipalti) that run **multi-step financial or data-integrity
workflows** — billing/invoicing reconciliation, payments & refund eligibility, **credit/risk
scoring**, analytics-and-reporting pipelines.

**The exact problem we own (one unowned gap):** the **silently-wrong INTERMEDIATE step** inside a
multi-call agent. A 5–10-call agent that is ~97% reliable per step is only **~60–85% reliable end
to end**, and a bad *intermediate* number is **invisible to any final-output check** — it flows
downstream and poisons everything. Assay verifies **each intermediate step** against deterministic
ground truth, mid-run.

**Why this is genuinely real + acute + under-served (cite these):**
- The failure is **documented industry consensus, not theatre:** a 2026 multi-model benchmark
  found 4 of 6 leading models **fabricate financial figures confidently, in authoritative format**;
  structured-analysis hallucination rates run **15–52%**.
- **Compounding:** ~97% per-step → **15–40% trajectory failure** across 5–10 calls.
- **Today's tools don't fix it mid-run:** observability (Datadog/Arize) **grades post-hoc**;
  guardrails **use an LLM-judge** (wrong the same way the agent is — correlated error); **structured
  outputs guarantee FORMAT, not VALUE**.
- **Deterministic > LLM-judge is a citable edge:** Cleanlab TLM shows deterministic/independent
  checking is **~25% better precision/recall than LLM-as-judge**.
- **Why-now / regulation:** high-risk financial-AI rules tightening in 2026 (e.g. Colorado AI Act
  effective **June 30, 2026**) raise the cost of a silent wrong financial decision.

---

## ❌ FORBIDDEN POSITIONINGS (verified ALREADY-SOLVED or poor fit — using these LOSES the deck)
Do **not** build a slide or example around any of these. If a judge raises them, our answer is
"that's already gated/solved — we don't compete there." Reasons included so you don't slip:
- **Invoice / AP extraction** — deterministic math validation, 3-way match, duplicate detection,
  confidence-gated human review are **table-stakes inside Rossum/Tipalti/Stampli/Dynamics/NetSuite**;
  ~40%+ non-PO invoices have no ground truth anyway. **Do NOT claim to out-validate Rossum.**
- **ETL / data-migration column-merge** — deterministic source-vs-target reconciliation
  (**dbt tests, Great Expectations, Datafold**) is the most mature, commoditized safeguard in data
  engineering. (NOTE: our LOI with *Julio* is data-migration — keep him as honest *traction*, but do
  **not** position data-migration as the unsolved frontier.)
- **Coding agents in CI** — the test suite **is** the ground truth: free, already run by CI,
  gameable, and insufficient ~59% of the time (OpenAI audit). **Least differentiated; never lead here.**
- **KYC / identity verification** — MRZ ICAO checksums have shipped the "recompute the field"
  check **for decades** inside Jumio/Onfido/Sumsub/Veriff; the cost is human review, not tokens.
- **Robotics / physical-AI** — no recomputable ground truth, irreversible actions, latency budget
  too tight; **CBF/formal-methods guardrails already beat an LLM-step-checker.** Not our market.
- **"We prevent the catastrophic wire" (treasury/settlement)** — the wire is **already gated** by
  TMS deterministic math + mandated four-eyes; high-stakes steps don't run cheap models. **Sharp
  judges will note the wire is already gated — do NOT make this claim.**
- **"Assay makes ALL agents reliable"** — dies instantly. The deterministic auto-fix covers only a
  *minority* of steps; on the rest we flag (a commodity). Always scope it.

---

## ✅ THE EXAMPLE TO LEAD WITH (verified real — use this as the hero)
**A multi-step credit-risk / billing-decision agent.** It returns perfectly valid JSON —
`risk_score: 72, confidence: 0.94, recommendation: "approve"` — **100% schema-compliant** — while
the applicant has three recent defaults and the **true score is ~30**. Every monitor sees
**200 OK**. Structured outputs pass (they guarantee format, not value). An LLM-judge guardrail can be
wrong the same way the agent was. **Assay recomputes the score against the source-of-truth records,
deterministically, catches the silent miss at that step, and fixes only it before it flows into the
decision.**
**How teams "solve" this badly today (put this on the slide):** (1) trust structured outputs
(format-only — misses it); (2) bolt on an LLM-judge (correlated failure); (3) catch it days later in
reconciliation / a customer dispute / an audit; (4) hand-roll a one-off assert that guards a single
step but not the intermediate steps of a multi-call agent.

**Runner-up real example (you may use as a second case):** **support/ops agents that take actions**
(refunds, credits, account changes) for teams on **home-grown** stacks. Lead with the CATCH
(recompute the refund amount/eligibility against the billing system **before** the write), not the
cross-provider auto-fix (a money-moving step wants a human escalation target). Weaker than the
finance/risk lead because incumbents (Lorikeet/Fini/Sierra) already productize deterministic policy.

---

## HOW TO FRAME THE DEMO (already built + submitted — don't rebuild it, reframe the story)
The demo shows `settle_trade`: **extract → compute → wire**, and Assay catches the 10×-slipped
notional **at the compute step, before the wire.** **Reframe the story** from *"we save the
catastrophic wire"* (already gated — forbidden) → **"we catch the silently-wrong INTERMEDIATE step
in a home-grown multi-call agent that no final check sees."** Same demo, correct + defensible story.
The pytest red→green cutaway = "checked against reality, not another model."

---

## THE 3 KILLER OBJECTIONS + ANSWERS (make this an "Objections" slide / Q&A appendix)
1. **"Provider structured outputs already do this."** → *They guarantee the FORMAT, not the VALUE.
   The model emits risk_score 72 in flawless JSON while the truth is 30 — that's 200 OK to every
   monitor. Format validity is exactly what makes the error silent.*
2. **"Isn't this a 5-line assert / an LLM-judge guardrail?"** → *One assert guards one step. The
   unsolved problem is the bad INTERMEDIATE step in a 5–10-call agent that no final check sees. And
   an LLM judge fails the same way the agent does — we use independent deterministic ground truth,
   ~25% more accurate than LLM-as-judge (Cleanlab TLM).*
3. **"What % of steps can you actually recompute?"** (volunteer this before they ask) → *A minority
   — the numeric / data-integrity ones — and we lead there. Where there's no ground truth we flag
   low-confidence; we never fake a pass.*

---

## DEMO NUMBERS (proof / receipts only — NOT the headline; verify with `python3 demo/scenarios.py`)
- Cheap model alone **60%** reliable → **Cheap + Assay 100%** (on the verifiable steps).
- Assay escalated only **2 of 5** steps; **74% cheaper** than running the strong model on everything.
- The caught bug: cheap model wired **$9,850,000** vs the true **$985,000** = an **$8,865,000**
  over-wire, caught by recomputing units × price.
Frame these as "we caught a wrong number that would have shipped," not "we save money."

---

## DIFFERENTIATION / MOAT (one slide)
- **4-axis matrix — only Assay has all four:** *cross-provider · runtime/in-loop · per-step
  correctness · active fix.* Routers (OpenRouter) retry only on hard errors; observability
  (Datadog) tells you after; guardrails (Portkey) verify but don't regenerate; eval (Raindrop,
  Galileo) fix offline.
- **The honest moat:** deterministic-not-judge (independent ground truth) + per-step + cross-provider.
- **Own the real competitor:** it is **NOT a model lab** — it's guardrail/eval incumbents
  (Arthur, NVIDIA NeMo, Braintrust, Phoenix) who own the runtime position and could bolt on a
  deterministic grader. So the real battle is **willingness-to-pay for a separate layer + speed to
  distribution**, not technical novelty. (Show you know this — it reads as maturity.)

---

## BUSINESS MODEL + PRICING (one slide)
- Meter the work we do, not the failures we find (so we're never incentivized to over-flag):
  **~$50/dev/mo seat + ~$0.50 per 1,000 verified steps**, per-catch as an optional ROI line.
- **~80–85% gross margin:** the verify path is deterministic (≈zero token cost); only escalations
  cost a strong-model call, **paid by the customer's own key** (bring-your-own-key).

## GO-TO-MARKET + FIRST-$10K (one slide)
- **Wedge:** seed–Series-A teams running **home-grown** multi-call agents on financial/data steps,
  who own their keys (one-line install) and have already been burned by a silent intermediate error.
- **Channels:** (1) warm founder network — 15-min "watch it catch a wrong number live" calls;
  (2) agent-builder communities (LiteLLM / LangChain / OpenRouter) with a free open-core proxy as
  top-of-funnel; (3) the hackathon/sponsor ecosystem.
- **First $10K:** convert the 2 existing LOIs to paid pilots ($500–1.5K/mo) → cash in days; add
  ~10 pilots from the channels → ~$10K MRR within ~6 weeks (~11 pilots × ~$900).

## TRACTION (one slide — keep it HONEST, commitments not revenue)
- **2 design partners:** **Julio** (verbal LOI, data-integrity / on-prem→BigQuery) + **Arjun** (LOI
  out for signature). Say "signed LOI / verbal commit," never "revenue." Do NOT quote any
  unverified "$50M-backed" or "$10k MRR" figure unless confirmed.

---

## SLIDE STRUCTURE (YC-style, rubric-mapped — 11 slides)
1. **Title** — Assay wordmark + *"Keep your model — Assay it."*
2. **Problem** (Problem Clarity /17) — the credit-risk valid-JSON-but-wrong-value example; "200 OK,
   nothing errored." Evidence: 4/6 models fabricate financial figures; 15–52% hallucination.
3. **Why the obvious fixes fail** — structured outputs (format not value) · LLM-judge (correlated) ·
   observability (post-hoc) · a 5-line assert (one step, not the intermediate one).
4. **The product / how it works** (Demo + Agentic Depth /15) — recompute against reality → recovery
   ladder (retry → cross-provider escalate → kill-switch) → honest low-confidence flag. Embed the
   demo trace screenshot (red → escalate → green) + the pytest cutaway.
5. **Demo proof** (Demo /17) — 60% → 100%, 74% cheaper, "caught a $8.86M over-wire" — as receipts.
6. **Differentiation / moat** (Differentiation /16) — the 4-axis matrix + deterministic-not-judge +
   "the real competitor is guardrail/eval, the battle is willingness-to-pay."
7. **Who it's for / market** — home-grown multi-call financial/data-integrity agent teams; TAM
   expansion path: "more workflows gain computable ground truth as agents replace fixed pipelines."
8. **Business model + unit economics** (Pricing /17).
9. **Go-to-market + first-$10K** (GTM /17).
10. **Traction** — the 2 honest LOIs.
11. **Ask / close** — restate the line; "if you ship agents that move money or decisions, we want
    three design partners." Contact + repo.
*(Appendix: the 3 objections + answers above.)*

---

## TONE / WHY-WE-WIN
Confident, plain, honest. The winning posture is **"we found the ONE unowned problem and we're
brutally clear about where we don't play."** A deck that names its narrowness, backs every claim
with the evidence above, and answers "structured outputs already do this" head-on will out-score a
broader, vaguer, more impressive-sounding deck — because the rubric says **"judge by proof."**

> Build the deck now using ONLY the ✅ positioning and examples above. If you're about to put a
> use-case on a slide that isn't in the ✅ list, STOP — it's probably on the ❌ already-solved list.
