"""
Assay gateway — the wired "point your base_url at Assay" path (stdlib only).

OpenAI-compatible POST /v1/chat/completions. Assay generates with your CHEAP model, VERIFIES
the step (zero-config `format` checker by default, or pass a `assay` field to choose another),
and on failure ESCALATES that step to a STRONG model on a DIFFERENT provider — returning the
corrected output plus a `assay` trace (what broke, what fixed it, cost).

This is how a real user would connect:  base_url = http://localhost:8129/v1 , keep your key.

Run:   python3 demo/gateway.py
Mock by default (no keys needed). For real calls: ASSAY_REAL=1 + MISTRAL_API_KEY + (ANTHROPIC_API_KEY or OPENAI_API_KEY).
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import providers
import scenarios

PORT = int(os.environ.get("ASSAY_GW_PORT", "8129"))
REAL = os.environ.get("ASSAY_REAL") == "1"
CHEAP_PROVIDER = "mistral"
STRONG_PROVIDER = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "openai"
COST = {"cheap": 1, "strong": 20}


def _gen(provider, prompt, mock_text):
    """Real provider call when enabled + keyed; otherwise a deterministic mock string."""
    if REAL and providers.have_key(provider):
        return providers.generate(provider, prompt)
    return mock_text


def _guidance(prompt, prev, reason):
    """The recovery prompt: tell the next model exactly what failed the check, so it can fix it.
    This is the difference between a router (blind retry) and Assay (informed recovery)."""
    return (f"{prompt}\n\n[An automated check REJECTED a previous attempt.]\n"
            f"Previous output: {prev}\nWhy it failed the check: {reason}\n"
            f"Return a corrected answer that will pass the check.")


def _mock_strong(checker, spec):
    """A deterministic 'good' answer the given checker will pass — so the mock escalation
    visibly recovers to green for ANY checker, not just 'format'."""
    if checker in ("json-schema", "tool-args") and isinstance(spec, list):
        return json.dumps({f: "ok" for f in spec})
    if checker == "finance" and isinstance(spec, dict):
        return json.dumps({"amount": round(spec.get("units", 0) * spec.get("price", 0), 2),
                           "ccy": spec.get("ccy", "USD")})
    return '{"answer": "corrected by the strong model"}'


def run_assay(messages, checker, spec):
    """The real reliability loop: cheap -> verify -> retry-cheap-with-guidance -> escalate
    cross-provider-with-guidance -> re-verify. Mock outputs are staged so the loop plays
    without keys; with ASSAY_REAL=1 + keys, every generate is a real provider call."""
    prompt = messages[-1].get("content", "") if messages and isinstance(messages[-1], dict) else ""
    trace, cost = [], 0

    # 1) cheap model generates (mock = a deliberately-broken output so the catch fires keyless)
    cheap_out = _gen(CHEAP_PROVIDER, prompt, mock_text='{"answer": ')  # malformed JSON
    cost += COST["cheap"]
    ok, detail = scenarios.verify(cheap_out, spec, checker)
    trace.append({"step": "generate", "provider": CHEAP_PROVIDER, "role": "cheap",
                  "checker": checker, "ok": ok, "detail": detail, "output": cheap_out})
    if ok:
        return {"content": cheap_out, "fixed_by": "cheap", "cost": cost, "advice": None, "trace": trace}

    fail = detail
    # rung 1 — retry the CHEAP model, now told why it failed (cheapest fix)
    gp = _guidance(prompt, cheap_out, fail)
    retry_out = _gen(CHEAP_PROVIDER, gp, mock_text='{"answer":')  # mock: still malformed
    cost += COST["cheap"]
    ok, detail = scenarios.verify(retry_out, spec, checker)
    trace.append({"step": "retry-cheap", "provider": CHEAP_PROVIDER, "role": "cheap",
                  "checker": checker, "ok": ok, "detail": detail, "output": retry_out})
    if ok:
        return {"content": retry_out, "fixed_by": "retry-cheap", "cost": cost,
                "advice": "Cheap model self-corrected once given the reason — no frontier spend.", "trace": trace}

    # rung 2 — escalate ONLY this step to a STRONGER model on a DIFFERENT provider, with guidance
    strong_out = _gen(STRONG_PROVIDER, gp, mock_text=_mock_strong(checker, spec))
    cost += COST["strong"]
    ok, detail = scenarios.verify(strong_out, spec, checker)
    trace.append({"step": "escalate", "provider": STRONG_PROVIDER, "role": "strong",
                  "checker": checker, "ok": ok, "detail": detail, "output": strong_out})
    fixed_by = "assay-escalation" if ok else "unrecovered"
    advice = (f"The cheap model ({CHEAP_PROVIDER}) failed the '{checker}' check ({fail}); a guided "
              f"retry didn't fix it, so Assay escalated to {STRONG_PROVIDER}. Pin this step type to "
              f"the strong model, or tighten the prompt.")
    return {"content": strong_out, "fixed_by": fixed_by, "cost": cost, "advice": advice, "trace": trace}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        if not self.path.startswith("/v1/chat/completions"):
            return self._send(404, {"error": "POST /v1/chat/completions"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(body, dict):
                raise ValueError("body must be a JSON object")
        except Exception as e:
            return self._send(400, {"error": f"invalid request JSON: {e}"})
        opts = body.get("assay", {}) or {}
        checker = opts.get("checker", "format")         # zero-config default
        spec = opts.get("spec", [])                     # only some checkers use this
        if checker not in scenarios.CHECKERS:
            return self._send(400, {"error": f"unknown checker '{checker}'; choose from {list(scenarios.CHECKERS)}"})
        model = body.get("model", "mistral-small")
        msgs = body.get("messages", [])
        if not isinstance(msgs, list):
            return self._send(400, {"error": "messages must be a list"})
        r = run_assay(msgs, checker, spec)
        # OpenAI-compatible shape + a `assay` block with the reliability trace
        self._send(200, {
            "id": "assay-gw", "object": "chat.completion", "model": model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": r["content"]}}],
            "assay": {"fixed_by": r["fixed_by"], "cost_units": r["cost"],
                          "advice": r["advice"], "trace": r["trace"],
                          "mode": "real" if REAL else "mock",
                          "providers": {"cheap": CHEAP_PROVIDER, "strong": STRONG_PROVIDER}},
        })


if __name__ == "__main__":
    print(f"\n  Assay gateway:  http://localhost:{PORT}/v1/chat/completions"
          f"   ({'REAL' if REAL else 'mock'} mode)\n"
          f"  Point your OpenAI client's base_url at http://localhost:{PORT}/v1 and keep your key.\n")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
