# Assay — Competitors & Differentiation

> **What this doc is for.** Read this if you're prepping the pitch, fielding a "isn't this
> just X?" question, or deciding what NOT to build. It maps the whole crowded landscape
> around Assay and pins down the *exact* lane Assay owns that nobody else does.
>
> It builds on the canonical docs — `info/SOURCE-OF-TRUTH.md` (§8 objections, §9 the stage
> line) and `docs/internal/VISION.md`. If anything here conflicts with SOURCE-OF-TRUTH, that file wins.
> The reliability loop this doc defends is the one already coded in `reliability.py`
> (cheap → retry cheap → escalate to strong, deterministic checkers, no AI judging AI).

---

## TL;DR (the one thing to remember)

The market is crowded but it splits into three buckets, and **all three are passive** —
they tell you *after the fact*, or they pick/cache/retry *before* generation. None of them
watch a single step's **output**, decide cheaply that it's **wrong**, and **fix that one
step at runtime, across any provider.**

That empty quadrant — **cross-provider + runtime + per-step correctness correction** — is
Assay's lane. It's a real gap (confirmed by independent analysis, see "The verified
verdict" below), not a marketing claim. The honest caveat: it's a *feature* gap being
actively contested, not an empty category — so we win on execution + the cross-provider
data moat, and we say that out loud.

---

## The three buckets everyone else lives in

### Bucket 1 — Eval & observability incumbents (they MEASURE)

These are the big, well-funded players. They capture traces, run evals, score quality,
and gate your CI. They are **passive**: they tell you something failed, they don't fix it
mid-run.

| Company | What they do | Why they're not Assay |
|---|---|---|
| **Arize** (Phoenix, $1B+) | OTel/OpenInference tracing, eval, drift | Observability + offline eval. Not an inline runtime corrector. |
| **Braintrust** (~$800M) | Evals, turns prod failures into CI test cases, quality gates | **Build-time / CI**, not runtime. No mid-request fix. |
| **LangChain / LangSmith** (unicorn) | Tracing + eval for LangChain apps | Measures your own agent. Framework-coupled. |
| **Datadog** (LLM/Agent Observability — their flagship) | Monitoring, traces, dashboards | After-the-fact monitoring. (See "Datadog precedent" below — this is *good* for us.) |
| **Langfuse** (→ ClickHouse) | Open-source LLM observability | Passive tracing. |
| **Galileo** (→ Cisco) | Runtime guardrails, Luna small-model checkers | **Closest on "runtime"** but intervenes on *safety/policy*, and its "override" returns a **fixed canned response** — it does not regenerate or escalate to a stronger model, and it's not a cross-provider proxy. |
| **Patronus** ($50M, Jun 2026) | Eval, TRAIL trace-error benchmark | Eval/benchmark vendor, not an inline corrector. |

**The pattern:** measure, score, alert, gate. The action stops at "here's what went wrong."

### Bucket 2 — Close YC companies (mostly DETECT / TEST)

These are the ones a YC judge will know by name. Most only *measure* (passive eval/
observability or pre-ship testing). Two have edged toward intervention — note them.

- **Raindrop** (W24, ~$15M seed) — **the closest.** Silent-failure alerts, and has moved
  toward "self-healing." **But its fix loop is OFFLINE / build-time**: a coding agent pulls
  the failing trace, makes the fix, writes a regression eval. Their own line: "a fix isn't
  done until you know it worked in production" — i.e. *not* mid-request correction. Raindrop
  centers detect + per-product custom models, **not cross-provider cost arbitrage.**
- **Confident AI / DeepEval** (W25) — CI eval-gating is literally their pitch. Build-time.
- **Baserun** (W26) — eval/observability.
- **Coval, AgentHub, Fulcrum, Lemma** — agent testing / eval / observability.
- Also in the earlier docs: **Chronicle, Respan, Arga, Roark** — dev tools to test your
  OWN agent *before* shipping (see `docs/internal/VISION.md` objection §). Different lane (pre-ship vs
  runtime).

**Why this matters for the pitch:** "we catch silent failures" alone no longer fully
differentiates us — Raindrop says that too. The durable wedge is **cross-provider proxy +
active *in-request* per-step correction + the explicit cost/overpay comparison**, which
none of them center.

### Bucket 3 — Cost gateways & routers (they ROUTE / CACHE / RETRY)

These sit in the request path like Assay does, so they *feel* closest — but they're
passive on correctness. They do four primitives, all of which happen **before** generation
or only on **infra** errors:

1. **Routing / cascading** — pick a cheaper or stronger model *up front* from query features.
2. **Failover / retry** — re-send the **same** request on HTTP errors (429, 5xx, timeouts).
3. **Caching.**
4. **Spend tracking / observability.**

| Product | What it does | The gap |
|---|---|---|
| **OpenRouter** | Unified API, routing, fallback, Auto Router | Failover on **errors**, not on a wrong-but-200 answer. |
| **LiteLLM** (MIT, self-host) | One OpenAI-compatible endpoint over 100+ providers | Provider normalization. *We can build ON it* (see "Build vs reuse"). |
| **Portkey** (open-sourced Apache 2.0) | Gateway **guardrails** — deny / log / fallback / retry / redact | **Closest real overlap, but verify-only.** Portkey's own docs: guardrails do **not** regenerate or self-correct, and act on "the last message," not agent-trajectory correctness. |
| **Helicone** (→ Mintlify, maintenance mode) | Proxy + observability | Acquired Mar 2026, no new features. **Don't build on it.** |
| **Cloudflare AI Gateway** | Hosted/edge routing, caching | Edge-hosted, less interception control. |
| **Routers: RouteLLM, NotDiamond, Martian, Unify** | Pre-generation model selection | Decide **before**, not after. RouterArena (2025) found all routers fall short of oracle precisely because they can't tell when the cheap model suffices — the exact gap Assay's per-step verification fills. |

**FrugalGPT is the closest intellectual ancestor**, not a runtime competitor: generate
cheap → score → escalate if low-confidence. But it's per single Q&A, single-provider in
spirit, and uses a *trained* scorer — not per-step inside a live multi-step agent across
Gemini/OpenAI/Anthropic/open models. **Assay = FrugalGPT's verify-and-escalate idea
generalized to cross-provider agent trajectories with active guidance/context-injection,
not just escalation.**

---

## Assay's lane (the empty quadrant)

Assay is the only layer that is **all four at once**:

1. **Vendor-neutral / cross-provider** — Gemini, OpenAI, Anthropic, open/Chinese models.
2. **Runtime, in the loop** — fixes *while the agent runs*, not a dashboard after.
3. **Per-step correctness** — verifies each step's **output** is *right*, not just safe or
   well-formed (deterministic checks first — code runs, schema validates, tool returns
   valid data, math recomputes, citation exists — exactly the checkers in `reliability.py`).
4. **Active correction** — retry-with-guidance / inject missing context / **escalate just
   the bad step** to a stronger model (the cheap → retry → strong cascade already coded).

Plus the side surface no one else has grounded in correctness: a **cost / overpay
dashboard** ("you're paying Pro for Flash-grade work") and **cross-provider reliability
scores**, built from real traffic — a data moat that compounds with every request.

### The competitor matrix, one glance

| | Cross-provider | Runtime (in-request) | Per-step **correctness** | **Active fix** (regen/escalate) |
|---|:---:|:---:|:---:|:---:|
| Eval/observability (Arize, Braintrust, Datadog) | ~ | ✗ | ~ (offline) | ✗ |
| YC detectors (Raindrop, Confident AI) | ✗ | ~ | ✓ (detect) | offline only |
| Gateways/routers (OpenRouter, LiteLLM, Portkey) | ✓ | ✓ | ✗ | ✗ (errors only) |
| Galileo runtime guardrails | ✗ | ✓ | safety, not correctness | canned response only |
| **Assay** | **✓** | **✓** | **✓** | **✓** |

---

## The verified verdict (use this, it's checked)

An independent adversarial check of the claim *"nobody already does cross-provider active
per-step correction"* returned: **SUPPORTED** — with one honest correction.

- **What holds:** The named competitors demonstrably stop short. Gateways/routers failover
  only on errors; **Portkey verifies but won't correct** (its docs confirm: deny/log/
  fallback/retry/redact — no regenerate); **Galileo blocks/overrides with canned text**,
  not regeneration or escalation; **Raindrop fixes offline**, not mid-request;
  Braintrust/Arize are observability/CI, not inline correctors. The quadrant
  (cross-provider + runtime + per-step correctness correction inside an agent loop) is
  recognized in the literature/architecture references as an **open gap**.
- **The honest correction — drop the absolute "nobody."** One convergent threat exists:
  **Future AGI's "Agent Command Center"** — an OpenAI-compatible cross-provider gateway
  that scores requests inline and *claims* a "quality-floor evaluator at egress" that
  blocks low-quality responses and "regenerates via the next provider." That is materially
  close to Assay. **Caveat:** this correctness-gated regeneration is asserted only in their
  marketing, not confirmed in their primary docs/GitHub — treat it as a real-but-unverified
  threat, not a shipped product.

**So on stage:** lead with the precise wedge, name Future AGI as the closest convergent
threat if pushed, and differentiate on the specifics they don't clearly have — **per-step
trajectory localization, targeted retry-with-guidance / context-injection (not just
whole-request regen or canned override), and the cross-provider reliability-score data
moat.** Expect a Datadog/Mistral/YC judge to surface a Portkey-guardrails or Future-AGI
counter; have the **"verify vs correct"** and **"pre-call routing vs in-loop step
correction"** distinctions ready.

---

## "Won't a lab / gateway just absorb this?" — with receipts

This is the #1 objection. The answers (from SOURCE-OF-TRUTH §8, kept here for the
competitive framing):

- **Cross-provider is the moat a lab will never build.** A model maker only ever improves
  its *own* model — it will never tell you "use the competitor's cheaper model." Assay sits
  *above* all of them. (A QRT advisor confirmed this is exactly why he'd use it.)
- **"You can't grade your own homework."** OpenAI is **deprecating its own Evals platform**
  (shutdown Nov 2026) and pointing users to third-party tools. Anthropic **endorses
  third-party evals** and says they get *harder* as models improve. The EU AI Act direction
  pushes toward **independent** assessment. (Note: the high-risk deadline slipped from
  Aug 2026 to Dec 2027 — use regulation as *tailwind*, not a timing hook.)
- **Datadog precedent.** AWS ships CloudWatch; Datadog is still a giant. An independent
  layer above the platforms wins even when the platforms have a first-party version.
- **Gateways are a feature away, but stop at correctness.** Portkey *could* add active
  correction — but its guardrails are verify-only today, single-request, and have no
  cross-provider reliability scoring. We're table-stakes on integration (one-line
  `base_url`, reuse LiteLLM underneath) so our time and our long-term edge both go into
  **runtime per-step correction + the cross-provider reliability database** — the part
  competitors can't copy by shipping one feature.

---

## Build vs reuse (so we don't reinvent the gateway)

The one-line `base_url` swap + keep-your-own-key + OpenAI-compatible proxy is **table
stakes** — OpenRouter, LiteLLM, and Portkey all do it. **Reuse LiteLLM (MIT) as the
provider-normalization layer underneath** so our hours go into the VERIFY → INTERVENE loop,
not 100 provider adapters. This is consistent with `proxy.py` (our cost/caching layer) and
`reliability.py` (the real step-runner) — the differentiated work is the loop, not the pipe.

---

## The one-sentence differentiation

> **Everyone else tells you your agent failed. Assay catches it and fixes it — on a cheaper
> model — across every provider, and shows you the cheapest model that still does the job.**

(Crisper stage variant: *"Gateways route and retry on errors; observability tells you after
the fact; Assay watches each step's output, cheaply decides it's wrong, and fixes that step
at runtime — on any model."*)

---

## DO NOT BUILD (focus list)

To protect the single sentence judges should remember, **do not** spend the 36h on:

- Generic **"LLM-as-judge eval #47"** — research shows naive judges are near-random on
  silent failure (AUROC ~0.54–0.65). Lead with deterministic/structural checks (as
  `reliability.py` does), not "ask a model if it looks right."
- **Raw trace capture** as a product → that's an OpenTelemetry commodity. Capture traces to
  *power the loop*, don't sell tracing.
- **Another orchestration framework** / MCP registry / memory layer / sandbox / browser- or
  voice-agent / thin wrapper.
- A standalone **eval/CI-gating product** → collides head-on with Confident AI (W25),
  Braintrust, Promptfoo. Keep only the *kernel* as the LEARN step (caught failures become
  stored regression cases), not a second product.
- A **scoped-permission / prompt-injection security firewall** as a built feature → that's a
  separate, also-crowded IAM/security lane. Keep as a one-line roadmap mention only.
- A pure **router / cost-cascade** as the headline → routing is commoditized (GPT-5 ships a
  built-in router; OpenRouter has Auto Router). Routing is the *loser's framing here*. Lead
  with runtime per-step **correction**; treat routing/cost-comparison strictly as the
  secondary surface.
