# Plumbline — Demo Example Choice

> **Purpose:** Pick the ONE workflow we demo on stage. This replaces **Brolly** (Håkan's
> video editor) as the *public* example. Brolly stays as an internal story, but it is not
> what we show the judges.
> **Reconciles with:** the team's "code agent" lean (`SOURCE-OF-TRUTH.md` §15, §16) and the
> deterministic-checker principle already coded in `reliability.py`.
> **TL;DR decision:** Primary = **a code agent that writes a function + tests** (auto-checkable,
> bulletproof). Backup = **structured data extraction** (the exact `check_meeting` logic
> already in `reliability.py`). Both are universal, both verify cheaply, both wow.

---

## 1. Why not Brolly

Brolly is a great *internal* origin story but a weak *stage* example, for three reasons:

1. **Nobody in the room knows it.** Judges (a YC GP, Datadog/Mistral/Genesis/QRT engineers)
   have to spend mental budget understanding "a video-editing agent" before they can even
   see the point. The example should be understood in one sentence.
2. **Taste is not cheaply verifiable.** "Is this the best clip?" has no deterministic right
   answer. That collides head-on with our hard technical core (`SOURCE-OF-TRUTH.md` §6):
   we win *because* we check against reality, not against another AI's opinion. Demoing on a
   fuzzy-taste task hands an engineer judge the exact "you're just an LLM judging an LLM"
   rebuttal — the one objection we most need to avoid.
3. **It looks niche.** It reads as "a tool for Håkan's app," not "a layer every agent team
   needs." The demo must say *universal*.

Brolly still earns one line in the pitch as proof we use this ourselves ("we built this
because our own video agent on Gemini kept failing silently"). It is not the live demo.

---

## 2. What a winning demo example must have (the ranking criteria)

We score candidates on four axes, in priority order:

| Axis | What it means | Why it matters |
|------|---------------|----------------|
| **Cheap verifiability** | Can Plumbline tell a step is wrong *deterministically, without knowing the answer in advance*? | This is the whole technical bet (`SOURCE-OF-TRUTH.md` §6). If the check needs an LLM judge, the demo's credibility breaks. Non-negotiable. |
| **Resonance** | Does the room understand it in one sentence, and is it a workflow the judge companies actually run? | A YC GP + Datadog/Mistral/Genesis/QRT engineers must instantly see themselves in it. |
| **Wow** | Does the cheap model *visibly* fail, and does Plumbline *visibly* catch and fix it live, with a real cost gap? | The stage moment is "watch it break, watch Plumbline save it." |
| **Breadth** | Does it imply "this works for any agent," not "this works for one toy task"? | We're selling a horizontal layer, not a point solution. |

The key tension the criteria resolve: **the most resonant examples (broad agents) are the
hardest to verify cheaply; the easiest-to-verify examples can look like toys.** The winner
is the example that is *both* universally understood *and* deterministically checkable. That
is exactly the "code agent" sweet spot the team already leans toward.

---

## 3. Candidate ranking

### Ranked shortlist

| Rank | Example | Cheap verifiability | Resonance | Wow | Breadth | Verdict |
|------|---------|--------------------|-----------|-----|---------|---------|
| **1** | **Code agent** (write function → run unit tests) | **Bulletproof** — test passes or fails | High — every team here ships code agents | High — red test → green test, live | High — "any code agent" | **PRIMARY** |
| **2** | **Structured data extraction** (text → strict JSON schema) | **Bulletproof** — schema validates or doesn't | High — extraction/tool-calls are everywhere | High — invalid JSON → valid, live | High — "any tool-calling agent" | **BACKUP** |
| 3 | Support RAG (answer with citations) | Medium — can check the cited source *exists*, not that it's the *best* answer | Very high — relatable | Medium — partial check only | High | Strong narrative, weaker live check |
| 4 | Math / financial calc (compute a number) | High — recompute deterministically | Medium — narrower | Medium | Medium | Good but narrower than code |
| 5 | Brolly / video clips (taste) | **Low** — pure taste isn't checkable | Low — niche | Low | Low | Cut from stage |

### Why code wins (#1)

- **Verifiability is perfect and visceral.** A unit test is the canonical "check against
  reality, no AI judging AI." Either the code runs and passes, or it doesn't. There is zero
  room for a judge to say "but how do you *know* it's wrong?" — they can read the failing
  assertion on the screen.
- **It's the judges' own world.** Software-for-Agents track; the room is engineers. Code
  agents are the single most-deployed agent type. They've all seen a cheap model produce
  confident, almost-right, broken code.
- **The cost gap is the cleanest story.** "Flash wrote code that failed the test. Plumbline
  retried with the failure as guidance, then escalated *only that step* to the strong model.
  Final: passing code, at a fraction of running everything on the expensive model." That's
  the `reliability.py` cascade (cheap → retry cheap → strong fallback; cost 1 vs 50) made
  visible.

### Why extraction is the backup (#2)

- It is the **already-built path.** `reliability.py`'s `check_meeting` is exactly this:
  extract `{title, date, attendees[], duration_min:int}` and validate fields, types, and
  constraints deterministically. Zero new verifier code needed — lowest demo risk.
- Equally bulletproof (schema validates or it doesn't), equally universal (every
  tool-calling / extraction agent), slightly less "wow" than a red→green test, but a
  rock-solid fallback if the code sandbox is flaky on the day.

### Reconciling with the team's "code agent" lean

This is **not a reversal** of the team's direction — it confirms it. `SOURCE-OF-TRUTH.md`
§14.2 and §15 already lean code because right/wrong is auto-checkable. This doc just makes
the call explicit and pairs it with the extraction example (which we already have working in
`reliability.py`) as a de-risked backup that runs on the same engine.

---

## 4. The exact demo workflow (primary: code agent)

A small multi-step coding agent runs on a **cheap** model. Plumbline sits in front of it (one
line: change `base_url`, keep the key). We show the same task twice — once raw, once through
Plumbline — side by side.

**The task (kept tiny so it's read in 5 seconds on screen):**
> "Write a Python function `merge_intervals(intervals)` that merges overlapping intervals,
> plus return it as a passing solution." We ship a fixed hidden test suite Plumbline runs.

**The agent's steps:**
1. **Plan** — outline the approach.
2. **Generate** — write `merge_intervals`.
3. **Self-check** — produce/return the function for testing.

**Run A — cheap model alone (the failure):**
1. Cheap model writes `merge_intervals` — but botches an edge case (e.g. adjacent/touching
   intervals, or an off-by-one on the sort/merge boundary).
2. **No error is thrown.** The code is well-formatted and looks right. This is the silent
   failure (`SOURCE-OF-TRUTH.md` §2) — the whole point.
3. We run the hidden tests on screen: **one assertion fails, red.** The raw cheap model
   shipped broken code and didn't know.

**Run B — cheap model + Plumbline (the save), live:**
1. **TRACE** — Plumbline captures the generate step (input, output, model, tokens, cost).
2. **VERIFY** — Plumbline runs the unit tests against the generated code. Deterministic. The
   test fails → Plumbline *knows the step is bad*, without an LLM judge, without knowing the
   answer in advance. **This is the moment to narrate: "verification is cheaper than
   generation — running a test costs nothing next to writing the code."**
3. **INTERVENE — step 1, retry cheap with guidance:** Plumbline re-runs the *same cheap model*,
   feeding back the exact failing assertion as guidance ("test X failed: input …, expected …,
   got …"). Often the cheap model fixes it for ~1 more cheap unit.
4. **INTERVENE — step 2, escalate just this step (if retry still red):** Plumbline falls back to
   the **strong model for this one step only** — not the whole workflow. Tests go **green.**
5. **LEARN** — Plumbline logs the failure + fix to the reliability database (the moat).

**The dashboard / scoreboard (the wow):** show three columns side by side, ideally as a
live counter:
- **Strong model, every step:** passes, but cost = high (e.g. ~50 units/step).
- **Cheap model alone:** cheap, but **tests fail** (broken).
- **Cheap + Plumbline:** **tests pass** AND cost ≈ cheap (a couple of cheap units, with at most
  one escalated step), i.e. a fraction of the all-strong bill.

**Headline line (already in `SOURCE-OF-TRUTH.md` §16):**
> "Pro-level reliability at Flash-level price."

**De-risk the live moment:** let a judge pick which of two pre-staged tasks runs, and show
the raw provider responses via the proxy so it's clearly not faked. Keep the failing
assertion visible on screen — the audience verifies the verdict with their own eyes, not our
score.

---

## 5. The exact demo workflow (backup: structured extraction)

Identical loop, runs on the existing `reliability.py` engine — **no new verifier code.**

**The task:** "Extract this meeting invite into `{title, date, attendees[list],
duration_min:int}`." (This is literally `check_meeting`.)

1. **Run A — cheap alone:** cheap model returns JSON that's *almost* right — e.g. `attendees`
   as a comma-separated string instead of a list, or `duration_min` as `"60"` (string) not
   `60`, or a missing field. Looks fine; silently wrong.
2. **Run B — cheap + Plumbline:**
   - **VERIFY:** `parse_json` + `check_meeting` flag the exact problem ("`attendees` must be
     a non-empty list" / "`duration_min` must be an integer"). Deterministic.
   - **INTERVENE:** retry cheap with the reason as guidance → if still bad, escalate that one
     step to the strong model.
   - **Result:** valid object, schema-clean, at near-cheap cost.
3. **Scoreboard:** same three-column cost-vs-correctness story as the code demo.

Use this if the code sandbox is unreliable on the day, or as a fast second example to prove
**breadth** ("same engine, totally different task — code *and* tool-calls").

---

## 6. What to say about the limits (honesty = credibility)

Pre-empt the obvious engineer question by being explicit on stage:

- We demo **verifiable step types** (code, structured output, tool calls, math, retrieval)
  on purpose — that's where deterministic checking is bulletproof and where production
  agents actually live.
- **Pure-taste steps** ("is this the best clip?", "is this prose good?") are the frontier;
  even there, the *checkable* parts (valid format, timestamps that exist, count/length
  constraints) can still be guarded. We say this plainly rather than overclaim — which is
  exactly the `SOURCE-OF-TRUTH.md` §6 stance.

This framing turns the one hard question ("can verification really be cheaper than
generation everywhere?") into a controlled answer: *not everywhere, but everywhere that
matters for real agents — and that's what we demo, live, checkable by you.*

---

## 7. Decision summary (for the team)

- **Primary stage example:** code agent (write function → run unit tests). Replaces Brolly.
- **Backup / breadth example:** structured extraction via existing `reliability.py`
  `check_meeting`. Zero new verifier code.
- **Brolly:** one origin-story line in the pitch, not the live demo.
- **Owner handoff:** Tech 1 (engine) wires the code sandbox + test runner into the
  `reliability.py` cascade; Tech 2 (surface) wires the three-column scoreboard into
  `dashboard.html`; Michelle owns the side-by-side stage choreography; Håkan delivers the
  "watch it break, watch Plumbline save it" beat.
