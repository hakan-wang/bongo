"""
Plumbline: a drop-in cost layer for LLM APIs.
Point your app's base_url at Plumbline, keep your code and key the same.
Plumbline caches repeated/near-repeated calls so you stop paying for the same tokens twice.

Run:  python3 proxy.py        (serves on http://localhost:8128)
No dependencies. Mock mode by default so it runs offline for the demo.
Set BONGO_REAL=1 and OPENAI_API_KEY to forward real calls.
"""
import json, os, re, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8128
PRICE_PER_1K = 0.01  # demo pricing, dollars per 1k tokens

cache = {}   # normalized prompt -> {"text":..., "tokens":...}
stats = {"requests": 0, "hits": 0, "tokens_saved": 0, "cost_saved": 0.0,
         "tokens_billed": 0, "cost_billed": 0.0, "events": []}

def est_tokens(text):  # rough: ~4 chars per token
    return max(1, len(text) // 4)

def normalize(messages):
    text = " ".join(m.get("content", "") for m in messages).lower().strip()
    return re.sub(r"\s+", " ", text)

def mock_completion(prompt):
    return "Here is a concise answer to: " + prompt[:60] + " ... (generated once, then cached by Plumbline)."

def real_completion(model, messages):
    body = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", ""),
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data["choices"][0]["message"]["content"]

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/stats"):
            s = dict(stats); s["hit_rate"] = (s["hits"]/s["requests"]) if s["requests"] else 0
            s["events"] = s["events"][-12:]
            return self._send(200, s)
        # serve dashboard
        try:
            with open(os.path.join(os.path.dirname(__file__), "dashboard.html"), "rb") as f:
                b = f.read()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        except FileNotFoundError:
            self._send(404, {"error": "no dashboard"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        messages = body.get("messages", [])
        model = body.get("model", "gpt-4o-mini")
        key = normalize(messages)
        prompt_tokens = est_tokens(key)
        stats["requests"] += 1

        if key in cache:  # CACHE HIT: free
            hit = cache[key]
            saved = prompt_tokens + hit["tokens"]
            stats["hits"] += 1
            stats["tokens_saved"] += saved
            stats["cost_saved"] += saved / 1000 * PRICE_PER_1K
            stats["events"].append({"t": time.time(), "cached": True, "saved": saved})
            text = hit["text"]
        else:             # MISS: pay once, then remember
            text = real_completion(model, messages) if os.environ.get("BONGO_REAL") else mock_completion(key)
            comp_tokens = est_tokens(text)
            cache[key] = {"text": text, "tokens": comp_tokens}
            billed = prompt_tokens + comp_tokens
            stats["tokens_billed"] += billed
            stats["cost_billed"] += billed / 1000 * PRICE_PER_1K
            stats["events"].append({"t": time.time(), "cached": False, "saved": 0})

        self._send(200, {
            "id": "bongo-" + str(stats["requests"]),
            "object": "chat.completion",
            "model": model,
            "bongo_cached": key in cache and stats["events"][-1]["cached"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text},
                         "finish_reason": "stop"}],
        })

if __name__ == "__main__":
    print("Plumbline cost layer on http://localhost:%d  (dashboard at /)" % PORT)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
