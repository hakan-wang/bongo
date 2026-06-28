# Assay Demo

This folder contains the main hackathon demo.

## Files

- [`index.html`](index.html): frontend UI shown during the demo
- [`server.py`](server.py): local HTTP server for the UI and `/api/run`
- [`scenarios.py`](scenarios.py): deterministic workflow engine, verifiers, and scoreboard logic
- [`gateway.py`](gateway.py): product-style integration path
- [`real_proof.py`](real_proof.py): optional real-provider escalation proof

## Run

```bash
py -3 server.py
```

Then open `http://127.0.0.1:8200/`.

## Demo behavior

The UI is presentation-first, but the underlying workflow engine is not fake.

- Step verification is deterministic.
- Cost and reliability numbers are computed.
- Outputs are pinned where needed to keep the live demo stable.

## Current story

The current demo is framed as a support workflow comparison:

- cheap path alone can fail
- Assay catches and escalates only the failed work
- the final verified path is cheaper than always using the strongest model
