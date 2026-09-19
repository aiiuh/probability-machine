import dataclasses
import random
import unittest
from capability_core import Kernel, Policy, Run
from capability_demo import demonstration, make_capabilities, normalize, grouped

class EndToEndTests(unittest.TestCase):
    def test_three_workload_types_and_verified_file(self):
        x=demonstration(120)
        self.assertTrue(x['identical_output']);self.assertEqual(x['decision_adapter_status'],'verified')
        self.assertEqual(x['file_effect']['actual_file_writes'],1)
    def test_fifty_deterministic_generated_inputs(self):
        rng=random.Random(19);caps=make_capabilities();k=Kernel(caps);p=Policy(frozenset(c.name for c in caps))
        for case in range(50):
            rows=[{'id':f' {rng.randrange(10000)} ','kind':rng.choice(['code','research','workflow']),'description':'test'} for _ in range(rng.randrange(50))]
            with self.subTest(case=case):
                output=k.call('catalog.recipe',rows,Run(p)).require_verified(k.artifacts)
                self.assertIn(f"{len(rows)} records",output['report'])
                self.assertEqual(sum(grouped(normalize(rows))['groups'].values()),len(rows))
    def test_cheap_wrong_candidate_cannot_pass(self):
        caps=make_capabilities();caps[3]=dataclasses.replace(caps[3],execute=lambda x,c:{'report':'Done','evidence_origin':'synthetic_fixture'})
        k=Kernel(caps);p=Policy(frozenset(c.name for c in caps))
        self.assertEqual(k.call('catalog.recipe',[],Run(p)).status,'failed')
    def test_changed_leaf_implementation_requires_reverification(self):
        caps=make_capabilities();caps[1]=dataclasses.replace(caps[1],release='broken-candidate',execute=lambda x,c:{'count':999,'groups':{}})
        k=Kernel(caps);p=Policy(frozenset(c.name for c in caps))
        self.assertEqual(k.call('catalog.recipe',[],Run(p)).status,'failed')
    def test_empty_input_recipe(self):
        caps=make_capabilities();k=Kernel(caps);p=Policy(frozenset(c.name for c in caps))
        output=k.call('catalog.recipe',[],Run(p)).require_verified(k.artifacts)
        self.assertTrue(output['report'].startswith('0 records'))
    def test_cross_domain_added_without_core_edit(self):
        from capability_core import Capability
        extra=Capability('text.reverse','1','Reverse text','pure',1,'str','str',lambda x:type(x) is str,lambda x:type(x) is str,lambda x,c:x[::-1],'reverse-involution',lambda x,y:y[::-1]==x)
        k=Kernel(make_capabilities()+[extra]);p=Policy(frozenset({'text.reverse'}))
        self.assertEqual(k.call('text.reverse','abcd',Run(p)).require_verified(k.artifacts),'dcba')


class BakeoffTests(unittest.TestCase):
    def test_correct_fused_candidate_wins_not_cheapest_wrong(self):
        from capability_eval import bakeoff
        r=bakeoff(cases=20)
        self.assertEqual(r['fixture_winner'],'fused')
        self.assertEqual(r['candidates']['cheap_wrong']['accepted'],0)
        self.assertFalse(r['production_promoted'])
    def test_bakeoff_reproducible(self):
        from capability_eval import bakeoff
        self.assertEqual(bakeoff(cases=3),bakeoff(cases=3))
    def test_empty_bakeoff_rejected(self):
        from capability_eval import bakeoff
        with self.assertRaises(ValueError):bakeoff(cases=0)

if __name__=='__main__':unittest.main()
