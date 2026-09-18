# Probability Machine: incentive models, causal design, and bounded optimal action

Version 0.3. Research and implementation draft, 19 September 2026. References [R1]–[R12] are in `research/SOURCES.md`. Implemented components are distinguished from proposed components throughout.

## 1. The corrected thesis

The project is not primarily about guessing a conversational user's personality. It is about constructing good explanations and predictions of action, then using them to improve products, layouts, gameplay, and other decisions. Incentives include perceived benefit, effort, uncertainty, anticipated enjoyment, delay, and other explicitly modeled consequences. Whether this is a useful primitive depends on predictive tests, not how elegantly it can redescribe an action afterward.

Three claims must remain separate:

1. **Representation:** behavior or goals can sometimes be represented using rewards and costs.
2. **Identification and prediction:** a model fitted from accessible observations can predict new behavior.
3. **Intervention and optimization:** the model can identify a change that improves an outcome when deployed.

Success at the first does not establish the second or third. A reward function constructed after observing each action is not a useful predictive explanation. Silver et al. advance a reward-based hypothesis for intelligent abilities [R1]; this is not a theorem that a fixed list of incentive weights identifies every human action. Work on scalar versus multiobjective reward [R2] is a reason to keep outcome vectors and constraints available rather than prematurely force every concern into one opaque number.

Perfect prediction is logically compatible with a specified deterministic system if its full relevant state, update rule, available actions, and computation are known. This conditional statement does not establish that incentive weights alone are a sufficient state description or that those quantities are identifiable from finite observations. Conversely, incomplete observation is not evidence against an underlying deterministic mechanism.

For a bounded task, test a family such as:

`P(action | perceived options, beliefs, context, history, incentive parameters, decision process)`.

The primitive we should expose to software is not a universal confidence scalar. It is an explicit decision model with identifiable inputs, assumptions, outcomes, and an evaluation contract.

## 2. Competing, falsifiable models

The research program should compare the following rather than simply keep adding features to the preferred story.

**H0: baseline.** Predict population action frequencies or use a simple task/layout rule. It is cheap, interpretable, and must not be omitted.

**H1: fixed incentives.** A linear utility over preregistered features followed by a choice rule. Hold features and preprocessing fixed before examining test outcomes. This is the simplest serious version of the incentive thesis.

**H2: contextual incentives and beliefs.** Add task, prior exposure, perceived outcome probability, skill, and limited interactions. Penalize complexity and evaluate on unseen layouts, people, and later time periods. More in-sample fit is not success.

**H3: perceptual/computational bottleneck.** Model what is noticed and understood before choice, and what can be executed afterward. A person cannot intentionally choose an option absent from their perceived action set. This hypothesis predicts that salience, layout familiarity, and input constraints can matter without a change in the underlying goal.

**H4: dynamic learned policy.** Add habit, changing skill, fatigue proxies when legitimately measured, delayed consequences, and state transitions. This must outperform simpler models on sequential tasks, not merely contain more parameters.

Score choice predictions by held-out log loss and Brier score; report calibration, uncertainty, subgroup performance, and shift performance. Score proposed designs by actual target outcomes and decision regret where ground truth is available. A better action predictor is not necessarily a better intervention selector.

IRL research formalizes reward ambiguity and behavior-model misspecification [R3]. Other work shows that additional environments or conditions can improve identification under explicit mathematical assumptions [R4]. The constructive response is to design distinguishing interventions, not declare inference impossible or pretend one observed policy uniquely reveals motives.

## 3. A causal model of interacting with a design

Use the following as a hypothesis-generating decomposition, not an assumption that the stages are independent:

`rendered design → noticed possibilities → understood consequences → subjective valuation → choice → motor execution → experienced outcome → learning → future action`.

Track the task and environment across the entire sequence. Correlated latent factors and feedback mean that multiplying isolated model scores is generally not a valid joint probability calculation. The implementation should introduce a joint or conditional model only where its assumptions are specified and tested.

For a button, the design representation should eventually include semantic role, geometry, label, competing elements, visual hierarchy, task importance, interaction sequence, prior exposure, and input method. A nearer, larger control can reduce modeled motor cost but also create clutter or require additional visual search. Current research on GUI search provides a suitable separate empirical target [R5]. Motor-time formulas do not measure beauty, trust, comprehension, or enjoyment.

For gameplay, distinguish the reward signal selected by a designer from the player's experience. Challenge, competence, autonomy, feedback clarity, discovery, and social interaction are candidate explanatory variables. Existing self-determination research associates several of these with reported enjoyment [R6]; it does not supply a universal equation for pleasure or addiction. Treat voluntary return, reported satisfaction, skill development, completion, and time spent as different outcomes. A design that increases time spent by increasing confusion is not necessarily better.

Avoid continuously moving controls in response to every click. The intervention changes familiarity and subsequent observations. Use stable assignment windows and explicitly model learning or carryover when appropriate.

## 4. The architecture

### 4.1 Evidence and observation layer — proposed schema, partial implementation

An observation needs source, time, task, displayed alternatives, chosen action, context, assignment probability, outcome horizon, missingness, and origin: real participant, simulation, model-generated estimate, or automated test. Derived summaries retain links to their parents so they cannot become independent corroboration.

The conclusion function already rejects duplicate IDs and declared dependence groups. This prevents a simple double-counting failure; it cannot verify real independence. A source string is provenance metadata, not proof of source accuracy.

Keep private participant records outside Git. The current browser collector stores records only in memory until an explicit local export. It does not silently send records to a provider or this repository.

### 4.2 Conclusion engine — implemented finite core, broader inference proposed

Its question is: **What does the evidence support?** Inputs are hypotheses, priors, likelihood assumptions, and observations. Product utility is intentionally not an input to the finite `conclude` function. The business outcome someone wants must not alter the posterior merely because it is desirable.

The current function performs exact finite Bayesian updating and returns provenance plus a qualification. It does not discover hypotheses, fit likelihoods, verify papers, or establish truth automatically. Broader versions need model checks, evidence dependence, contradiction handling, alternatives outside the current hypothesis set, and calibrated abstention.

### 4.3 Behavioral/world-model registry — proposed

Maintain a small competing set of baseline, incentive, perceptual, and dynamic models. Each model has training data, domain of validity, held-out scores, calibration status, causal assumptions, and revision history. Treat a provider's semantic output as a feature or proposal until measured against a relevant target.

Start with fixed task representations and interpretable statistical baselines. Add Jev, generative models, or learned visual representations only when they improve the required metric enough to justify cost, latency, complexity, and failure modes. Do not train and evaluate on synthetic personas generated by the same model and call that human validation.

### 4.4 Action engine — implemented bounded core

Its question is: **Given current beliefs, which feasible candidate best serves the declared objective?** The JSON specification includes scenario probabilities, an outcome vector per action and scenario, objective weights, hard limits, and an action budget. The implementation computes expected utility, lists alternatives, rejects violating actions, and separately identifies a minimax-regret action.

Hard limits currently apply to every supplied scenario, including zero-prior scenarios. This is deliberately conservative and is only a specification check. It does not prove that unmodeled real-world hazards are absent. Cost is a feasibility budget unless also explicitly represented in the objective; avoid silently counting it twice.

The engine does not claim to have generated every possible design. Its output certificate identifies the input hash, model origin, alternatives, rejected actions, assumptions, and whether action or further evidence is recommended. The current `executed` field is always false. Real deployment requires a separate authorized executor and effect receipt.

### 4.5 Experiment selector — implemented one-step finite core

Its question is: **Which measurement is worth obtaining before choosing?** Compute the expected increase in best feasible utility after an observation and subtract the experiment's cost in the same objective units. An informative but decision-irrelevant question has no positive value merely because it reduces uncertainty.

The supplied layout example recommends an informative layout comparison but rejects an unrelated color question. Its likelihoods are invented and labeled synthetic. The browser's four-arm session randomization is an independent measurement harness; the example's named counterbalanced experiment is not a model fitted from that harness.

Extensions should include physical or digital interventions, retrieval, model calls, and diagnostic tests as candidate information actions. Dependence and horizon matter: this implementation is not a multistep adaptive-experiment planner.

### 4.6 Sequential planning — implemented known-MDP reference

Backward induction computes the exact optimum for a supplied finite, fully observed MDP, horizon, and discount. A small gameplay fixture shows how an easy immediate reward can lose to an action that enables later mastery. The fixture's rewards are not human enjoyment measurements.

A real gameplay model will be partially observed and learned, with uncertainty over skill, player interpretation, and transitions. Do not substitute the reference solver for an established player model. Compare myopic, finite-horizon, robust, and simple rule-based policies on held-out sequences.

### 4.7 Evaluation and execution boundary

Implementations of IPS, self-normalized IPS, and doubly robust contextual-bandit evaluation are supplied [R7]. They require overlap, reliable logging probabilities or appropriate reward-model conditions, consistent outcomes, and a relevant population. The code refuses absent declared action support, reports effective sample size, and does not clip estimates into a reassuring probability range.

These functions do not establish causal identification merely by returning numbers. Learned reward models require proper splitting/cross-fitting. Repeated, adaptive, or clustered observations need additional analysis. The simple A/B posterior assumes independent Bernoulli observations; do not feed it all clicks from the same participant as if they were independent people.

One runtime should own permissions, durable state, side effects, retry policy, and budgets. This project currently owns none of those external effects. Do not add an autonomous second interpreter merely to obtain concise syntax.

## 5. Experiments actually run

All results in this section are synthetic fixtures or exact mathematical constructions, not measurements of human participants.

**Hidden state:** a deterministic balanced action rule can be predicted perfectly with the relevant cue and only 50% accurately without it. Determinism and observer predictability are different claims.

**Incentive-scale ambiguity:** multiplying all utilities by ten and dividing the softmax inverse temperature by ten produces the same distribution. The maximum difference in the fixture is zero. Choice data alone do not identify those two scales separately.

**Observation versus intervention:** one model sets `Y=A` with randomized A; another uses a hidden U with `A=U, Y=U`. Both produce exactly the same observational pairs, but changing A has effect one in the first model and zero in the second. This is a counterexample to inferring intervention effects from perfect observational prediction alone.

**Confounded design ranking:** across seeds 0–19, each with 20,000 generated events, true population values are A=0.75 and B=0.60. A is disproportionately shown to novices; B to experienced users. Naive averages choose B in every run. IPS, SNIPS, and DR choose A in every run. Mean absolute value errors are approximately 0.1796, 0.00964, 0.00730, and 0.00786 respectively. SNIPS wins this error comparison; we do not select DR by reputation. Propensities and relevant context are known by construction.

**Myopic gameplay:** the greedy action returns 7 now; a learning action returns 3 now and enables 8 next. With discount 0.9, two-step planning chooses learning with value 10.2. This validates the reference mechanics, not those reward values.

**Motor-only design:** the illustrative pointing model favors the near large target; adding an explicitly assumed visual-search penalty reverses the ranking. This is a constructed omitted-variable challenge, not an empirical measurement of a particular layout.

**Decision-relevant information:** the planner chooses a useful experiment, rejects an irrelevant question, and excludes an attractive-looking action that violates an error constraint. The 64 unit/HTTP tests cover these mechanics, malformed inputs, provenance requirements, overlap, budgets, and endpoint boundaries.

## 6. What to build and validate next

The shortest credible next milestone is one real task with a closed measurement loop, not a bigger general-agent framework. Use the included harness or an owned product with participant permission. Define a target such as successful task completion within a time window, plus error rate and a separate enjoyment response. Choose a meaningful difference and a statistical analysis before inspecting results.

Randomize at the session or participant level, keep variants stable, and record the full assignment distribution. Cluster repeated trials, account for practice and input modality, distinguish technical failure from participant abandonment, and do not silently discard difficult sessions. Repeated exports and automated smoke sessions must be detected. If a person returns in multiple sessions, session independence is still not guaranteed.

Use a real GUI-search dataset to test perceptual models separately from motivation. VSGUI10K is a relevant target [R5]; its linked data could not be retrieved in the current execution environment. No external behavioral dataset was analyzed in this version. Record the license, dataset version, exact splits, exclusions, and hashes before using it. Never turn a visual-search benchmark into a claim about long-term enjoyment.

Compare H0–H4 with fixed holdouts. Promote a model only after it improves decision outcomes and calibration without unacceptable operational costs. Report negative results. A complex system that fails to beat simple rules should be simplified.

## 7. Probably and Jev: components, not the thesis

Probably supplies an authoring concept for visible semantic uncertainty [R8]. Jev supplies typed semantic decisions [R9]. Neither supplies observed product outcomes, an identified causal model, or a complete player simulation. TypeSafe's documented confidence statistic must not be conflated with a universally calibrated probability of correctness [R10].

The provisional choice is a typed library and JSON decision representation. Later a Probably-like front end may compile to the same representation. Compare that with directly extending Probably or retaining only isolated helper functions. A new language must earn its parser, debugging, deployment, and maintenance costs. No live Jev/Weft integration or comparative latency benchmark was run here.

## 8. Open concepts and useful research bets

**Decision-relevant equivalence classes.** Multiple incentive models may remain indistinguishable yet recommend the same action. Optimize across the equivalence class; spend on identification only when disagreement changes the action.

**Perceptual gates as interventions.** Test whether changing what is noticed or understood explains a design improvement better than changing the reward. This makes the incentive hypothesis more precise instead of expanding it post hoc to explain anything.

**Experiments that maximize useful disagreement.** Choose variants where credible models disagree about the best action, not variants where every model predicts the same outcome. Include intervention cost and generalization to later decisions.

**Belief updates separated from goal optimization.** Preserve evidence even when it undermines the preferred feature or product thesis. Generate a decision certificate that another implementation can recompute without trusting a persuasive narrative.

**Horizon-aware experience design.** Evaluate whether a feature develops skill, understanding, or future enjoyment rather than merely maximizes the next click. Examine when shortening a session is an improvement rather than a failure.

**A budget for thinking.** Treat deeper reasoning, more data, a stronger model, and an experiment as alternative investments. Learn their marginal contribution to decision quality; stop when their expected value does not exceed cost.

**Shift-sensitive incentive models.** Determine which learned quantities transfer between layouts, devices, tasks, and later sessions. Distinguish changed goals from changed perceived options and learned habits.

**Proof obligations for the word optimal.** Every claim must name the candidate domain, objective, constraints, horizon, model, and uncertainty. Exact finite computation can coexist with uncertain empirical premises. Never let a theorem about the solver become a claim that its world model is correct.
