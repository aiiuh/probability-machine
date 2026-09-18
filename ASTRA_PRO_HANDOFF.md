# Research, challenge, and build the next Probability Machine

Read README.md, docs/ARCHITECTURE.md, research/SOURCES.md, STATUS.md, and the tests before changing the architecture. The intended system is an action and conclusion engine; product layouts and gameplay are initial testbeds. Do not reinterpret the task as profiling a conversational user's personal preferences.

## Mandate

Challenge the incentive hypothesis and the proposed architecture. Preserve stronger alternatives, negative results, and evidence that contradicts the desired outcome. Implement useful tested capabilities rather than merely expanding documentation. A fixed incentive model, contextual model, perceptual bottleneck model, and dynamic model are competitors, not mandatory layers.

## First bounded build

1. Run the 64 tests, reproduce experiments.py, inspect browser/server source, and run scripts/browser_smoke.py where loopback browsing is permitted. Fix failures and record actual evidence. Do not claim a browser test passed from HTTP tests alone.
2. Finish one real-data ingestion and evaluation path. Prefer a small authorized layout experiment or the authors' VSGUI10K data after reviewing license/schema. Include origin tags, participant/session grouping, assignment probabilities, repeated-export detection, missingness, outcome horizons, and declared exclusions. Do not commit real participant exports.
3. Compare a cheap task-frequency/layout baseline with fixed incentive, context-aware, and perceptual models. Hold out whole people/layouts and later time periods; never allow random-row leakage. Report log loss, Brier score/calibration, task outcome, uncertainty, and decision quality. Do not automatically feed repeated trials into independent Bernoulli A/B analysis.
4. Complete an intervention-aware recommendation loop with a report and a bounded next experiment. Observational fit alone does not identify the effect of changing a button or gameplay rule.
5. Test provider additions only after the baseline exists. Compare Jev with simple statistics and a structured-output generative model on the same held-out cases. Verify API schemas and confidence semantics. No real provider calls without an explicit bounded budget and available credentials; never print or commit credentials.

## Architecture decisions to earn

Keep one side-effect authority. Do not assume any MCP server, subagent launcher, Weft runtime, local path, or model is present without inspecting it. If unavailable, continue offline testing and preserve an exact blocker. Optional SDK/JSON and optional Probably-like syntax should use one decision representation; compare authoring/debugging effort before creating another language runtime.

The current engine ranks a supplied finite set and never executes an action. Candidate generation, hypothesis generation, calibration, real-data learning, causal identification, durable execution, and deployed human feedback are incomplete. Treat current example weights and probabilities as synthetic. Model sources are declared provenance, not automatically verified evidence.

## Next research questions

- Under which interventions can competing incentive models be distinguished? When do unidentifiable models still agree on the useful action?
- Does modeling attention and understanding outperform simply adding reward features?
- What transfers between tasks, devices, people, and future sessions? Which uncertainty is consequential for the decision?
- How should immediate enjoyment, learning, completion, voluntary return, and unwanted friction be measured separately?
- Which candidate experiment, extra model call, or source inspection has positive decision value after its costs?
- Can a Probably-like front end improve real editing/debugging tasks without duplicating runtime state?

## Completion evidence

Provide runnable code, reproducible commands, versioned sources/data manifests, honest benchmark results including losses, an inspectable decision certificate, and a clear status separating implemented, tested, blocked, and proposed. Use commit/PR references. Do not call a supplied-model optimum a universally optimal real-world recommendation.
