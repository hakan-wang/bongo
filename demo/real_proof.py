"""
Bongo — ONE genuinely-real cross-provider escalation, captured.

This proves the moat is real (not just a pinned label): a CHEAP model on one provider
generates code, Bongo runs the REAL tests, and on failure escalates that step to a STRONG
model on a DIFFERENT provider — then re-verifies. Run it once with your keys and screen-record
the output as proof; the on-stage demo stays pinned (cheap LLMs are non-deterministic).

Requires (stdlib only, no pip):
  export MISTRAL_API_KEY=...        # the cheap model (Mistral)
  export ANTHROPIC_API_KEY=...      # the strong model (Anthropic)   [or OPENAI_API_KEY]
Run:
  python3 demo/real_proof.py            # default task: roman_to_int (trips small models)
  python3 demo/real_proof.py slugify
"""
import json, os, re, sys, urllib.request
import scenarios

CHEAP = {"provider": "Mistral", "model": os.environ.get("BONGO_CHEAP_MODEL", "mistral-small-latest")}
USE_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
STRONG = ({"provider": "Anthropic", "model": os.environ.get("BONGO_STRONG_MODEL", "claude-sonnet-4-5")}
          if USE_ANTHROPIC else
          {"provider": "OpenAI", "model": os.environ.get("BONGO_STRONG_MODEL", "gpt-4o")})


def _post(url, headers, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def call_mistral(prompt):
    data = _post("https://api.mistral.ai/v1/chat/completions",
                 {"Authorization": "Bearer " + os.environ["MISTRAL_API_KEY"],
                  "Content-Type": "application/json"},
                 {"model": CHEAP["model"], "temperature": 0,
                  "messages": [{"role": "user", "content": prompt}]})
    return data["choices"][0]["message"]["content"]


def call_strong(prompt):
    if USE_ANTHROPIC:
        data = _post("https://api.anthropic.com/v1/messages",
                     {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                      "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                     {"model": STRONG["model"], "max_tokens": 1024,
                      "messages": [{"role": "user", "content": prompt}]})
        return "".join(b.get("text", "") for b in data["content"])
    data = _post("https://api.openai.com/v1/chat/completions",
                 {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                  "Content-Type": "application/json"},
                 {"model": STRONG["model"], "temperature": 0,
                  "messages": [{"role": "user", "content": prompt}]})
    return data["choices"][0]["message"]["content"]


def extract_code(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def prompt_for(task):
    return (f"Write a correct Python function for this task. Return ONLY a code block.\n\n"
            f"Task: {task['desc']}\nIt must pass these tests:\n{task['tests']}")


def main():
    for k in (["MISTRAL_API_KEY"] + (["ANTHROPIC_API_KEY"] if USE_ANTHROPIC else ["OPENAI_API_KEY"])):
        if not os.environ.get(k):
            sys.exit(f"Set {k} (and MISTRAL_API_KEY). See the header of this file.")

    name = sys.argv[1] if len(sys.argv) > 1 else "roman_to_int"
    task = next(t for t in scenarios.TASKS if t["name"] == name)
    p = prompt_for(task)

    print(f"\n=== Bongo real cross-provider proof — task: {name}() ===\n")
    print(f"[1] CHEAP model  ({CHEAP['provider']} / {CHEAP['model']}) generating...")
    cheap_code = extract_code(call_mistral(p))
    ok, detail = scenarios.verify(cheap_code, task["tests"], "run-tests")
    print(f"    -> Bongo verify (real tests): {'PASS' if ok else 'FAIL'} — {detail}")

    if ok:
        print("\n    Cheap model passed this time (non-deterministic). Re-run, or try a harder task:\n"
              "      python3 demo/real_proof.py slugify\n")
        return

    print(f"\n[2] Bongo caught a SILENT failure -> escalating THIS step across providers")
    print(f"[3] STRONG model ({STRONG['provider']} / {STRONG['model']}) re-generating...")
    strong_code = extract_code(call_strong(p))
    ok2, detail2 = scenarios.verify(strong_code, task["tests"], "run-tests")
    print(f"    -> Bongo verify (real tests): {'PASS' if ok2 else 'FAIL'} — {detail2}")
    print(f"\n=== RESULT: {CHEAP['provider']} failed -> escalated to {STRONG['provider']} -> "
          f"{'GREEN (real, cross-provider)' if ok2 else 'still red, try another task'} ===\n")


if __name__ == "__main__":
    main()
