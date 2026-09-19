# Probability Machine — extensible Machine core

**v0.4 research branch.** Build a broadly capable assistant by composing verified capabilities, not by turning every task into a probability model. UI/gameplay and incentive research remain optional v0.3 workloads.

Start with [the core architecture decision](docs/MACHINE_CORE_DECISION.md), [current handoff](CORE_HANDOFF.md), and [research ledger](research/CORE_SOURCES.md). The historical `ASTRA_PRO_HANDOFF.md` UI-first assignment is superseded by `CORE_HANDOFF.md`.

## Run

Python 3.10+. Core, examples and unit/HTTP tests use only the standard library. No model key or paid service is needed.

```bash
python3 -m unittest discover -s tests -v
python3 capability_demo.py
python3 capability_eval.py
python3 experiments.py
```

The complete development suite passed **128 tests**, including the original 64. The new examples execute synthetic data transformations, a wrapper around the existing decision engine, and a verified temporary-file write. The procedure comparison evaluates three hand-written candidates on 50 generated cases; no automatic synthesis or production promotion occurs.

## New modules

`capability_core.py` supplies versioned contracts, bounded discovery, scoped calls, dependency checks, pre-call work reservations, artifact hashes, explicit verification receipts and pure-result reuse. `capability_demo.py` composes these across different workload types. `capability_eval.py` rejects an incorrect cheap candidate instead of selecting it solely on cost.

**This is a trusted synchronous contract reference, not a sandbox, scheduler or durable execution service.** Callbacks must be reviewed. Effect deduplication is only within one Run; a test demonstrates that a new Run can repeat an effect. Production must reuse the existing runtime's persistent effect identity and reconciliation. Declared work units are not dollars, tokens or memory/time limits.

## Evidence

The composed catalogue example retains identical output while reducing the selected intermediate/final JSON bodies from 177,396 bytes to 104 bytes for 5,000 synthetic records. The initial input is common to both and excluded. The same three leaf operations still execute. This is not a measured token, latency or billing improvement.

The new source and tests are in this branch. Full logs, manifests and generated reports are included in the accompanying project ZIP; regenerate them with the commands above. Live model, Monty, DBOS, Weft/Mac and X-bookmark integrations were not executed or verified here.

## Retained v0.3 experiments

The original `probability_machine.py`, synthetic challenges, test suite, [architecture](docs/ARCHITECTURE.md), and [sources](research/SOURCES.md) remain unchanged. They include finite Bayesian/decision calculations, value of information, MDP planning and off-policy/A-B helpers. Example probabilities are invented, not measurements of real people.

The optional local layout workbench remains available:

```bash
python3 server.py
```

Open `http://127.0.0.1:8765`. Browser smoke verification was previously blocked; HTTP tests are not a substitute for browser or human validation.

This is a public repository. Do not commit credentials, participant exports, private bookmark contents, personal profiles or local-machine details.
