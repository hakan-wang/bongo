"""
Bongo reliability core: watch a cheap model's step, catch bad output, correct it.

This is the MAIN feature. The logic here is real:
- checkers are deterministic (valid JSON, required fields, right types, constraints)
- recovery is real (retry the cheap model, then fall back to the strong model)

Only the model calls are simulated (no API key yet). Swap simulate_* for real API
calls and nothing else changes.
"""
import json

# relative cost units: the strong model costs 50x the cheap one
COST = {"cheap": 1, "strong": 50}

# ---- deterministic checkers (how Bongo knows a step is wrong, no AI judging AI) ----
def check_meeting(obj):
    """Return (ok, reason). The task: extract {title, date, attendees[list], duration_min int}."""
    if not isinstance(obj, dict):
        return False, "not a JSON object"
    for field in ("title", "date", "attendees", "duration_min"):
        if field not in obj:
            return False, f"missing field '{field}'"
    if not isinstance(obj["attendees"], list) or not obj["attendees"]:
        return False, "'attendees' must be a non-empty list"
    if not isinstance(obj["duration_min"], int):
        return False, "'duration_min' must be an integer"
    if not (0 < obj["duration_min"] <= 24 * 60):
        return False, "'duration_min' out of range"
    return True, "valid"

def parse_json(text):
    try:
        return json.loads(text), None
    except Exception as e:
        return None, f"invalid JSON: {e}"

# ---- the step runner: trace, check, recover ----
def run_step(task_input, cheap_model, strong_model, max_retries=1):
    """
    Run one agent step through Bongo. Returns a trace dict.
    Order: cheap model -> check -> retry cheap -> fall back to strong.
    """
    trace = {"input": task_input, "attempts": [], "cost": 0, "final": None, "fixed_by": None}

    # attempt 1 + retries on the CHEAP model
    for attempt in range(max_retries + 1):
        raw = cheap_model(task_input, attempt)
        trace["cost"] += COST["cheap"]
        obj, perr = parse_json(raw)
        ok, reason = (False, perr) if perr else check_meeting(obj)
        trace["attempts"].append({"model": "cheap", "attempt": attempt + 1, "ok": ok, "reason": reason})
        if ok:
            trace["final"] = obj
            trace["fixed_by"] = "cheap" if attempt == 0 else "cheap-retry"
            return trace

    # fall back to the STRONG model for this one step
    raw = strong_model(task_input)
    trace["cost"] += COST["strong"]
    obj, perr = parse_json(raw)
    ok, reason = (False, perr) if perr else check_meeting(obj)
    trace["attempts"].append({"model": "strong", "attempt": 1, "ok": ok, "reason": reason})
    trace["final"] = obj if ok else None
    trace["fixed_by"] = "strong-fallback" if ok else "UNRECOVERED"
    return trace
