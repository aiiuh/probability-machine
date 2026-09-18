"""Probability Machine v0.3: bounded decision calculations, not mind reading.

Standard library only. No provider calls, external effects, or hidden data access.
All supplied models, likelihoods, objectives and causal assumptions are explicit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Mapping

VERSION = "0.3.0"


def number(value, name="number"):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def distribution(row: Mapping[str, float]):
    if not isinstance(row, dict) or not row:
        raise ValueError("a nonempty explicit distribution is required")
    if any(not isinstance(k, str) or not k.strip() for k in row):
        raise ValueError("distribution labels must be nonempty strings")
    row = {k: number(v, k) for k, v in row.items()}
    if any(v < 0 or v > 1 for v in row.values()):
        raise ValueError("probabilities must lie in [0,1]")
    if not math.isclose(math.fsum(row.values()), 1, abs_tol=1e-9, rel_tol=0):
        raise ValueError("probabilities must sum to one")
    return row


def softmax(utilities, beta=1.0):
    """Finite-temperature choice model, NOT a universal model of human behavior."""
    beta = number(beta, "beta")
    if beta < 0 or not utilities:
        raise ValueError("nonnegative beta and nonempty utilities required")
    values = {k: number(v, "utility") for k, v in utilities.items()}
    if beta == 0:
        return distribution({k: 1 / len(values) for k in values})
    peak = max(values.values())
    weights = {k: math.exp(min(0.0, (v - peak) * beta)) for k, v in values.items()}
    total = math.fsum(weights.values())
    return distribution({k: v / total for k, v in weights.items()})


def update(prior, likelihood):
    prior = distribution(prior)
    if set(prior) != set(likelihood):
        raise ValueError("likelihood labels must match prior")
    likelihood = {k: number(v, "likelihood") for k, v in likelihood.items()}
    if any(v < 0 or v > 1 for v in likelihood.values()):
        raise ValueError("likelihoods must lie in [0,1]")
    weights = {k: prior[k] * likelihood[k] for k in prior}
    total = math.fsum(weights.values())
    if total <= 0:
        raise ValueError("observation impossible under every supported hypothesis")
    return distribution({k: v / total for k, v in weights.items()})


def conclude(prior, evidence):
    """Finite Bayes update. Independence is an assumption, not inferred from IDs."""
    posterior = distribution(prior)
    ids, groups, sources = set(), set(), []
    for item in evidence:
        if not all(isinstance(item.get(k), str) and item[k].strip()
                   for k in ("id", "independence_group", "source")):
            raise ValueError("evidence needs ID, independence group, and source")
        if item["id"] in ids or item["independence_group"] in groups:
            raise ValueError("duplicate or dependent evidence cannot be counted twice")
        posterior = update(posterior, item["likelihood"])
        ids.add(item["id"]); groups.add(item["independence_group"])
        sources.append(item["source"])
    return {"posterior": posterior, "evidence_ids": sorted(ids), "sources": sources,
            "qualification": "Conditional on supplied hypotheses, prior, likelihoods and independence assumptions; not proof."}


def expected(prior, utilities):
    prior = distribution(prior)
    if not utilities:
        raise ValueError("no candidate actions")
    scores = {}
    for action, row in utilities.items():
        if not isinstance(action, str) or not action or set(row) != set(prior):
            raise ValueError("action labels and utility model coverage must be exact")
        scores[action] = math.fsum(prior[m] * number(row[m], "utility") for m in prior)
    return scores


def information_value(prior, utilities, answers, cost):
    """Exact one-step expected value of sample information in objective units."""
    prior = distribution(prior)
    base = max(expected(prior, utilities).values())
    cost = number(cost, "experiment cost")
    if cost < 0 or not answers:
        raise ValueError("nonnegative cost and nonempty answer model required")
    if any(set(row) != set(prior) for row in answers.values()):
        raise ValueError("answer model coverage must match prior")
    for model in prior:
        distribution({a: row[model] for a, row in answers.items()})
    after = 0.0
    for row in answers.values():
        mass = math.fsum(prior[m] * row[m] for m in prior)
        if mass > 0:
            after += mass * max(expected(update(prior, row), utilities).values())
    gross = max(0.0, after - base)
    return {"gross_value": gross, "cost": cost, "net_value": gross - cost}


def plan(spec):
    """Choose among explicit candidates; never executes a recommended action.

    Hard limits apply to ALL supplied scenarios, including zero-prior scenarios.
    This is a conservative specification check, not proof of real-world safety.
    """
    if not isinstance(spec, dict):
        raise ValueError("specification must be a JSON object")
    if spec.get("schema_version") != "0.3":
        raise ValueError("unsupported schema_version")
    origin = spec.get("model_origin")
    if origin not in {"synthetic", "assumed", "measured"}:
        raise ValueError("model_origin must be synthetic, assumed, or measured")
    sources = spec.get("model_sources", [])
    if not isinstance(sources, list) or any(not isinstance(s, str) or not s.strip() for s in sources):
        raise ValueError("model_sources must be a list of nonempty references")
    if origin == "measured" and not sources:
        raise ValueError("measured models require source references; references are not independently verified")
    prior = distribution(spec["prior"])
    weights = {k: number(v, "objective weight") for k, v in spec["objective"].items()}
    if not weights or not any(weights.values()):
        raise ValueError("an explicit nonzero objective is required")
    budget = number(spec.get("action_budget", 0), "action_budget")
    if budget < 0:
        raise ValueError("negative action budget")
    actions = spec["actions"]
    if not isinstance(actions, dict) or not actions or len(actions) > 1000:
        raise ValueError("1..1000 candidate actions required")
    limits = spec.get("limits", [])
    for limit in limits:
        if limit.get("operator") not in {"min", "max"} or not limit.get("metric"):
            raise ValueError("limit requires metric and min/max operator")
        number(limit["value"], "limit")
    feasible, rejected = {}, {}
    for action, detail in actions.items():
        cost = number(detail.get("cost", 0), "action cost")
        if cost < 0:
            raise ValueError("negative action cost")
        models = detail["outcomes"]
        if set(models) != set(prior):
            raise ValueError("outcomes must cover every scenario exactly")
        reasons, scores = [], {}
        if cost > budget:
            reasons.append("action budget exceeded")
        for model, metrics in models.items():
            metrics = {k: number(v, "outcome metric") for k, v in metrics.items()}
            if not set(weights) <= set(metrics):
                raise ValueError("missing objective metric")
            scores[model] = math.fsum(weights[k] * metrics[k] for k in weights)
            for limit in limits:
                key, threshold = limit["metric"], number(limit["value"])
                if key not in metrics:
                    raise ValueError("missing limit metric")
                bad = metrics[key] > threshold if limit["operator"] == "max" else metrics[key] < threshold
                if bad:
                    reasons.append(f"{model}: {key} violates {limit['operator']} {threshold}")
        if reasons:
            rejected[action] = reasons
        else:
            feasible[action] = scores
    if not feasible:
        return {"status": "no_feasible_action", "rejected": rejected, "executed": False}
    values = expected(prior, feasible)
    best = sorted(values, key=lambda a: (-values[a], a))[0]
    scenario_best = {m: max(row[m] for row in feasible.values()) for m in prior}
    regrets = {a: max(scenario_best[m] - row[m] for m in prior) for a, row in feasible.items()}
    robust = sorted(regrets, key=lambda a: (regrets[a], a))[0]
    alternatives = [{"action": a, "expected_utility": values[a], "max_scenario_regret": regrets[a]}
                    for a in sorted(values, key=lambda a: (-values[a], a))]
    experiments = []
    for name, query in spec.get("experiments", {}).items():
        val = information_value(prior, feasible, query["answers"], query["cost"])
        experiments.append({"experiment": name, **val})
    experiments.sort(key=lambda x: (-x["net_value"], x["experiment"]))
    next_step = {"kind": "action", "name": best}
    if experiments and experiments[0]["net_value"] > 1e-9:
        next_step = {"kind": "experiment", "name": experiments[0]["experiment"]}
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {"status": "conditional_recommendation", "version": VERSION,
            "spec_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "model_origin": origin, "model_sources": sources, "recommended_next_step": next_step,
            "best_action_now": best, "minimax_regret_action": robust,
            "decision_robust_across_supplied_scenarios": all(
                feasible[best][m] >= scenario_best[m] - 1e-9 for m in prior),
            "alternatives": alternatives, "experiments": experiments, "rejected": rejected,
            "executed": False, "qualification": "Optimal only within the supplied candidate set, models, objective and one-step information model."}


def fitts_ms(distance, width, a_ms=50, b_ms=100):
    """Illustrative Shannon-form motor-time model; not a full UX score."""
    distance, width, a_ms, b_ms = [number(v) for v in (distance, width, a_ms, b_ms)]
    if distance < 0 or width <= 0 or min(a_ms, b_ms) < 0:
        raise ValueError("invalid geometry or coefficients")
    return a_ms + b_ms * math.log2(1 + distance / width)


def finite_horizon(mdp, horizon, discount=1.0):
    """Exact backward induction for a finite, fully observed, known MDP."""
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 0 <= horizon <= 100:
        raise ValueError("horizon must be an integer in 0..100")
    discount = number(discount)
    if not 0 <= discount <= 1 or not mdp or len(mdp) > 1000:
        raise ValueError("invalid discount or state count")
    for state, actions in mdp.items():
        if not actions:
            raise ValueError("every state needs an action (use zero-reward self-loop for terminal states)")
        for item in actions.values():
            number(item["reward"])
            trans = distribution(item["next"])
            if not set(trans) <= set(mdp):
                raise ValueError("unknown next state")
    value = {s: 0.0 for s in mdp}
    stages = []
    for remaining in range(1, horizon + 1):
        q = {s: {a: number(item["reward"]) + discount * math.fsum(p * value[n]
                   for n, p in item["next"].items()) for a, item in actions.items()}
             for s, actions in mdp.items()}
        policy = {s: sorted(row, key=lambda a: (-row[a], a))[0] for s, row in q.items()}
        value = {s: q[s][policy[s]] for s in mdp}
        stages.append({"steps_remaining": remaining, "values": value, "policy": policy})
    return {"horizon": horizon, "values": value, "stages": stages,
            "qualification": "Known finite MDP only; not an empirically learned human model or POMDP solver."}


def off_policy(events, target, reward_model):
    """Contextual-bandit IPS, SNIPS and DR, with declared support checks.

    Assumes reliable propensities, no hidden confounding conditional on context,
    consistent outcomes, and a target population represented by these contexts.
    reward_model must be external/cross-fitted for valid learned-model use.
    No confidence interval is returned; clustered/sequential data need extra work.
    """
    if not events:
        raise ValueError("no observations")
    weights, ips, direct, dr, seen = [], [], [], [], set()
    for event in events:
        if not isinstance(event.get("id"), str) or not event["id"] or event["id"] in seen:
            raise ValueError("missing or duplicated observation ID")
        seen.add(event["id"])
        context, action = event["context"], event["action"]
        logging = distribution(event["logging_policy"])
        policy = distribution(target[context])
        if set(policy) != set(logging):
            raise ValueError("logging and target action sets must match")
        if any(policy[a] > 0 and logging[a] <= 0 for a in policy):
            raise ValueError("unsupported target action: no overlap")
        if action not in logging or logging[action] <= 0:
            raise ValueError("observed action has invalid propensity")
        reward = number(event["reward"])
        q = {a: number(v) for a, v in reward_model[context].items()}
        if set(q) != set(policy) or not 0 <= reward <= 1 or any(not 0 <= v <= 1 for v in q.values()):
            raise ValueError("bounded rewards/models and exact action coverage required")
        weight = policy[action] / logging[action]
        estimate = math.fsum(policy[a] * q[a] for a in policy)
        weights.append(weight); ips.append(weight * reward); direct.append(estimate)
        dr.append(estimate + weight * (reward - q[action]))
    n, sum_w = len(events), math.fsum(weights)
    if sum_w == 0:
        raise ValueError("no observed target-policy support in sample")
    ess = sum_w * sum_w / math.fsum(w*w for w in weights)
    return {"n": n, "ips": math.fsum(ips)/n, "snips": math.fsum(ips)/sum_w,
            "direct": math.fsum(direct)/n, "doubly_robust": math.fsum(dr)/n,
            "effective_sample_size": ess, "max_importance_weight": max(weights),
            "low_effective_support": ess < 30,
            "qualification": "Conditional off-policy estimates; not a causal certificate. Estimates are not clipped to [0,1]."}


def ab_posterior(success_a, n_a, success_b, n_b, practical_delta=0.0, draws=10000, seed=19):
    """Independent Bernoulli/Beta(1,1) model. No universal stopping guarantee."""
    for s, n in ((success_a, n_a), (success_b, n_b)):
        if any(isinstance(v, bool) or not isinstance(v, int) for v in (s, n)) or not 0 <= s <= n:
            raise ValueError("integer counts with 0 <= success <= n required")
    if isinstance(draws, bool) or not isinstance(draws, int) or not 100 <= draws <= 100000:
        raise ValueError("draws must be an integer in 100..100000")
    practical_delta = number(practical_delta)
    if not 0 <= practical_delta <= 1:
        raise ValueError("practical_delta must lie in [0,1]")
    rng = random.Random(seed)
    deltas = sorted(rng.betavariate(success_b+1, n_b-success_b+1) -
                    rng.betavariate(success_a+1, n_a-success_a+1) for _ in range(draws))
    mean_a, mean_b = (success_a+1)/(n_a+2), (success_b+1)/(n_b+2)
    return {"mean_a": mean_a, "mean_b": mean_b,
            "probability_b_exceeds_practical_delta": sum(d > practical_delta for d in deltas)/draws,
            "delta_interval_95": [deltas[int(.025*draws)], deltas[min(draws-1, int(.975*draws))]],
            "expected_regret_choose_a": math.fsum(max(d, 0) for d in deltas)/draws,
            "expected_regret_choose_b": math.fsum(max(-d, 0) for d in deltas)/draws,
            "draws": draws, "seed": seed, "prior": "independent Beta(1,1)",
            "qualification": "Posterior conditional on independent Bernoulli observations, chosen prior and stable population; not evidence of latent incentives."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "conclude", "mdp", "off-policy", "ab"])
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 10_000_000:
            raise ValueError("input exceeds 10 MB")
        data = json.loads(args.input.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        funcs = {"conclude": conclude, "mdp": finite_horizon, "off-policy": off_policy, "ab": ab_posterior}
        result = plan(data) if args.command == "plan" else funcs[args.command](**data)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"Invalid input: {exc}\n")


if __name__ == "__main__":
    main()
