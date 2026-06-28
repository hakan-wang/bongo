# Assay: Plan (living document)

This plan will be updated continuously as Håkan gives more clarity. Latest info always wins. Everything gets pushed to GitHub.

## Status
- [x] Empty repo created (hakan-wang/bongo)
- [x] v0 cost proxy built (`proxy.py`): OpenAI-compatible, caches repeated/near-duplicate calls, tracks tokens and dollars saved. Runs offline in mock mode.
- [x] Live savings dashboard (`dashboard.html`)
- [x] Demo traffic script (`demo_traffic.py`) — shows ~70% bill cut on agent-style traffic
- [ ] Reliability core (watch a step, detect failure, correct) — NOT built yet, this is the main feature
- [ ] Decide first domain (code vs general) — needs Håkan's call
- [ ] Wire a real API key (currently mock mode)
- [ ] Demo polish

## Open decisions (need Håkan)
1. Lead promise: "make cheap models reliable" (reliability) or "cut my bill" (cost)? Recommended: lead with the combined line "run cheap, stay reliable," show cost as the proof.
2. First domain for the demo: code agents (right/wrong is automatically checkable, bulletproof demo) vs general agents like Brolly (broader, but harder to verify). Recommended: code for the demo, vision covers all agents.
3. On catching a bad step, Assay should: alert / auto-retry the cheap model / fall back to a stronger model for that step? Recommended: retry first, fall back if still failing.
4. Real-time in the loop (block and fix before the user sees it) vs after-the-fact dashboard? Recommended: in the loop, that is the magic.

## Architecture (current + intended)
- **Proxy** (built): app points base_url at Assay, Assay forwards to the real API with the user's key.
- **Cache** (built): repeated/near-duplicate calls served free.
- **Tracer** (to build): record every step of a multi-step workflow (inputs, outputs, tool calls, cost, latency).
- **Checkers** (to build): per-step verifiers. Start deterministic: schema validation, execution, constraint checks, existence checks. These are what make "is this step wrong" answerable without another AI.
- **Recovery** (to build): on a failed check, retry with guidance / supply missing context / escalate to a stronger model for that one step.
- **Router/advisor** (side feature): recommend cheaper model + API based on observed reliability.

## Demo target (36h)
A multi-step agent runs on a CHEAP model. It makes a mistake. Assay catches it live, corrects it, and the dashboard shows: same result quality as the expensive model, at a fraction of the cost. The headline number: "Pro-level reliability at Flash-level price."

## Principles
- Independent and cross-model. Never locked to one vendor.
- Deterministic checks where possible. Avoid AI-judging-AI for the core verdict.
- One-line integration. Keep the user's own key.
- Push everything to GitHub continuously.
