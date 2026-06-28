# Team workloads — who builds what (morning of submission)

> **Submission deadline: 13:00 Paris, Sun Jun 28.** Track: Software for Agents.
> Required: public GitHub repo + README + demo video (≤5 min) + pitch deck.
>
> - **Filip** → your tasks are in **[`TEAM-BUILD-PLAN.md`](TEAM-BUILD-PLAN.md)** → "FILIP — START HERE"
>   (get API keys, run `demo/real_proof.py`, screen-record the real cross-provider catch + a fallback demo video).
> - **Haonan** → your tasks are **below** in this file.
> - **Michelle** → pitch + video (script in [`positioning/VIDEO-SCRIPT.md`](positioning/VIDEO-SCRIPT.md), deck in [`positioning/deck.html`](positioning/deck.html)).
> - **Håkan** → GTM / live pitch / close LOIs. Claude has built the product, demo, README, deck, positioning.

The product is named **Assay**. One line: *"Keep your model. We verify it against reality."*
Run the demo: `python3 demo/server.py` → http://localhost:8200 → click "Run the agent".

---

## HAONAN — START HERE

Treat each step as exact. After each, check the "→ you should see" line. If you don't, ping Håkan.
Your Claude can read this whole repo — point it at `README.md` and `positioning/POSITIONING.md` first.

### Task 1 — Clean-clone test (catches submission-killing bugs) [~15 min]
A judge will clone the repo fresh. Make sure it runs from nothing.
1. In Terminal: `cd /tmp && rm -rf assay-test && git clone https://github.com/hakan-wang/bongo.git assay-test && cd assay-test`
   → you should see it clone with no error.
2. `python3 demo/scenarios.py`
   → you should see the scoreboard: **Cheap 60% → Assay 100%, 74% cheaper**, and lines about the kill-switch + low-confidence flag.
3. `python3 demo/server.py` then open http://localhost:8200 and click **Run the agent**.
   → left column ends with a red "wired the wrong amount"; right column catches it, escalates, ends green; a scoreboard appears.
4. If ANY step errors, copy the exact error and ping Håkan immediately. **This is the most important task — do it first.**

### Task 2 — Deploy the static demo to GitHub Pages (gives judges a clickable link) [~15 min]
`docs/index.html` is a static, judge-facing version (no install).
1. On GitHub: repo **Settings → Pages**. Under "Build and deployment", Source = **Deploy from a branch**; Branch = **main**, folder = **/docs**. Save.
   → you should see "Your site is live at https://hakan-wang.github.io/bongo/".
2. Open that URL.
   → you should see the Assay page render (no "Bongo" text anywhere — if you see "Bongo", ping Håkan).
3. Put the live link in the submission form's "demo" field and at the top of `README.md`.

### Task 3 — Confirm the LOI / traction details (we quote these on stage) [~20 min]
Open `info/design-partners.md`. It has **placeholders** we must NOT quote until confirmed.
1. Confirm the real company name + backing figure for the LOI currently written as "**Skeptiva** (≈$50M-backed) [confirm]".
2. Confirm **Julio Anthony Leonard**'s company + email + that the on-prem→BigQuery use case is accurately described.
3. Replace each `[PLACEHOLDER]` with a real signed/verbal LOI, or delete it. Keep phrasing honest: "signed LOI / verbal commit / pipeline," never "revenue."
4. Update the "~$10K MRR pipeline" line so every number is backed.
   → `info/design-partners.md` has zero `[PLACEHOLDER]` left and every figure is real. Commit + push.

### Task 4 — Name / domain quick check (optional, ~10 min)
We renamed the product to **Assay**.
1. Check if `assay.com`, `assay.dev`, `assay.ai`, or `getassay.com` are available (any domain registrar search).
2. Note which are free in a message to Håkan. Don't buy anything without his OK.
3. (Optional, only if Håkan says yes) rename the GitHub repo from `bongo` to `assay`: repo Settings → rename. *Warning: this changes the URL — do NOT do this within 2 hours of the deadline.*

### Task 5 — Backup: record the deck as video if Michelle needs a hand [only if asked]
`positioning/deck.html` opens in a browser; arrow keys advance the 11 slides. It can be screen-recorded (Cmd+Shift+5) as a backup pitch video.

---

### When done, message Håkan:
> "Clean-clone runs ✓. Pages live at <link>. LOI details confirmed (no placeholders). Domains: <which are free>."

**Do NOT:** rename the repo near the deadline, quote unconfirmed LOI numbers, or edit `demo/` code (that's built + tested). If anything is unclear, ping Håkan.
