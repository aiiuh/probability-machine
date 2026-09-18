# Status — v0.3

## Implemented and executed

- Stdlib decision/conclusion core, finite-MDP solver, propensity-based evaluation, Bayesian A/B helper.
- JSON command-line interface and a loopback HTTP plan endpoint.
- 64 passing unit and HTTP tests; JavaScript syntax check passed.
- Twenty synthetic seeds, 20,000 simulated events per seed, plus mathematical counterexamples and illustrative fixtures.
- Public-source research ledger, architecture, and next-build assignment.

## Implemented but not fully verified

- Browser decision workbench and session-randomized layout collector (four variants, opt-in local memory/export).
- Optional Playwright script. The actual attempt was blocked at loopback navigation with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. No browser smoke pass, visual verification, accessibility audit, or real-user measurement is claimed.

## Not implemented or not established

- Real-data model fitting/import/clustered analysis, learned incentive weights, calibrated human predictions, identified real-world interventions.
- Jev or generative-model adapters, actual model-cost/latency comparisons, Weft/MCP execution, independent subagents, durable autonomous execution.
- Automatic candidate generation, general POMDP planning, open-world hypothesis discovery, universal optimality.
- Real gameplay experience tests. Current gameplay rewards are invented.

## Research limitations

The linked GUI-search dataset could not be retrieved in the build environment. The supplemental research connector was rate-limited; public web research was used. Source claims and synthetic tests are not empirical human validation. The next milestone is a measured, held-out, intervention-aware design evaluation, not additional orchestration layers.
