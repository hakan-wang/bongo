# Judges & How to Win This Room

> **Purpose:** This is the jury playbook for the "Paris Builds" 36h hackathon (Unaite × Y Combinator, Software-for-Agents track). It tells you **who is judging**, the **one anxiety they all share**, **what makes each judge lean in**, and the **3–4 concrete moves** that win this specific room.
>
> Read this alongside `info/SOURCE-OF-TRUTH.md` (the canonical product doc) and `VISION.md`. Nothing here changes the product — it's about aiming the same product at these specific people. Prize: a YC interview + €20,000.

---

## 1. Who is in the room

| Judge / org | Who they are | What they live and breathe |
|---|---|---|
| **Nicolas Dessaigne** | General Partner at Y Combinator; co-founder & ex-CEO of **Algolia** (search infra/dev-tool that scaled huge) | A dev-tools founder turned VC. Thinks in moats, "is this a real company," and developer adoption. Has said publicly that **"evals are the moat"** and that **"devtools sell to agents now."** |
| **Datadog engineer(s)** | Datadog's flagship push is **LLM / Agent Observability** | They watch agents fail in production for a living. Care about traces, root-cause, "what actually broke and where." |
| **Mistral engineer(s)** | A model lab; ships open + frontier models | They know **tool-calling is a liability** — models call the wrong tool, with wrong args, confidently. Live the cheap-vs-reliable tradeoff from the model side. |
| **Genesis AI engineer(s)** | Frontier/robotics-adjacent AI | Internal mantra: **"evaluation is the bottleneck."** They feel the pain that you can't ship what you can't measure. |
| **QRT engineer(s)** | Quant trading firm (Qube Research & Technologies) | Care about **reproducibility, cost, and audit** — every decision must be explainable and replayable. **A QRT advisor already confirmed Assay's cross-provider angle is exactly why he'd use it.** |
| **Sponsors:** Hugging Face, OpenArm | Open-source / open-hardware ecosystem | Lean toward **open core, vendor-neutral, no lock-in.** |

**Takeaway:** this is not a generic crowd. Almost every judge has *personally been burned by agents failing silently in production.* That is the lever.

---

## 2. The one thing they all share: **reliability anxiety**

Every judge in this room, from different angles, is afraid of the same thing: **agents fail silently.** A confident, well-formatted, **wrong** answer comes back as an HTTP 200 — nothing crashes, nothing alerts, the bad step poisons the rest of the run, and the bill keeps climbing.

Each judge feels a different face of the same fear:

- **Datadog** — *we can see the trace, but the failure is invisible inside a "successful" response.*
- **Mistral** — *tool-calling is where our models bite users; wrong tool, wrong args, looks fine.*
- **Genesis** — *evaluation is the bottleneck; we can't trust our own scores.*
- **QRT** — *we can't ship anything we can't reproduce, cost-control, and audit.*
- **Dessaigne** — *evals are the moat; whoever owns trust owns the agent stack.*

**Assay speaks directly to this anxiety.** Assay doesn't just *tell* you the agent failed (that's observability — passive, after the fact). Assay **catches the bad step while the agent runs and fixes it** — on a cheaper model, across any provider. That is the emotional hook: *"You already know your agents fail silently. We catch it and fix it, live."*

> Lead the pitch by naming their pain before naming the product. The room should be nodding before you say what Assay does.

---

## 3. Per-judge "what makes them lean in"

Use this to tailor a sentence, a demo beat, or a Q&A answer to whoever asks.

| Judge | They lean in when you show… | One line to say to them | Watch out for |
|---|---|---|---|
| **Dessaigne (YC)** | A real company: clear moat, "labs can't build this," pay-from-savings business model, instant developer adoption (one-line `base_url` swap). | *"A model lab only ever makes its OWN model better. Assay sits above all of them — the cross-provider reliability data is the moat that compounds."* | He'll probe "why won't OpenAI/Anthropic just build this?" — have the receipts (§5). Don't pitch routing as the innovation; routing is commoditized. |
| **Datadog** | That Assay is the **active** layer above observability — it doesn't just trace, it **intervenes per step**; a clean root-cause "here's the exact bad step" view. | *"You tell people their agent failed. We catch the failed step and fix it at runtime — observability is the floor, correction is the product."* | They know traces cold. Don't oversell raw trace capture (that's commodity / OpenTelemetry). Lead with the **correction**, not the trace. |
| **Mistral** | Deterministic catching of **tool-call / schema** failures — the exact liability they live with — on a cheap model, with that one bad step escalated. | *"Tool-calling is a liability. We validate the tool call deterministically and retry-or-escalate just that step — no AI judging AI."* | They'll test the core bet. Be precise: verification is cheap **for checkable steps** (schema, code, tool args). Don't claim it works on open-ended taste. |
| **Genesis** | That Assay turns "evaluation is the bottleneck" into a solved, in-loop step — cheap verification that actually catches silent failure. | *"Evaluation is the bottleneck — so we made verification cheap and put it in the live loop, not in a notebook after the fact."* | Cite the cheap-verifier evidence (Weaver, cheap structural detectors beating LLM-judges). Don't claim a generic LLM judge solves it — they'll know that's false. |
| **QRT** | **Reproducibility + cost + audit:** a "show me the exact bad step, the verdict, and what we did about it" panel; per-(model × task) reliability scores; measured cost savings. | *"Every intervention is logged and replayable — here's the step that went wrong, the check that caught it, and the fix. Reproducible and auditable."* | This is your warmest judge (advisor already validated). Give him the audit/replay panel and the cross-provider reliability DB explicitly. |
| **Hugging Face / OpenArm** | Open core, vendor-neutral, self-hostable, no lock-in. | *"Drop-in proxy, keep your own key, open core, runs on open/Chinese models too — zero lock-in."* | Don't sound like a closed SaaS gateway. Emphasize self-host + open core (see `GTM.md`). |

---

## 4. The 3–4 moves that win THIS room

These are the concrete things to actually do on stage. Each maps to the anxiety in §2 and the judges in §3.

### Move 1 — Open by naming the silent-failure pain, then show the live catch
Don't open with "we cut your AI bill" (that lands as a router/FinOps tool — the **loser's framing** in a room full of infra people). Open with the fear they all share: *"Agents fail silently — confident, well-formatted, wrong, HTTP 200, and nobody knows."* Then **run the live demo** where a cheap model fails on a checkable step and **Assay catches and fixes it in real time.** The live catch-and-fix is the magic moment — see `info/SOURCE-OF-TRUTH.md` §16 and the demo plan.

**Why it wins:** turns every judge's private anxiety into "oh — they fixed it." Active beats passive.

### Move 2 — Make the verifier deterministic and audience-checkable (no AI judging AI)
Demo on a **verifiable step type** — code that runs, schema that validates, a tool call with checkable args, a citation that either resolves or 404s. The verdict must be something a judge can confirm **with their own eyes**, not a "95%" Assay computed about itself.

**Why it wins:** the Mistral/Genesis/Datadog engineers will immediately ask "isn't this just an LLM grading an LLM?" — and the research says naive LLM-judges are near-random on silent failure. Pre-empt it: *"No AI judging AI — we check against reality."* This is also Assay's honest, defensible scope (`SOURCE-OF-TRUTH.md` §6).

### Move 3 — Answer "won't the labs absorb this?" with receipts, then state the cross-provider moat
This is the question Dessaigne *will* ask. Don't hand-wave. Have the receipts ready:
- A model lab only ever improves **its own** model — it will never tell you to use a competitor's cheaper one. **Cross-provider is the moat.**
- **OpenAI is deprecating its own Evals platform** (shutdown ~Nov 2026) and pointing users to third-party tools.
- **Anthropic endorses third-party evals** and says they get *harder* as models improve.
- **"You can't grade your own homework"** — independent assessment is the direction of travel.
- Precedent: **AWS ships CloudWatch; Datadog is still huge.** A first-party tool doesn't kill the independent one.

**Why it wins:** converts the single biggest "this is a feature, not a company" objection into proof of a durable, independent category. (See `SOURCE-OF-TRUTH.md` §8.)

> ⚠️ **Do NOT** anchor this to a specific EU AI Act deadline. The "independent assessment is coming" tailwind is real and worth one line, but the specific timing has slipped — use it as direction, not as a dated mandate.

### Move 4 — Close on cost as PROOF, not as the pitch
End with the measured result: **cheap model + Assay ≈ expensive-model reliability at a fraction of the cost** (the `reliability.py` cascade: cheap=1, strong=50; escalate **only the bad step**). Show it as **cost-per-completed-task**, not per-token, so the number survives scrutiny. Tie it to the business model: **pay-from-savings** (`GTM.md`) — "save you nothing, you pay nothing" is the easiest yes a YC partner can imagine.

**Why it wins:** cost is the *proof* that the reliability works, and pay-from-savings is the cleanest ROI story. It lands the company question (Dessaigne) and the cost/audit question (QRT) at the same time. Leading with cost would have lost the room; closing with it wins it.

---

## 5. One-sentence framing to drill before the pitch

> **"Gateways route and retry on errors; observability tells you after the fact; Assay watches each step's output, cheaply decides it's wrong, and fixes that step at runtime — on any model."**

If a judge remembers one sentence, make it that one. It positions Assay against everything else in the room (routers, gateways, eval/observability tools) in a single breath, and it centers the moat: **runtime, per-step, cross-provider correction.**

---

## 6. Quick "don'ts" for this room

- **Don't** lead with cost / "cut your bill" — it reads as a router and invites the commodity rebuttal.
- **Don't** pitch routing as the innovation — routing is solved/commoditized; runtime per-step **correction** is the new thing.
- **Don't** claim "verification is always cheaper than generation" — it's true for **checkable** steps; say so and demo there.
- **Don't** demo on a taste/fuzzy task where correctness is arguable — the thesis visibly breaks on stage.
- **Don't** rely on an LLM judging an LLM in the demo — these judges know that's near-random on silent failure.
- **Don't** pin the pitch to a dated regulatory mandate — use "independent assessment is coming" as tailwind only.

---

*Cross-references: `info/SOURCE-OF-TRUTH.md` (canonical), `VISION.md`, `GTM.md` (business model + open core), `reliability.py` (the cascade you're demoing), and the demo plan in `SOURCE-OF-TRUTH.md` §15–16.*