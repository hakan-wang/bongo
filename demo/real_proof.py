"""
Plumbline — ONE genuinely-real cross-provider escalation, captured.

Proves the moat is real (not just a pinned label): a CHEAP model on one provider generates,
Plumbline runs the REAL tests, and on failure escalates that step to a STRONG model on a
DIFFERENT provider — then re-verifies. Run it once with your keys and screen-record it; the
on-stage demo stays pinned (cheap LLMs are non-deterministic).

Requires (stdlib only, no pip):
  export MISTRAL_API_KEY=...        # the cheap model (Mistral)
  export ANTHROPIC_API_KEY=...      # the strong model (Anthropic)   [or OPENAI_API_KEY]
Run:
  python3 demo/real_proof.py            # real call, default task: roman_to_int
  python3 demo/real_proof.py slugify    # a harder task if the cheap model gets lucky
  python3 demo/real_proof.py --mock     # NO keys — dry-run the narrative/formatting
"""
import os
import sys

import providers
import scenarios

CHEAP = {"provider": "Mistral", "model": os.environ.get("BONGO_CHEAP_MODEL", "mistral-small-latest")}
USE_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
STRONG = ({"provider": "Anthropic", "model": os.environ.get("BONGO_STRONG_MODEL", "claude-sonnet-4-5")}
          if USE_ANTHROPIC else
          {"provider": "OpenAI", "model": os.environ.get("BONGO_STRONG_MODEL", "gpt-4o")})


def prompt_for(task):
    return (f"Write a correct Python function for this task. Return ONLY a code block.\n\n"
            f"Task: {task['desc']}\nIt must pass these tests:\n{task['tests']}")


def gen_cheap(prompt, task, mock):
    return task["cheap_code"] if mock else providers.extract_code(providers.call_mistral(prompt, CHEAP["model"]))


def gen_strong(prompt, task, mock):
    if mock:
        return task["strong_code"]
    text = providers.call_anthropic(prompt, STRONG["model"]) if USE_ANTHROPIC \
        else providers.call_openai(prompt, STRONG["model"])
    return providers.extract_code(text)


def main():
    args = [a for a in sys.argv[1:]]
    mock = "--mock" in args
    args = [a for a in args if a != "--mock"]
    name = args[0] if args else "roman_to_int"

    if not mock:
        need = ["MISTRAL_API_KEY"] + (["ANTHROPIC_API_KEY"] if USE_ANTHROPIC else ["OPENAI_API_KEY"])
        for k in need:
            if not os.environ.get(k):
                sys.exit(f"Set {k} (and MISTRAL_API_KEY) — or run with --mock. See the file header.")

    task = next(t for t in scenarios.TASKS if t["name"] == name)
    p = prompt_for(task)
    tag = " (MOCK — no real API calls)" if mock else ""

    print(f"\n=== Plumbline real cross-provider proof — task: {name}(){tag} ===\n")
    print(f"[1] CHEAP model  ({CHEAP['provider']} / {CHEAP['model']}) generating...")
    cheap_code = gen_cheap(p, task, mock)
    ok, detail = scenarios.verify(cheap_code, task["tests"], "run-tests")
    print(f"    -> Plumbline verify (real tests): {'PASS' if ok else 'FAIL'} — {detail}")

    if ok:
        print("\n    Cheap model passed this time (non-deterministic). Re-run, or try a harder task:\n"
              "      python3 demo/real_proof.py slugify\n")
        return

    print(f"\n[2] Plumbline caught a SILENT failure -> escalating THIS step across providers")
    print(f"[3] STRONG model ({STRONG['provider']} / {STRONG['model']}) re-generating...")
    strong_code = gen_strong(p, task, mock)
    ok2, detail2 = scenarios.verify(strong_code, task["tests"], "run-tests")
    print(f"    -> Plumbline verify (real tests): {'PASS' if ok2 else 'FAIL'} — {detail2}")
    print(f"\n=== RESULT: {CHEAP['provider']} failed -> escalated to {STRONG['provider']} -> "
          f"{'GREEN (real, cross-provider)' if ok2 else 'still red, try another task'} ===\n")


if __name__ == "__main__":
    main()
