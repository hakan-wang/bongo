"""Send sample agent-style traffic to Assay to show savings. python3 demo_traffic.py"""
import json, urllib.request

URL = "http://localhost:8128/v1/chat/completions"
# Agents resend the same / overlapping prompts constantly. That is the waste Assay kills.
prompts = [
    "What is the refund policy for double charges?",
    "What is the refund policy for double charges?",
    "what is the refund policy for double charges?",   # near-dup (case/space)
    "Summarize the Q3 onboarding checklist.",
    "Summarize the Q3 onboarding checklist.",
    "What is the refund policy for double charges?",
    "Translate 'hello' to French.",
    "Summarize the Q3 onboarding checklist.",
    "What is the refund policy for double charges?",
    "Translate 'hello' to French.",
]

def call(p):
    body = json.dumps({"model": "gpt-4o-mini", "messages": [{"role": "user", "content": p}]}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

for p in prompts:
    res = call(p)
    tag = "CACHED (free)" if res.get("assay_cached") else "billed"
    print(f"  [{tag:13}] {p}")

s = json.loads(urllib.request.urlopen("http://localhost:8128/stats").read())
print("\n  requests:    ", s["requests"])
print("  cache hits:  ", s["hits"], f"({s['hit_rate']*100:.0f}% hit rate)")
print("  tokens saved:", s["tokens_saved"])
print(f"  $ billed:     ${s['cost_billed']:.4f}")
print(f"  $ saved:      ${s['cost_saved']:.4f}")
spent = s['cost_billed'] + s['cost_saved']
print(f"  bill cut:     {(s['cost_saved']/spent*100) if spent else 0:.0f}%  (would have been ${spent:.4f})")
