# Assay — Quickstart

**Assay makes a cheap AI model reliable.** You pick your model; Assay watches every step of
your agent, catches when the model is wrong, and fixes it — by escalating only the broken step
to a stronger model (on any provider), or telling you how to improve. It is **not a router**:
you keep the model you chose.

Everything below runs offline (Python 3, stdlib only — **no `pip install`, no keys** to start).

---

## 1. See the demo (30 seconds, no keys)
```bash
python3 demo/server.py
# open http://localhost:8200  and click "Run the agent"
```
A cheap agent runs a finance step and silently wires the wrong amount (a 10× notional). Assay
catches it against the trade's real arithmetic, walks the recovery ladder (retry → escalate
cross-provider), and ends correct. Scoreboard: cheap **60%** → **cheap + Assay = 100%, 74% cheaper**.

## 2. See a real cross-provider catch (needs keys)
```bash
python3 demo/real_proof.py --mock     # dry-run the narrative, no keys
# then, with keys set (see .env.example):
python3 demo/real_proof.py            # real Mistral -> Anthropic escalation
```

## 3. Connect your own workflow (the product)
Point your OpenAI-compatible client at the Assay gateway and keep your own key:
```bash
python3 demo/gateway.py               # http://localhost:8129/v1  (mock by default)
```
```python
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8129/v1",   # <- the only change
    api_key=YOUR_KEY,                        # your key, passes through
)
# optional: tell Assay how to check this step (zero-config 'format' is the default)
resp = client.chat.completions.create(
    model="mistral-small",
    messages=[{"role": "user", "content": "..."}],
    extra_body={"assay": {"checker": "format"}},
)
print(resp.assay)   # what Assay caught / fixed / advised
```

**How does Assay know YOUR step is wrong if you have no unit tests?** You bring a check, or use
a zero-config one. Built-in checkers: `format` (valid/non-empty — the default), `schema-from-example`
(paste one good output), `json-schema`, `tool-args`, and `llm-judge` (fuzzy fallback, lower
confidence — we lead with the deterministic ones).

---

## Honest status (mid-build)
- The on-stage demo's **model outputs are pinned** (deterministic) so it always works; the
  **verification is real** (it runs the tests). The one un-pinned, genuinely-real artifact is
  `demo/real_proof.py`.
- `demo/gateway.py` is a working **mock** of the connect path; flip `ASSAY_REAL=1` + keys to
  make the calls real. Pointing it at an arbitrary production workflow end-to-end is the next
  milestone, not done yet.
- `localhost:8129` shown in some screens is **aspirational** — the real local endpoint is
  `http://localhost:8129/v1`.
