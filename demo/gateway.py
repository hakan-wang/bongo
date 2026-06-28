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


def run_assay(messages, checker, spec):
    prompt = messages[-1].get("content", "") if messages and isinstance(messages[-1], dict) else ""
    trace, cost = [], 0

    # 1) cheap model generates. In mock mode it returns a deliberately-thin output so the
    #    zero-config `format` checker trips — proving the catch loop without any keys.
    cheap_out = _gen(CHEAP_PROVIDER, prompt, mock_text='{"answer": ')  # malformed JSON in mock
    cost += COST["cheap"]
    ok, detail = scenarios.verify(cheap_out, spec, checker)
    trace.append({"step": "generate", "provider": CHEAP_PROVIDER, "role": "cheap",
                  "checker": checker, "ok": ok, "detail": detail, "output": cheap_out})

    final, fixed_by, advice = cheap_out, "cheap", None
    # 2) on failure, escalate ONLY this step to a stronger model on a DIFFERENT provider
    if not ok:
        strong_out = _gen(STRONG_PROVIDER, prompt,
                          mock_text='{"answer": "corrected by the strong model"}')
        cost += COST["strong"]
        ok2, detail2 = scenarios.verify(strong_out, spec, checker)
        trace.append({"step": "escalate", "provider": STRONG_PROVIDER, "role": "strong",
                      "checker": checker, "ok": ok2, "detail": detail2, "output": strong_out})
        final = strong_out
        fixed_by = "assay-escalation" if ok2 else "unrecovered"
        advice = (f"The cheap model ({CHEAP_PROVIDER}) failed the '{checker}' check ({detail}). "
                  f"Assay escalated to {STRONG_PROVIDER}. To save cost next time, pin this step "
                  f"to the strong model or tighten the prompt.")

    return {"content": final, "fixed_by": fixed_by, "cost": cost, "advice": advice, "trace": trace}


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
