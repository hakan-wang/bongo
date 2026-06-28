"""
Assay demo engine — the PROOF.

A cheap model runs a multi-step agent. Assay checks every step against REALITY (it runs the
test; it RE-COMPUTES the arithmetic from the source figures — not another AI's opinion),
catches the silently-wrong step, and recovers it with a LADDER:
  rung 1  retry the cheap model WITH the failure reason (cheapest fix)
  rung 2  escalate ONLY that step to a stronger model on a DIFFERENT provider
  rung 3  kill-switch: a real loop-detector halts a runaway step before it burns budget
and, when a step has no deterministic ground truth, Assay is HONEST: it flags it
low-confidence instead of pretending it passed.

Model outputs are PINNED so the demo always fires on stage; the VERIFICATION is real
(the test runs; the notional is recomputed from units x price).
Run:  python3 demo/scenarios.py
"""
import json

NAME = "Assay"
COST = {"cheap": 1, "strong": 20}
CHEAP = {"provider": "Mistral", "model": "mistral-small"}
STRONG = {"provider": "Anthropic", "model": "claude-sonnet"}
BUDGET_CEILING = 5  # cost units before the kill-switch fires


# ----------------------------- deterministic checkers -----------------------------
def _check_run_tests(code, spec):
    """Execute candidate code, then run real unit tests. Reality is the judge."""
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


def _check_finance(output, gt):
    """Recompute the notional from the SOURCE figures (units x price) and check the model's
    tool call against it — real arithmetic, not constant-vs-constant.
    gt = {'units', 'price', 'ccy'}."""
    if not isinstance(gt, dict) or "units" not in gt or "price" not in gt:
        return False, "finance checker needs spec={units, price, ccy}"
    expected = round(gt["units"] * gt["price"], 2)
    try:
        obj = json.loads(output)
    except Exception as e:
        return False, f"invalid tool call JSON: {e}"
    amt, ccy = obj.get("amount"), obj.get("ccy")
    if amt != expected and amt != int(expected):
        amt_str = f"{amt:,}" if isinstance(amt, (int, float)) else repr(amt)
        hint = ""
        if isinstance(amt, (int, float)) and expected:
            f = amt / expected
            if f in (10, 100, 0.1, -1):
                hint = f" ({f:g}x the true notional)"
        return False, f"amount {amt_str} != units x price = {expected:,.0f}{hint}"
    if ccy != gt["ccy"]:
        return False, f"currency {ccy} != ground truth {gt['ccy']}"
    return True, f"matches units x price = {expected:,.0f} {gt['ccy']}"


def _check_json_schema(output, required):
    try:
        obj = json.loads(output)
    except Exception as e:
        return False, f"invalid JSON: {e}"
    for fld in required:
        if fld not in obj:
            return False, f"missing required field '{fld}'"
    return True, "schema valid"


def _check_format(output, _ignored=None):
    s = (output or "").strip()
    if not s:
        return False, "empty output"
    if s[0] in "{[":
        try:
            json.loads(s); return True, "valid JSON"
        except Exception as e:
            return False, f"looks like JSON but is malformed: {e}"
    return (len(s) > 1, "non-empty text" if len(s) > 1 else "malformed/too short")


def _check_schema_from_example(output, example):
    try:
        got, want = json.loads(output), json.loads(example)
    except Exception as e:
        return False, f"invalid JSON: {e}"
    if isinstance(want, dict) and isinstance(got, dict):
        for k in want:
            if k not in got:
                return False, f"missing field '{k}' (present in your example)"
    return True, "matches your example's shape"


def _check_tool_args(output, required):
    return _check_json_schema(output, required)


def _check_llm_judge(output, _rubric):
    return (bool((output or "").strip()), "llm-judge (lower confidence)")


CHECKERS = {"run-tests": _check_run_tests, "finance": _check_finance, "json-schema": _check_json_schema,
            "format": _check_format, "schema-from-example": _check_schema_from_example,
            "tool-args": _check_tool_args, "llm-judge": _check_llm_judge}


def verify(output, spec, checker):
    return CHECKERS[checker](output, spec)


# real loop-detector for the kill-switch (rung 3) — computed, not hardcoded
def detect_runaway(signatures, budget=BUDGET_CEILING):
    seen, cost = {}, 0
    for sig in signatures:
        cost += 1
        seen[sig] = seen.get(sig, 0) + 1
        if seen[sig] >= 3:
            return True, f"same call repeated {seen[sig]}x with no new info", cost
        if cost >= budget:
            return True, f"hit the ${budget} budget ceiling", cost
    return False, "completed", cost


# --------------------------------- the tasks ---------------------------------
TASKS = [
    {"name": "settle_trade", "kind": "chain", "domain": "finance",
     "desc": "Settle a trade: extract the ticket, compute the notional, wire it."},
    {"name": "roman_to_int", "kind": "normal", "domain": "code",
     "desc": "Implement roman_to_int() (handles subtractive forms like IV, IX).",
     "checker": "run-tests",
     "spec": "assert roman_to_int('IV') == 4\nassert roman_to_int('MCMXCIV') == 1994\nassert roman_to_int('III') == 3\n",
     "cheap_out": "def roman_to_int(s):\n v={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n return sum(v[c] for c in s)\n",
     "strong_out": "def roman_to_int(s):\n v={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n t=0\n for i,c in enumerate(s):\n  t += -v[c] if i+1<len(s) and v[c]<v[s[i+1]] else v[c]\n return t\n"},
    {"name": "is_palindrome", "kind": "normal", "domain": "code",
     "desc": "Implement is_palindrome() ignoring case/spaces.", "checker": "run-tests",
     "spec": "assert is_palindrome('Race car') is True\nassert is_palindrome('hello') is False\n",
     "cheap_out": "def is_palindrome(s):\n s=''.join(c.lower() for c in s if c.isalnum())\n return s==s[::-1]\n",
     "strong_out": "def is_palindrome(s):\n s=''.join(c.lower() for c in s if c.isalnum())\n return s==s[::-1]\n"},
    {"name": "fizzbuzz", "kind": "normal", "domain": "code",
     "desc": "Implement fizzbuzz(n).", "checker": "run-tests",
     "spec": "assert fizzbuzz(15)=='FizzBuzz'\nassert fizzbuzz(3)=='Fizz'\nassert fizzbuzz(7)=='7'\n",
     "cheap_out": "def fizzbuzz(n):\n if n%15==0:return 'FizzBuzz'\n if n%3==0:return 'Fizz'\n if n%5==0:return 'Buzz'\n return str(n)\n",
     "strong_out": "def fizzbuzz(n):\n if n%15==0:return 'FizzBuzz'\n if n%3==0:return 'Fizz'\n if n%5==0:return 'Buzz'\n return str(n)\n"},
    {"name": "extract_contact", "kind": "normal", "domain": "data",
     "desc": "Extract the lead as JSON {name, email, phone}.", "checker": "json-schema",
     "spec": ["name", "email", "phone"],
     "cheap_out": '{"name": "Dana Lee", "email": "dana@acme.io", "phone": "+1-415-555-0102"}',
     "strong_out": '{"name": "Dana Lee", "email": "dana@acme.io", "phone": "+1-415-555-0102"}'},
    {"name": "reconcile_ledger", "kind": "runaway", "domain": "finance",
     "desc": "Reconcile the ledger — the cheap agent loops the same query, never terminating."},
    {"name": "draft_summary", "kind": "unverifiable", "domain": "text",
     "desc": "Write a one-line summary of the deal memo (subjective — no ground truth)."},
]

# the runaway agent's actual call trace (a repeated signature) — the kill-switch reads THIS
RECONCILE_TRACE = ["query_ledger(page=1)"] * 6


def _step(steps, role, label, detail, status, **extra):
    p = {"cheap": CHEAP, "strong": STRONG}.get(role, {"provider": NAME, "model": "verifier"})
    steps.append({"label": label, "role": role, "provider": p["provider"], "model": p["model"],
                  "detail": detail, "status": status, **extra})


# ---- the FINANCE money-shot: a real multi-step chain (extract -> compute -> wire) ----
def run_settle_trade(mode):
    """units x price = the wire amount. The cheap model 10x-slips the notional at the COMPUTE
    step; left lets it flow into the wire, Assay catches it before step 3."""
    units, price, ccy = 10000, 98.50, "USD"
    gt = {"units": units, "price": price, "ccy": ccy}
    expected = round(units * price, 2)  # 985,000.00 — COMPUTED, not a constant
    steps, cost = [], 0
    role = "strong" if mode == "strong" else "cheap"

    _step(steps, role, "Step 1 — extract ticket figures", f"units={units:,}, price=${price}", "ok")
    cost += COST[role]
    _step(steps, role, "Step 2 — compute notional, build settle_trade()", "amount = units × price", "ok")
    cost += COST[role]
    out = ('{"tool":"settle_trade","amount":985000,"ccy":"USD"}' if mode == "strong"
           else '{"tool":"settle_trade","amount":9850000,"ccy":"USD"}')  # cheap: 10x decimal slip
    ok, detail = _check_finance(out, gt)
    _step(steps, "verifier", "Verify against reality — recompute units × price", detail,
          "pass" if ok else "fail", checker="finance", output=detail)

    fixed_by, advice = mode, None
    if not ok and mode == "assay":
        fail = detail
        _step(steps, "assay", "Assay caught the wrong number BEFORE the wire",
              f"failed the recomputed check ({fail})", "catch")
        retry = '{"tool":"settle_trade","amount":985000,"ccy":"EUR"}'  # fixes amount, wrong ccy
        _step(steps, "cheap", "Rung 1 — retry cheap with the reason", "regenerated", "ok")
        cost += COST["cheap"]
        ok, detail = _check_finance(retry, gt)
        _step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail",
              checker="finance", output=detail)
        if not ok:
            strong = '{"tool":"settle_trade","amount":985000,"ccy":"USD"}'
            _step(steps, "strong", f"Rung 2 — escalate this step to {STRONG['provider']}",
                  "re-generated on a different provider", "ok")
            cost += COST["strong"]
            ok, detail = _check_finance(strong, gt)
            _step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail",
                  checker="finance", output=detail)
        fixed_by = "cross-provider-escalate"
        advice = (f"The cheap model slipped a decimal on the notional ({fail}). Assay recomputed "
                  f"units×price, caught it, and escalated to {STRONG['provider']}. Pin money-moving "
                  f"steps to the strong model, or add the recompute check inline.")

    # step 3 — the wire. only the VERIFIED amount goes out.
    if mode == "assay":
        _step(steps, "assay", "Step 3 — wire the VERIFIED amount", f"wired {expected:,.0f} {ccy} ✓", "pass")
    elif not ok:
        _step(steps, role, "Step 3 — WIRE the unchecked amount", "wired 9,850,000 USD — 10× too much", "fail")
    else:
        _step(steps, role, "Step 3 — wire the amount", f"wired {expected:,.0f} {ccy}", "pass")

    return {"task": "settle_trade", "desc": TASKS[0]["desc"], "mode": mode, "domain": "finance",
            "steps": steps, "passed": ok, "cost": cost, "fixed_by": fixed_by, "advice": advice,
            "flagged": False, "shipped_broken": (not ok), "scored": True}


def run_task(task, mode):
    kind = task["kind"]
    if kind == "chain":
        return run_settle_trade(mode)

    if kind == "runaway":
        steps, cost = [], 0
        role = "cheap" if mode != "strong" else "strong"
        _step(steps, role, "Run step", "agent starts re-querying the ledger…", "ok")
        if mode == "assay":
            killed, reason, loops = detect_runaway(RECONCILE_TRACE)
            cost += loops * COST["cheap"]
            _step(steps, "verifier", "Assay: loop detector", reason, "catch")
            _step(steps, "assay", "Kill-switch fired", f"halted after {loops} calls before the bill ran", "kill")
            return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                    "steps": steps, "passed": True, "cost": cost, "fixed_by": "kill-switch",
                    "advice": "Pin a hard budget/loop ceiling on this step.", "flagged": False,
                    "shipped_broken": False, "scored": False}
        killed, reason, loops = detect_runaway(RECONCILE_TRACE, budget=10 ** 9)  # no guard -> runs away
        cost += min(loops, 6) * COST[role]
        _step(steps, role, "No guard", f"looped {min(loops,6)}x, burned budget, never finished", "fail")
        return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                "steps": steps, "passed": False, "cost": cost, "fixed_by": "UNGUARDED",
                "advice": None, "flagged": False, "shipped_broken": True, "scored": False}

    if kind == "unverifiable":
        steps = []
        role = "strong" if mode == "strong" else "cheap"
        _step(steps, role, "Generate", "wrote a one-line summary", "ok")
        cost = COST[role]
        if mode == "assay":
            _step(steps, "verifier", "Assay: no ground truth", "subjective step — cannot verify deterministically", "flag")
            _step(steps, "assay", "Flagged for a human", "marked LOW-CONFIDENCE — not auto-passed (we don't fake a green)", "flag")
            return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                    "steps": steps, "passed": False, "cost": cost, "fixed_by": "flagged-low-confidence",
                    "advice": "Route to human review, or add a rubric/reference to make it checkable.",
                    "flagged": True, "shipped_broken": False, "scored": False}
        return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                "steps": steps, "passed": True, "cost": cost, "fixed_by": mode, "advice": None,
                "flagged": False, "shipped_broken": False, "scored": False}

    # ---- normal: generate -> verify -> ladder ----
    checker, spec = task["checker"], task["spec"]
    steps, cost = [], 0
    if mode == "strong":
        _step(steps, "strong", "Generate", f"wrote {task['name']}", "ok")
        cost += COST["strong"]
        ok, detail = verify(task["strong_out"], spec, checker)
        _step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
        return _result(task, mode, steps, ok, cost, "strong", None)

    _step(steps, "cheap", "Generate", f"wrote {task['name']}", "ok")
    cost += COST["cheap"]
    ok, detail = verify(task["cheap_out"], spec, checker)
    _step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
    if ok or mode != "assay":
        return _result(task, mode, steps, ok, cost, "cheap", None)

    fail = detail
    _step(steps, "assay", "Assay caught the silently-wrong step", f"failed the reality check ({fail})", "catch")
    _step(steps, "strong", f"Escalate this step to {STRONG['provider']}", "re-generated on a different provider", "ok")
    cost += COST["strong"]
    ok, detail = verify(task["strong_out"], spec, checker)
    _step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
    advice = (f"Cheap {CHEAP['provider']} failed the reality check ({fail}); escalated to "
              f"{STRONG['provider']} and it passed. Pin this step type to the stronger model.")
    return _result(task, mode, steps, ok, cost, "cross-provider-escalate", advice)


def _result(task, mode, steps, ok, cost, fixed_by, advice):
    return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
            "steps": steps, "passed": ok, "cost": cost, "fixed_by": fixed_by, "advice": advice,
            "flagged": False, "shipped_broken": (not ok), "scored": True}


def run_all():
    modes = ["cheap", "assay", "strong"]
    results = {m: [run_task(t, m) for t in TASKS] for m in modes}

    def agg(m):
        scored = [r for r in results[m] if r["scored"]]
        passed = sum(1 for r in scored if r["passed"])
        return {"mode": m, "passed": passed, "total": len(scored),
                "reliability": round(100 * passed / len(scored)) if scored else 0,
                "cost_units": sum(r["cost"] for r in results[m]),
                "broken_shipped": sum(1 for r in scored if r["shipped_broken"])}

    sb = {m: agg(m) for m in modes}
    PRICE, scale = 0.002, 1000 / len([t for t in TASKS if t["kind"] in ("normal", "chain")])
    for m in modes:
        sb[m]["cost_per_1k_usd"] = round(sb[m]["cost_units"] * scale * PRICE, 2)

    cb, bg, st = sb["cheap"], sb["assay"], sb["strong"]
    escalated = sum(1 for r in results["assay"] if r["fixed_by"] in ("cross-provider-escalate", "retry-cheap"))
    headline = {"assay_reliability": bg["reliability"], "cheap_reliability": cb["reliability"],
                "savings_vs_strong_pct": round(100 * (st["cost_units"] - bg["cost_units"]) / st["cost_units"]) if st["cost_units"] else 0,
                "cheap_broken_shipped": cb["broken_shipped"],
                "escalated": escalated, "total_steps": len([t for t in TASKS if t["kind"] in ("normal", "chain")]),
                "bug_amount": 9850000, "bug_correct": 985000, "bug_over": 8865000}
    return {"results": results, "scoreboard": sb, "headline": headline,
            "providers": {"cheap": CHEAP, "strong": STRONG}, "checkers": list(CHECKERS), "name": NAME}


if __name__ == "__main__":
    d = run_all(); sb = d["scoreboard"]; h = d["headline"]
    print(f"\n=== {NAME} — scoreboard (verifiable steps, per 1,000 runs) ===\n")
    for m in ["cheap", "assay", "strong"]:
        s = sb[m]; name = {"cheap": "Cheap model alone", "assay": f"Cheap + {NAME}", "strong": "Expensive model alone"}[m]
        print(f"  {name:24s} reliability {s['reliability']:3d}%   ${s['cost_per_1k_usd']:>7}/1k   broken shipped: {s['broken_shipped']}")
    print(f"\n  -> {NAME}: {h['assay_reliability']}% reliable (vs cheap {h['cheap_reliability']}%), "
          f"{h['savings_vs_strong_pct']}% cheaper than the big model. Escalated only {h['escalated']}/{h['total_steps']} steps.")
    print(f"  -> Money-shot: cheap wired {h['bug_amount']:,} vs the true {h['bug_correct']:,} (an {h['bug_over']:,} over-wire), caught by recomputing units×price.")
    print(f"  -> Recovery ladder + real kill-switch loop + honest low-confidence flag all fire. Cross-provider Mistral->Anthropic.\n")
