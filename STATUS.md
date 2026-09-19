# Current status — v0.4 research branch

## Implemented and executed

- Versioned capability contracts, bounded lexical discovery, dependency/effect checks and narrowed call policies.
- Pre-call work reservations, content-addressed JSON artifacts and explicit verification receipts.
- Verified pure-result reuse and per-run duplicate effect-key handling.
- Catalogue composition, existing decision-function adapter, verified local temporary-file write.
- Three hand-written procedure candidates compared on 50 generated cases.
- Combined suite: **128 passing tests**, including all 64 original tests.

## Boundaries

The new runner is a trusted synchronous contract/conformance reference, not a sandbox, scheduler, full permission broker or durable runtime. A new Run can repeat an effect; a test explicitly demonstrates that limit. Work reservations are declared units, not real billing or hard resource limits. The decision adapter verifies a structural no-effect condition, not empirical correctness.

No actual model/provider, automatic skill synthesis, optimizer, production promotion, independent subagent, live X bookmark, Mac MCP, or Weft integration was executed. Monty/DBOS installation failed on network/DNS, before any library evaluation. No external runtime benchmarks are claimed.

## Retained work

The v0.3 decision/conclusion core, examples, 64 tests and optional layout collector remain unchanged. No real human data/model fitting or gameplay validation is established. The existing browser implementation still lacks a completed browser smoke run because navigation was blocked in the earlier environment.

## Next milestone

Follow `CORE_HANDOFF.md`, not the historical UI-first handoff. Attach the contracts to the existing authorized runtime and complete a repository-evidence-to-reviewable-patch workflow. Reuse the same boundary on an unrelated data/artifact task before adding infrastructure.
