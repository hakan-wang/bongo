# TEAM-BUILD-PLAN.md

> **FOR FILIP — your tasks are in the "## FILIP — START HERE" section below. Your Claude can read this file directly.** You do not need to read the rest. Scroll to your section, do the numbered steps in order, and after each step check the "→ you should see" line. If you don't see it, STOP and ping Håkan.

---

## What Bongo is (refined)

Bongo is a **reliability layer for companies that run an LLM API inside a multi-step agentic workflow** (e.g. Håkan's "Brolly" video editor on Gemini, Michelle's "PlugClar", or any startup with an API-powered agent).

- **You pick your own model + provider.** Bongo never swaps your model behind your back.
- **Bongo is NOT a router and NOT OpenRouter.** Those pick a model *for* you by task. Bongo does the opposite: you keep the model you chose, and Bongo watches it.
- **Bongo sits in the request path and TRACES each step.** No model is 100% accurate — they fetch the wrong data, write the wrong thing, mis-step. Bongo **CATCHES** when your chosen model is inaccurate, **PINPOINTS** which step went wrong, then **INTERVENES** with a solution:
  - **(a) escalate that one step** to a stronger model (cross-provider), and/or
  - **(b) tell you how to improve it next time** (advice on the prompt / which step to pin to the strong model).
- **The moat: cross-provider + in-the-loop + per-step.** A model lab can only ever improve its *own* model. Bongo improves reliability *across* providers, *inside* your live run, at the *individual step* level.

**One-line moat statement (verbatim for the pitch):** "Cross-provider + in-the-loop + per-step — a model lab only ever improves its own model."

**Wedge line (verbatim):** "You pick the model and the provider. Bongo doesn't pick for you — it catches when YOUR chosen model is wrong, mid-run, and escalates only that step."

---

## Honest status

Be precise. Do not overclaim — if a judge inspects the source, every claim below must hold.

**What genuinely exists today:**
- **A convincing, self-contained DEMO** (`demo/`): `scenarios.py` runs a **real, deterministic verifier** on staged coding tasks; `server.py` serves it on **http://localhost:8200**; `index.html` shows a side-by-side run + scoreboard (cheap ~67% → Bongo 100% → strong 100%). The model outputs are **PINNED** (staged for stage-safety, because small LLMs are non-deterministic); the **verification is real**.
- **`reliability.py`**: the real reliability-loop logic (cheap → verify → escalate), standalone.
- **`proxy.py`**: an OpenAI-compatible proxy skeleton (caching only, mock mode by default, serves on **http://localhost:8128**) — the *beginning* of the "connect your API" mechanism, not yet wired to the reliability loop or to real provider calls beyond OpenAI.
- **`demo/real_proof.py`**: a script for ONE genuinely-real cross-provider escalation (Mistral → Anthropic/OpenAI). It reads `MISTRAL_API_KEY` + (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`), generates with the cheap model, runs the **real** tests, and on failure escalates to the strong model on a different provider. **Needs API keys.**

**What is still a demo / not real yet (say this out loud):**
- There is **no working way today** for a real founder to point Bongo at their own arbitrary workflow (e.g. Brolly) and have it catch failures live. The proxy is not wired to the reliability loop, and reaches only OpenAI's wire format.
- The stage demo outputs are **pinned**. The only un-pinned, genuinely-real artifact is `real_proof.py`.
- The Connect card's hosted snippet (`api.bongo.dev`) is **aspirational** — that domain does not resolve. The real, runnable endpoint is `http://localhost:8128`.

**The 36h hackathon deliverable is:** the convincing DEMO + the real cross-provider PROOF (recorded) + crystal clarity on how a user *would* use it. **Not** a full production product.

---

## What we were missing

Two gap audits asked "how would a real founder actually USE this today?" Here is what they found and the fixes. The headline: the demo proves the *concept*, but a real founder hits a wall in 60 seconds because **"how does Bongo know MY step is wrong when I have no unit tests?"** is unanswered.

**P0 — blockers (without these, "use Bongo" is impossible):**
1. **The verifier is "bring your own" and that's the whole product — but it's hard-coded.** Both real engines only catch a failure because the user pre-supplied ground truth (`reliability.py:check_meeting` is one fixed schema; `scenarios.py` needs you to hand it unit tests). Brolly has neither.
   - **Fix:** Reframe as "you bring the check," and ship 3–4 zero-config generic checkers in the `CHECKERS` registry: (a) JSON/format validity, (b) schema-from-one-example, (c) tool-arg validity, (d) LLM-judge-with-rubric as the explicit lower-confidence fallback. Onboarding becomes "paste one good output," not "write unit tests."
2. **No connect-your-workflow path.** `reliability.py` (the catch loop) and `proxy.py` (the transport) are separate, unconnected files; the proxy only caches and only reaches OpenAI.
   - **Fix:** Wire ONE provider end-to-end: proxy receives request → calls provider → runs the matching checker → on fail, escalates via `reliability.run_step` → returns corrected response.
3. **Provider lock-in.** The only "real" proxy reaches OpenAI only; Brolly is on Gemini.
   - **Fix:** Lift `real_proof.py`'s four hand-rolled provider shapers into a shared `providers.py`; pick by `BONGO_TARGET_PROVIDER`.

**P1 — "I connected it but I'm confused":**
4. **No QUICKSTART for an outside founder** — all docs are internal stage-prep, and the snippet points at a non-existent domain. **Fix:** a 5-line QUICKSTART using `http://localhost:8128`, written to Filip's idiot-proof bar.
5. **No key/env story** — no `.env.example`, no preflight. **Fix:** `.env.example` + a startup check that prints "✓ key found / ✗ key MISSING" per role.
6. **The "(b) how to improve next time" advice output does not exist in any file** — it's promised in the definition, absent in code. **Fix:** per failed step, surface the failing input + checker reason + cheap-vs-strong diff + one templated "why it missed / how to fix" line.
7. **README sells the wrong product** (cost/caching, not reliability). **Fix (cheapest credibility win):** rewrite the README lede to lead with trace → catch → escalate cross-provider; demote caching to one line. Update `proxy.py`'s docstring too.

**P2 — honesty / "will it survive a judge":**
8. The demo is fully pinned — only safe if said out loud; keep `real_proof.py` recorded next to it as the "this is real" exhibit.
9. No error handling on the real path (no retry/timeout/4xx handling). **Fix:** wrap provider calls; on transport error, record a trace event ("provider error → escalated") instead of throwing.
10. "Per-step" is claimed but the unit is a single step. **Fix (scope honestly):** make the trace show a 3-step chain where step 2 fails and Bongo isolates it (pinned is fine).

**The one fix if we only do one:** the zero-config generic checkers (#1) + one wired end-to-end provider path (#2/#3), so a user can point a real app at Bongo and watch it catch one real failure — plus the recorded `real_proof.py`. That is a defensible "you can use it today."

---

## Work split

### HÅKAN-SIDE (Claude builds this — no human credentials needed)

Build order is critical-path: do **B + C6 + README + QUICKSTART first** (Filip is blocked until the run-card and a mock-validated `real_proof.py` exist), then A/C/D in parallel.

**B — Make Bongo work end-to-end for one simple workflow (mock/offline, no keys):**
- [ ] **B1.** Wire `reliability.py:run_step()` (cheap→verify→retry→strong) into `proxy.py`'s POST handler, behind the existing `BONGO_REAL` flag; default to mock. **Done-when:** POSTing a JSON-extraction prompt to `localhost:8128` returns a Bongo trace (attempts + fixed_by) in mock mode, no key.
- [ ] **B2.** Add a per-request verify hook: a `bongo_verify` field (or a default JSON-schema check) selects a checker from `CHECKERS`. **Done-when:** the proxy records pass/fail per request.
- [ ] **B3.** Add Mistral + Anthropic call sites to the proxy/strong path, mirroring `real_proof.py`'s `call_mistral`/`call_strong`, gated behind `BONGO_REAL` + env keys, mock strings otherwise. **Done-when:** cross-provider code paths exist and pass in mock; flipping the flag + adding a key is the ONLY thing Filip must do.
- [ ] **B4.** Add a `--mock` mode to `demo/real_proof.py` that fakes the Mistral failure + Anthropic fix so Claude can validate the script's narrative/output formatting WITHOUT keys. **Done-when:** `python3 demo/real_proof.py --mock` prints the full red→escalate→green narrative with no keys.
- [ ] **B5 (contingency — do before hour 12).** Confirm at least one task in `scenarios.TASKS` reliably trips `mistral-small`. If `roman_to_int`/`slugify` are flaky, **add a guaranteed-failing task** (e.g. subtractive-notation edge or a tricky parsing case) so Filip's recording can't get stuck on a lucky pass. **Done-when:** `--mock` and a code-read confirm a task designed to fail exists and is documented in the run-card.

**Checkers (the actual product gap):**
- [ ] **B6.** Ship the zero-config generic checkers in `CHECKERS`: `format` (JSON/structure valid — the zero-config default), `schema-from-example`, `tool-args`, `llm-judge` (labeled lower-confidence). **Done-when:** a step with no unit tests can still be checked by `format`.
- [ ] **B7.** Add the **"(b) how to fix next time"** advice output: per failed step, emit failing input + checker reason + cheap-vs-strong diff + one templated advice line. **Done-when:** the trace shows advice text, not just pass/fail.

**A — Make install/use unmistakable in the DEMO:**
- [ ] **A1.** Connect card: add a second snippet pointing at the **real** `http://localhost:8128`, next to the aspirational hosted URL. **Done-when:** the "change one line" claim is copy-pasteable and actually runs.
- [ ] **A2.** Add a 4th "how it works" step showing what Bongo gives BACK ("step 3 fetched wrong data → escalated to Anthropic → fixed; step 5 was fine"). **Done-when:** a non-technical viewer can state the per-step output in one sentence.
- [ ] **A3.** Bridge toy → real: one line framing the coding demo as a stand-in for Brolly's steps (storyboard → fetch clips → cut → caption). **Done-when:** the demo explicitly ties coding tasks to a real agent's steps.
- [ ] **A4.** Kill router/OpenRouter confusion on screen: put "you pick your model" in the hero. **Done-when:** the wedge line is in the hero, not just the footer.

**README + QUICKSTART + env (credibility):**
- [ ] **R1.** Rewrite `README.md` lede: reliability-first (trace → catch → escalate cross-provider), caching demoted to one line. Update `proxy.py` docstring. **Done-when:** a founder reading the repo sees a reliability layer, not a cache.
- [ ] **R2.** Write `QUICKSTART.md` for an outside founder, honest about current state: (1) run the demo locally `python3 demo/server.py` → 8200; (2) see a real cross-provider catch `python3 demo/real_proof.py` (needs keys); (3) connecting your own workflow is the next milestone, here's the 1-line proxy change (`base_url=http://localhost:8128`). No fictional domains. **Done-when:** an outsider can follow it cold.
- [ ] **R3.** Add `.env.example` listing exactly which key for which role (cheap = Mistral, strong = Anthropic/OpenAI, target = your provider) + a startup preflight printing "✓/✗ key found". **Done-when:** Filip can't run blind.

**C — Stage-proofing (deterministic, no human):**
- [ ] **C1.** Determinism gate: run `python3 demo/scenarios.py` 10× and assert byte-identical scoreboard. **Done-when:** prints "10/10 identical" or fails loudly.
- [ ] **C2.** Smoke-test: start `demo/server.py`, GET `/api/run`, assert 200 + `results`/`scoreboard`/`headline`/`providers`/`checkers` present.
- [ ] **C3.** Confirm the literal failing-assert text (e.g. `FAILED: assert roman_to_int('IV') == 4`) renders in the red column.
- [ ] **C4.** Confirm every step row shows `provider·model` and cheap=Mistral / strong=Anthropic are visibly DIFFERENT providers.
- [ ] **C5.** Stats path: `demo_traffic.py` lives at **repo root** and targets the **proxy (8128)**, NOT the stage demo (8200). The stats demo requires `python3 proxy.py` running separately. Document this exact path + dependency. **Done-when:** with the proxy up, running `python3 demo_traffic.py` then GET `localhost:8128/stats` shows non-zero hit_rate/cost_saved.
- [ ] **C6.** Write the idiot-proof RUN-CARD (the "## FILIP — START HERE" section below IS this card). Exact commands, exact ports (demo 8200, proxy 8128), success checks, port-busy recovery.
- [ ] **C7.** "Reset to clean state" task: before stage, kill stray servers on 8128/8200, clear proxy cache/stats. **Done-when:** both ports bind cleanly and stats start fresh.

**D — Pitch / GTM (Håkan-facing, Claude-authored):**
- [ ] **D1.** 90-second demo script + memorized wedge line + honesty line, as a print-ready one-pager.
- [ ] **D2.** Pre-write the two rebuttals: "Is it faked?" (verify is real, outputs pinned for stage-safety, recorded real proof exists) and "How does a user actually adopt this?" (QUICKSTART + 1-line base_url change).
- [ ] **D3.** Moat statement verbatim on the demo screen and in pitch notes.

---

### FILIP — START HERE

**Read this first (10 seconds).** Your ONE job: get two API keys, set them as environment variables, run ONE Python script, and screen-record it. Then record a 90-second backup video of the demo. That's it. **Do NOT edit any code. Do NOT pick different models. Do NOT paste keys into any file in the repo.** Follow each step exactly. After each step there's a "→ you should see" line — if you do NOT see that, STOP and ping Håkan. Total time ~25 minutes.

- The repo is at: `/Users/hakanwang/Bongo`
- The script you'll run is: `/Users/hakanwang/Bongo/demo/real_proof.py`

---

#### PART A — GET THE MISTRAL API KEY (the "cheap" model)

**1.** Open a browser and go to EXACTLY: `https://console.mistral.ai`
→ you should see a Mistral sign-in / sign-up page. **(Use console.mistral.ai, NOT admin.mistral.ai — admin keys are the wrong artifact.)**

**2.** Sign up ("Continue with Google" with your own account, or email). Verify email if asked.
→ you should see the Mistral console dashboard ("La Plateforme" / "Mistral Studio").

**3.** In the LEFT sidebar click **Billing** (may be under "Workspace" or a wallet/`$` icon). Add a credit card. This is REQUIRED — without billing the key is locked to a tiny free tier and the script may fail with a quota error.
→ you should see your card listed, no red warning.

**4.** In the LEFT sidebar click **API Keys**.
→ you should see an "API Keys" page with a create button.

**5.** Click **Create new key** (or "Create API key"). Name it `bongo-proof`. Any future expiration is fine.
→ you should see a popup with a long key string.

**6.** Click **Copy**. Paste it into a plain text note so you don't lose it.
→ The key is one long string of letters/numbers (~32+ chars), no spaces.

**COMMON MISTAKES:**
- The key you want appeared **ONCE in a popup right after clicking Create**. If you can see the full key on a *list* page later, it's the wrong thing — that's a name/ID, not the secret.
- Do NOT copy the key NAME (`bongo-proof`). Do NOT copy a "Workspace ID" / "Project ID" / "Org ID".
- The key shows only once. If you closed the popup, just click **Create new key** again for a fresh one.
→ you should now have the Mistral key saved in your note.

---

#### PART B — GET THE ANTHROPIC API KEY (the "strong" model) — PRIMARY

Use Anthropic. Only fall back to OpenAI (Part B-ALT) if Anthropic billing won't go through.

**7.** Go to EXACTLY: `https://console.anthropic.com` (it will redirect to `platform.claude.com` — that is the SAME console, this is normal).
→ you should see an Anthropic / Claude sign-in page.

**8.** Sign up or log in (Google is fine).
→ you should see the Anthropic developer console.

**9.** LEFT sidebar → **Settings** → **Billing**. Add a card and buy the minimum prepaid credits (usually $5 is plenty).
→ you should see a positive balance (e.g. "$5.00") and a saved card. (Skipping this is the #1 reason a brand-new key errors.)

**10.** LEFT sidebar → **API Keys**.
→ you should see an "API Keys" page with a "Create Key" button.

**11.** Click **Create Key**, name it `bongo-proof`, confirm.
→ you should see a key that STARTS WITH `sk-ant-` (full form `sk-ant-api03-...`).

**12.** Click **Copy** and paste it into your note next to the Mistral key. **Label them clearly.**
→ you now have TWO keys: Mistral (no prefix) and Anthropic (starts `sk-ant-`).

**COMMON MISTAKES:**
- The Anthropic key MUST start with `sk-ant-`. If it doesn't, you copied the wrong thing — make a new key.
- Don't mix them up. Mistral = no prefix. Anthropic = `sk-ant-`.

**Part B-ALT (ONLY if Anthropic billing fails — otherwise SKIP):**
Go to `https://platform.openai.com/api-keys`, log in, add billing, click "Create new secret key", name it `bongo-proof`, copy it (starts `sk-`, often `sk-proj-`). If you use this instead of Anthropic, in step 14 export `OPENAI_API_KEY` instead of `ANTHROPIC_API_KEY`, **and first run `unset ANTHROPIC_API_KEY`** (the script auto-picks Anthropic if its var is set, even if blank).

---

#### PART C — SET THE KEYS AS ENVIRONMENT VARIABLES (macOS)

Open Terminal: press `Cmd+Space`, type `Terminal`, press Enter.
→ you should see a Terminal window with a text prompt.

**13.** Confirm your shell. Copy-paste and press Enter:
```
echo $SHELL
```
→ you should see something ending in `/zsh`. If it says `/bash`, tell Håkan (the persist file differs; the temporary exports below still work).

**14.** Set BOTH keys for THIS terminal. Replace the ALL-CAPS placeholder with YOUR key (no quotes, no spaces around `=`), press Enter after each:
```
export MISTRAL_API_KEY=PASTE_YOUR_MISTRAL_KEY_HERE
export ANTHROPIC_API_KEY=PASTE_YOUR_ANTHROPIC_KEY_HERE
```
(If you used OpenAI instead, first run `unset ANTHROPIC_API_KEY`, then:)
```
export OPENAI_API_KEY=PASTE_YOUR_OPENAI_KEY_HERE
```
→ pressing Enter shows no output and no error. Silence = success.
**Set exactly ONE strong key.** A stale/blank `ANTHROPIC_API_KEY` silently beats your OpenAI key — that's why you `unset` it.

**15.** VERIFY both are set — **use this MASKED check (it prints only the first 4 characters, so it's safe even while recording):**
```
echo ${MISTRAL_API_KEY:0:4}
echo ${ANTHROPIC_API_KEY:0:4}
```
→ you should see 4 characters on each line (e.g. the start of your Mistral key, then `sk-a`). If a line is BLANK, the export didn't take — redo step 14 for that key. **Do this verification BEFORE you start any screen recording — never echo the full key while recording.**

**16 (optional, recommended — make them persist).** Replace placeholders with your real keys, press Enter after each:
```
echo 'export MISTRAL_API_KEY=PASTE_YOUR_MISTRAL_KEY_HERE' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY=PASTE_YOUR_ANTHROPIC_KEY_HERE' >> ~/.zshrc
source ~/.zshrc
```
→ `echo ${MISTRAL_API_KEY:0:4}` still prints 4 chars in a new terminal. **Do NOT commit `~/.zshrc` or any key into the git repo. Keys are secret.**

---

#### PART D — RUN THE REAL PROOF SCRIPT

**17.** Run the proof. The script imports `scenarios.py` from the same folder, so run it from inside `demo/`. Copy-paste exactly:
```
cd /Users/hakanwang/Bongo/demo && python3 real_proof.py
```
(If that errors with "No module named scenarios", instead run: `cd /Users/hakanwang/Bongo && python3 demo/real_proof.py` — but try the first one FIRST.)
→ you should see output with this SHAPE (exact code/text varies):
```
=== Bongo real cross-provider proof — task: roman_to_int() ===
[1] CHEAP model  (Mistral / mistral-small-latest) generating...
    -> Bongo verify (real tests): FAIL — <some detail>
[2] Bongo caught a SILENT failure -> escalating THIS step across providers
[3] STRONG model (Anthropic / claude-sonnet-4-5) re-generating...
    -> Bongo verify (real tests): PASS — ...
=== RESULT: Mistral failed -> escalated to Anthropic -> GREEN (real, cross-provider) ===
```
**That "Mistral failed -> escalated to Anthropic -> GREEN" line is the gold. That is the proof.**

**IF the cheap model PASSES instead** (output says it passed and to re-run): the small model got lucky. Run a harder task:
```
python3 real_proof.py slugify
```
Re-run (try `slugify`, then `roman_to_int` a couple times) until you get the GREEN escalation. **If after 5 tries you still can't get a red→green, STOP and ping Håkan — Claude will hand you a guaranteed-failing task name to use.**

**TROUBLESHOOTING (match the error text):**
- "Set MISTRAL_API_KEY…" / "Set ANTHROPIC_API_KEY…" → the var isn't set in THIS terminal. Redo step 14 here, re-run.
- "command not found: python3" → run `python3 --version`; if it fails, tell Håkan.
- "No module named scenarios" → wrong folder. Use `cd /Users/hakanwang/Bongo/demo && python3 real_proof.py`.
- "401" / "Unauthorized" / "invalid api key" → key has a typo/space. Re-copy (Mistral = no prefix, Anthropic = `sk-ant-`), redo step 14.
- "402" / "billing" / "credit" / "quota" / "insufficient" → billing not set up. Go back to step 3 (Mistral) or step 9 (Anthropic).
- "urlopen error" / timeout → check wifi, re-run.

---

#### PART E — SCREEN-RECORD THE RUN (this recording IS the deliverable)

**18.** Get ready BEFORE recording: Terminal open, in `/Users/hakanwang/Bongo/demo`, keys verified with the MASKED check in step 15. Make the Terminal window big. **Do not echo full keys on screen.**

**19.** Start the macOS recorder: press `Cmd + Shift + 5`.
→ a small control bar appears at the bottom.

**20.** Click **Record Entire Screen** (or "Record Selected Portion" and box the Terminal), then click **Record**.
→ a recording indicator appears top-right.

**21.** Click into Terminal, run:
```
python3 real_proof.py
```
(or `python3 real_proof.py slugify` if needed). Let it finish, including the final `=== RESULT: ... GREEN ... ===` line. Wait 2 extra seconds.
→ the GREEN result line is fully visible.

**22.** Stop: press `Cmd + Shift + 5` → **Stop**, or click the stop square top-right.
→ a thumbnail pops up bottom-right, then the file saves to the Desktop.

**23.** Rename to `bongo-real-proof.mov` and move it into the repo. Copy-paste (adjust source name if needed):
```
mv ~/Desktop/bongo-real-proof.mov /Users/hakanwang/Bongo/demo/bongo-real-proof.mov
```
(If the Desktop file still has its default name, rename in Finder first, or use `mv ~/Desktop/"Screen Recording"*.mov /Users/hakanwang/Bongo/demo/bongo-real-proof.mov`.)
→ `ls /Users/hakanwang/Bongo/demo/bongo-real-proof.mov` prints that path (no "No such file"). Done — the real proof is captured.

---

#### PART F — RECORD A 90-SECOND FALLBACK DEMO VIDEO (the pinned on-stage demo)

This is the safe backup. Outputs are PINNED (deterministic) so it ALWAYS works — **no keys needed for this part.**

**24.** Open a NEW Terminal window (`Cmd+N`). Copy-paste and press Enter:
```
cd /Users/hakanwang/Bongo && python3 demo/server.py
```
→ you should see a line mentioning **port 8200** (e.g. "Bongo dashboard: http://localhost:8200"). **LEAVE this terminal running.** (If it says "Address already in use", the server is already up — fine, continue.)

**25.** In your browser go to EXACTLY: `http://localhost:8200`
→ you should see the Bongo demo page (side-by-side view + scoreboard).

**26.** Start recording: `Cmd + Shift + 5` → **Record Entire Screen** (or box the browser) → **Record**.
→ recording indicator top-right.

**27.** Click the **Run** button (may read "Run demo" / "Run all"). Let the scenarios play and the scoreboard fill in. Keep it under ~90 seconds; once the scoreboard shows the result, wait 2 seconds, then stop.
→ the page shows side-by-side results + an updated scoreboard (cheap ~67% / Bongo 100% / strong 100%).

**28.** Stop the recording (`Cmd + Shift + 5` → Stop). It saves to the Desktop.

**29.** Rename and move into the repo:
```
mv ~/Desktop/"Screen Recording"*.mov /Users/hakanwang/Bongo/demo/bongo-demo-fallback.mov
```
(If the wildcard matches several files, rename by hand in Finder to `bongo-demo-fallback.mov` and drag it into `/Users/hakanwang/Bongo/demo/`.)
→ `ls /Users/hakanwang/Bongo/demo/bongo-demo-fallback.mov` prints that path. Done.

---

#### WHEN YOU'RE DONE — message Håkan exactly this:

> "Both videos are in `/Users/hakanwang/Bongo/demo/`:
> 1. `bongo-real-proof.mov` — real Mistral→Anthropic escalation, ended GREEN.
> 2. `bongo-demo-fallback.mov` — the pinned side-by-side + scoreboard demo.
> Keys are set in my terminal (and `~/.zshrc`). I did not edit any code or commit any keys."

**DO NOT:** edit any `.py` or `.html` file, change model names, paste keys into any file in the repo, or `git commit` keys. If anything doesn't match a "→ you should see" line, STOP and ping Håkan.

**Sources (verified mid-2026):** Mistral console (key has no prefix, billing required) `https://console.mistral.ai`; Anthropic console (redirects to platform.claude.com, key starts `sk-ant-`) `https://console.anthropic.com`; OpenAI fallback (key starts `sk-`) `https://platform.openai.com/api-keys`.

---

## Definition of done (hackathon)

We are DONE when ALL of these are true:

1. **The pinned demo runs in one command, offline, deterministically.** `python3 demo/server.py` → `http://localhost:8200` → "Run" shows left ending RED with a real failing-assert line, right flipping RED→GREEN with "escalated to Anthropic." Scoreboard matches `python3 demo/scenarios.py` (cheap ~67% / Bongo 100% / strong 100%). Verified 10/10 identical (C1) and works with wifi off.
2. **The real cross-provider proof is RECORDED.** `bongo-real-proof.mov` exists in `demo/`, showing two real providers, a real Mistral failure, real escalation to Anthropic, and a real GREEN re-verify. (And we've confirmed a guaranteed-failing task exists so this is reproducible — B5.)
3. **The 90-second fallback video exists** (`bongo-demo-fallback.mov` in `demo/`) on the presenting laptop.
4. **A founder can answer "how do I use this?" in 3 steps.** `QUICKSTART.md` is honest and outsider-followable; the Connect card shows the real `http://localhost:8128` snippet; the README leads with reliability, not caching.
5. **The "how does Bongo know MY step is wrong?" answer exists and is demonstrable** — at least the `format` zero-config checker works on a step with no unit tests (B6), and the trace shows the "(b) how to fix next time" advice (B7).
6. **We can stay honest under questioning.** Both rebuttals ("is it faked?" / "how do users adopt?") are written; the pinned-vs-real distinction is stated out loud; no fictional `api.bongo.dev` is shown as if live.
7. **Stage is safe.** `BONGO_REAL` is OFF for the stage demo (it never reads a key); ports 8128/8200 are free and reset clean (C7); Håkan has local copies of both videos and the pitch one-pager.