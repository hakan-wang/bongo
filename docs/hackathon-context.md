> ⚠️ **SUPERSEDED — earlier idea / context recap.** Current canonical direction is
> **Bongo = make cheap models reliable + cut cost**, see
> [`/info/SOURCE-OF-TRUTH.md`](../info/SOURCE-OF-TRUTH.md). Useful here: the data points,
> market figures, competitor list, and event context.

# Paris Builds: Conversation Recap

## The event
Paris Builds by Unaite (Jun 27-28, 48 Rue Cambon). Judges: Nicolas Dessaigne (YC GP, co-founded Algolia) + people from Datadog, Mistral, Genesis AI, plus Hugging Face / OpenArm / QRT per the brief. Three tracks: Software for Agents, Robotics, The Next Big DecaCorn. Note: judges are not named publicly; sponsor list is from the brief.

## The strategy
Research the judges, build a demo for a problem they already feel, so you skip explaining the problem and spend everything on demo + pitch.

## The problem (validated, data-backed)
AI agents grab the wrong information and can fake their own success, and nobody can tell. The data is not inaccurate; the agent goes to the wrong place. You cannot fix it with a prompt (the mistake happens before the prompt). A prompt cannot grade itself.

Numbers (industry estimates, treat as direction not precision):
- Retrieval is the dominant failure point; naive RAG fetches wrong context ~40% of the time; ~73% of RAG *failures* originate at retrieval.
- ~37% gap between lab benchmark scores and real deployment.
- UC Berkeley agent scored 100% on top benchmarks while solving zero tasks (faked success).

## The market
AI agents ~$8B (2025) to ~$52B by 2030 (46% CAGR). Adjacent: RAG ~$1.9B to ~$9.9B; agent observability small and fast-growing.

## Idea 1: the verifier / proof layer (what we built a prototype of)
An independent check: when an agent claims success, re-run the real tests on a clean copy it could not touch. Verdict: VERIFIED / CONTRADICTED / CHEATED. Prototype engine built in Python (real, runs, catches a cheat) plus a polished demo page.

Open objections we hit:
1. Why won't Anthropic build it? Answer: a verifier should not be the model maker (independence, like an auditor); must be cross-model; different business.
2. Solution thin in theory? The "re-run existing tests" version is narrow. Stronger version: generate your own check the agent never sees, then run it.
3. Does it die when models get perfect? Only if framed as error-catching. Framed as the proof / accountability / audit layer, it survives (proof is about trust and liability, not error rate).
4. Crowded with YC startups: Coval, Chronicle Labs, Respan, Arga Labs, Roark, Janus, Alter, Sepal. Differentiator: independent third-party proof + deterministic execution + block at the moment of action, not another self-testing eval tool.

## New direction (current thinking)
A layer on top of the LLM API that does two things:
1. Cuts token cost (efficiency layer for anyone using an API key / GPT wrapper).
2. Improves first-time retrieval accuracy so agents fetch the right thing up front, not just verified after.

## Other ideas considered
- Auto-MCP: make any API/website usable by an agent in 60 seconds (Dessaigne's "sell to agents" thesis).
- Agent cost firewall: kill runaway/looping agents in real time (Datadog pain).
- Robot arm by voice on OpenArm (Robotics track, less crowded).
- ESG claims auditor (strong standalone, weak judge fit for this event).

## Assets built so far
- Working Python engine: /Users/michellezhang/agent-reality-check/engine/realitycheck.py
- Demo page: /Users/michellezhang/agent-reality-check/demo.html
- LOI PDF ready for Arjun (design partner).
- Google Doc write-up of problem/market/solution/business.
