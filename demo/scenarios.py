"""
Plumbline demo engine — the PROOF.

A cheap model runs a multi-step agent. Plumbline checks every step against REALITY
(run the tests / arithmetic against ground truth — NOT another AI's opinion), catches the
silently-wrong step, and recovers it with a LADDER:
  rung 1  retry the cheap model WITH the failure reason (cheapest fix)
  rung 2  escalate ONLY that step to a stronger model on a DIFFERENT provider
  rung 3  kill-switch: halt a runaway/looping step before it burns budget
and, when a step has no deterministic ground truth, Plumbline is HONEST: it flags it
low-confidence instead of pretending it passed.

Model outputs are PINNED so the demo always fires on stage; the VERIFICATION is real.
Relative cost units: a frontier "strong" model ~= 20x a cheap one.
Run:  python3 demo/scenarios.py
"""
import json

COST = {"cheap": 1, "strong": 20}
CHEAP = {"provider": "Mistral", "model": "mistral-small"}
STRONG = {"provider": "Anthropic", "model": "claude-sonnet"}


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
    """Arithmetic ground-truth check for a money-moving tool call.
    gt = {'amount': <correct>, 'ccy': <correct>}. Catches sign flips, 10x slips, wrong ccy."""
    try:
        obj = json.loads(output)
    except Exception as e:
        return False, f"invalid tool call JSON: {e}"
    amt, ccy = obj.get("amount"), obj.get("ccy")
    if amt != gt["amount"]:
        if isinstance(amt, (int, float)) and gt["amount"]:
            factor = amt / gt["amount"]
            hint = f" ({factor:g}x the true notional)" if factor in (10, 100, 0.1, -1) else ""
        else:
            hint = ""
        return False, f"amount {amt:,} != ground truth {gt['amount']:,}{hint}"
    if ccy != gt["ccy"]:
        return False, f"currency {ccy} != ground truth {gt['ccy']}"
    return True, f"matches ground truth: {gt['amount']:,} {gt['ccy']}"


def _check_json_schema(output, required):
    try:
        obj = json.loads(output)
    except Exception as e:
        return False, f"invalid JSON: {e}"
    for f in required:
        if f not in obj:
            return False, f"missing required field '{f}'"
    return True, "schema valid"


CHECKERS = {"run-tests": _check_run_tests, "finance": _check_finance, "json-schema": _check_json_schema}


def verify(output, spec, checker):
    return CHECKERS[checker](output, spec)


# --------------------------------- the tasks ---------------------------------
# kind: "normal" (catch + ladder), "runaway" (kill-switch), "unverifiable" (honest flag)
TASKS = [
    {   # ★ HEADLINE — money-moving finance agent. Cheap model 10x-slips the notional.
        "name": "settle_trade", "kind": "normal", "domain": "finance",
        "desc": "Read the trade ticket (10,000 units @ $98.50) and emit settle_trade(amount, ccy).",
        "checker": "finance", "spec": {"amount": 985000, "ccy": "USD"},
        "cheap_out": '{"tool": "settle_trade", "amount": 9850000, "ccy": "USD"}',   # 10x decimal slip
        "retry_out": '{"tool": "settle_trade", "amount": 985000, "ccy": "EUR"}',    # fixes amount, wrong ccy
        "strong_out": '{"tool": "settle_trade", "amount": 985000, "ccy": "USD"}',   # correct
    },
    {   # MECHANISM cutaway — code agent, the un-fakeable red->green pytest proof.
        "name": "roman_to_int", "kind": "normal", "domain": "code",
        "desc": "Implement roman_to_int() (handles subtractive forms like IV, IX).",
        "checker": "run-tests",
        "spec": "assert roman_to_int('IV') == 4\nassert roman_to_int('MCMXCIV') == 1994\nassert roman_to_int('III') == 3\n",
        "cheap_out": "def roman_to_int(s):\n v={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n return sum(v[c] for c in s)\n",
        "strong_out": "def roman_to_int(s):\n v={'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}\n t=0\n for i,c in enumerate(s):\n  t += -v[c] if i+1<len(s) and v[c]<v[s[i+1]] else v[c]\n return t\n",
    },
    # three steps the cheap model gets RIGHT (so escalation rate stays low — most stay cheap)
    {   "name": "is_palindrome", "kind": "normal", "domain": "code",
        "desc": "Implement is_palindrome() ignoring case/spaces.", "checker": "run-tests",
        "spec": "assert is_palindrome('Race car') is True\nassert is_palindrome('hello') is False\n",
        "cheap_out": "def is_palindrome(s):\n s=''.join(c.lower() for c in s if c.isalnum())\n return s==s[::-1]\n",
        "strong_out": "def is_palindrome(s):\n s=''.join(c.lower() for c in s if c.isalnum())\n return s==s[::-1]\n"},
    {   "name": "fizzbuzz", "kind": "normal", "domain": "code",
        "desc": "Implement fizzbuzz(n).", "checker": "run-tests",
        "spec": "assert fizzbuzz(15)=='FizzBuzz'\nassert fizzbuzz(3)=='Fizz'\nassert fizzbuzz(7)=='7'\n",
        "cheap_out": "def fizzbuzz(n):\n if n%15==0:return 'FizzBuzz'\n if n%3==0:return 'Fizz'\n if n%5==0:return 'Buzz'\n return str(n)\n",
        "strong_out": "def fizzbuzz(n):\n if n%15==0:return 'FizzBuzz'\n if n%3==0:return 'Fizz'\n if n%5==0:return 'Buzz'\n return str(n)\n"},
    {   "name": "extract_invoice", "kind": "normal", "domain": "finance",
        "desc": "Extract the invoice as JSON {vendor, total, due_date}.", "checker": "json-schema",
        "spec": ["vendor", "total", "due_date"],
        "cheap_out": '{"vendor": "Acme Corp", "total": 4210.00, "due_date": "2026-07-15"}',
        "strong_out": '{"vendor": "Acme Corp", "total": 4210.00, "due_date": "2026-07-15"}'},
    {   # rung 3 — runaway/looping step, kill-switch halts it before it burns budget
        "name": "reconcile_ledger", "kind": "runaway", "domain": "finance",
        "desc": "Agent loops re-querying the ledger, never terminating — burning tokens."},
    {   # honesty boundary — no deterministic ground truth; Plumbline flags, does NOT auto-pass
        "name": "draft_summary", "kind": "unverifiable", "domain": "text",
        "desc": "Write a one-line summary of the deal memo (subjective — no ground truth)."},
]


def _gen_step(steps, role, label, detail, status, **extra):
    p = CHEAP if role == "cheap" else STRONG if role == "strong" else {"provider": "Plumbline", "model": "verifier"}
    steps.append({"label": label, "role": role, "provider": p["provider"], "model": p["model"],
                  "detail": detail, "status": status, **extra})


def run_task(task, mode):
    kind = task["kind"]
    steps, cost, advice, flagged = [], 0, None, False

    # ---- special kinds (Agentic Depth showcases) ----
    if kind == "runaway":
        _gen_step(steps, "cheap", "Run step", "agent starts re-querying the ledger…", "ok")
        if mode == "bongo":
            cost += COST["cheap"]
            _gen_step(steps, "verifier", "Plumbline: loop detected", "same call 5x, no progress — runaway", "catch")
            _gen_step(steps, "bongo", "Kill-switch fired", "halted at a $5 budget ceiling before the bill ran", "killswitch")
            return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                    "steps": steps, "passed": True, "cost": cost, "fixed_by": "kill-switch",
                    "advice": "Pin a hard budget/loop ceiling on this step.", "flagged": False,
                    "shipped_broken": False, "scored": False}
        # cheap/strong alone: loops, burns budget
        cost += COST[mode] * 5
        _gen_step(steps, mode, "No guard", "looped 5x, burned budget, never finished", "fail")
        return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                "steps": steps, "passed": False, "cost": cost, "fixed_by": "UNGUARDED",
                "advice": None, "flagged": False, "shipped_broken": True, "scored": False}

    if kind == "unverifiable":
        _gen_step(steps, "cheap", "Generate", "wrote a one-line summary", "ok")
        cost += COST["cheap" if mode != "strong" else "strong"]
        if mode == "bongo":
            _gen_step(steps, "verifier", "Plumbline: no ground truth", "subjective step — cannot verify deterministically", "flag")
            _gen_step(steps, "bongo", "Flagged for a human", "marked LOW-CONFIDENCE — not auto-passed (we don't fake a green)", "flag")
            return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                    "steps": steps, "passed": False, "cost": cost, "fixed_by": "flagged-low-confidence",
                    "advice": "Route to human review or add a rubric/reference to make it checkable.",
                    "flagged": True, "shipped_broken": False, "scored": False}
        return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
                "steps": steps, "passed": True, "cost": cost, "fixed_by": mode,
                "advice": None, "flagged": False, "shipped_broken": False, "scored": False}

    # ---- normal: generate -> verify -> (ladder) ----
    checker, spec = task["checker"], task["spec"]
    if mode == "strong":
        _gen_step(steps, "strong", "Generate", f"wrote {task['name']}", "ok")
        cost += COST["strong"]
        ok, detail = verify(task["strong_out"], spec, checker)
        _gen_step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
        return _result(task, mode, steps, ok, cost, "strong", None)

    _gen_step(steps, "cheap", "Generate", f"wrote {task['name']}", "ok")
    cost += COST["cheap"]
    ok, detail = verify(task["cheap_out"], spec, checker)
    _gen_step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
    if ok or mode != "bongo":
        return _result(task, mode, steps, ok, cost, "cheap", None)

    # bongo recovery ladder
    fail_reason = detail
    # rung 1 — retry cheap WITH guidance (cheapest fix)
    if task.get("retry_out"):
        _gen_step(steps, "bongo", "Plumbline: caught silently-wrong step", f"failed reality check ({fail_reason})", "catch")
        _gen_step(steps, "cheap", "Rung 1 — retry cheap with the failure reason", "fed the error back, regenerated", "ok")
        cost += COST["cheap"]
        ok, detail = verify(task["retry_out"], spec, checker)
        _gen_step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
        if ok:
            return _result(task, mode, steps, True, cost, "retry-cheap",
                           f"Cheap model self-corrected once given the failure reason — no frontier spend.")
    else:
        _gen_step(steps, "bongo", "Plumbline: caught silently-wrong step", f"failed reality check ({fail_reason})", "catch")

    # rung 2 — escalate ONLY this step to a stronger model on a DIFFERENT provider
    _gen_step(steps, "strong", f"Rung 2 — escalate this step to {STRONG['provider']}",
              f"re-generated with a stronger model on another provider", "ok")
    cost += COST["strong"]
    ok, detail = verify(task["strong_out"], spec, checker)
    _gen_step(steps, "verifier", "Verify against reality", detail, "pass" if ok else "fail", checker=checker, output=detail)
    advice = (f"Cheap {CHEAP['provider']} model failed the reality check ({fail_reason}); escalated to "
              f"{STRONG['provider']} and it passed. Pin this step type to the stronger model, or tighten the prompt.")
    return _result(task, mode, steps, ok, cost, "cross-provider-escalate", advice)


def _result(task, mode, steps, ok, cost, fixed_by, advice):
    return {"task": task["name"], "desc": task["desc"], "mode": mode, "domain": task["domain"],
            "steps": steps, "passed": ok, "cost": cost, "fixed_by": fixed_by, "advice": advice,
            "flagged": False, "shipped_broken": (not ok), "scored": True}


def run_all():
    modes = ["cheap", "bongo", "strong"]
    results = {m: [run_task(t, m) for t in TASKS] for m in modes}

    def agg(m):
        scored = [r for r in results[m] if r["scored"]]
        passed = sum(1 for r in scored if r["passed"])
        return {"mode": m, "passed": passed, "total": len(scored),
                "reliability": round(100 * passed / len(scored)) if scored else 0,
                "cost_units": sum(r["cost"] for r in results[m]),
                "broken_shipped": sum(1 for r in results[m] if r["shipped_broken"])}

    sb = {m: agg(m) for m in modes}
    PRICE = 0.002
    scale = 1000 / len([t for t in TASKS if t["kind"] == "normal"])
    for m in modes:
        sb[m]["cost_per_1k_usd"] = round(sb[m]["cost_units"] * scale * PRICE, 2)

    cb, bg, st = sb["cheap"], sb["bongo"], sb["strong"]
    escalated = sum(1 for r in results["bongo"] if r["fixed_by"] in ("cross-provider-escalate", "retry-cheap"))
    headline = {"bongo_reliability": bg["reliability"], "cheap_reliability": cb["reliability"],
                "savings_vs_strong_pct": round(100 * (st["cost_units"] - bg["cost_units"]) / st["cost_units"]),
                "cheap_broken_shipped": cb["broken_shipped"],
                "escalated": escalated, "total_steps": len([t for t in TASKS if t["kind"] == "normal"])}
    return {"results": results, "scoreboard": sb, "headline": headline,
            "providers": {"cheap": CHEAP, "strong": STRONG}, "checkers": list(CHECKERS)}


if __name__ == "__main__":
    d = run_all(); sb = d["scoreboard"]; h = d["headline"]
    print("\n=== PLUMBLINE — scoreboard (verifiable steps, per 1,000 runs) ===\n")
    for m in ["cheap", "bongo", "strong"]:
        s = sb[m]; name = {"cheap": "Cheap model alone", "bongo": "Cheap + Plumbline", "strong": "Expensive model alone"}[m]
        print(f"  {name:24s} reliability {s['reliability']:3d}%   ${s['cost_per_1k_usd']:>7}/1k   broken shipped: {s['broken_shipped']}")
    print(f"\n  -> Plumbline: {h['bongo_reliability']}% reliable (vs cheap {h['cheap_reliability']}%), "
          f"{h['savings_vs_strong_pct']}% cheaper than the big model. Escalated only {h['escalated']}/{h['total_steps']} steps.")
    print("  -> Recovery ladder + kill-switch + honest low-confidence flag all fire. Cross-provider Mistral->Anthropic.\n")
