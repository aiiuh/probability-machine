"""Bounded recipe bake-off. Hand-written candidates, fixed generated fixtures.

This exercises eligibility and selection, not automatic synthesis, ML training,
or a statistically calibrated promotion rule. Tests/verifiers stay fixed.
"""
from collections import Counter
from dataclasses import replace
import json
import random
from capability_core import Kernel, Policy, Run
from capability_demo import make_capabilities


def expected(rows):
    counts=Counter(row['kind'] for row in rows)
    return {'report':f'{len(rows)} records: '+', '.join(f'{key}={counts[key]}' for key in sorted(counts)),
            'evidence_origin':'synthetic_fixture'}


def bakeoff(seed=41,cases=50):
    if type(cases) is not int or not 1<=cases<=1000:
        raise ValueError('cases must be in 1..1000')
    rng=random.Random(seed)
    fixtures=[[{'id':f' example-{i} ','kind':rng.choice(['code','research','workflow']),
                'description':'synthetic evaluation case'} for i in range(rng.randrange(0,80))] for _ in range(cases)]
    base=make_capabilities();recipe=base[3]
    candidates={
        'composed':recipe,
        'fused':replace(recipe,release='candidate-fused-1',dependencies=(),units=1,
            execute=lambda x,c:{'report':str(len(x))+' records: '+', '.join(k+'='+str(sum(r['kind']==k for r in x)) for k in sorted({r['kind'] for r in x})),
                                'evidence_origin':'synthetic_fixture'}),
        'cheap_wrong':replace(recipe,release='candidate-wrong-1',dependencies=(),units=0,
            execute=lambda x,c:{'report':'Task complete','evidence_origin':'synthetic_fixture'}),
    }
    report={}
    for name,candidate in candidates.items():
        passes,adapter_calls,reserved_units=0,0,0
        for rows in fixtures:
            # Fresh kernel each case; duplicate fixture reuse cannot distort counts.
            caps=base[:3]+[candidate]+base[4:];k=Kernel(caps)
            run=Run(Policy(frozenset(c.name for c in caps)))
            result=k.call('catalog.recipe',rows,run)
            output=k.artifacts.get(result.output_hash) if result.output_hash else None
            passes+=result.status=='verified' and output==expected(rows)
            adapter_calls+=sum(not r.reused and r.status!='denied' for r in run.trace)
            reserved_units+=run.used
        report[name]={'accepted':passes,'cases':cases,'mean_adapter_invocations':adapter_calls/cases,
                      'mean_reserved_work_units':reserved_units/cases,'eligible_on_fixture':passes==cases}
    eligible=[n for n,r in report.items() if r['eligible_on_fixture']]
    winner=min(eligible,key=lambda n:(report[n]['mean_adapter_invocations'],n)) if eligible else None
    return {'evidence_class':'deterministic_candidate_selection_fixture','seed':seed,'candidates':report,
            'fixture_winner':winner,'production_promoted':False,
            'qualification':'Hand-written candidates; no live models, automated optimization, costs or calibration measured. Fixed checker cost remains; adapter counts do not imply end-to-end latency savings.'}

if __name__=='__main__':print(json.dumps(bakeoff(),indent=2,sort_keys=True))
