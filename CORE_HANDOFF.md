# Current priority: extensible Machine capabilities

Read `docs/MACHINE_CORE_DECISION.md`, `research/CORE_SOURCES.md`, and the new code/tests. This supersedes the UI-first next milestone in historical `ASTRA_PRO_HANDOFF.md`. Preserve UI/gameplay/incentive research as optional domains, not the core architecture.

## Reproduce

```bash
python3 -m unittest discover -s tests -v
python3 capability_demo.py
python3 capability_eval.py
python3 experiments.py
```

Expected current suite: 128 passing tests. The demonstration uses synthetic catalogue records, the existing decision function and a real verified temporary-file write. The bake-off evaluates hand-written candidates against fixed checkers; no model-based optimizer is invoked.

## Next useful implementation

Connect one existing authorized execution route to the capability contract, then complete a repository-evidence-to-reviewable-patch workflow. Reuse the same interface on an unrelated artifact/data task before expanding architecture. Keep a single owner for durable state and external effects.

Do not assume the Mac bridge, Weft source/API, bookmarks or subagents are available: inspect actual capabilities and record tested identity. Do not substitute an unrelated public repository named Weft. Do not make missing bookmarks block public-source work. Never copy private source contents, credentials or participant records into this public project.

The Python core is a trusted synchronous conformance reference, not a new production workflow engine, sandbox or security boundary. Its effect deduplication is only in the same Run; a test demonstrates a new Run can duplicate an effect. Production requires persistent operation identity and downstream reconciliation/idempotency. Work-unit reservations are not billing/time/memory enforcement.

Evaluate code-mode/Monty, Jev, a worker toolkit or GEPA only where a measured bottleneck warrants it. Include checker, retry, operator and optimization costs. Do not build a new DSL, add a permanent swarm or change durable runtimes merely to match a stack diagram. Trace-derived candidates may not rewrite their own acceptance tests or permissions.

Deliver real receipts, data/model/version provenance, bounded comparisons and a clean implementation/tested/proposed status. Challenge this design where a simpler alternative wins; preserve the broadly extensible Machine objective.
