"""
Bongo demo engine — the PROOF.

Real coding tasks, REAL deterministic verification (we actually run the tests — no AI
judging AI), and the Bongo reliability loop: cheap model -> verify -> on fail, escalate
THAT step to a strong model on a DIFFERENT provider -> verify -> pass.

Model outputs are PINNED (staged) so the demo always fires on stage — cheap LLMs are
non-deterministic, so we don't gamble on that live. The VERIFY step is the only thing that
is genuinely computed, and it's deterministic (run the unit tests).

For a genuinely-real cross-provider escalation (Mistral -> Anthropic/OpenAI) using your own
keys, see demo/real_proof.py.

Relative cost units (realistic-ish): a frontier "strong" model ~= 20x a cheap one.
Run:  python3 demo/scenarios.py     # prints the aggregate scoreboard
"""

COST = {"cheap": 1, "strong": 20}

# Cross-provider identity — Bongo is vendor-neutral. The cheap model and the strong model
# we escalate to are on DIFFERENT providers (a single lab will never route you off itself).
PROVIDER = {
    "cheap":    {"provider": "Mistral",   "model": "mistral-small"},
    "strong":   {"provider": "Anthropic", "model": "claude-sonnet"},
    "verifier": {"provider": "Bongo",     "model": "deterministic"},
    "bongo":    {"provider": "Bongo",     "model": "reliability-layer"},
}

# ---------------------------------------------------------------------------
# The tasks. Each has REAL unit tests. cheap_code is what the cheap model "wrote"
# (some are silently buggy: pass some tests, fail others). strong_code is correct.
# ---------------------------------------------------------------------------
TASKS = [
    {
        "name": "is_palindrome",
        "desc": "True if a string reads the same forwards and backwards (ignore case/spaces).",
        "tests": (
            "assert is_palindrome('racecar') is True\n"
            "assert is_palindrome('Race car') is True\n"
            "assert is_palindrome('hello') is False\n"
        ),
        "cheap_buggy": False,
        "cheap_code": (
            "def is_palindrome(s):\n"
            "    s = ''.join(c.lower() for c in s if c.isalnum())\n"
            "    return s == s[::-1]\n"
        ),
        "strong_code": (
            "def is_palindrome(s):\n"
            "    s = ''.join(c.lower() for c in s if c.isalnum())\n"
            "    return s == s[::-1]\n"
        ),
    },
    {
        "name": "fizzbuzz",
        "desc": "Return 'Fizz'/'Buzz'/'FizzBuzz' for multiples of 3/5/15, else the number as a string.",
        "tests": (
            "assert fizzbuzz(3) == 'Fizz'\n"
            "assert fizzbuzz(5) == 'Buzz'\n"
            "assert fizzbuzz(15) == 'FizzBuzz'\n"
            "assert fizzbuzz(7) == '7'\n"
        ),
        "cheap_buggy": False,
        "cheap_code": (
            "def fizzbuzz(n):\n"
            "    if n % 15 == 0: return 'FizzBuzz'\n"
            "    if n % 3 == 0: return 'Fizz'\n"
            "    if n % 5 == 0: return 'Buzz'\n"
            "    return str(n)\n"
        ),
        "strong_code": (
            "def fizzbuzz(n):\n"
            "    if n % 15 == 0: return 'FizzBuzz'\n"
            "    if n % 3 == 0: return 'Fizz'\n"
            "    if n % 5 == 0: return 'Buzz'\n"
            "    return str(n)\n"
        ),
    },
    {
        "name": "slugify",
        "desc": "Turn a title into a URL slug: lowercase, strip punctuation/accents, words joined by '-'.",
        "tests": (
            "assert slugify('Hello World') == 'hello-world'\n"
            "assert slugify('  Multiple   Spaces ') == 'multiple-spaces'\n"
            "assert slugify('Cafe & Bar!') == 'cafe-bar'\n"
            "assert slugify('Already-Slugged') == 'already-slugged'\n"
        ),
        # SILENT BUG: cheap version lowercases + hyphenates spaces but never strips
        # punctuation, so 'Cafe & Bar!' -> 'cafe-&-bar!' . Passes the simple cases.
        "cheap_buggy": True,
        "cheap_code": (
            "def slugify(s):\n"
            "    return '-'.join(s.lower().split())\n"
        ),
        "strong_code": (
            "import re\n"
            "def slugify(s):\n"
            "    s = re.sub(r'[^a-z0-9]+', ' ', s.lower())\n"
            "    return '-'.join(s.split())\n"
        ),
    },
    {
        "name": "roman_to_int",
        "desc": "Convert a Roman numeral string to an integer (handles subtractive forms like IV, IX).",
        "tests": (
            "assert roman_to_int('III') == 3\n"
            "assert roman_to_int('IV') == 4\n"
            "assert roman_to_int('IX') == 9\n"
            "assert roman_to_int('LVIII') == 58\n"
            "assert roman_to_int('MCMXCIV') == 1994\n"
        ),
        # SILENT BUG: cheap version just sums values, ignoring subtractive notation.
        # 'III'->3 (ok), 'LVIII'->58 (ok), but 'IV'->6, 'MCMXCIV'->2026 (wrong).
        "cheap_buggy": True,
        "cheap_code": (
            "def roman_to_int(s):\n"
            "    v = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n"
            "    return sum(v[c] for c in s)\n"
        ),
        "strong_code": (
            "def roman_to_int(s):\n"
            "    v = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n"
            "    total = 0\n"
            "    for i, c in enumerate(s):\n"
            "        if i+1 < len(s) and v[c] < v[s[i+1]]:\n"
            "            total -= v[c]\n"
            "        else:\n"
            "            total += v[c]\n"
            "    return total\n"
        ),
    },
    {
        "name": "flatten",
        "desc": "Flatten a list that may contain nested lists into a single flat list.",
        "tests": (
            "assert flatten([1, [2, 3], [4, [5]]]) == [1, 2, 3, 4, 5]\n"
            "assert flatten([]) == []\n"
            "assert flatten([1, 2, 3]) == [1, 2, 3]\n"
        ),
        "cheap_buggy": False,
        "cheap_code": (
            "def flatten(lst):\n"
            "    out = []\n"
            "    for x in lst:\n"
            "        if isinstance(x, list): out.extend(flatten(x))\n"
            "        else: out.append(x)\n"
            "    return out\n"
        ),
        "strong_code": (
            "def flatten(lst):\n"
            "    out = []\n"
            "    for x in lst:\n"
            "        if isinstance(x, list): out.extend(flatten(x))\n"
            "        else: out.append(x)\n"
            "    return out\n"
        ),
    },
    {
        "name": "word_count",
        "desc": "Return a dict mapping each word (case-insensitive) to its count.",
        "tests": (
            "assert word_count('a a b') == {'a': 2, 'b': 1}\n"
            "assert word_count('The the THE') == {'the': 3}\n"
            "assert word_count('') == {}\n"
        ),
        "cheap_buggy": False,
        "cheap_code": (
            "def word_count(s):\n"
            "    out = {}\n"
            "    for w in s.lower().split():\n"
            "        out[w] = out.get(w, 0) + 1\n"
            "    return out\n"
        ),
        "strong_code": (
            "def word_count(s):\n"
            "    out = {}\n"
            "    for w in s.lower().split():\n"
            "        out[w] = out.get(w, 0) + 1\n"
            "    return out\n"
        ),
    },
]


# ---------------------------------------------------------------------------
# Pluggable verifier registry. Bongo's "how do we know a step is wrong?" is NOT one
# if-statement and NOT an LLM judging an LLM — it's a registry of cheap, deterministic
# checkers. The demo leads with `run-tests` (free ground truth); the others ship too.
# ---------------------------------------------------------------------------
def _check_run_tests(code, spec):
    """Execute the candidate code, then run real unit tests. Reality is the judge."""
    ns = {}
    try:
        exec(code, ns)
    except Exception as e:
        return False, f"code did not run: {type(e).__name__}: {e}"
    try:
        exec(spec, ns)
    except AssertionError:
        for line in spec.strip().splitlines():
            try:
                exec(line, ns)
            except AssertionError:
                return False, f"FAILED: {line.strip()}"
            except Exception as e:
                return False, f"ERROR on {line.strip()} ({type(e).__name__})"
        return False, "a test assertion failed"
    except Exception as e:
        return False, f"test error: {type(e).__name__}: {e}"
    return True, "all tests passed"


def _check_json_schema(obj_text, required):
    """Deterministic structured-output check (shared shape with reliability.py:check_meeting)."""
    import json
    try:
        obj = json.loads(obj_text)
    except Exception as e:
        return False, f"invalid JSON: {e}"
    for f in required:
        if f not in obj:
            return False, f"missing field '{f}'"
    return True, "schema valid"


# --- ZERO-CONFIG checkers: how Bongo checks a step when you have NO unit tests ---
# This is the onboarding answer: "you bring a check, or we use a generic one." A real
# founder (Brolly, a support bot) doesn't have unit tests — these work out of the box.
def _check_format(output, _ignored=None):
    """Zero-config default: is the output well-formed?
    If it looks like JSON (starts with { or [) it MUST parse; otherwise just non-empty."""
    import json
    s = (output or "").strip()
    if not s:
        return False, "empty output"
    if s[0] in "{[":
        try:
            json.loads(s)
            return True, "valid JSON"
        except Exception as e:
            return False, f"looks like JSON but is malformed: {e}"
    return (len(s) > 1, "non-empty text" if len(s) > 1 else "malformed/too short")


def _check_schema_from_example(output, example):
    """Paste ONE good output; Bongo checks new outputs match its shape (keys + types)."""
    import json
    try:
        got, want = json.loads(output), json.loads(example)
    except Exception as e:
        return False, f"invalid JSON: {e}"
    if not isinstance(got, dict) or not isinstance(want, dict):
        return (type(got) == type(want), "shape matches example")
    for k, v in want.items():
        if k not in got:
            return False, f"missing field '{k}' (present in your example)"
        if type(got[k]) != type(v):
            return False, f"field '{k}' has wrong type (got {type(got[k]).__name__})"
    return True, "matches your example's shape"


def _check_tool_args(output, required):
    """Check a tool/function call's arguments are valid JSON with the required fields."""
    return _check_json_schema(output, required)


def _check_llm_judge(output, rubric):
    """Lower-confidence fallback for fuzzy steps (no deterministic ground truth).
    Stub here; the real gateway plugs in a small judge model. Labeled lower-confidence
    on purpose — we LEAD with deterministic checks."""
    s = (output or "").strip()
    return (len(s) > 0, "llm-judge (lower confidence) — needs a model to score the rubric")


# the registry — surfaced in the UI so judges see it's a verification *system*,
# not one if-statement and not an LLM grading an LLM.
CHECKERS = {
    "run-tests":          _check_run_tests,            # code: execute + assert (this demo)
    "format":             _check_format,               # ZERO-CONFIG default (valid/non-empty)
    "schema-from-example": _check_schema_from_example,  # paste one good output
    "json-schema":        _check_json_schema,          # required fields/types
    "tool-args":          _check_tool_args,            # tool-call arguments valid
    "llm-judge":          _check_llm_judge,            # fuzzy fallback (lower confidence)
}


def verify(code, tests, checker="run-tests"):
    """Run a deterministic checker. Returns (passed, detail)."""
    return CHECKERS[checker](code, tests)


def run_task(task, mode):
    """Run one task. mode in {'cheap', 'bongo', 'strong'}.
    Returns a trace dict with per-step events, final pass/fail, and cost."""
    steps = []
    cost = 0

    def step(label, role, detail, status, checker=None, output=None):
        p = PROVIDER[role]
        steps.append({
            "label": label, "role": role,
            "provider": p["provider"], "model": p["model"],
            "detail": detail, "status": status,
            "checker": checker, "output": output,
        })

    # --- generation step ---
    if mode == "strong":
        step("Analyze failing tests", "strong", "read the test suite", "ok")
        step("Generate implementation", "strong", f"wrote {task['name']}()", "ok")
        cost += COST["strong"]
        code = task["strong_code"]
    else:
        step("Analyze failing tests", "cheap", "read the test suite", "ok")
        step("Generate implementation", "cheap", f"wrote {task['name']}()", "ok")
        cost += COST["cheap"]
        code = task["cheap_code"]

    # --- verify step (REAL, deterministic) ---
    passed, detail = verify(code, task["tests"], "run-tests")
    step("Verify — run tests", "verifier", detail,
         "pass" if passed else "fail", checker="run-tests", output=detail)

    fixed_by = mode
    advice = None
    # --- Bongo intervention: escalate ONLY the failing step, to a DIFFERENT provider ---
    if mode == "bongo" and not passed:
        fail_reason = detail  # capture the pinpointed reason before re-verify overwrites it
        step("Bongo: silent failure caught", "bongo",
             f"the cheap model's output failed the check ({fail_reason}) — no error was thrown; "
             f"escalating just this step", "catch")
        step(f"Escalate this step to {PROVIDER['strong']['provider']}", "strong",
             f"re-generated {task['name']}() with a stronger model on another provider", "ok")
        cost += COST["strong"]
        code = task["strong_code"]
        passed, detail = verify(code, task["tests"], "run-tests")
        step("Verify — run tests", "verifier", detail,
             "pass" if passed else "fail", checker="run-tests", output=detail)
        fixed_by = "bongo-escalation"
        # (b) advise how to improve next time — Bongo doesn't just fix, it tells you why
        advice = (f"'{task['name']}' failed the run-tests check ({fail_reason}). Bongo escalated it "
                  f"from {PROVIDER['cheap']['provider']} to {PROVIDER['strong']['provider']} and it passed. "
                  f"Next time: pin this step to the stronger model, or add a prompt constraint covering "
                  f"the case that broke.")
        step("Bongo advice", "bongo", advice, "advice")

    return {
        "task": task["name"],
        "desc": task["desc"],
        "mode": mode,
        "steps": steps,
        "passed": passed,
        "cost": cost,
        "fixed_by": fixed_by,
        "advice": advice,
        "shipped_broken": (not passed),
    }


def run_all():
    """Run every task in all three modes and compute the aggregate scoreboard."""
    modes = ["cheap", "bongo", "strong"]
    results = {m: [run_task(t, m) for t in TASKS] for m in modes}

    def agg(m):
        rs = results[m]
        total = len(rs)
        passed = sum(1 for r in rs if r["passed"])
        cost = sum(r["cost"] for r in rs)
        return {
            "mode": m,
            "passed": passed,
            "total": total,
            "reliability": round(100 * passed / total),
            "cost_units": cost,
            "broken_shipped": sum(1 for r in rs if r["shipped_broken"]),
        }

    scoreboard = {m: agg(m) for m in modes}
    # scale to "per 1,000 runs" with a tiny per-unit price for a tangible $ number
    PRICE_PER_UNIT = 0.002  # $ per cheap-call-equivalent
    scale = 1000 / len(TASKS)
    for m in modes:
        sb = scoreboard[m]
        sb["cost_per_1k_usd"] = round(sb["cost_units"] * scale * PRICE_PER_UNIT, 2)

    cb, bg, st = scoreboard["cheap"], scoreboard["bongo"], scoreboard["strong"]
    headline = {
        "bongo_reliability": bg["reliability"],
        "cheap_reliability": cb["reliability"],
        "savings_vs_strong_pct": round(100 * (st["cost_units"] - bg["cost_units"]) / st["cost_units"]),
        "bongo_cost_pct_of_strong": round(100 * bg["cost_units"] / st["cost_units"]),
        "cheap_broken_shipped": cb["broken_shipped"],
    }
    return {"results": results, "scoreboard": scoreboard, "headline": headline,
            "cost_model": COST, "providers": PROVIDER, "checkers": list(CHECKERS)}


if __name__ == "__main__":
    data = run_all()
    sb = data["scoreboard"]
    h = data["headline"]
    print("\n=== BONGO DEMO — scoreboard (per 1,000 runs) ===\n")
    for m in ["cheap", "bongo", "strong"]:
        s = sb[m]
        name = {"cheap": "Cheap model alone", "bongo": "Cheap + Bongo",
                "strong": "Expensive model alone"}[m]
        print(f"  {name:24s}  reliability {s['reliability']:3d}%   "
              f"${s['cost_per_1k_usd']:>7}/1k   broken shipped: {s['broken_shipped']}")
    print(f"\n  -> Bongo: {h['bongo_reliability']}% reliable (vs cheap {h['cheap_reliability']}%), "
          f"{h['savings_vs_strong_pct']}% cheaper than the expensive model "
          f"({h['bongo_cost_pct_of_strong']}% of its cost).")
    print(f"  -> Cheap-alone silently shipped {h['cheap_broken_shipped']} broken results.")
    print(f"  -> Cross-provider: cheap={PROVIDER['cheap']['provider']} -> "
          f"escalate={PROVIDER['strong']['provider']}.  Checkers: {', '.join(data['checkers'])}.\n")
