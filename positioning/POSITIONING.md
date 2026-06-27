# POSITIONING.md — Verity

## The decision (locked)
**BLEND, anchored on a high-stakes vertical.** Keep the anti-router *catch-and-recover engine* as the spine. Lead the video with a **finance / money-moving tool-call agent**. Demote swarm to an optional in-demo *mechanism* beat. Demote cost to *closing receipts*. (Unanimous council, confidence 8.)

We are **not** a router. Routers pick a model for you. We keep *your* model and verify it against reality.

## The line (first words of the video, zero jargon)
> **"Your agent's cheap model just confidently produced a wrong number — and nothing errored. We catch it against reality, pinpoint the exact step, and fix only that step."**

One-sentence product: **Verity is the independent reliability layer that catches an AI agent's silently-wrong steps against deterministic ground truth, pinpoints the broken step, and escalates only that step to a stronger model on another provider — so a cheap model runs as reliably as an expensive one, on any provider.**

## Why this line wins (mapped to rubric)
- **Agentic Depth /15** — "catch against reality + per-step pinpoint + cross-provider escalate + recover" maps 1:1 onto the rubric line (multi-step autonomy + recovers-from-failure + defensible-beyond-base-model).
- **Differentiation /16** — anti-router framing + the one thing a single lab *structurally cannot ship*.
- **Problem Clarity /17** — a silent wrong number that moves money is the canonical "cheap/wrong model is catastrophically costly" story.
- **Demo /17** — 100% buildable tonight: swap staged task content into the existing checker registry; reuse the cheap→verify→escalate loop unchanged.

## The vertical (video anchor)
**Finance — a money-moving tool-call agent.** A cheap model reads a financial doc (10-K excerpt / invoice / trade ticket) and emits structured numbers + a `settle_trade(amount, ccy, account)` call. It silently fabricates or mis-sets one value (sign-flipped net_debt, 10x notional, wrong currency). **HTTP 200, no error.** Verity's deterministic check goes red on exactly that step, escalates only it cross-provider (Mistral → Anthropic), green.

**Mechanism inoculation shot (~15s coding cutaway):** real failing `pytest` turning green after escalation — the irrefutable "ground truth, not another AI's opinion" proof. This pre-empts the #1 judge objection ("is the checker just another LLM?").

**Fallbacks (never fall to swarm-as-headline):**
1. If finance staging reads as over-claimed → coding red→green standalone (most bulletproof artifact we own).
2. Data-migration ("wrong column to prod = compliance incident", existing LOI) → **deck GTM beachhead**, not video lead.

## The moat (say it on screen at the moment of escalation)
Three things, none of which a single lab will ever ship:
1. **Cross-provider** — Anthropic will never escalate a failed step to Mistral; Mistral will never escalate to Anthropic.
2. **In-the-loop, per-step** — wired into your live multi-step task, not a benchmark.
3. **Deterministic ground-truth verification** — we run reality (the tests / the arithmetic / the schema), not another AI's opinion.

On-screen sentence at the cross-provider hop:
> "Anthropic's model can't tell you to use Mistral. Mistral can't escalate to Anthropic. Only an independent layer does."

**Compounding moat (Q&A):** "The loop is copyable in a month. The cross-provider per-(model × task) reliability data that accumulates with traffic is not."

## Swarm: mechanism, not thesis
Use FrugalGPT cascade + generator-verifier asymmetry + verifier-based best-of-N / PRM as the **proof wall** behind the catch. Optionally show a "several cheap models, reality picks the winner" lane **only if the core ships with hours to spare.** Never the headline, because:
- The 2025 **Self-MoA** paper shows mixing diverse models is often *worse* than sampling one strong model — a sharp judge has a literal kill-shot citation.
- Cost-first re-files us under router/FinOps and dies to "Anthropic already does this" (reasoning-effort levels).
- Parallel fan-out + 4-lane animation is net-new engine on the critical path; the vertical re-skin is zero new engine.

## Objection rebuttals
- **"Isn't this just a router / FrugalGPT?"** — Routers *replace* your model with a guess. We *keep* your model and verify it against reality, escalating only the steps that actually fail. Cascade is our mechanism; verification is our product.
- **"Doesn't this just become the expensive model?"** — No. Live escalation counter: "47 steps stayed cheap, 3 escalated." We retry-cheap-with-guidance *first*, escalate only on repeat failure.
- **"Isn't the checker just another LLM judging an LLM?"** — No. We run the actual unit tests / arithmetic equality / schema validation. Watch the pytest go red then green. (Blind self-correction AUROC 0.54–0.65; deterministic check = 1.0.)
- **"Won't Anthropic just build this?"** — They will never escalate your failed step to a competitor's model, and they verify on benchmarks, not on your live task. The moat is structural, not a feature gap.
- **"What if you can't verify a step?"** — We say so. The honesty-boundary case (open-ended step, no ground truth) is flagged **low-confidence, NOT auto-passed.** Knowing *when* we can vouch is the defensibility.

## DO-NOT-SAY (buzzword blacklist for all assets)
- "reliability layer" / "observability" / "LLMOps" / "eval" in the **first 20 seconds**
- "we proxy across providers" / "we connected two databases"
- "swarm" / "ensemble" / "mixture-of-agents" / "provably beat" (anywhere a non-technical viewer can hear it)
- "cut your AI bill" / "save tokens" as a **headline** (cost is closing receipts only: ~62% cheaper, 67% → 100%)
- "router" (except to say what we are NOT)

## The name
**Verity** (winner). One word, premium, says the moat (deterministic truth-based verification), works as a noun and a verb ("Verity caught it"), scales beyond coding. Domain plan: `getverity.ai` / `tryverity.com`. Fallback **Plumbline** if clearance is crowded — the best metaphor in the set (a physical, deterministic check against true reality via gravity).
