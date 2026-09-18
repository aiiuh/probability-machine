"""Reproducible synthetic challenges. No results here are human measurements."""
import json
import math
import random
import statistics
from pathlib import Path
from probability_machine import softmax, off_policy, plan, finite_horizon, fitts_ms, ab_posterior

ROOT = Path(__file__).resolve().parent


def confounding(seed, n=20000):
    rng = random.Random(seed)
    truth = {"novice": {"A": .55, "B": .35}, "experienced": {"A": .95, "B": .85}}
    events = []
    for i in range(n):
        context = "novice" if rng.random() < .5 else "experienced"
        p = .9 if context == "novice" else .1
        action = "A" if rng.random() < p else "B"
        events.append({"id": str(i), "context": context, "action": action,
                       "logging_policy": {"A": p, "B": 1-p},
                       "reward": int(rng.random() < truth[context][action])})
    naive = {a: statistics.mean(e["reward"] for e in events if e["action"] == a) for a in ("A", "B")}
    # Deliberately poor fixed outcome model; known simulated propensities are correct.
    model = {c: {"A": .5, "B": .5} for c in truth}
    estimates = {a: off_policy(events, {c: {"A": float(a=="A"), "B": float(a=="B")} for c in truth}, model)
                 for a in ("A", "B")}
    return {"naive": naive, "estimates": estimates, "ground_truth_population_value": {"A": .75, "B": .60}}


def run():
    baseline = softmax({"A": 2, "B": -1}, beta=1.5)
    rescaled = softmax({"A": 20, "B": -10}, beta=.15)
    runs = [confounding(seed) for seed in range(20)]
    summary = {}
    for method in ("naive", "ips", "snips", "doubly_robust"):
        values = [(r["naive"] if method == "naive" else {a: r["estimates"][a][method] for a in ("A", "B")}) for r in runs]
        summary[method] = {"picked_correct_action_runs": sum(v["A"] > v["B"] for v in values),
                           "runs": len(values),
                           "mean_absolute_value_error": statistics.mean(abs(v[a]-t) for v in values for a,t in (("A", .75), ("B", .60))),
                           "mean_A": statistics.mean(v["A"] for v in values),
                           "mean_B": statistics.mean(v["B"] for v in values)}
    layout = plan(json.loads((ROOT/"examples/layout.json").read_text()))
    game = json.loads((ROOT/"examples/gameplay.json").read_text())
    one = finite_horizon(game["mdp"], 1, game["discount"])
    two = finite_horizon(**game)
    near, far = fitts_ms(100, 60), fitts_ms(250, 40)
    ab = ab_posterior(80,100,85,100,practical_delta=.02)
    return {
        "evidence_type": "synthetic and exact mathematical counterexamples ONLY",
        "not_established": ["universal behavior prediction", "true incentive recovery", "real UI superiority", "real gameplay enjoyment", "Jev performance"],
        "observational_equivalence": {"same_observational_distribution": {"A0_Y0": .5, "A1_Y1": .5}, "causal_model_1_ATE": 1.0, "causal_model_2_ATE": 0.0, "models": ["A randomized, Y=A", "U randomized, A=U, Y=U"], "lesson": "Identical observational behavior can imply different effects of changing the action."},
        "hidden_state": {"description": "Same known reward weights. Action is determined by an unobserved balanced binary cue.",
                         "best_accuracy_without_cue": .5, "accuracy_with_cue_and_correct_deterministic_policy": 1.0},
        "incentive_identifiability": {"description": "Scaling utilities by 10 and inverse temperature by 0.1 leaves predictions unchanged.",
                                      "max_probability_difference": max(abs(baseline[k]-rescaled[k]) for k in baseline)},
        "confounded_design_test": {"first_seed": runs[0], "twenty_seed_summary": summary,
                                   "sample_size_per_seed": 20000, "limitation": "Simulated known propensities, measured context, no hidden confounding. Does not validate these assumptions in real logs."},
        "layout_decision": layout,
        "horizon_test": {"one_step_action": one["stages"][-1]["policy"]["start"], "two_step_action": two["stages"][-1]["policy"]["start"],
                         "two_step_optimal_value": two["values"]["start"], "limitation": "Rewards and transition model are invented."},
        "motor_model_omission": {"near_motor_ms": near, "far_motor_ms": far,
                                "near_with_assumed_search_ms": near+700, "far_with_assumed_search_ms": far+100,
                                "lesson": "A motor-only ranking can reverse when missing visual-search costs are added. Coefficients and search costs are illustrative."},
        "small_ab_test": ab,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
