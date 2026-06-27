# Positioning — Council Verdict

> **What this doc is.** A decisive synthesis of the POSITIONING council (a multi-advisor
> debate on Bongo's one-sentence pitch). It answers one question: **what is the first sentence
> out of our mouths on stage, and why.** Read this with `info/SOURCE-OF-TRUTH.md` (the product)
> and `VISION.md` open — this doc refines *how we say it*, it does not change *what we built*.
>
> _Audience: the whole team, including non-technical readers. If you only read one section,
> read "The Verdict" and "The One Tension You Must Know."_

---

## TL;DR (the verdict in four lines)

1. **Lead sentence:** *"Bongo is the independent reliability layer that catches and fixes an AI
   agent's bad steps in real time — so a cheap model runs as reliably as an expensive one, on
   any provider."*
2. **Lead with reliability + independence. Show cost as the PROOF, never as the headline.**
3. **Demo only on checkable steps** (code, tool calls, structured output) so the claim never
   breaks on stage.
4. The strongest dissent isn't about the words — it's that an over-broad promise hands the
   engineer-judges a kill-shot. The fix is in the wording itself (see below).

---

## The Verdict — our one sentence

> ### "Bongo is the independent reliability layer that catches and fixes an AI agent's bad steps in real time — so a cheap model runs as reliably as an expensive one, on any provider."

This is the sentence to drill and repeat. It does three jobs at once, which is exactly why it
won the council over every alternative:

- **Outcome (lands with the buyer / GP):** "cheap model as reliable as expensive, on any
  provider" = save money, stay safe. A non-technical decision-maker gets it in five seconds.
- **Mechanism (lands with the engineers):** "catches and fixes bad steps in real time" =
  active, per-step, runtime correction — not another passive eval dashboard.
- **Moat (answers the obvious attack):** "independent / any provider" = vendor-neutral, the
  cross-provider layer no single model lab will ever build, and the "you can't grade your own
  homework" point.

Crucially, it claims **reliability**, not "verification is free." That one word choice is what
lets the sentence *survive* the inevitable judge question "is verification really cheaper than
generation?" instead of dying on it.

### How it relates to our current canonical line

`SOURCE-OF-TRUTH.md §1` and `VISION.md` currently lead with **"Run the cheap model. Bongo makes
it reliable, and cuts your bill."** That line is the right *product*, but the council says the
**order of emphasis on stage is wrong**: "cuts your bill" / "cheap model" first triggers the
"this is just a router/FinOps tool" reflex. The verdict keeps every element of the canonical
promise — it just **reorders** them so reliability + independence lead and cost becomes the
proof slide. This is the recommended resolution to `SOURCE-OF-TRUTH.md §14, open decision #1`
("make cheap models reliable" vs "cut your bill" → **combined, reliability-first, cost as proof**).

---

## Backups (use if the room or judge mix calls for it)

Ranked. Each is safe to say; pick by audience.

**Backup 1 — the contrast line (best for an engineer-heavy room).**
> *"Gateways route and retry on errors; observability tells you after the fact; Bongo watches
> each step's output, cheaply decides it's wrong, and fixes that step at runtime — on any model."*

- **Lands with:** Datadog / Mistral / QRT engineers, Dessaigne. It draws the category boundary
  explicitly and signals we know the competitive map (routers, observability) cold.
- **Use when:** someone has just name-dropped OpenRouter, Portkey, LiteLLM, Arize, or Raindrop,
  or asked "how is this different from X."

**Backup 2 — the tightest version of our existing line (best for a fast/noisy room or a CEO).**
> *"Bongo makes a cheap model behave like an expensive one — and we fix it live, across any provider."*

- **Lands with:** the YC GP and any outcome-focused buyer. Closest to `VISION.md`'s framing, so
  it's consistent with the rest of our materials.
- **Use when:** you have five seconds, or the listener is non-technical.

**Backup 3 — the category claim (use sparingly, only once credibility is established).**
> *"Bongo is the independent reliability/QA layer for AI agents."*

- **Lands with:** investors thinking about defensibility and TAM; nods to the EU AI Act /
  independent-assessment tailwind.
- **Risk:** said *cold*, it reads passive (the Arize/Braintrust/Raindrop lane). Only deploy it
  **after** the live demo has shown active correction, never as the opener.

---

## What NOT to say (the council was unanimous on these)

These are the framings that lose the room. Avoid them as the *lead*:

- ❌ **"Cut your AI bill" / "save 70% on LLM costs"** as the headline. Judges instantly file us
  next to routers (RouteLLM, OpenRouter Auto, FrugalGPT) — a commoditized category that GPT-5
  ships natively. This is "the loser's framing." Cost is our **proof slide**, not our pitch.
- ❌ **"We make any cheap model reliable" / "we fix the model anywhere."** Over-promises the
  unsolved core. It invites the engineers to point out that verification is *conditional*
  (it collapses on open-ended steps), making our deliberately-narrow demo look like
  cherry-picking. Claim reliability **on checkable steps**, not universally.
- ❌ **"The trust / insurance layer for the agent economy."** Grand, unfalsifiable VC-poetry.
  The CEO can't picture a product; the engineer tunes out. No proof of pull behind it.
- ❌ **Do NOT pin the pitch to EU AI Act timing.** The high-risk deadline slipped (now ~Dec 2027,
  not Aug 2026). Use "independent assessment is coming" as a *tailwind*, never as the timing hook.

---

## The One Tension You Must Know (the strongest dissent)

Every advisor converged on the *words*, but the sharpest dissent — the thing most likely to
sink us — is **not** about phrasing. It's this:

> **An over-broad promise hands the YC/Datadog/Mistral judges a kill-shot.**
> Our core bet — "verification is cheaper than generation" — is *conditional, not universal*.
> It holds for checkable steps (code runs, schema validates, tool output is well-formed) and
> **breaks** on open-ended/creative steps. If our one-liner implies we can fix *any* model
> *anywhere*, then a demo scoped to narrow verifiable tasks looks like we're hiding the weakness,
> and an engineer judge can make the whole thesis visibly collapse on stage.

**Why we don't just ignore the dissent:** it's correct, and our own verification research
([the claim was rated only *conditionally* supported]) backs it. A naive "ask another model if
this looks right" verifier is near-random on silent failures — the judges may know this.

**How the verdict already absorbs the dissent (this is the important part):**

1. **The wording is defensive by design.** We say a cheap model runs *as reliably as* an
   expensive one (a checkable outcome), **not** "verification is free." The claim is about the
   *result*, scoped, not the magic.
2. **Scope the demo to verifiable step types** — code, tool calls, structured output, math,
   citation-exists. This is already the team's lean (`SOURCE-OF-TRUTH.md §6, §16`). Where the
   check is deterministic ("check against reality, not another AI's opinion"), the catch-and-fix
   is *visibly true* and un-riggable.
3. **State the boundary out loud, first.** Naming the regime ("this works where steps are
   checkable — which is where production agents actually run") is a *strength* signal to
   engineers, not a weakness. Pre-empting the attack defuses it.
4. **Report cost-per-COMPLETED-task, not per-token.** Honest net savings on a real workload,
   so the cost-proof survives scrutiny (and tokenizer-difference gotchas across providers).

> **Bottom line of the dissent:** the danger isn't the sentence — it's *over-claiming around* it.
> Say the scoped sentence, demo on checkable steps, name the boundary, and the kill-shot misses.

---

## Why "independent" is the load-bearing word

Worth calling out because it's easy to drop under stage pressure. "Independent" does double duty
and is the word the engineers respect most:

- **Vendor-neutral / cross-provider** = the moat. A model lab only ever sharpens *its own* model;
  it will never tell you "use the competitor's cheaper one." Bongo sits above all of them.
  (A QRT advisor confirmed this is exactly why he'd use it — `SOURCE-OF-TRUTH.md §3, §8`.)
- **"Can't grade your own homework"** = the durability answer. Independent assessment is the
  direction the whole industry is moving (OpenAI deprecating its own Evals platform; Anthropic
  endorsing third-party evals). Datadog thrives even though AWS ships CloudWatch.

Keep "independent" in the sentence every time. It's not a filler adjective — it's the moat and
the durability rebuttal in one word.

---

## Delivery checklist (tape this to the laptop)

- [ ] Open with the verdict sentence. Reliability + independence first. **Never** "cut your bill" first.
- [ ] Demo on a **checkable** step type (code agent is the team's bulletproof lean).
- [ ] Name the boundary out loud — "works where steps are checkable" — *before* a judge asks.
- [ ] Use cost as the **proof** slide: "Flash + Bongo matches Pro at ~Nx less," cost-per-completed-task.
- [ ] Keep the word **"independent"** in the sentence.
- [ ] Have **Backup 1** (the contrast line) loaded for any "how is this different from \[router/eval tool]" question.

---

## Council confidence

The advisors converged with **~7/10 confidence** on the verdict sentence and emphasis order. The
agreement was strong on *what to avoid* (cost-first, over-broad "fix any model," vaporware
"trust layer," EU-Act timing) and on the defensive wording; the residual uncertainty is the
universal tension above, which the demo scoping is designed to neutralize rather than eliminate.
