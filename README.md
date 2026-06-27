# Bongo

**Run the cheap model. Bongo makes it reliable, and cuts your bill.**

Bongo is a drop-in layer that sits between your app and the LLM API. Change one line (the base URL), keep your own key. Bongo watches every step of a multi-step agent, catches the cheap model's mistakes, corrects them, and stops you paying twice for the same tokens. Independent and cross-model (Gemini, OpenAI, Anthropic, open models).

Built at Paris Builds (Unaite hackathon).

## Repo
- `VISION.md` — what Bongo is, the core insight, objections answered.
- `PLAN.md` — living build plan and open decisions.
- `proxy.py` — v0 cost proxy (OpenAI-compatible, caching, savings tracking). Runs offline in mock mode.
- `dashboard.html` — live savings dashboard.
- `demo_traffic.py` — sample agent traffic that shows the bill being cut.
- `docs/` — background research and hackathon context.

## Run the v0
```
python3 proxy.py        # serves http://localhost:8128 , dashboard at /
python3 demo_traffic.py # in another terminal, sends sample traffic
```

## Status
Cost layer works (about 70% bill cut on repeated agent traffic). The reliability core (watch, catch, correct cheap-model errors) is the main feature and is next.
