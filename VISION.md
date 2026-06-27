# Bongo (working name)

## One line
**Run the cheap model. Bongo makes it reliable, and cuts your bill.**

## The core insight
Today developers pay for the expensive model (e.g. Gemini 3.5 Pro) because they cannot trust the cheap one (e.g. Gemini Flash). The cheap model is 10 to 50x cheaper but makes more mistakes, and worse, when it makes a mistake nobody knows.

Bongo sits between an app and the LLM API, watches every step of a multi-step agent, catches the cheap model's bad steps, and corrects them. Result: a cheap model performs like an expensive one. You stop overpaying for reliability you can get another way.

## What Bongo is
A drop-in layer (one line: change the base_url, keep your own key). It is:
1. **Independent** of any model vendor. It works across Gemini, OpenAI, Anthropic, open models. A model maker will only ever make its own model better. Bongo sits above all of them. (This is also the answer to "why won't a big LLM company build it" — they would only do it for their own agent. Confirmed by a QRT advisor.)
2. **Runtime, in the loop.** It watches and fixes while the agent runs, not just a dashboard after the fact.
3. **Multi-agent / multi-API.** It can watch many agents and many APIs at once, not one.

## Main feature: reliability (watch, catch, correct)
For a multi-step agent workflow, Bongo traces each step, detects when a step went wrong, and helps it recover (retry with guidance, supply missing info, or fall back to a stronger model just for that step). The point: make a cheap, error-prone model trustworthy enough to use in production.

## Side feature: cost + comparison
Because Bongo sees every step and its quality, it can:
- Tell you where you are overpaying (e.g. "you are using Pro where Flash + Bongo would do").
- Compare reliability across APIs as it gathers data, and suggest cheaper or better ones for a given job.

## The hard question (the real technical core)
"Watch every step and catch the bad ones" only works if Bongo can tell a step is wrong. How it knows depends on the domain:
- **Verifiable steps (start here):** code (run the test), structured output (validate the schema), tool calls (did it return valid data), math (recompute), retrieval (does the cited source exist). Here the check is deterministic and bulletproof. No AI judging AI.
- **Fuzzy steps (harder):** "is this the best video clip" has no clean right answer. For these, even the parts that ARE checkable (valid output format, timestamps that exist in the video, clip count and length constraints) can be guarded deterministically, while pure taste cannot.

Strategy: lead with verifiable steps and structured checks. Be honest that pure-taste judgments are the frontier.

## Worked example: Brolly (Håkan's video editing app)
Brolly is a multi-step agentic workflow on the Gemini API: analyze a raw video, reason about the best clips, then cut and assemble. Bongo would:
- Trace each Gemini step.
- Catch failures that are checkable (invalid output, timestamps that do not exist, broken cuts, malformed responses) and retry or correct them.
- Let Håkan run cheaper Gemini Flash instead of Pro, because Bongo backstops Flash's mistakes.
- Tell him when Pro is overkill and Flash + Bongo is enough.

## Who needs it
Any startup or team that put an LLM API inside their product, especially with multi-step agent workflows (analyze, reason, act). They all face the same tradeoff: cheap-and-unreliable vs expensive-and-safe. Bongo removes the tradeoff.

## Objections, answered
- **Won't a big LLM company build it?** Only for their own model. Bongo is independent and cross-model. (QRT advisor confirmed this is exactly why he would use it.)
- **Does it die when models get perfect?** No. It is about the cost/reliability tradeoff and making the cheap option safe, which always matters. Framed as the proof/reliability layer, not just error-catching, it lasts.
- **Crowded (Coval, Chronicle, Respan, Arga, Roark)?** Those are dev tools to test your OWN agent before shipping. Bongo is a runtime layer that catches and corrects in production, across models, and saves cost. Different lane.
