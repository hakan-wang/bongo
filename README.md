# Bongo

**Run the cheap model. Bongo makes it reliable.**

You pick your own AI model. Bongo sits in front of it, **watches every step** of your agent,
**catches when the model is wrong** — even when it fails silently (looks fine, nothing crashes,
the answer is just inaccurate) — **pinpoints what broke**, and **fixes it**: it escalates only
that one step to a stronger model (on any provider), or tells you how to improve. You keep the
cheap model's price and get the expensive model's reliability.

> **Not a router.** OpenRouter and friends pick a model *for* you. Bongo does the opposite —
> you keep the model you chose, and Bongo catches when it's wrong, mid-run, per step.
> The moat: **cross-provider + in-the-loop + per-step** — a model lab only improves its own model.

Built at Paris Builds (Unaite × Y Combinator).

## Try it in 30 seconds (no keys, offline)
```bash
python3 demo/server.py     # open http://localhost:8200 and click "Run the demo"
```
A cheap coding agent fails a test silently; Bongo runs the real tests, catches it, and
escalates only that step to a stronger model on another provider → red turns green.
**Cheap ~67% reliable → cheap + Bongo = 100%, ~62% cheaper than the expensive model.**

See **[`QUICKSTART.md`](QUICKSTART.md)** to connect your own workflow.

## Repo map
- **[`QUICKSTART.md`](QUICKSTART.md)** — run the demo, see the real proof, connect your API.
- **[`TEAM-BUILD-PLAN.md`](TEAM-BUILD-PLAN.md)** — what's left + the work split (**Filip: start here**).
- **[`info/`](info/)** — strategy, judges, competitors, technical playbook, pitch (start at `info/SOURCE-OF-TRUTH.md`).
- `demo/` — the reliability demo + the real cross-provider proof:
  - `scenarios.py` — real deterministic verifier (runs tests) + the cheap→verify→escalate loop + checker registry.
  - `server.py` / `index.html` — the previewable dashboard (`:8200`).
  - `gateway.py` — the wired "point your `base_url` at Bongo" path (`:8129`, OpenAI-compatible, mock by default).
  - `real_proof.py` — ONE genuinely-real Mistral→Anthropic escalation (needs keys; `--mock` to dry-run).
  - `providers.py` — shared cross-provider call shapers.
- `reliability.py` — the core reliability-loop logic (cheap → verify → escalate).
- `proxy.py` + `dashboard.html` + `demo_traffic.py` — the cost/caching side (a kicker, ~70% bill cut on repeated traffic), `:8128`.

## Honest status
The on-stage demo's model outputs are **pinned** (deterministic, so it always works); the
**verification is real**. `demo/real_proof.py` is the un-pinned, genuinely-real cross-provider
proof. `demo/gateway.py` is a working mock of the connect path (flip `BONGO_REAL=1` + keys for
real calls). Full production "point at any workflow" is the next milestone — see `TEAM-BUILD-PLAN.md`.
