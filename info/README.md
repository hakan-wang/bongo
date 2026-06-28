# `/info` — Start Here

If you just opened this repo and want to understand **what we're building and why**, this
folder is your map. Read this page, then open `SOURCE-OF-TRUTH.md`.

## What is Assay? (3 sentences)

Assay is a **drop-in layer between an app and its LLM API** — change one line (the
`base_url`), keep your own key, and it proxies to any provider (Gemini, OpenAI, Anthropic,
open models). For a multi-step agent it **watches every step, cheaply catches the bad ones,
and corrects them live** (retry / supply context / escalate just that step to a stronger
model) — so a **cheap model performs like an expensive one**. As a side effect it sees each
step's cost + quality, so it also tells you **where you're overpaying** and cuts your bill.

> One line: **"Run the cheap model. Assay makes it reliable, and cuts your bill."**

> 👷 **Building? Read [`../TEAM-BUILD-PLAN.md`](../TEAM-BUILD-PLAN.md).** It has the work split
> (Håkan/Claude-side vs **Filip — START HERE**) and idiot-proof step-by-step tasks. **Filip:
> open that file, scroll to "FILIP — START HERE".**

## Doc layers (know which you're reading)

1. **Canonical / the truth:** [`SOURCE-OF-TRUTH.md`](./SOURCE-OF-TRUTH.md) — if anything
   anywhere conflicts, this wins. Primary source = **Håkan** (founder).
2. **Canonical supporting (repo root):** `VISION.md`, `PLAN.md`, `GTM.md`, plus the code
   (`reliability.py`, `proxy.py`).
3. **Background research (this folder):** the deep-dives below. They all defer to the
   Source of Truth.

> ⚠️ The two files in **`docs/`** describe an **earlier, superseded idea** — keep them only
> for market figures + competitor lists.

## Index of `/info`

| Doc | What's in it | Read it when… |
|---|---|---|
| [`SOURCE-OF-TRUTH.md`](./SOURCE-OF-TRUTH.md) | The definitive Assay description: insight, reliability loop, the hard bet, objections, team, what's built. | **First. Always.** |
| [`judges-and-how-to-win.md`](./judges-and-how-to-win.md) | Who's judging (YC/Datadog/Mistral/Genesis/QRT), the shared "reliability anxiety," per-judge lean-in, and the moves to win the room. | Prepping the pitch / a specific judge. |
| [`judge-api-usage.md`](./judge-api-usage.md) | What each judge company ACTUALLY uses agents/APIs for + a tailored "Assay helps you here" example per judge + the best demo example for the room. | Tailoring the pitch to a specific judge. |
| [`competitors-and-differentiation.md`](./competitors-and-differentiation.md) | Eval/observability incumbents + cost gateways/routers, and Assay's exact lane. | Someone asks "isn't this just X?" |
| [`technical-playbook.md`](./technical-playbook.md) | The engineering guide: tracing/proxy, failure taxonomy, cheap verification (lead deterministic), correction/cascades + honest limits, reliability scoring. | Building/extending `reliability.py`. |
| [`model-landscape.md`](./model-landscape.md) | Mid-2026 cheap-vs-expensive models, price ratios, best cheap/open backstop candidates. | Picking demo models / cost feature. |
| [`demo-example-choice.md`](./demo-example-choice.md) | Which demo workflow to run (code vs support-RAG vs extraction) + the exact steps. | Deciding what the live demo shows. |
| [`positioning-council.md`](./positioning-council.md) | Council verdict on the slide-1 positioning line + backups. | Writing the deck / elevator pitch. |
| [`wow-metric-and-pitch.md`](./wow-metric-and-pitch.md) | The wow number/moment, how to make it un-rigged, a DRAFT 60s script + slides + Q&A, and the Tripwire/Greenlight/etc. feature-borrow call. | Designing the demo / rehearsing. |
| [`research-verification.md`](./research-verification.md) | Adversarial fact-check verdicts on the riskiest claims (what to lean on vs hedge). | Before stating a strong claim on stage. |

## If you only have 60 seconds
1. Assay makes a **cheap LLM behave as reliably as an expensive one** — watch each step,
   catch the bad ones cheaply, fix them live, **across any provider**.
2. Moat: a lab only improves *its own* model; Assay sits **above all of them** and gets
   smarter as it sees more traffic.
3. The hard bet: **verification is cheaper than generation** — true for *checkable* steps
   (code, schemas, tool calls, math, retrieval), where we lead and where the demo lives.

Then open [`SOURCE-OF-TRUTH.md`](./SOURCE-OF-TRUTH.md).
