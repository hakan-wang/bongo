# Assay Quickstart

This quickstart is for the current hackathon MVP.

## Run the main demo

```bash
py -3 demo/server.py
```

Open `http://127.0.0.1:8200/` in the browser and click the run button.

## What you will see

The demo compares three paths across the same workflow:

- cheap model only
- cheap model plus Assay verification
- strong model only

Assay verifies each step, catches failures, escalates only the broken step, and shows the final reliability and cost difference.

## Print the numbers in the terminal

```bash
py -3 demo/scenarios.py
```

This prints the computed scoreboard that powers the demo:

- cheap only: 60% reliability
- cheap plus Assay: 100% reliability
- strong only: 100% reliability
- Assay path: 74% cheaper than always using the strong model

## Optional: run the gateway path

```bash
py -3 demo/gateway.py
```

This is the product-shaped integration path where an OpenAI-compatible client points to Assay as its base URL.

## Optional: real-provider proof

```bash
py -3 demo/real_proof.py --mock
```

Use this first if you want to preview the flow without keys. The full real-provider version requires model credentials.

## Honest status

- The main demo uses pinned outputs so the flow is deterministic on stage.
- The verifiers and scoreboard calculations are real.
- The gateway path exists, but the default demo is optimized for a stable live presentation.
