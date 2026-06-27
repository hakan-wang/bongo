# PITCH-DECK.md — Verity (YC structure, rubric-mapped)

**Design rule:** every slide is PROOF, not vibes. Lead reliability + the vertical, never cost. Cost is one receipts slide. Name competitors before judges do.

---

## Slide 1 — Title / Hook
- **Verity** wordmark. Tagline: *"Keep your model. We verify it against reality."*
- One line under it: *"The independent reliability layer that catches your AI agent's silently-wrong steps — and fixes only the step that broke."*
- *(Rubric: Pitch Delivery — removes the placeholder-name credibility tax.)*

## Slide 2 — The Problem (Problem Clarity /17)
- A finance agent on a cheap model read a trade ticket and queued a wire with a 10x-wrong notional. **HTTP 200. No error.**
- "Cheap models fail confidently and silently. The wrong number flows into a wire, a trade, a board deck, a downstream model."
- Evidence line: blind LLM self-correction AUROC 0.54–0.65 — models can't reliably catch themselves.

## Slide 3 — Why the obvious fixes fail
- Run frontier-on-every-step → 20x cost to dodge a problem on ~5% of steps.
- Use a router → it *replaces* your model with a guess; you lose control and still can't tell when it's wrong.
- **We are not a router. You keep your model; we verify it.**

## Slide 4 — The Product / How it works (Demo + Agentic Depth)
- Trace each step → **catch against deterministic ground truth** (run the tests / arithmetic / schema — not another AI) → **pinpoint** the broken step → **recover**: retry-cheap-with-guidance → cross-provider escalate (Mistral → Anthropic) → Tripwire kill-switch.
- Honesty boundary: when it can't verify, it flags low-confidence — never auto-passes.
- *(Embed the trace screenshot: red step → escalation badge → green.)*

## Slide 5 — Demo proof (Demo /17)
- Scoreboard: cheap-alone **67%** → Verity **100%**, **~62% cheaper** than frontier-everywhere.
- Escalation counter: "47 cheap / 3 escalated."
- ~15s coding red→green pytest still — "ground truth, not an opinion."
- *(Mirror of the video money-shot; judges who skim the deck after the video see the same artifact.)*

## Slide 6 — Differentiation / Moat (Differentiation /16)
- 4-column matrix: **cross-provider / runtime / per-step correctness / active-fix.** Only Verity has all four checks.
- Name the threats first: Future AGI (Agent Command Center), Portkey (guardrails verify-but-don't-correct), Raindrop (fixes *offline*).
- "Loop is copyable in a month. The cross-provider per-(model × task) reliability data that compounds with traffic is not."
- The structural moat: **no single lab will escalate a failed step to a competitor, or wire a deterministic check into your live task.**

## Slide 7 — Agentic Depth (TRACK /15)
- Multi-step autonomy + **recovers from failure/edge cases** + defensible beyond the base model.
- The 3-rung ladder + the honesty case shown as the proof.
- One line: *"Anthropic's model can't tell you to use Mistral. Only an independent layer does."*

## Slide 8 — Pricing & Business Model (Pricing /17)
- **Meter the thing only we do.** $50/dev/mo platform seat + $0.50 per 1,000 verified steps + per-catch premium ($0.01–0.05 each silent failure caught/intervened). Bring-your-own-key → escalation cost never hits our margin.
- Unit economics: verify path is **deterministic, ~zero token COGS → 80–90% gross margin.** Only escalations cost a strong-model call, paid by the customer's key.
- Worked example: team at 5M steps/mo, 10% silent-fail = 500K catches → ~$12.8K/mo; their all-frontier bill would be ~20x the cheap bill — our fee is a slice of the gap we close.
- Two SKUs: "Pay-as-you-verify" (horizontal code/agent teams) + flat "Reliability SLA" per-pipeline (regulated buyers who want a budget line).
- Savings-share kept only as an optional ROI-framed upsell — never the billed metric (unmeasurable counterfactual).

## Slide 9 — Go-To-Market (GTM /17)
- **Wedge:** Seed–Series A AI product teams (2–20 eng) running multi-step code/data-pipeline agents on cheap models, who own their keys (one-line install) and have been burned by a silent failure.
- **High-stakes beachhead vertical:** regulated data migration / financial data pipelines — "data sameness" is deterministic ground truth; a wrong column-mapping to prod is a compliance incident (the existing LOI's exact pain).
- **Channels:** (1) warm founder network — 15-min "watch it break, watch Verity save it" calls; (2) agent-builder communities (LiteLLM / OpenRouter / LangChain) with the free open-core base_url proxy as PLG top-of-funnel; (3) hackathon/sponsor ecosystem (Mistral, Datadog) — literal ICP.
- **First $10K (concrete):** convert 2 existing LOIs (data-migration prospect + Arjun) to PAID flat-fee pilots ($500–$1.5K/mo, 4–6 wks, named catch-rate success metric) → cash in days; add 8–12 pilots via the 3 channels. 10–12 × ~$1K ≈ $10–12K, converting to seat + per-verified-step once value shows in their own logs.

## Slide 10 — Traction
- 2 LOIs / design partners (data-migration prospect + Arjun); pilots structured as paid.
- Open-core proxy public on GitHub — self-serve install path live.
- State plainly as commitments, not revenue.

## Slide 11 — Expansion (one line only)
- Same engine, regulated verticals next: healthcare/legal where a deterministic check exists. *Named as expansion, not demoed* (sharp judges distrust a thin medical demo).

## Slide 12 — Ask / Close
- Restate the line: *"Keep your model. We verify it against reality."*
- The ask. Contact + repo.

---

### Rubric coverage map
| Slide | Rubric criterion |
|---|---|
| 2 | Problem Clarity /17 |
| 4,5 | Demo Quality /17 |
| 8 | Pricing & Business /17 |
| 9 | Go-To-Market /17 |
| 6 | Differentiation /16 |
| 1,12 | Pitch Delivery /16 |
| 7 | Agentic Depth /15 (track) |
