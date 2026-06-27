# Plumbline — Technical Playbook (for Tech 1 & Tech 2)

> **Audience:** the two engineers. Some of this is read cold by non-technical teammates too,
> so each section starts with a plain-English "why."
> **This builds on what's already in the repo.** It does not replace it. The canonical product
> doc is `info/SOURCE-OF-TRUTH.md` (§6 is the technical core); the working engine is
> `reliability.py`; the cost layer is `proxy.py`. Everything below extends those.
> **Golden rule from §6:** Plumbline checks a step **against reality, not against another AI's opinion.**
> Lead with deterministic checks. Be honest about where they stop.

---

## 0. The one bet this whole product rides on

**"Verification is cheaper than generation."** Plumbline runs a *cheap* model, watches each step,
catches the bad ones with a *cheap* check, and only spends real money (retry / escalate to a
strong model) on the steps that actually failed.

This bet is **true — but only in a specific regime**, and getting the regime right is the
difference between a demo that wins and a demo that breaks on stage:

- ✅ It holds for **checkable steps**: code that runs, JSON that validates, tool args that
  parse, math you can recompute, citations whose source you can look up. This is the
  cheap-generator regime — *errors from a weak model are easier to catch than errors from a
  strong one* (the asymmetry actually works **in our favour** because we run the cheap model).
- ⚠️ It **shrinks or breaks** for open-ended/creative steps with no ground truth ("is this the
  best video clip", "is this summary good"). There a cheap check is weak and a naive
  "ask another LLM if it looks right" judge is **near-random** (more below).

**Build implication:** the demo lives on verifiable steps. `reliability.py` already does exactly
the right thing — deterministic checkers, no AI judging AI. We extend *that*, we do not pivot to
a generic LLM-judge.

---

## 1. How Plumbline sits on top of provider APIs (Tech 2's surface)

**Plain English:** the customer changes one line — points `base_url` at Plumbline, keeps their own
key — and Plumbline proxies to the real provider while watching every step.

### 1a. The integration we already have, and where it goes
`proxy.py` is an OpenAI-compatible HTTP server (caching + cost stats). That is the right shape.
The job now is to make it (a) **multi-provider** and (b) **trace-emitting** so the reliability
loop can run in-band.

### 1b. Three ways to get the trace — pick by time budget

| Path | What it is | When to use | Effort |
|------|-----------|-------------|--------|
| **A. Extend `proxy.py`** | Our own OpenAI-compatible proxy, add provider routing + a hook surface | We control everything; best for the demo | Low–Med |
| **B. LiteLLM proxy under the hood** | MIT, self-hostable, one OpenAI-compatible endpoint over 100+ providers (OpenAI, Anthropic `/v1/messages`, Gemini), translates formats | If we want real cross-provider in 36h without writing N adapters | Low |
| **C. OTel auto-instrumentation** | If the customer app uses a framework (LangChain/LlamaIndex/CrewAI), one-line OpenInference or OpenLLMetry instrumentor emits spans; Plumbline receives OTLP | Second integration path, post-demo | Low (their side) |

**Recommendation for the 36h:** keep `proxy.py` as the **demo-controlled** path (Path A) so we
own the live story, and have **LiteLLM (Path B)** ready as the "and it works across every
provider" proof. Reuse LiteLLM for provider normalization so our hours go into VERIFY/INTERVENE,
not into writing 100 provider adapters.

### 1c. The hook surface (this is where the reliability loop lives)
If we adopt LiteLLM, its `CustomLogger` gives us the exact loop in-band:
- `async_pre_call_hook` — **modify or reject** the outgoing request (swap `data["model"]` to
  escalate; inject guidance/context). This is our **INTERVENE** lever.
- `async_moderation_hook` — runs **in parallel** with the call → cheap verification with **no
  added latency**.
- `async_post_call_success_hook` / `async_post_call_streaming_hook` — inspect the output → our
  **VERIFY** step.
- `async_log_success_event` — emit the trace → our **TRACE** step.

If we stay on our own `proxy.py`, we implement the same four points by hand in `do_POST`.

> **Caveat (verified):** LiteLLM's *retry-this-step-with-guidance* story is thin — the hooks let
> you rewrite the model or reject, but the actual retry/escalation control flow is **ours to
> build** (it already exists in `reliability.py:run_step` — that loop is the asset). Budget time
> for the control flow, not the hooks.

### 1d. Trace data model — use OTel GenAI semantic conventions
Don't invent a schema. Adopt the OpenTelemetry GenAI conventions so we're standard and
OTLP-exportable later:
- Span ops: `chat`, `execute_tool`, `invoke_agent`, `embeddings`.
- Attributes: `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`,
  `gen_ai.usage.input_tokens` / `output_tokens`, `gen_ai.response.finish_reasons`,
  `gen_ai.tool.name`.
- **Multi-step structure = a span tree under one `trace_id`**: `invoke_agent` (parent) → child
  `chat` spans per LLM call → `execute_tool` per tool. Stamp every span with a
  `session.id` / `conversation.id` so turns group correctly. This is how Plumbline reconstructs
  "every step" and attributes a bad step to its place in the workflow.

> **Caveats (verified):** (1) OTel GenAI conventions are still drifting (`gen_ai.provider.name`
> vs older `gen_ai.system`) — **pin a version**. (2) Capturing full prompt/response content is
> privacy-gated and **off by default** in many instrumentors; we **need** it for verification, so
> explicitly enable content capture and handle PII. (3) Streaming: you can't fully judge an
> output until the stream completes — either buffer (adds latency) or verify post-hoc and
> intervene on the *next* step.

> **Latency budget (verified):** LiteLLM proxy overhead is ~8ms P95 at 1,000 RPS — cheap enough
> to sit in the hot path. Run verification in the parallel moderation hook so it overlaps
> generation.

---

## 2. The failure taxonomy — what we are actually catching

**Plain English:** before you can catch a bad step you need a list of how steps go bad. Research
converges on a clean taxonomy. The single most important class is **silent failure**.

### The #1 target: SILENT FAILURE ("false success")
The agent says "done" (confident, well-formatted, **HTTP 200, no exception**) while the actual
state disagrees. This is the exact thing `SOURCE-OF-TRUTH.md` §2 calls out: *"when it makes a
mistake, nobody knows."* In studies it's **45–48%** of single-control tool-agent failures and
**75.8%** of self-assessing coding trajectories. **This is what kills cheap models in production.**

### The catchable failure modes (map each to a checker)
| Failure mode | Cheap signal that catches it |
|---|---|
| **Schema / tool-arg violation** (numbers-as-strings, missing required field, truncated JSON) | JSON-schema / type / required-field validation — *the highest-ROI fix; pre-enforcement compliance <40% → 100% with strict schema* |
| **Infinite loop / no-progress** | `hash(tool_name + canonical_args)` over a sliding window; bail on repeat. Cheap to detect, expensive to miss (one runaway burned 847 steps at $47/min) |
| **False success / wrong-but-200** | **state-diff** (claimed completion vs actual env/API state); cheap statistical detector — *not* a generic LLM judge |
| **Instruction drift / multi-turn collapse** | re-inject the instruction (drift responds to lightweight goal reminders); compare against original task spec |
| **Retrieval / citation hallucination** | does the cited source **exist** (DOI/URL lookup)? does it **entail** the claim (small NLI model)? |
| **Premature / incorrect termination** | did the verifier pass before the agent declared done? |

### Why the LLM-judge approach (which we are NOT using as the core) fails here
**Verified, and this is the load-bearing caveat for the whole product:** a naive
"ask another model if this looks right" judge is **near-random** at catching silent failure —
**max AUROC 0.65 / 0.54** across many judge+prompt configs, barely above a coin flip. Judges get
fooled by confident closing language and high action counts. Meanwhile a **trivial cheap detector
(TF-IDF / state-diff) hit AUROC 0.83–0.95, caught 4–8× more false successes, at 3,300× lower
latency.** This is the empirical proof of our bet — **lead with it on stage.**

### The business case (compounding errors) — for the pitch, but it's also why per-step matters
At 95% per-step accuracy a **10-step task succeeds only ~60%** of the time; 90% → 35%; only **24%
of real agent tasks complete first try.** One bad early step poisons everything downstream. That
is exactly why Plumbline verifies **per-step, incrementally**, not once at the end. (Bonus, verified:
post-hoc localization of *which* step failed in a finished 6M-token trace is essentially unsolved
— best SOTA ~11%. So **verify as the trace streams**, don't try to debug the whole thing after.)

---

## 3. Cheap verification methods, ranked (lead with deterministic)

**Plain English:** this is the cascade of checks, cheapest and most reliable first. You only pay
for the next tier when the previous tier is inconclusive. `reliability.py`'s `check_meeting` /
`parse_json` are **Tier 1** — everything below extends that pattern.

### Tier 1 — Deterministic / against-reality (FREE, near-100% precise) — START HERE
This is the demo backbone and the thing that makes "no AI judging AI" true.
1. **JSON-schema / Pydantic / type / required-field / range validation** — generalize
   `check_meeting` into a schema-driven validator (see §6).
2. **Code execution** — run generated code against unit tests (right/wrong is binary). *Best
   live-demo material: the test passes or it doesn't, in front of the judges.*
3. **Math recompute** — extract the expression, run it in Python.
4. **Citation / source existence** — Crossref/DOI lookup, HTTP HEAD on URLs. (Models are bad at
   self-checking citations — ~38% — but an existence check is deterministic and trustworthy.)
5. **Constraint checks** — referenced IDs exist in the input, dates valid, counts in range,
   timestamps exist in the source (this is how Brolly's *checkable* parts get guarded).
6. **Loop / no-progress detection** — the `hash(tool+args)` sliding window from §2.

> **Caveat:** narrow coverage — Tier 1 only catches steps that *have* structure. It says nothing
> about free-form prose. That's fine: the demo is scoped to structured/verifiable steps.

### Tier 2 — Cheap statistical / structural (cheap, label-free)
7. **State-diff / false-success detector** (TF-IDF or a small distilled cross-encoder) — the
   AUROC-0.83–0.95 winner from §2. The highest-leverage non-deterministic signal.
8. **Cross-model disagreement / cross-model perplexity** — run the cheap model's answer through a
   *second* model for **one forward pass** (no second generation, no labels) and measure
   surprise. AUROC ~0.75 vs ~0.59 baseline; specifically catches **confident** errors that
   self-uncertainty misses. Natural fit for a cross-provider proxy that already has multiple
   endpoints.

### Tier 3 — Self-consistency (effective but a generation-side cost multiplier)
9. **Sample the step N times, measure agreement; low agreement = likely wrong.** For code/math,
   cluster by **execution output**, not text, for a cheaper sharper signal. **Gate this** to
   steps already flagged by Tier 1/2 — it costs N× generation, the opposite of our thesis if used
   everywhere. (Also: a model can be *confidently and consistently wrong* — agreement measures
   stability, not truth.)

### Tier 4 — Small specialized judge model (narrow yes/no only)
10. **A 440M DeBERTa-class NLI / faithfulness checker** (Luna-style) — ~97% cheaper, ~91% lower
    latency than a GPT-3.5 judge, millisecond inference. Use **only** for narrow entailment
    ("does the retrieved context entail this claim?"), **never** open-ended quality scoring.

### What we do NOT do
- ❌ **Generic LLM-as-judge as the core verifier** (AUROC ~0.54 on silent failure; fooled by a
  single token; verbosity/position bias). Reserve a judge for narrow yes/no, prefer a fine-tuned
  encoder.
- ❌ **Logprob/self-confidence alone** — poorly calibrated after RLHF (confidence pinned 80–100%
  regardless of correctness); misses confident hallucinations. Also often **unavailable** through
  closed provider APIs, so a vendor-neutral proxy can't rely on it.

> **The blueprint number to cite (Weaver, Stanford):** an ensemble of weak verifiers, distilled
> into a **400M cross-encoder, retains 98.7% of full-ensemble accuracy at ~0.03–0.57% of the
> verification compute.** This is the proof that a cheap verifier can police an expensive
> generator. It's also the recipe if we want a single learned verifier later: combine weak signals
> with weak supervision (no ground-truth labels), then distill.

---

## 4. Correction / cascade / routing — with honest limits

**Plain English:** once a step is flagged bad, how do we fix it without just buying the expensive
model for everything? `reliability.py:run_step` already implements the core ladder
(cheap → retry cheap → strong-fallback, cost 1 vs 50). This is the spine. Here's how to extend it
and the traps to avoid.

### 4a. THE most important limit — intrinsic self-correction does NOT work
**Verified, strongly:** a model reviewing its own answer with **no external signal** makes
reasoning **worse** (GPT-4 ~95.5%→91.5% on GSM8K; models flip correct→wrong more than
wrong→correct). Prior "self-correction works" papers secretly used oracle stop labels. Merely
challenging a model ("are you sure?") with no new info also degrades it.

**So the INTERVENE step must inject NEW information**, never just "try again":
- ✅ attach the **actual** validator/execution error,
- ✅ supply the **missing context** / tool result,
- ✅ **escalate that one step** to a stronger model (or different provider),
- ✅ or supply the **error location** — the good news: models *can* fix an error once told **where**
  it is (localization is the bottleneck, not the fix). Our verifier's job is to cheaply pinpoint
  the bad step; the cheap model can often repair it given that.
- ❌ a bare retry plateaus after round 1.

This directly validates the `reliability.py` design: retry carries the *reason* from the checker,
and escalation supplies a genuinely different (stronger) signal.

### 4b. The intervention ladder (cheapest first) — extend `run_step`
1. retry cheap **with the checker's reason as guidance** (already in `run_step` — make sure the
   `reason` is fed back into the prompt, not discarded),
2. inject missing context / tool result,
3. **escalate that one step** to a stronger model (Flash→Pro, Haiku→Sonnet),
4. escalate to a different **provider**,
5. **Tripwire kill-switch** — if a loop/no-progress or a per-run token/$ budget ceiling trips,
   **halt** (the safety intervention; visceral demo moment).

### 4c. Cascades & routing — real savings, but DON'T overclaim
- **Cascade (FrugalGPT-style):** cheap → score → escalate. Reported up to 98% cost cut at GPT-4
  parity. **Honest caveat (verified):** that 98% is the **best-case, per-dataset, threshold-tuned**
  number; the *same* paper shows 59–73% on other datasets, and an independent 2026 reproduction
  found a cascade scoring **below** an always-strong baseline out-of-distribution. The scorer needs
  in-distribution calibration.
- **Routing (RouteLLM-style):** pick weak vs strong **before** generation. ~95% of GPT-4 quality
  at ~11–26% of strong-model calls; routers transfer across model pairs without retraining (good
  for vendor-neutral). **But:** routing is *pre-generation* and partly **commoditized** (GPT-5
  ships a built-in router; OpenRouter Auto exists). **Do not pitch routing as the innovation** —
  it's the loser's framing. Plumbline's edge is **per-step runtime correction**, which routing/cascades
  don't do; routing is at most a secondary lever.

> **Cost honesty (verified):** sampling N× for agreement, or running a judge step, is **not free**.
> If a meaningful fraction of steps need 3–5 samples + escalation, total cost can creep toward just
> using the expensive model. **Report cost-per-COMPLETED-task, not cost-per-token** (also normalizes
> tokenizer differences across providers — Anthropic's newer tokenizer can emit up to ~35% more
> tokens for the same text). Expose **escalation-rate as a live metric** so a drifting verifier that
> silently escalates everything is visible immediately.

> **Test-time-scaling ceiling (verified):** more retries ≠ free reliability; agent accuracy peaks
> ~3–7 turns then degrades from context pollution. INTERVENE must be **targeted** (fix *this* step),
> not "sample more."

---

## 5. Reliability scoring of unknown models + the reliability-DB moat

**Plain English:** the side feature ("which model is actually reliable for *your* job") and the
long-term moat. Because Plumbline proxies real traffic, it measures reliability on the task the
customer *actually* runs — which no public benchmark covers.

### 5a. Don't trust leaderboards as per-task scores
Public benchmarks (MMLU etc.) are **contaminated** (~29% for MMLU; models drop ~13 points on clean
re-tests) and stale. Use them as a **weak prior only**, never as the reliability score for a random
open/Chinese model.

### 5b. Measure, with a prior — the design
Treat each **(model, task-cluster)** as a Bernoulli arm:
- Keep a **Beta(α, β)** posterior over pass-probability; `α = benchmark_prior + observed_passes`,
  `β = observed_fails`. `task_cluster` = embedding cluster of the request.
- Report **Wilson confidence intervals** (better than the normal approximation at small n or p near
  0/1).
- **Sample-size rules of thumb:** ~30–60 verified samples for a usable per-(model,task) score; **n
  ≥ 100** before trusting CLT-based comparisons. Detecting a gap half as large needs **4×** the
  samples.
- **Sequential stopping:** pilot n₀=10, stop when the CI half-width ≤ target.

### 5c. Frame model selection as a contextual bandit
Arms = models, reward = **verified-correct − cost**. This gives principled exploration of cheap
models and exploitation of reliable ones — **and builds the reliability DB as a byproduct of
serving traffic.** This is the moat: a cross-provider, per-(model × task) reliability database from
real production traffic that **compounds with every request**. No model lab will build it (a lab
only optimizes its own ladder), and no single-provider gateway has it.

### 5d. Honest caveats (verified)
- **The reliability score is only as good as the verifier.** Without a deterministic oracle, the
  pass/fail *label* is itself an estimate — so prefer the Tier-1-checkable task types where the
  label is trustworthy, and track verifier-vs-reality drift.
- **Cold-start:** the first N requests for a new (model, task) have wide CIs; route conservatively
  (fall back to strong) until the CI tightens. The bandit's exploration budget handles this.
- **Non-stationary:** providers silently update models; pass-rates shift. Add **decay /
  change-detection**, or stale scores mislead routing.
- **Clustering:** real traffic isn't i.i.d. (same user, same prompt template) — this can inflate
  true standard error up to ~3×. Use clustered standard errors or you'll be overconfident.

---

## 6. Concrete: how to extend `reliability.py` (the to-do list)

`reliability.py` is already the right shape. The work is to generalize it from one hard-coded
checker to a cascade, and to plug it into the proxy. Concrete steps:

1. **Generalize the checker.** Turn `check_meeting` into a **schema-driven validator** (pass a
   Pydantic model / JSON Schema). Keep the exact same `(ok, reason)` return contract — `run_step`
   already consumes it.
2. **Add the verifier cascade (Tiers 1→4 from §3)** as an ordered list of `(name, fn) -> (ok,
   reason)` checkers. `run_step` calls them cheapest-first and stops at the first failure. Most
   steps never leave Tier 1.
3. **Feed `reason` back into the retry prompt.** The retry must carry the checker's reason as
   *guidance* (§4a — new information, not a bare retry). Verify this is actually injected, not
   dropped.
4. **Add loop / budget tripwire.** Maintain the `hash(tool+args)` window and a per-run token/$
   ceiling; trip → halt. This is both a checker and the safety intervention.
5. **Swap `simulate_*` for real model calls** via the proxy (the module comment already promises
   "nothing else changes"). Route cheap vs strong through Path A/B from §1.
6. **Emit an OTel GenAI span per attempt** (§1d). The `trace` dict `run_step` already returns maps
   almost 1:1 onto spans (`input`, `attempts[]`, `cost`, `final`, `fixed_by`).
7. **Log every caught failure to the reliability DB** (§5) — this is the **LEARN** step and the
   moat. Each `(model, task_cluster, ok)` updates the Beta posterior.
8. **Track cost-per-completed-task and escalation-rate** (§4c) — feed the dashboard. These are the
   honest numbers; don't ship cost-per-token.

**Keep the cost-unit convention** (`COST = {"cheap": 1, "strong": 50}`) for the demo — it makes
the savings legible. Replace with real per-model token pricing once real calls are wired
(LiteLLM exposes cost tracking natively).

---

## 7. One-paragraph summary (read this if you read nothing else)

Plumbline is a proxy (extend `proxy.py`, optionally LiteLLM underneath) that emits OTel GenAI spans,
runs a **cheapest-first verifier cascade** (deterministic schema/exec/citation/loop checks →
state-diff/cross-model → gated self-consistency → narrow NLI judge — **never a generic LLM judge as
the core**), and on a flagged step **intervenes with new information** (checker reason, missing
context, or single-step escalation — **never a bare self-recheck**, which provably makes things
worse). It scores each `(model, task)` as a Beta/bandit arm from real traffic, building a
cross-provider reliability DB that is the moat. `reliability.py:run_step` is the spine; §6 is the
to-do list. **Demo only on verifiable step types** (lead with a code agent — the test passes or it
doesn't, live) so the core bet never visibly breaks. Report **cost-per-completed-task**, not
per-token.
