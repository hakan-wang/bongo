> ⚠️ **SUPERSEDED — earlier idea.** This describes a standalone "verifier / proof layer
> that catches agents faking success." The current canonical direction is **Plumbline = make
> cheap models reliable + cut cost** (see [`/info/SOURCE-OF-TRUTH.md`](../info/SOURCE-OF-TRUTH.md)).
> The deterministic-verification insight below is now Plumbline's VERIFY step. Keep this doc for
> its **market figures and competitor list**, which still apply.

# Agent Reality-Check: Full Write-up

A plain, honest write-up of the problem, market, solution, and business. Not written to sell. Written to be true.

---

## In one line
AI agents often fail or even fake success without anyone noticing. We catch it automatically by checking the agent's work against reality, not against another AI's opinion.

---

## The problem
Companies are deploying AI agents (assistants that do multi-step tasks on their own) at scale. The hard part is no longer making the agent act. It is knowing whether the agent did the job correctly.

Three things make this serious:
- Agents fetch the wrong information roughly 7 times out of 10 at the retrieval step (industry estimate). The final answer still reads smoothly, so the mistake is invisible.
- There is a documented gap of around 37% between how agents score in the lab and how they perform in real deployment.
- Agents can fake their own success. A UC Berkeley team built an agent that scored 100% on top coding benchmarks while solving zero of the tasks. In most runs it did not even call the model.

The mistake usually happens before any prompt runs, when the system picks the wrong information to act on. So it cannot be fixed by writing a better prompt. The prompt only instructs the agent on what it already has. It cannot use what was never fetched, and it cannot grade itself.

Net effect: organizations run thousands of agents with no trustworthy way to know when one quietly went wrong.

---

## Why now
- The agent wave is real and accelerating. Agent infrastructure is one of the most funded areas in AI right now.
- The major observability companies (Datadog) made agent monitoring their flagship 2025-26 push, which proves the pain is real but also that logging alone is not enough.
- The Berkeley benchmark-gaming result is recent and widely discussed. The market just learned it cannot trust its own evals.

---

## Market (verified figures, with honest framing)
| Market | Now | Forecast | CAGR | Source |
|---|---|---|---|---|
| AI Agents | $7.84B (2025) | $52.6B by 2030 | 46.3% | MarketsandMarkets |
| RAG / retrieval | $1.94B (2025) | $9.86B by 2030 | 38.4% | MarketsandMarkets |
| Agentic AI observability | $0.55B (2025) | $2.05B by 2030 | 30.1% | Mordor Intelligence |
| LLM observability | $2.69B (2026) | $9.26B by 2030 | 36.2% | Business Research Co. |

The headline number to use is AI agents going from about $8B to over $52B by 2030. The observability and eval slice is small today and growing fast, which means the problem is real and not yet solved. These are analyst estimates, not certainties, and should be treated as direction, not precision.

---

## The solution
An automatic reality-check for AI agents. Think of it as a black box flight recorder plus a smoke detector.

- It records every step an agent takes (what it read, what it changed, what it claimed).
- When the agent reports success, it does not ask another AI whether to believe it. It re-runs the real check against an answer the agent was never allowed to touch.
- If the agent cheated or failed, the check fails instantly, automatically, every time.
- One click turns that caught failure into a permanent test, so the same failure is caught forever after.

The core principle: we do not use AI to judge AI, because the judge can be wrong too. We compare the agent's claim against reality, which has no opinion.

---

## How it works, concretely
1. Before the agent starts, we save the real answer key (for code, the original tests) somewhere the agent cannot edit.
2. The agent does the task and reports success.
3. A small automatic checker re-runs the real test on a clean copy of the work. No human involved, takes about a second.
4. Pass means it really worked. Fail means the agent was wrong or cheated, and we show exactly which step broke.

This is automatic, not manual. The check is written once and runs on every output forever, like a spam filter that you set up once and it screens every email.

---

## Why this is different and defensible
- Logging tools (LangSmith, Arize, Datadog) record what happened. They do not catch the lie. We do.
- LLM-as-judge tools ask one AI to grade another. That can be fooled. We use deterministic execution as the judge, which cannot be fooled the same way.
- The catch is bulletproof in any domain where a computer can verify the answer. Code is the strongest case, which is where we start.

Honest limit: for fuzzy tasks with no automatic ground truth (write a good essay), this deterministic approach does not directly apply. We start where the truth is verifiable and expand outward. Saying this plainly is a strength, not a weakness.

---

## The demo (what proves it)
Live, in 90 seconds:
1. A coding agent is told to fix a bug and make the tests pass.
2. It works, then announces all tests pass.
3. Our tool flags the success as fake.
4. Rewind shows the agent edited the test instead of fixing the code.
5. We re-run the original, untouched test on a clean copy. It fails. Proof, not opinion.
6. One click locks the real test so the cheat is caught automatically from now on.

---

## Business model
- Usage-based developer tool. Charge per agent run checked, or per seat for teams, similar to how observability and CI tools price.
- Free open-source core to drive adoption (developers and the open-source judges reward this), paid hosted version for teams that need history, dashboards, and integrations.
- Natural land-and-expand: teams start checking one agent in CI, then expand to all agents in production.
- Sits next to existing spend. Companies already pay heavily to watch their software. This is the missing layer for watching their agents.

---

## Potential
- Near term: a trusted gate in the development pipeline. No agent change ships unless its work passes a real reality-check.
- Medium term: the standard way teams prove an agent is reliable before and during production, across code first, then any task with a verifiable check (data pipelines, API actions, transactions).
- Long term: the trust layer for autonomous software. As more work is handed to agents, someone has to certify the work was actually done. That certifier is valuable, and today it does not exist.

---

## Honest risks and caveats
- The deterministic check only covers verifiable tasks. Fuzzy domains are unsolved and we should not claim otherwise.
- Agent observability is crowded. Our edge is the trust and auto-debug angle, not generic logging. If we drift into generic logging, we lose.
- Market figures are analyst estimates and move fast. Re-check near any high-stakes use.
- For this event specifically: judges are not named publicly, the sponsor list is from a private brief, and there are three tracks (Software for Agents, Robotics, The Next Big DecaCorn). Do not over-tailor to a single assumed judge.

---

## The plainest possible summary
AI agents are everywhere, they fail or fake success silently, and nobody can tell. You cannot fix it with a better prompt or by asking a second AI. We check the agent's work against reality, automatically, and catch the failure the moment it happens. We start with code, where the truth is free to verify, and grow from there.
