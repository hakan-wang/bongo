"""
Plumbline reliability demo:  python3 reliability_demo.py

A multi-step agent extracts meeting details into JSON.
The CHEAP model is unreliable (it really produces broken outputs here).
Plumbline catches every bad step and recovers it, so the final result is 100% correct,
while costing far less than always using the strong model.

Real logic (checkers + recovery). Models are simulated (no API key yet).
"""
from reliability import run_step, COST

INPUTS = [
    "Sync with Ana and Theo about the launch, Tuesday, 30 minutes.",
    "1:1 with Priya, Monday, half an hour.",
    "Board review with the exec team, Friday, 90 minutes.",
    "Standup with the eng team, daily, 15 minutes.",
    "Investor call with Khosla, Thursday, 45 minutes.",
]

GOOD = {
    INPUTS[0]: '{"title":"Launch sync","date":"Tue","attendees":["Ana","Theo"],"duration_min":30}',
    INPUTS[1]: '{"title":"1:1 with Priya","date":"Mon","attendees":["Priya"],"duration_min":30}',
    INPUTS[2]: '{"title":"Board review","date":"Fri","attendees":["exec team"],"duration_min":90}',
    INPUTS[3]: '{"title":"Standup","date":"daily","attendees":["eng team"],"duration_min":15}',
    INPUTS[4]: '{"title":"Investor call","date":"Thu","attendees":["Khosla"],"duration_min":45}',
}
# the cheap model fails first try on these (real, common failures)
CHEAP_FAILS = {
    INPUTS[1]: 'Sure! {"title":"1:1 with Priya","date":"Mon","attendees":["Priya"]}',  # missing duration
    INPUTS[2]: '{"title":"Board review","date":"Fri","attendees":"exec team","duration_min":"90"}',  # wrong types
    INPUTS[4]: 'Here you go:\n{"title":"Investor call" "date":"Thu"}',  # broken JSON
}

def cheap_model(task, attempt):
    # attempt 0 may be broken; on retry (attempt 1) the cheap model gets it right
    if attempt == 0 and task in CHEAP_FAILS:
        return CHEAP_FAILS[task]
    return GOOD[task]

def strong_model(task):
    return GOOD[task]

def main():
    print("\nBONGO RELIABILITY  ·  cheap model, watched and corrected\n" + "-"*60)
    total_cost = 0
    correct = 0
    cheap_alone_correct = 0
    for task in INPUTS:
        t = run_step(task, cheap_model, strong_model, max_retries=1)
        total_cost += t["cost"]
        if t["final"]: correct += 1
        # how the cheap model would have done with NO Plumbline (first attempt only)
        first = t["attempts"][0]
        if first["ok"]: cheap_alone_correct += 1
        status = {"cheap":"ok first try","cheap-retry":"caught -> retried -> fixed",
                  "strong-fallback":"caught -> fell back to strong","UNRECOVERED":"FAILED"}[t["fixed_by"]]
        print(f"\n• {task}")
        for a in t["attempts"]:
            mark = "ok " if a["ok"] else "BAD"
            print(f"    [{mark}] {a['model']} try {a['attempt']}: {a['reason']}")
        print(f"    => {status}")

    baseline_cost = len(INPUTS) * COST["strong"]      # always use the strong model
    cheap_only_cost = len(INPUTS) * COST["cheap"]
    print("\n" + "-"*60)
    print(f"Correctness WITH Plumbline:        {correct}/{len(INPUTS)}  ({correct/len(INPUTS)*100:.0f}%)")
    print(f"Correctness cheap model alone: {cheap_alone_correct}/{len(INPUTS)}  ({cheap_alone_correct/len(INPUTS)*100:.0f}%)")
    print(f"\nCost WITH Plumbline:        {total_cost} units")
    print(f"Cost always-strong:     {baseline_cost} units")
    print(f"Savings vs always-strong: {(1-total_cost/baseline_cost)*100:.0f}%")
    print(f"\n=> Pro-level reliability ({correct/len(INPUTS)*100:.0f}%) at {(1-total_cost/baseline_cost)*100:.0f}% lower cost.\n")

if __name__ == "__main__":
    main()
