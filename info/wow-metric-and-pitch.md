# Wow Metric & Pitch

> **Read this when:** you're designing the live demo moment, or rehearsing the 60-second pitch.
> **Defers to:** [`SOURCE-OF-TRUTH.md`](./SOURCE-OF-TRUTH.md) — if anything here conflicts with it, that wins.
> This doc synthesizes the team's WOW-metric council into one recommended on-stage moment, then stores the current pitch draft (script, slides, Q&A). The pitch section is explicitly a **DRAFT — will change**.

---

## Part 1 — The Wow Metric (the one number that wins the room)

### The headline number

> **Cheap model alone: ~70%. Cheap model + Bongo: ~95%. Same model, same price — Bongo recovered 5 of every 6 failures live, at roughly 1/50th the cost of just buying the expensive model.**

The council's strongest finding: **don't lead with the cost ratio.** If you put "95% vs 95%" on screen and shout "50× cheaper," judges hear *router / cascade* — a thing they've already seen (RouteLLM, FrugalGPT, OpenRouter Auto) — and they file you under "cost optimizer." That is the loser's framing.

Instead lead with the **recovery ratio**: the cheap model failed, and Bongo *caught and fixed* most of those failures **live**. That centers Bongo's actual moat — **active per-step correction** — not routing. Cost is the *proof slide* that lands after, never the headline.

**One memorable line to say out loud:** *"Five of six silent failures, caught and fixed, for pennies."*

### Why this number and not the alternatives

The council (4 advisors, avg confidence ~8) converged on this. Rejected framings and why:

- **"Same 95% at 50× less"** → read as a quality *tie*; judges fixate on cost → sounds like a router. Rejected.
- **A static three-bar chart** (`Pro $X/95% · Flash $X/70% · Flash+Bongo $X/95%`) → looks **rigged**. Numbers on a slide are claims judges must *trust*; a 36h hackathon's strongest asset is live, unfakeable execution. **Demote the three-bar chart to a closing summary slide — it is not the proof.**
- **Cost-per-call** → wrong unit. The buyer (QRT, Datadog eng) cares about **cost-per-CORRECT-task**, because cheap-per-token means nothing if the task fails. Report cost-per-completed-task, normalized across tokenizers (different providers tokenize differently — see `model-landscape.md`).

### How to make it un-riggable on stage

The whole point is that the judges *don't have to trust your slide*. Make the verdict something the **audience can check with their own eyes**, and let them poke it. Concretely:

1. **Run it LIVE, three columns racing** — expensive model / cheap-alone / cheap+Bongo — on the same prompts, same seed. Not a recording.
2. **Use a deterministic, audience-checkable verdict — not Bongo's own judge.** The check must be something the room can verify directly: the JSON either parses or it doesn't; the unit test either passes or it doesn't; the cited URL either 404s or resolves. **No "trust our 95%."** This is the team's own "check against reality, not another AI's opinion" principle (`SOURCE-OF-TRUTH.md` §6) and it is exactly what `reliability.py` already does (`check_meeting`, `parse_json` → deterministic ok/reason).
3. **Let a judge pick the input.** Hand them the prompt choice on the spot. Nothing says "not staged" like a held-out task you didn't pre-tune.
4. **Show the receipts of each recovery.** When Bongo catches a step, surface the trace: the exact bad step highlighted, the verifier's verdict, and the intervention taken (retry-with-guidance / context injection / single-step escalation). This is the Regret-lite "bad-step panel" (see Part 3) and it makes the catch *believable*.
5. **Show real money.** A live `$` counter from actual API billing (own-key proxy → real provider calls). Show raw provider responses so it's clearly not mocked.
6. **Pin model versions on screen.** Models churn monthly (see `model-landscape.md`); naming exact versions reads as rigorous, not hand-wavy.
7. **Include the per-step escalation log** — e.g. *"47 steps ran on Flash, 3 escalated to a stronger model."* This makes the cost auditable (most steps genuinely stayed cheap) and pre-empts the "doesn't this just become the expensive model?" objection.
8. **Include one task Bongo can't save.** A deliberately unrecoverable case proves the demo isn't staged and shows you're honest about the boundary (verifiable steps; open-ended taste is the frontier).

### Scope discipline (so the bet never visibly breaks)

The core bet — *verification is cheaper than generation* — is **real but conditional**. It holds for **checkable steps** (code that runs, schema/tool-arg validation, math recompute, citation-exists) and gets weak on open-ended prose with no ground truth. **Scope the live demo to verifiable step types** (the team's lean toward a **code agent** is exactly right). Name the regime out loud — engineer judges (Datadog/Mistral) respect "here's where it works and here's where it doesn't" far more than an over-claim that breaks under their first question.

> **Demo target (restated from `SOURCE-OF-TRUTH.md` §16):** a multi-step agent runs on a cheap model, makes a mistake, Bongo catches it live and corrects it, and the dashboard shows pro-level reliability at flash-level price — proven on a check the room can verify itself.

---

## Part 2 — The Pitch

> ## ⚠️ DRAFT — WILL CHANGE
> Everything below is a working draft from the pitch council. Numbers, model names, and wording **will be revised** before the event — re-verify all pricing/version figures near demo time (`model-landscape.md`), and Håkan owns final wording. Treat this as a starting skeleton, not the final script.

### 60-second spoken script (DRAFT)

> **(0:00)** Every startup building on LLMs faces the same trap. The cheap model is 30 to 90 times cheaper — but it fails silently. The expensive model is reliable, but you're burning cash on every call, even the easy ones.
>
> **(0:12)** Here's what that looks like. You build a support agent. It looks up an order, checks a refund policy, issues the refund. On the cheap model it works nine times out of ten. The tenth time, step two hallucinates the policy — confidently, HTTP 200, no error — and the agent refunds money it shouldn't. So you "fix it" by upgrading every step to the expensive model. Now you're paying frontier prices to look up an order number.
>
> **(0:34)** Bongo is the layer in between. You change one line — point your `base_url` at us, keep your own key. We proxy to any provider. We watch every step, catch the bad one cheaply — verification is far cheaper than generation — and intervene on just that step: retry with guidance, or escalate only that call to a stronger model. Cheap by default, expensive exactly where it matters.
>
> **(0:52)** "Won't the labs build this?" A lab only makes its own model better. Bongo is vendor-neutral — Gemini, OpenAI, Anthropic, open models — and the cross-provider reliability data is the moat. We make a cheap model behave like an expensive one.

### Slide outline (6 slides, DRAFT)

| # | Title | Core content |
|---|-------|--------------|
| **1** | **Cheap fails silently. Expensive bankrupts you.** | Audience = any startup shipping multi-step agents on LLM APIs. Pain: cheap models are 30–90× cheaper but fail **silently** (confident wrong answer, HTTP 200, no exception), so teams over-pay for the frontier model on *every* step to de-risk the 5–10% tail. *"You're paying Opus prices to look up an order number."* Visual: a fork with no good option. |
| **2** | **One bad step poisons the whole run.** | Relatable example: support/refund agent — (1) look up order, (2) check policy, (3) issue refund. Step 2 hallucinates the policy, no error thrown. Then the math: at 95% per-step accuracy a 10-step task succeeds only ~60% of the time; 90% → 35%. The failure is **reliability, not capability**. Visual: 3-step chain, step 2 flips red mid-run. |
| **3** | **Make a cheap model behave like an expensive one.** | The product. One-line integration (`base_url` swap, keep your key, proxy to any provider). The loop: **TRACE → VERIFY (cheap) → INTERVENE on the bad step (retry-with-guidance / inject context / escalate just that step) → LEARN.** Default cheap; spend frontier dollars only where needed. (This is `reliability.py` in code.) Visual: app → Bongo → providers, loop badge over the step chain. |
| **4** | **Verification is cheaper than generation.** | The hard technical core, now literature-backed. Stanford's *Weaver*: a distilled 400M verifier retains ~98.7% of full-ensemble accuracy at a 99.97% compute cut. On agent loops, verifying takes ~4× fewer tool calls than generating. And cheap beats clever: a trivial structural detector caught 4–8× more silent failures than the best LLM-judge at ~3,300× lower latency. We layer **cheapest-first**: schema/tool/execution checks (free) → cross-model agreement → small distilled verifier → escalate only the flagged step. Honest scope: **checkable steps** — exactly where agents run. |
| **5** | **A lab only sharpens its own model. We sit above all of them.** | Rebuttal + durability. Cross-provider is the moat — no lab optimizes across its competitors. Receipts: OpenAI is deprecating its own Evals platform (shutdown Nov 2026); Anthropic endorses third-party evals and says they get *harder* as models improve; "you can't grade your own homework." Durable asset: a cross-provider, per-(model × task) **reliability database** from real production traffic that compounds. Precedent: AWS ships CloudWatch; Datadog is still huge. |
| **6** | **Gateways route. Observability watches. Bongo fixes — at runtime, across providers.** | The wedge + ask. Gateways retry only on infra errors (429/5xx); routers pick a model *before* generation; observability tells you *after the fact* — Bongo is the only layer that inspects each step's **output**, cheaply decides it's wrong, and corrects that step **live, on any provider**. Side feature: cost/overpay dashboard + cross-provider reliability scores + a Tripwire cost/loop kill-switch. Ask: cheap + Bongo ≈ expensive-model reliability at a fraction of the cost. |

### Tough Q&A prep (DRAFT)

**Q1 — "Isn't your verifier just another LLM-as-judge, which barely beats chance on silent failures (AUROC 0.54–0.65)?"**
Exactly why we **don't** lead with a generic judge — and we won't pretend a model can reliably check itself (Huang et al., ICLR 2024: blind self-correction makes reasoning *worse*). Our verifier is an **external, cheapest-first cascade**: deterministic checks first (JSON/tool-arg schema validation, code execution, math recompute, citation-exists) — near-free, near-100% precise; then cross-model agreement and self-consistency; then a small distilled cross-encoder (Weaver-style); and **only the flagged step escalates** to a strong model. On false-success detection a trivial structural detector beat the best LLM judge by 4–8× at ~3,300× lower latency. We scope the demo to checkable step types — code, tool calls, structured output, grounded claims — which is where production agents live. Open-ended creative prose with no checkable structure is the honest weak spot; we don't claim coverage there.

**Q2 — "If you sample multiple times and escalate a chunk of steps, doesn't total cost approach just running the expensive model?"**
The right question, answered with measurement, not assumption. Three things keep us net-cheap: (1) most verification is **deterministic and effectively free** — schema/execution/grounding checks cost no extra generation; (2) we **gate** the expensive signals (sampling, distilled verifier) so they fire only on already-suspicious steps; (3) we **escalate per step, not per request** — a 10-step run might escalate one step, so you pay frontier price on ~10% of *one* call, not 100% of ten. RouteLLM-style work already gets ~95% of frontier quality at ~11–14% of strong-model calls at the *query* level; we do it at finer *step* granularity. And we expose **escalation-rate as a live metric**, so a drifting verifier that silently escalates everything is visible immediately. We pitch measured net savings on a real workload, not a hand-wave.

**Q3 — "Portkey already does gateway guardrails with retry/fallback, and Raindrop (YC) now ships auto-fix loops. What stops them owning this in a month?"**
Two structural moats. **First, the category gap:** Portkey's guardrails are verification-*only* — their docs are explicit they deny/log/fallback but do **not** regenerate or repair output, and they're single-request, not agent-trajectory aware; pure gateways (OpenRouter, LiteLLM, Cloudflare) only retry on *infra* errors, never on a wrong-but-200 response. Raindrop has moved toward intervention but centers on detect + per-product custom models built **offline**, not mid-request cross-provider correction. **Second, and more durable:** the moat isn't the loop — anyone can build a loop — it's the **cross-provider, per-(model × task) reliability database** built from real production traffic, which compounds with every request and which no single-provider gateway and no model lab will ever assemble (a lab only optimizes its own ladder). We're table-stakes on integration (one-line `base_url`, reuse LiteLLM underneath) so both our 36 hours and our long-term edge go into runtime per-step correction plus that cross-provider data.

> **One honesty note for whoever rehearses this:** the "nobody does this" framing is slightly too strong — a convergent product (Future AGI's Agent Command Center) claims inline cross-provider quality-floor + regenerate. Don't say "nobody"; differentiate on specifics: per-step trajectory localization, targeted retry-with-guidance (not whole-request regen or canned override), and the cross-provider reliability-score data moat. (Full detail will live in `competitors-and-differentiation.md`.)

---

## Part 3 — Feature-borrow: which of Tripwire / Chokepoint / Greenlight / Regret to fold in

Four earlier candidate ideas were considered as features to fold into Bongo. The council's verdict (build *on* the reliability loop, don't spawn a second product):

| Idea | What it was | Verdict | What to actually do |
|------|-------------|---------|---------------------|
| **Tripwire** | Runtime cost kill-switch + block dangerous/looping calls | **FOLD IN (headline safety/INTERVENE feature)** | Cheapest possible add — Bongo already sits in-path and has the step trace. Loop detection = hash `(tool + args + output-hash)`, stop on N consecutive no-progress repeats; detect ping-pong (A→B→A→B) and failure streaks; add a per-run token/$ budget ceiling. It's the most **visceral** demo moment (stop a live runaway before it burns the budget) and it *is* the natural intervention when the verifier flags a stuck step. |
| **Regret** | Deterministic causal replay to prove the root-cause step | **FOLD IN (near-free explainability, scoped DOWN)** | Ship the **"show the bad step" panel only**, NOT a full replay engine. Bongo already records each step for verification, so surfacing *"this exact step is the root cause + its prompt/response + the intervention we took"* is ~90% UI. This is the receipts panel from Part 1 step 4, and it serves the QRT (reproducibility/audit) and Datadog (root-cause) judges. **Do not** call it "deterministic replay" on stage — that invites a request to re-execute, which we didn't build. |
| **Greenlight** | Auto-generate evals from traces + CI red/green merge gate | **CUT as core; fold only its kernel as LEARN** | Full Greenlight is build-time/CI (breaks our "active correction in production" positioning) and collides head-on with Confident AI (W25), Braintrust, Promptfoo. Fold **only the cheap kernel**: every verifier-caught production failure auto-becomes a saved regression case shown in the dashboard (the **LEARN** step). Show a counter — *"N failures captured → N regression cases."* Stop there; do **not** build the GitHub merge-gate or scheduled-eval runner. |
| **Chokepoint** | Authorization firewall — scoped permissions, block over-permissioned/injected calls | **CUT from build (keep one roadmap line)** | It's a different security-product lane (OWASP/IAM/JIT tokens) that drags Bongo into the crowded agent-security market and dilutes the single sentence judges should remember. Mention only: *"because we already proxy every call, the same chokepoint can later block over-permissioned or injected tool calls."* |

**Net for the demo:** reliability loop = the **CORE**; **Tripwire** kill-switch = the headline INTERVENE/safety side feature; **Regret-lite** bad-step panel and **Greenlight-lite** failure→regression memory = near-free reinforcements of the same loop. One product, one sentence.

> **Watch-out — the kill-switch false positive:** legitimately repeated tool calls with *different* outputs are progress, not a loop. Use result-aware detection (same input + different output must NOT trip) or you'll halt a healthy agent on stage. Show it working, don't assert it.
