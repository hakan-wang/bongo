# Assay

Assay is a hackathon MVP for AI workflow reliability and cost control.

It shows a simple idea: let a cheap model handle a multi-step workflow by default, verify each step deterministically where possible, and escalate only the failed step to a stronger model. In the current demo, that produces the same final correctness as the strong model path while staying 74% cheaper than running the strong model on every step.

Live demo: [assay-demo.vercel.app](https://assay-demo.vercel.app)

## What the product does

Assay sits inside a multi-step AI workflow and answers one question at every step:

`Did the model produce the correct output according to reality, not according to another model?`

If the answer is yes, the workflow continues on the cheap path.

If the answer is no, Assay:

1. catches the exact failed step
2. retries or escalates only that step
3. leaves the rest of the workflow on the cheap model
4. reports the reliability and cost impact

This is intentionally not a generic observability tool and not a model router. The core wedge is step-level verification plus selective escalation.

## Demo summary

The demo is a support-workflow-style interface backed by a deterministic Python engine.

Under the hood, the engine simulates three paths:

- cheap model only
- cheap model plus Assay verification
- strong model on every step

The current benchmark output is:

| Path | Reliability | Cost per 1,000 runs | Broken results shipped |
|---|---:|---:|---:|
| Cheap model only | 60% | $4.00 | 2 |
| Cheap + Assay | 100% | $20.40 | 0 |
| Strong model only | 100% | $80.00 | 0 |

That is where the `74% cheaper than always using Opus 4.8` style story comes from: the verified cheap path reaches the same final reliability as the strong path without paying strong-model cost on every step.

## What is real vs mocked

This repo is honest about what is deterministic and what is staged for the demo.

- Real: the verification logic in [`demo/scenarios.py`](demo/scenarios.py) actually recomputes arithmetic, executes tests, checks schemas, detects loops, and flags unverifiable steps.
- Real: the scoreboard numbers are computed from the workflow runs.
- Mocked or pinned: the specific model outputs are fixed so the demo behaves deterministically on stage.
- Optional real-provider proof: [`demo/real_proof.py`](demo/real_proof.py) is the path for a genuine cross-provider escalation run when API keys are available.

## Repo structure

- [`demo/`](demo) contains the main hackathon demo
- [`demo/index.html`](demo/index.html) is the UI shown in the browser
- [`demo/server.py`](demo/server.py) serves the UI and `/api/run`
- [`demo/scenarios.py`](demo/scenarios.py) contains the workflow engine, verifiers, and scoreboard
- [`demo/gateway.py`](demo/gateway.py) is the mocked product-style gateway integration path
- [`QUICKSTART.md`](QUICKSTART.md) contains fast local run instructions

The rest of the root-level markdown files are planning, positioning, and hackathon support material.

## How to run locally

### 1. Run the demo UI

```bash
py -3 demo/server.py
```

Then open `http://127.0.0.1:8200/`.

### 2. Print the benchmark numbers directly

```bash
py -3 demo/scenarios.py
```

### 3. Try the gateway path

```bash
py -3 demo/gateway.py
```

## Tech stack

- Python 3
- Standard library HTTP server for the local demo
- Vanilla HTML, CSS, and JavaScript for the UI
- Optional provider integrations for future real-model execution

The main demo does not require external dependencies or API keys.

## Why this matters

Most teams either:

- run a strong model everywhere and overpay, or
- run a cheap model everywhere and silently accept wrong intermediate steps

Assay demonstrates a third path:

- keep most of the workflow cheap
- verify each step against reality when possible
- escalate only the broken step
- measure the savings clearly

That gives a sharper product wedge than generic token tracking or generic AI observability.

## Submission notes

This repository is public and contains the full codebase for the current hackathon MVP, including:

- the working demo UI
- the deterministic verification engine
- the mock gateway path
- the supporting positioning and build documents used during the project

## License

MIT. See [`LICENSE`](LICENSE).
