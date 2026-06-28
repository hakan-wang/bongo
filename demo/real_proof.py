"""
Assay — ONE genuinely-real cross-provider escalation, captured.

Proves the moat is real (not just a pinned label): a CHEAP model on one provider generates,
Assay runs the REAL unit tests, and on failure escalates that step to a STRONG model on a
DIFFERENT provider — then re-verifies. Run it once with your keys and screen-record it; the
on-stage demo stays pinned (cheap LLMs are non-deterministic).

Requires (stdlib only, no pip):
  export MISTRAL_API_KEY=...        # the cheap model (Mistral)
  export ANTHROPIC_API_KEY=...      # the strong model (Anthropic)   [or OPENAI_API_KEY]
Run:
  python3 demo/real_proof.py            # real call, default task: roman_to_int (trips small models)
  python3 demo/real_proof.py --mock     # NO keys — dry-run the narrative/formatting
"""
import os
import sys

import providers
import scenarios

CHEAP = {"provider": "Mistral", "model": os.environ.get("ASSAY_CHEAP_MODEL", "mistral-small-latest")}
USE_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
STRONG = ({"provider": "Anthropic", "model": os.environ.get("ASSAY_STRONG_MODEL", "claude-sonnet-4-5")}
          if USE_ANTHROPIC else
          {"provider": "OpenAI", "model": os.environ.get("PL_STRONG_MODEL", "gpt-4o")})

# real_proof works on the CODE tasks (checker == run-tests): the un-fakeable red->green proof.
CODE_TASKS = {t["name"]: t for t in scenarios.TASKS if t.get("checker") == "run-tests"}


def prompt_for(task):
    return (f"Write a correct Python function for this task. Return ONLY a code block.\n\n"
            f"Task: {task['desc']}\nIt must pass these tests:\n{task['spec']}")


def gen_cheap(prompt, task, mock):
    return task["cheap_out"] if mock else providers.extract_code(providers.call_mistral(prompt, CHEAP["model"]))


def gen_strong(prompt, task, mock):
    if mock:
        return task["strong_out"]
    text = providers.call_anthropic(prompt, STRONG["model"]) if USE_ANTHROPIC \
        else providers.call_openai(prompt, STRONG["model"])
    return providers.extract_code(text)


def main():
    args = [a for a in sys.argv[1:]]
    mock = "--mock" in args
    args = [a for a in args if a != "--mock"]
    name = args[0] if args else "roman_to_int"

    if name not in CODE_TASKS:
        sys.exit(f"Unknown task '{name}'. Try one of: {', '.join(CODE_TASKS)}")
    task = CODE_TASKS[name]

    if not mock:
        need = ["MISTRAL_API_KEY"] + (["ANTHROPIC_API_KEY"] if USE_ANTHROPIC else ["OPENAI_API_KEY"])
        for k in need:
            if not os.environ.get(k):
                sys.exit(f"Set {k} (and MISTRAL_API_KEY) — or run with --mock. See the file header.")

    p = prompt_for(task)
    tag = " (MOCK — no real API calls)" if mock else ""
    print(f"\n=== Assay real cross-provider proof — task: {name}(){tag} ===\n")
    print(f"[1] CHEAP model  ({CHEAP['provider']} / {CHEAP['model']}) generating...")
    cheap_code = gen_cheap(p, task, mock)
    ok, detail = scenarios.verify(cheap_code, task["spec"], "run-tests")
    print(f"    -> Assay verify (real tests): {'PASS' if ok else 'FAIL'} — {detail}")

    if ok:
        others = [n for n in CODE_TASKS if n != name]
        print(f"\n    Cheap model passed this time (non-deterministic). Re-run, or try: "
              f"python3 demo/real_proof.py {others[0] if others else name}\n")
        return

    print(f"\n[2] Assay caught a SILENT failure -> escalating THIS step across providers")
    print(f"[3] STRONG model ({STRONG['provider']} / {STRONG['model']}) re-generating with the reason...")
    # informed escalation: tell the strong model exactly what the cheap one got wrong
    guided = (f"{p}\n\n[A previous attempt FAILED the tests.]\nIt produced:\n{cheap_code}\n"
              f"Failing check: {detail}\nReturn corrected code that passes the tests.")
    strong_code = gen_strong(guided if not mock else p, task, mock)
    ok2, detail2 = scenarios.verify(strong_code, task["spec"], "run-tests")
    print(f"    -> Assay verify (real tests): {'PASS' if ok2 else 'FAIL'} — {detail2}")
    print(f"\n=== RESULT: {CHEAP['provider']} failed -> escalated to {STRONG['provider']} -> "
          f"{'GREEN (real, cross-provider)' if ok2 else 'still red, try another task'} ===\n")


if __name__ == "__main__":
    main()
