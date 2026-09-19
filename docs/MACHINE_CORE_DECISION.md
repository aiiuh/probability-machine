# The Machine: small core, expanding capabilities

Decision draft and tested reference, 19 September 2026. This changes priority, not the entire project: the broad Machine is the product; probability-based judgments, UI design, gameplay and incentive research are optional capabilities or evaluation domains. Historical v0.3 architecture remains available but its UI-first milestone is no longer the immediate build priority.

## Decision

Build a **capability system that turns successful work into verified, reusable procedures**. Its core is an interoperable work contract, typed capability calls, explicit authority, evidence and outcome receipts. Reasoning, probabilistic judgments, ordinary code and tools are interchangeable implementations at appropriate boundaries, not interchangeable guarantees.

Do not first build a new general agent framework, workflow engine, programming language, universal psychology model or large swarm. The current reference adds roughly 300 lines of trusted-host contract logic; it deliberately does not implement scheduling, provider clients, a sandbox, distributed locks, durable recovery or automatic self-modification.

The first practical workflow should be **evidence to reusable capability**: inspect a public repository or an authorized bookmark/export, establish what a proposed component actually does, test a narrowly useful operation, produce a reviewable integration, and retain the verified procedure. This directly serves future research, coding and automation. A second unrelated workflow should reuse the same contracts before expanding the infrastructure.

“Do anything” means an open-ended capability surface with general computation and authorized interfaces to the world. It does not mean every capability is preinstalled, every action is permitted, every problem is soluble within a fixed budget, or every answer is correct. One small interface can support new capabilities indefinitely without claiming universal competence.

## 1. What belongs in the core

| Contract | Contents and purpose | Extensibility rule |
|---|---|---|
| Goal / work order | Objective, acceptance criteria, scope, budget and unresolved material constraints | Different domains provide different acceptance tests; no universal scalar success meter |
| Artifact / evidence | Content reference, origin, source, versions, sensitivity and relevant validity interval | Raw artifacts can live outside context; derived records retain provenance |
| Capability | Versioned input/output contract, callable implementation, declared dependencies/effects, verifier and measured limits | A tool, model judgment, function or procedure can share the invocation interface |
| Invocation / policy | Input references, allowed capabilities, effect grants, reservations, attempt and cancellation state | A child can only narrow authority; the existing runtime owns actual execution lifecycle |
| Judgment / outcome | Proposed decision, evidence/assumptions, abstention when needed; output and verification receipt separately | Probabilities are optional estimates, not permissions or proof |
| Evaluation / promotion | Task-family cases, fixed checker, quality/cost observations, proposed version and rollback | Better code/models/recipes are evaluated without editing their own acceptance requirements |

The original operational language remains useful: Q/question-decompose, R/research, V/verify, A/act, E/error-correct, M/measure, Rf/refine, Ev/evolve. These are composable operations and methods, not eight separate services. A method such as Bayesian inference, causal analysis, backtracking, search or expected utility is a capability implementation, not a competing definition of the whole Machine.

Three distinctions prevent confusion:

1. A **tool** exposes an operation; a **skill** supplies instructions; a **capability** adds a contract, implementation path and evidence of competence.
2. A **judgment** estimates something; a **verifier** checks a defined property; neither silently acquires authority to act.
3. A **procedure** reuses a known way to work; a **planner** invents or adapts one when necessary. Both use the same permission and receipt boundary.

## 2. The practical architecture

```
Chat / voice / authorized event
             |
Goal, scope, acceptance and budget
             |
Progressive context + capability discovery
             |
Simple known recipe OR bounded planner
             |
Versioned capability calls
  | code | semantic judgment | model | tool | child recipe |
             |
Existing single execution authority
             |
Output artifacts + checks + effect receipts
             |
Accepted result, explicit failure, or useful next question
             |
Offline trace review -> candidate recipe -> fixed evaluation -> promotion
```

The graphical interface should display and edit future plan versions and expose evidence; it must not become another source of execution state. Long-term memory retains source records, decisions and useful procedures; retrieval is a projection. Large transcripts and tool results stay outside model context until relevant.

The current Weft route remains the integration target, conditional on inspecting its actual deployed API and guarantees. No Weft adapter or runtime migration was implemented here. Public repositories named `weft` that are literate-programming tools are not evidence about that deployment. A runtime name is insufficient identity: pin its real repository/release and run contract tests.

If durable execution is genuinely missing, compare one narrow DBOS implementation with the existing runtime on a crash/restart/uncertain-effect task. Do not keep both as competing authorities for the same run. Preserve contracts so a later replacement need not rewrite capabilities. DBOS documentation describes step/workflow checkpointing; it does not remove the need to handle non-atomic external effects and downstream idempotency. [S8]

## 3. The most attainable capability increases

### 3.1 Code-mode composition

Instead of letting a model repeatedly copy data between tools, let a bounded program perform deterministic intermediate work and return a compact result. Anthropic's MCP code-execution article describes progressive tool loading and intermediate-data processing outside model context. It also explicitly notes sandbox and operational overhead. Its headline savings are example-specific, not a prediction for this project. [S1]

Use this for parsing, filtering, aggregating, joining and deterministic validation. Leave novel reasoning and semantic judgments in explicit calls. The host must validate every permitted callback and impose whole-run budgets; making a function callable from a sandbox does not make its effects safe.

Monty is a relevant candidate for restricted generated Python. Its documented security model exposes only granted host access, but callbacks run with host authority. Its VM limits do not automatically bound every host operation or an indefinitely renewed session. It therefore needs a host policy/budget broker. It is a candidate to canary-test, not an installed or verified security boundary here. [S2]

### 3.2 Progressive capability and context discovery

Discover a few relevant capability names/descriptions, then fetch their exact schemas and supporting material. Do not send every installed tool, skill or archived discussion to every model. The Agent Skills specification standardizes metadata/instructions/resources and progressive disclosure, but a valid skill package is not proof of task competence. [S3]

The supplied reference has a bounded lexical discovery baseline and separate full manifests. It is intentionally not a claim that lexical discovery always finds the right tool. A semantic reranker can compete later against this baseline on task completion and missed-capability rates.

For exceptionally large archives, Recursive Language Models offer a useful research direction: treat long context as an external environment that can be programmatically inspected, with focused subcalls. The authors' results are benchmark-specific; do not translate them into a guarantee of complete corpus understanding. [S4]

### 3.3 Trace to tested procedure, then selective simplification

When a difficult task succeeds, retain the inputs, meaningful steps, assumptions, outputs, checks and failure conditions. Propose a parameterized recipe. Test new instances. Where a simpler implementation preserves the acceptance contract, replace unnecessary model steps or computations. Retain uncertain semantic steps where they earn their cost.

This is more useful than copying the entire successful chat into a permanent prompt. A recipe needs an applicability range and invalidation conditions, not just an inspiring example.

GEPA is an appropriate offline challenger: it optimizes textual components using evaluator feedback and execution traces. Its gains are not universal and its search consumes evaluation/model budget. First establish task-family checkers and clean evaluation splits; then test whether it beats hand-written recipes or simpler prompt changes. It must not modify production permissions, secrets or its acceptance tests. [S5]

### 3.4 Selective semantic judgments

Jev can be tested for relevance, category selection, candidate ranking or escalation signals. Probably makes the distinction between semantic judgment and generation visible in syntax. Neither substitutes for a causal model, permissions or an executable checker. The current hosted Probably version is a tiny experimental language with specific limits, not a full Machine runtime. [S6,S7]

Batch questions only if each can be expressed from the available state. API batching does not make model errors statistically independent, and dependent questions still need staged information. Keep raw option probabilities, provider confidence statistics and empirical correctness calibration separate. [S7]

### 3.5 Bounded parallel work, not permanent swarms

Run independent research branches, isolated implementation candidates or reversible checks concurrently when their value justifies the cost. Give each a bounded packet and return artifacts/receipts, not every intermediate transcript. One component resolves the result and one authorized runtime commits effects. A vote among related models is not independent corroboration.

Parallelism is an optimization, not a prerequisite for this release. The reference runner is synchronous and does not expose independent subagents.

## 4. Shortlist and choices

| Option | Useful contribution | Current decision | Evidence required before expansion |
|---|---|---|---|
| Small capability contracts + existing execution route | Preserves current work; fits code, models and tools without new runtime | Build this boundary now | Two unrelated end-to-end workflows, failure receipts, integration canary |
| Monty / code mode | Potentially efficient generated-program composition | Canary candidate behind bounded host calls | Escape/permission/resource tests and end-to-end comparison with direct calls |
| Pi and Herdr | Worker toolkit and persistent terminal operations | Optional worker/supervisor, not a second brain | A concrete worker task with verified result and recovery behavior |
| GEPA | Trace-informed offline optimization | Add only after useful fixed evaluations exist | Measured improvement including optimization spend and failure rates |
| Probably or a new DSL | Readable authoring of semantic decisions | Preserve as optional front end; do not create another interpreter now | Real editing/debugging wins over ordinary code using the same contracts |
| Full replacement agent OS / framework stack | Broad packaged features | Do not adopt wholesale from a demo or social claim | Clearly better accepted outcomes with lower total setup/maintenance burden |

Pi's current official repository describes a modular agent toolkit. Herdr describes persistent terminal sessions across local/remote environments. A persistent terminal is not the same as durable, reconciled business effects. [S9,S10]

One candidate repository named Collie describes fail-before/pass-after reproduction and permission boundaries. Those are useful patterns to evaluate. The identity of the Collie in a saved social post was not conclusively established, and its README is not an independent benchmark. The associated “Executor” project was not uniquely resolved. Do not install a whole stack based on ambiguous names. [S11]

## 5. What was built and tested

New files:

- `capability_core.py`: versioned registry, finite JSON artifacts, bounded discovery, declaration/linking checks, narrowed policies, pre-call work reservations, receipts, exact pure-result reuse, and per-run effect-key handling.
- `capability_demo.py`: composition of a synthetic catalogue report, the existing v0.3 decision function, and a real host-bound temporary file write with read-back checking.
- `capability_eval.py`: bounded comparison of three hand-written procedure candidates against unchanged checkers.
- Two new test modules; existing code and tests remain.

The complete suite passed **128 tests**, including the original 64. One generated-input test additionally evaluates 50 deterministic cases. This is contract/regression evidence, not a security audit or empirical proof of autonomous intelligence.

### Composition result

For 5,000 synthetic records, direct intermediate output bodies totaled **177,396 JSON bytes**. Returning only the composed final report exposed **104 bytes**, with identical final output. The initial input is common to both and excluded; receipts/metadata are also outside this body-only comparison. The same three leaf operations still ran. No live LLM tokens, money, latency or user outcomes were measured.

This is a concrete demonstration of where code mode can avoid unnecessary context transfer, not a general 99.94% system-efficiency claim.

### Recipe comparison

Fifty fixed generated cases were used for each candidate:

| Candidate | Accepted cases | Mean adapter invocations | Production promoted |
|---|---:|---:|---|
| Composed recipe | 50/50 | 4, including wrapper | No |
| Hand-written fused candidate | 50/50 | 1 | No |
| Cheapest but wrong candidate | 0/50 | 1 | No |

The fused candidate wins the fixture's invocation-count criterion. Its checker still does work; invocation reduction is not proof of net speed or dollar savings. This is not automated synthesis, machine learning or a calibrated deployment gate.

### Failure tests and deliberate counterexample

The suite rejects unauthorized/undeclared calls, hidden read/effect dependencies in pure recipes, invalid inputs/outputs, missing verification, truthy non-boolean checker results, exhausted work budgets, changed operation-key payloads, artifact corruption and attempts to reuse without permission. It checks child-version invalidation, cancellation, depth/call bounds and failures after an effect may already have happened.

A duplicate effect is suppressed inside one live Run. **A new Run can repeat the same effect**, and a test explicitly demonstrates that limit. In-memory deduplication is not durable exactly-once execution. Production needs the actual runtime's persistent intent identity and reconciliation/idempotency contract; do not deploy this reference as a payment/publication engine.

### Limits that remain important

- Trusted callbacks only. They can access the host; this module is not a sandbox or complete security boundary.
- Synchronous single-threaded reference; no distributed recovery, scheduler, automatic retries or concurrent mutation safety.
- Budgets count declared work units, not measured billing or a hard memory/time limit.
- Release fingerprints cover declared metadata and dependency versions; reviewed adapter authors must change their release identity when code, closures, prompts or validators change.
- Verifier scope matters. The decision adapter checks a no-effect structural property, not the truth of its supplied outcome probabilities.
- Raw artifacts, caching and discovery are in-memory per kernel instance, not a persistent global memory service.
- No live Jev, Monty, DBOS, Weft, agent-model or X-bookmark integration was tested.

## 6. How to stay clever without becoming fragile

**Be clever inside replaceable implementations; be conservative at boundaries.** A new planner, optimizer, model or language may propose better work, but it should not redefine permissions, historical evidence or success.

Use the simplest adequate path first. A one-step operation gets one call and an appropriate checker. A repeated task gets a recipe. A genuinely novel task gets a bounded plan. A hard separable task may earn a small team. Do not make all tasks pay for the most sophisticated architecture.

Require an observable reason for complexity. Adding a database, agent, model, framework or intermediate representation should remove a measured bottleneck or enable a concrete task. Do not keep multiple complete implementations merely to preserve theoretical optionality. Keep portable contracts instead.

Cache only pure, versioned transformations of explicit inputs. External information needs a snapshot/time identity or a fresh read. Replaying a recording is not re-observing the world. Never replay a write because the previous assistant response sounded incomplete.

Keep proposals separate from promotions. Generated skills enter a candidate registry with scoped permissions and fixed evaluations. Their proof is task-specific; they must not generalize an easy arithmetic pass into authority over publication or financial actions.

Stop upgrading a path when additional complexity does not improve accepted result quality, operator burden, failure rate or measured total cost. The Machine should get more capable by accumulating dependable building blocks, not by growing a more elaborate permanent prompt.

## 7. Next bounded build

1. Inspect the actual existing runtime/bridge and implement this contract over one verified route. Reuse its execution state; do not bolt on another durable controller.
2. Complete a repository-evidence-to-reviewable-patch workflow. Read exact versions, record source coverage, run an isolated test, return a patch and executable acceptance evidence. Keep bookmarks as an optional input connector, not a blocker for all progress.
3. Reuse the same contracts on an unrelated artifact/data task. Compare direct calls, a saved procedure and a selective-judgment version. Include all verifier and repair costs.
4. Test a sandboxed code-mode worker or one offline recipe optimizer, whichever removes the larger observed bottleneck. Do not simultaneously adopt a new language, agent OS and workflow engine.
5. Only after a real workflow benefits, expand the cockpit, autonomy and standing scouts. They invoke the same work orders and controls.

Open research: guard applicability when reusing recipes; quantify when another reasoning call changes a decision; discover new capabilities without bloating context; learn failure-specific repairs; select complementary rather than merely numerous reviewers; map model competence to task families; improve plans without allowing them to edit their own acceptance criteria. These are direct extensions of the Machine, not a detour into modeling all human behavior.

## Sources and coverage

See `research/CORE_SOURCES.md` for exact public primary sources. Private historical requirements were consulted to preserve scope but are not copied into this public repository.

The live GitHub project and public repositories/docs were inspected. No live X bookmark connector, Mac bridge or independent-subagent launcher was available in this conversation; only a saved X-related screenshot and historical references were located. External dependency installation was attempted but failed on network/DNS, so no Monty/DBOS execution benchmark is claimed. The new core and evaluations run without those packages.
