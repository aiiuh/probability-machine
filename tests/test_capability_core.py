import dataclasses
import unittest
from capability_core import Artifacts, Capability, ContractError, Kernel, Policy, Receipt, Run, digest, encode


def cap(name='math.double', **changes):
    base = Capability(name, '1', 'Double an integer for a calculation', 'pure', 1,
        'integer/v1', 'integer/v1', lambda x:type(x) is int, lambda y:type(y) is int,
        lambda x,c:x*2, 'exact-double/v1', lambda x,y:y == x*2)
    return dataclasses.replace(base, **changes)


def policy(*names, effects=()): return Policy(frozenset(names), frozenset(effects))


class CapabilityTests(unittest.TestCase):
    def test_roundtrip(self):
        k=Kernel([cap()]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.require_verified(k.artifacts),4)
    def test_input_boolean_is_not_integer(self):
        k=Kernel([cap()]);r=k.call('math.double',True,Run(policy('math.double')))
        self.assertEqual(r.status,'denied')
    def test_wrong_output_schema(self):
        k=Kernel([cap(execute=lambda x,c:'4')]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'failed')
    def test_false_success_rejected(self):
        k=Kernel([cap(execute=lambda x,c:5)]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'failed')
    def test_absent_verifier_not_pass(self):
        k=Kernel([cap(verify=None)]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'unverified')
        with self.assertRaises(ContractError):r.require_verified(k.artifacts)
    def test_unknown_verifier_not_pass(self):
        k=Kernel([cap(verify=lambda x,y:None)]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'unverified')
    def test_truthy_string_not_pass(self):
        k=Kernel([cap(verify=lambda x,y:'yes')]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'failed')
    def test_input_validator_truthy_not_true(self):
        k=Kernel([cap(validate_input=lambda x:'yes')]);r=k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(r.status,'denied')
    def test_budget_reserved_before_call(self):
        run=Run(policy('math.double'),budget=1)
        k=Kernel([cap(execute=lambda x,c:run.used*2)])
        self.assertEqual(k.call('math.double',1,run).status,'verified')
    def test_over_budget_never_enters_adapter(self):
        seen=[]; k=Kernel([cap(execute=lambda x,c:seen.append(1))])
        r=k.call('math.double',2,Run(policy('math.double'),budget=0))
        self.assertEqual((r.status,seen),('denied',[]))
    def test_failure_reservation_not_refunded(self):
        k=Kernel([cap(execute=lambda x,c:1/0)]);run=Run(policy('math.double'))
        k.call('math.double',1,run); self.assertEqual(run.used,1)
    def test_exception_secret_not_returned(self):
        def fail(x,c):raise ValueError('sensitive-token-123')
        k=Kernel([cap(execute=fail)]);r=k.call('math.double',1,Run(policy('math.double')))
        self.assertNotIn('sensitive-token',str(r))
    def test_unknown_tool_denied(self):
        k=Kernel([cap()]);self.assertEqual(k.call('missing',1,Run(policy('missing'))).status,'denied')
    def test_no_authority_from_input(self):
        k=Kernel([cap()]);self.assertEqual(k.call('math.double',{'confidence':1,'permission':True},Run(policy())).status,'denied')
    def test_policy_narrow(self):
        p=policy('a','b',effects=('b',));self.assertEqual(p.narrow(['a']).effect_grants,frozenset())
    def test_policy_cannot_widen(self):
        with self.assertRaises(ContractError):policy('a').narrow(['b'])
    def test_mutable_policy_rejected(self):
        with self.assertRaises(ContractError):Policy({'a'})
    def test_effect_grant_must_be_allowed(self):
        with self.assertRaises(ContractError):policy('a',effects=('b',))
    def test_cancelled_no_invocation(self):
        run=Run(policy('math.double'));run.cancel()
        self.assertEqual(Kernel([cap()]).call('math.double',1,run).status,'denied');self.assertEqual(run.used,0)
    def test_count_bound_includes_reuse(self):
        k=Kernel([cap()]);run=Run(policy('math.double'),max_calls=1)
        k.call('math.double',1,run);self.assertEqual(k.call('math.double',1,run).status,'denied')
    def test_pure_verified_reuse(self):
        k=Kernel([cap()]);run=Run(policy('math.double'))
        k.call('math.double',2,run);r=k.call('math.double',2,run)
        self.assertTrue(r.reused);self.assertEqual(run.used,1)
    def test_reuse_still_needs_permission(self):
        k=Kernel([cap()]);k.call('math.double',2,Run(policy('math.double')))
        self.assertEqual(k.call('math.double',2,Run(policy())).status,'denied')
    def test_changed_input_not_reused(self):
        k=Kernel([cap()]);run=Run(policy('math.double'))
        k.call('math.double',2,run);self.assertFalse(k.call('math.double',3,run).reused)
    def test_read_not_cached(self):
        k=Kernel([cap(kind='read')]);run=Run(policy('math.double'))
        k.call('math.double',1,run);self.assertFalse(k.call('math.double',1,run).reused);self.assertEqual(run.used,2)
    def test_unknown_not_cached(self):
        k=Kernel([cap(verify=None)]);run=Run(policy('math.double'))
        k.call('math.double',1,run);self.assertFalse(k.call('math.double',1,run).reused)
    def test_release_change_changes_fingerprint(self):
        a,b=Kernel([cap()]),Kernel([cap(release='2')]);p=policy('math.double')
        self.assertNotEqual(a.describe('math.double',p)['release_hash'],b.describe('math.double',p)['release_hash'])
    def test_verifier_change_changes_fingerprint(self):
        a,b=Kernel([cap()]),Kernel([cap(verifier_id='v2')]);p=policy('math.double')
        self.assertNotEqual(a.describe('math.double',p)['release_hash'],b.describe('math.double',p)['release_hash'])
    def test_artifact_copy_isolated(self):
        a=Artifacts();h=a.put({'x':[1]});v=a.get(h);v['x'].append(2);self.assertEqual(a.get(h),{'x':[1]})
    def test_artifact_corruption_detected(self):
        a=Artifacts();h=a.put([1]);a._values[h]=b'[]'
        with self.assertRaises(ContractError):a.get(h)
    def test_json_forbids_nonfinite_and_implicit_keys(self):
        for x in (float('nan'),float('inf'),{1:'x'},{'x':set()},b'hello'):
            with self.subTest(x=x),self.assertRaises(ContractError):encode(x)
    def test_json_depth_limit(self):
        v=[]
        for _ in range(42):v=[v]
        with self.assertRaises(ContractError):encode(v)
    def test_json_byte_limit(self):
        with self.assertRaises(ContractError):encode('x'*100,max_bytes=50)
    def test_mapping_order_canonical(self):self.assertEqual(digest({'a':1,'b':2}),digest({'b':2,'a':1}))
    def test_duplicate_registry_rejected(self):
        with self.assertRaises(ContractError):Kernel([cap(),cap()])
    def test_missing_dependency_rejected(self):
        with self.assertRaises(ContractError):Kernel([cap(dependencies=('missing',))])
    def test_cycle_rejected(self):
        with self.assertRaises(ContractError):Kernel([cap('a',dependencies=('b',)),cap('b',dependencies=('a',))])
    def test_pure_cannot_hide_read(self):
        with self.assertRaises(ContractError):Kernel([cap('a',dependencies=('b',)),cap('b',kind='read')])
    def test_read_cannot_hide_effect(self):
        with self.assertRaises(ContractError):Kernel([cap('a',kind='read',dependencies=('b',)),cap('b',kind='effect')])
    def test_negative_budget_rejected(self):
        with self.assertRaises(ContractError):Run(policy(),budget=-1)
    def test_bad_cost_rejected(self):
        with self.assertRaises(ContractError):Kernel([cap(units=True)])
    def test_discovery_bounded_and_scoped(self):
        k=Kernel([cap('math.double'),cap('math.other')]);p=policy('math.double')
        self.assertEqual([x['name'] for x in k.discover('integer',p)],['math.double'])
        self.assertNotIn('input_contract',k.discover('integer',p)[0])
    def test_discovery_empty_not_dump(self):self.assertEqual(Kernel([cap()]).discover('',policy('math.double')),[])
    def test_describe_denied(self):
        with self.assertRaises(ContractError):Kernel([cap()]).describe('math.double',policy())
    def test_nested_recipe(self):
        recipe=cap('math.quad',dependencies=('math.double',),execute=lambda x,c:c.value(c.call('math.double',c.value(c.call('math.double',x)))),verify=lambda x,y:y==x*4)
        k=Kernel([cap(),recipe]);run=Run(policy('math.double','math.quad'))
        self.assertEqual(k.call('math.quad',3,run).require_verified(k.artifacts),12);self.assertEqual(len(run.trace),3)
    def test_undeclared_dependency_blocked(self):
        k=Kernel([cap(),cap('bad',execute=lambda x,c:c.value(c.call('math.double',x)))])
        self.assertEqual(k.call('bad',1,Run(policy('bad','math.double'))).status,'failed')
    def test_missing_child_authority_before_parent(self):
        seen=[];k=Kernel([cap(),cap('recipe',dependencies=('math.double',),execute=lambda x,c:seen.append(1))])
        self.assertEqual(k.call('recipe',1,Run(policy('recipe'))).status,'denied');self.assertEqual(seen,[])
    def test_child_release_invalidates_parent(self):
        recipe=cap('recipe',dependencies=('math.double',))
        a,b=Kernel([cap(),recipe]),Kernel([cap(version='2'),recipe]);p=policy('recipe')
        self.assertNotEqual(a.describe('recipe',p)['release_hash'],b.describe('recipe',p)['release_hash'])
    def test_child_budget_failure_not_hidden(self):
        recipe=cap('recipe',dependencies=('math.double',),execute=lambda x,c:c.value(c.call('math.double',x)))
        k=Kernel([cap(),recipe]);run=Run(policy('recipe','math.double'),budget=1)
        self.assertEqual(k.call('recipe',1,run).status,'failed');self.assertEqual(run.used,1)
    def test_child_depth_bound(self):
        recipe=cap('recipe',dependencies=('math.double',),execute=lambda x,c:c.value(c.call('math.double',x)))
        k=Kernel([cap(),recipe]);self.assertEqual(k.call('recipe',1,Run(policy('recipe','math.double'),max_depth=0)).status,'failed')


class EffectTests(unittest.TestCase):
    def setUp(self):self.seen=[]
    def build(self,**kw):
        return Kernel([cap('effect.append',kind='effect',execute=lambda x,c:(self.seen.append(x),x*2)[1],**kw)])
    def test_grant_and_key_required(self):
        for p,key in ((policy('effect.append'),'op'),(policy('effect.append',effects=('effect.append',)),None)):
            self.assertEqual(self.build().call('effect.append',1,Run(p),effect_key=key).status,'denied')
        self.assertEqual(self.seen,[])
    def test_duplicate_success_suppressed_in_run(self):
        k=self.build();run=Run(policy('effect.append',effects=('effect.append',)))
        k.call('effect.append',2,run,effect_key='op');r=k.call('effect.append',2,run,effect_key='op')
        self.assertEqual(self.seen,[2]);self.assertTrue(r.reused)
    def test_duplicate_key_different_payload_denied(self):
        k=self.build();run=Run(policy('effect.append',effects=('effect.append',)))
        k.call('effect.append',2,run,effect_key='op');r=k.call('effect.append',3,run,effect_key='op')
        self.assertEqual(r.status,'denied');self.assertEqual(self.seen,[2])
    def test_effect_happened_then_error_not_retried(self):
        def fail(x,c):self.seen.append(x);raise TimeoutError('remote may have committed')
        k=Kernel([cap('effect.append',kind='effect',execute=fail)]);run=Run(policy('effect.append',effects=('effect.append',)))
        a=k.call('effect.append',2,run,effect_key='op');b=k.call('effect.append',2,run,effect_key='op')
        self.assertEqual((a.status,b.status),('uncertain','uncertain'));self.assertEqual(self.seen,[2])
    def test_unknown_effect_verification_not_success(self):
        k=self.build(verify=None);run=Run(policy('effect.append',effects=('effect.append',)))
        r=k.call('effect.append',2,run,effect_key='op');self.assertEqual(r.effect_state,'uncertain')
    def test_in_memory_dedup_does_not_claim_durable(self):
        k=self.build();p=policy('effect.append',effects=('effect.append',))
        k.call('effect.append',2,Run(p),effect_key='op');k.call('effect.append',2,Run(p),effect_key='op')
        self.assertEqual(self.seen,[2,2])  # Explicit counterexample: a new run lacks durable reconciliation.

if __name__=='__main__':unittest.main()
