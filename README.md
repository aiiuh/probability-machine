# Probability Machine

An evidence-driven action and conclusion engine, with product design, interface layout, and gameplay as initial application domains.

## Goal

Turn a goal into competing hypotheses, candidate actions, predicted outcomes, targeted experiments, and a verified decision. Test whether incentive-based models predict behavior out of sample rather than assuming that probabilities, engagement, or model confidence reveal human utility.

## Development status

Initial repository bootstrap. The implementation, reproducible hypothesis tests, research ledger, and next-stage work orders are being added in this development session. This initial commit does not contain a finished engine.

## Design commitments

- Separate predictions about human behavior from objectives chosen for the product.
- Represent context, perceived options, uncertainty, incentives, and costs explicitly.
- Compare simple rules, statistical models, and semantic/LLM models before adding complexity.
- Treat clicks, enjoyment, task success, and voluntary return as different measurements.
- Use causal experiments for claims about changing a design; observational correlations alone are insufficient.
- Optimize under explicit constraints and budgets. Do not infer execution permission from a probability.
- Record provenance, model versions, alternatives, uncertainty, and actual test outcomes.
- Keep provider integrations and Probably-like authoring optional. Use one execution authority.

No private project notes, credentials, personal profiles, or local-machine details belong in this public repository.
