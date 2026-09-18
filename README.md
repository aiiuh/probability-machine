# Probability Machine

**v0.3 — an executable research foundation for choosing actions and reaching evidence-based conclusions.** Product design, interface layout, and gameplay are the first application domains, not the limits of the architecture.

The central hypothesis is that incentives and disincentives can provide a useful model of action. We test its predictive and causal usefulness rather than assume that a probability score reveals utility or that knowing reward weights alone guarantees prediction.

## Run locally

Python 3.10+; the core, server, and unit tests use only the standard library. No API key, paid model, or external service is required.

```bash
python3 -m unittest discover -s tests -v
python3 experiments.py
python3 probability_machine.py plan examples/layout.json
python3 probability_machine.py mdp examples/gameplay.json
python3 server.py
```

Open `http://127.0.0.1:8765`. On macOS, `bash scripts/Start-Lab.command` starts the same loopback-only workbench. This is not a production server.

To create local result files:

```bash
mkdir -p results
python3 -m unittest discover -s tests -v > results/unit-tests.txt 2>&1
python3 experiments.py > results/synthetic-challenges.json
python3 probability_machine.py plan examples/layout.json > results/layout-certificate.json
```

## What exists

- A conclusion function with explicit Bayesian assumptions, source references, and duplicate/dependent-evidence rejection.
- Expected-utility action selection, scenario constraints, a budget, minimax-regret comparison, and one-step value-of-information selection.
- Exact finite-horizon planning for supplied, fully observed finite MDPs.
- IPS, self-normalized IPS, and doubly robust contextual-bandit evaluation with support checks.
- Beta/Bernoulli A/B posterior calculation and an illustrative motor-time model.
- A browser workbench: edit a decision specification and collect an opt-in, local-only, randomized four-variant layout session.
- Reproducible synthetic challenges, 64 passing unit/HTTP tests, and a research/build handoff.

The browser layout collector does not automatically fit a human model. Repeated trials are clustered within a session; exports are not independent A/B observations. The included example probabilities and outcome models are synthetic, not measurements of users.

## Evidence status

The development run executed 20 seeded simulations of 20,000 events each. In this deliberately confounded fixture, naive averages chose the wrong layout in 20/20 runs; the three propensity-based estimators chose correctly in 20/20. SNIPS, not DR, had the smallest mean absolute value error in this fixture. This is a regression experiment with known assumptions, not a real-user benchmark.

All 64 unit/HTTP tests passed in the development environment. JavaScript syntax validation passed. Raw result-log upload was blocked by the connector safety check; the logs are included in the accompanying downloadable project package, not committed here. The commands above regenerate them locally.

Full browser smoke verification was attempted but blocked by the build environment's browser navigation policy. The optional `scripts/browser_smoke.py` requires Playwright and its browser installation, or an explicit `CHROMIUM_PATH`; create the `results` directory before running it. Browser interaction quality, accessibility, live Jev performance, and real-user prediction accuracy are **not validated**.

## Read next

- [Architecture and hypotheses](docs/ARCHITECTURE.md)
- [Research ledger](research/SOURCES.md)
- [Next build and evaluation assignment](ASTRA_PRO_HANDOFF.md)
- [Implementation status](STATUS.md)

## Boundaries

The current engine produces recommendations; it does not execute product changes, spend money, or grant permissions. A mathematical optimum is conditional on the candidate set, model, objective, constraints, and horizon. Keep these visible. Do not call model confidence a calibrated probability without testing it. Do not publish participant exports, credentials, private notes, or local-machine details to this public repository.
