import copy
import json
import math
import unittest
from pathlib import Path
from probability_machine import *

ROOT = Path(__file__).resolve().parents[1]

class MachineTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT/"examples/layout.json").read_text())
    def test_plan_prefers_informative_experiment(self):
        out = plan(self.spec)
        self.assertEqual(out["recommended_next_step"], {"kind":"experiment","name":"counterbalanced_layout_test"})
        self.assertFalse(out["executed"])
    def test_plan_guardrail_not_offset_by_high_reward(self):
        self.assertIn("oversized_overlay", plan(self.spec)["rejected"])
    def test_budget(self):
        self.spec["action_budget"] = 0
        self.assertEqual(plan(self.spec)["status"], "no_feasible_action")
    def test_unknown_prior_not_uniform(self):
        self.spec["prior"] = {}
        with self.assertRaises(ValueError): plan(self.spec)
    def test_version_fail_closed(self):
        self.spec["schema_version"] = "99"
        with self.assertRaises(ValueError): plan(self.spec)
    def test_origin_required(self):
        del self.spec["model_origin"]
        with self.assertRaises(ValueError): plan(self.spec)
    def test_missing_model_rejected(self):
        del self.spec["actions"]["compact_top"]["outcomes"]["motor_cost_dominates"]
        with self.assertRaises(ValueError): plan(self.spec)
    def test_missing_metric_rejected(self):
        del self.spec["actions"]["compact_top"]["outcomes"]["motor_cost_dominates"]["enjoyment"]
        with self.assertRaises(ValueError): plan(self.spec)
    def test_invalid_limit(self):
        self.spec["limits"][0]["operator"] = "approximately"
        with self.assertRaises(ValueError): plan(self.spec)
    def test_no_objective(self):
        self.spec["objective"] = {}
        with self.assertRaises(ValueError): plan(self.spec)
    def test_trace_reproducible(self):
        self.assertEqual(plan(self.spec), plan(copy.deepcopy(self.spec)))
    def test_spec_change_changes_digest(self):
        old = plan(self.spec)["spec_sha256"]
        self.spec["objective"]["enjoyment"] = 11
        self.assertNotEqual(old, plan(self.spec)["spec_sha256"])
    def test_no_experiments_select_action(self):
        self.spec["experiments"] = {}
        self.assertEqual(plan(self.spec)["recommended_next_step"]["kind"], "action")
    def test_zero_prior_scenario_still_limit_checked(self):
        self.spec["prior"] = {"motor_cost_dominates":1.,"discoverability_dominates":0.}
        self.assertIn("oversized_overlay", plan(self.spec)["rejected"])
    def test_beta_zero_uniform(self):
        self.assertEqual(softmax({"a":10,"b":-10},0), {"a":.5,"b":.5})
    def test_softmax_shift_invariant(self):
        a,b=softmax({"a":2,"b":1}),softmax({"a":102,"b":101})
        self.assertAlmostEqual(a["a"],b["a"])
    def test_scale_nonidentifiability(self):
        self.assertEqual(softmax({"a":2,"b":-1},1.5), softmax({"a":20,"b":-10},.15))
    def test_softmax_no_overflow(self):
        self.assertAlmostEqual(sum(softmax({"a":10000,"b":-10000}).values()),1)
    def test_finite_temperature_not_certain(self):
        p=softmax({"a":1,"b":0})["a"]
        self.assertTrue(.5 < p < 1)
    def test_negative_beta(self):
        with self.assertRaises(ValueError): softmax({"a":0},-1)
    def test_invalid_distributions(self):
        for row in ({},{"a":.4},{"a":1.1,"b":-.1},{"a":True},{"a":float('nan')},{"a":float('inf')}):
            with self.subTest(row=row), self.assertRaises(ValueError): distribution(row)
    def test_bayes(self):
        self.assertEqual(update({"a":.5,"b":.5},{"a":.8,"b":.2}),{"a":.8,"b":.2})
    def test_impossible_observation(self):
        with self.assertRaises(ValueError): update({"a":.5,"b":.5},{"a":0,"b":0})
    def test_update_wrong_labels(self):
        with self.assertRaises(ValueError): update({"a":1},{"b":1})
    def test_conclusion(self):
        x=json.loads((ROOT/"examples/conclusion.json").read_text())
        self.assertEqual(conclude(**x)["posterior"]["reach_cost"],.8)
    def test_correlated_evidence_rejected(self):
        x=json.loads((ROOT/"examples/conclusion.json").read_text())
        e=copy.deepcopy(x["evidence"][0]);e["id"]="another-summary";x["evidence"].append(e)
        with self.assertRaises(ValueError): conclude(**x)
    def test_unsourced_evidence_rejected(self):
        x=json.loads((ROOT/"examples/conclusion.json").read_text()); x["evidence"][0]["source"]=""
        with self.assertRaises(ValueError): conclude(**x)
    def test_information_value(self):
        v=information_value({"x":.5,"y":.5},{"a":{"x":10,"y":0},"b":{"x":0,"y":10}},
                            {"yes":{"x":1,"y":0},"no":{"x":0,"y":1}},1)
        self.assertEqual(v["net_value"],4)
    def test_information_but_no_decision_value(self):
        v=information_value({"x":.5,"y":.5},{"a":{"x":10,"y":10},"b":{"x":0,"y":0}},
                            {"yes":{"x":1,"y":0},"no":{"x":0,"y":1}},.1)
        self.assertEqual(v["net_value"],-.1)
    def test_negative_query_cost(self):
        with self.assertRaises(ValueError): information_value({"x":1},{"a":{"x":1}},{"yes":{"x":1}},-1)
    def test_fitts_monotonic_distance(self): self.assertLess(fitts_ms(100,40), fitts_ms(200,40))
    def test_fitts_monotonic_width(self): self.assertLess(fitts_ms(100,80), fitts_ms(100,40))
    def test_fitts_invalid_width(self):
        with self.assertRaises(ValueError): fitts_ms(100,0)
    def test_horizon_changes_action(self):
        g=json.loads((ROOT/"examples/gameplay.json").read_text())
        self.assertEqual(finite_horizon(g["mdp"],1)["stages"][-1]["policy"]["start"],"easy_now")
        self.assertEqual(finite_horizon(**g)["stages"][-1]["policy"]["start"],"learn_skill")
        self.assertAlmostEqual(finite_horizon(**g)["values"]["start"],10.2)
    def test_zero_horizon(self):
        self.assertEqual(finite_horizon({"s":{"a":{"reward":4,"next":{"s":1}}}},0)["values"],{"s":0})
    def test_bad_horizon(self):
        for h in (-1,101,True,1.5):
            with self.subTest(h=h),self.assertRaises(ValueError): finite_horizon({"s":{}},h)
    def test_mdp_unknown_state(self):
        with self.assertRaises(ValueError): finite_horizon({"s":{"a":{"reward":4,"next":{"z":1}}}},2)
    def test_ab_reproducible(self): self.assertEqual(ab_posterior(2,3,2,3,draws=100),ab_posterior(2,3,2,3,draws=100))
    def test_ab_empty_no_certainty(self):
        out=ab_posterior(0,0,0,0)
        self.assertTrue(.47 < out["probability_b_exceeds_practical_delta"] < .53)
    def test_ab_invalid_counts(self):
        for args in ((4,3,0,1),(-1,3,0,1),(True,3,0,1)):
            with self.subTest(args=args),self.assertRaises(ValueError): ab_posterior(*args)
    def test_ab_mc_cap(self):
        with self.assertRaises(ValueError): ab_posterior(1,2,1,2,draws=100001)
    def test_ab_practical_margin(self):
        self.assertGreater(ab_posterior(50,100,70,100,draws=1000)["probability_b_exceeds_practical_delta"],
                           ab_posterior(50,100,70,100,practical_delta=.3,draws=1000)["probability_b_exceeds_practical_delta"])

class OffPolicyTests(unittest.TestCase):
    def setUp(self):
        self.events=[{"id":"1","context":"c","action":"a","logging_policy":{"a":.5,"b":.5},"reward":1},
                     {"id":"2","context":"c","action":"b","logging_policy":{"a":.5,"b":.5},"reward":0}]
        self.target={"c":{"a":1,"b":0}};self.q={"c":{"a":.5,"b":.5}}
    def test_estimators(self):
        x=off_policy(self.events,self.target,self.q)
        for m in ("ips","snips","doubly_robust"):self.assertEqual(x[m],1)
        self.assertEqual(x["effective_sample_size"],1)
    def test_no_overlap_rejected(self):
        self.events[0]["logging_policy"]={"a":0,"b":1}
        with self.assertRaises(ValueError):off_policy(self.events,self.target,self.q)
    def test_duplicate_rejected(self):
        self.events.append(self.events[0])
        with self.assertRaises(ValueError):off_policy(self.events,self.target,self.q)
    def test_bad_reward(self):
        self.events[0]["reward"]=2
        with self.assertRaises(ValueError):off_policy(self.events,self.target,self.q)
    def test_unknown_action_coverage(self):
        self.target["c"]={"a":.5,"c":.5}
        with self.assertRaises(ValueError):off_policy(self.events,self.target,self.q)
    def test_empty(self):
        with self.assertRaises(ValueError):off_policy([],self.target,self.q)
    def test_no_observed_support(self):
        with self.assertRaises(ValueError):off_policy(self.events[1:],self.target,self.q)
    def test_missing_q(self):
        self.q["c"]={"a":.5}
        with self.assertRaises(ValueError):off_policy(self.events,self.target,self.q)

if __name__ == '__main__':unittest.main()
