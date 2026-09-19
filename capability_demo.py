"""Executable reference workloads. Synthetic inputs, real local computation/files.

No LLMs, Jev, X account, network, or background agents are called. Output byte
comparisons count selected JSON bodies, not tokens, latency, or production cost.
"""
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tempfile
from capability_core import Capability, ContractError, Kernel, Policy, Run, encode
from probability_machine import plan

ROOT = Path(__file__).resolve().parent


def records_valid(x):
    return type(x) is list and all(type(r) is dict and set(r) == {'id','kind','description'}
        and all(type(r[k]) is str for k in r) and r['kind'] in {'code','research','workflow'} for r in x)


def normalize(x):
    return sorted([{'id':r['id'].strip().lower(),'kind':r['kind']} for r in x],key=lambda r:(r['kind'],r['id']))


def grouped(x):
    return {'count':len(x),'groups':dict(sorted(Counter(r['kind'] for r in x).items()))}


def make_capabilities():
    def recipe(x,c):
        normalized=c.value(c.call('catalog.normalize',x))
        summary=c.value(c.call('catalog.group',normalized))
        return c.value(c.call('report.render',summary))
    def normalized_valid(x):
        return type(x) is list and all(type(r) is dict and set(r)=={'id','kind'} and
            type(r['id']) is str and r['kind'] in {'code','research','workflow'} for r in x)
    def summary_valid(x):
        return (type(x) is dict and set(x)=={'count','groups'} and type(x['count']) is int and
            type(x['groups']) is dict and all(type(v) is int and v>=0 for v in x['groups'].values()))
    def render(x):
        return {'report':f"{x['count']} records: " + ', '.join(f'{k}={v}' for k,v in sorted(x['groups'].items())),
                'evidence_origin':'synthetic_fixture'}
    return [
        Capability('catalog.normalize','1','Normalize a supplied source catalogue','pure',1,
            'catalog.raw/v1','catalog.normalized/v1',records_valid,normalized_valid,
            lambda x,c:normalize(x),'exact-normalization/v1',lambda x,y:y==normalize(x)),
        Capability('catalog.group','1','Aggregate normalized records by kind','pure',1,
            'catalog.normalized/v1','catalog.summary/v1',normalized_valid,summary_valid,
            lambda x,c:grouped(x),'exact-counts/v1',lambda x,y:y==grouped(x)),
        Capability('report.render','1','Render a compact catalogue report','pure',1,
            'catalog.summary/v1','report/v1',summary_valid,lambda x:type(x) is dict,
            lambda x,c:render(x),'exact-report/v1',lambda x,y:y==render(x)),
        Capability('catalog.recipe','1','Create a source catalogue report through verified composition','pure',0,
            'catalog.raw/v1','report/v1',records_valid,lambda x:type(x) is dict,
            recipe,'report-end-to-end/v1',lambda x,y:y==render(grouped(normalize(x))),
            ('catalog.normalize','catalog.group','report.render')),
        Capability('decision.rank','1','Rank explicit actions or experiments under uncertainty','pure',1,
            'decision-spec/0.3','conditional-decision/0.3',lambda x:type(x) is dict,
            lambda y:type(y) is dict and 'status' in y,
            lambda x,c:plan(x),'no-effects-structural/v1',lambda x,y:y.get('executed') is False),
    ]


def demonstration(count=5000):
    rows=[{'id':f' Item {i} ','kind':('code','research','workflow')[i%3],
           'description':'Synthetic record used to test aggregation; not a bookmarked post.'} for i in range(count)]
    caps=make_capabilities();policy=Policy(frozenset(c.name for c in caps))
    direct=Kernel(caps);dr=Run(policy)
    a=direct.call('catalog.normalize',rows,dr).require_verified(direct.artifacts)
    b=direct.call('catalog.group',a,dr).require_verified(direct.artifacts)
    c=direct.call('report.render',b,dr).require_verified(direct.artifacts)
    composed=Kernel(caps);cr=Run(policy)
    receipt=composed.call('catalog.recipe',rows,cr)
    final=receipt.require_verified(composed.artifacts)
    assert final==c
    before=cr.used
    repeated=composed.call('catalog.recipe',rows,cr)
    assert repeated.reused and cr.used==before
    spec=json.loads((ROOT/'examples/layout.json').read_text())
    decision=composed.call('decision.rank',spec,cr)
    assert decision.require_verified(composed.artifacts)==plan(spec)
    # A reviewed callback has only one fixed destination; request contains no path.
    with tempfile.TemporaryDirectory() as tmp:
        target=Path(tmp)/'report.json';writes=[]
        def write(x,ctx):
            target.write_bytes(encode(x));writes.append(True)
            return {'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
        effect=Capability('report.save','1','Save report at a host-bound temporary destination','effect',1,
            'report/v1','write-receipt/v1',lambda x:type(x) is dict,lambda x:type(x) is dict,
            write,'readback-bytes/v1',lambda x,y:target.read_bytes()==encode(x))
        writer=Kernel([effect]);wp=Policy(frozenset({'report.save'}),frozenset({'report.save'}));wr=Run(wp)
        saved=writer.call('report.save',final,wr,effect_key='save-report-1')
        saved.require_verified(writer.artifacts)
        duplicate=writer.call('report.save',final,wr,effect_key='save-report-1')
        assert len(writes)==1 and duplicate.reused
        effect_result={'verified':saved.status=='verified','actual_file_writes':len(writes),
                       'duplicate_suppressed_in_same_run':duplicate.reused}
    # No full schemas or tools outside the policy appear in initial discovery.
    discovered=composed.discover('catalogue report',policy,limit=3)
    direct_bytes=sum(len(encode(v)) for v in (a,b,c))
    composed_bytes=len(encode(final))
    return {'evidence_class':'deterministic_reference_workloads_with_synthetic_inputs',
            'records':count,'identical_output':final==c,
            'direct_result_bodies_bytes':direct_bytes,'composed_final_body_bytes':composed_bytes,
            'exposure_reduction_pct':100*(1-composed_bytes/direct_bytes),
            'direct_leaf_calls':len(dr.trace),'composed_leaf_calls':3,
            'composed_wrapper_calls':1,'reused_recipe_extra_adapter_calls':0,
            'decision_adapter_status':decision.status,
            'decision_verifier_scope':'no-effect structural invariant only; NOT factual correctness',
            'file_effect':effect_result,'discovered':discovered,
            'report':final,'receipt':asdict(receipt),
            'limits':['No LLM/token/dollar/latency improvement measured',
                      'Composed execution retains the same three leaf operations',
                      'One outer result rather than intermediate bodies; initial input common to both excluded',
                      'Trusted synchronous callbacks only; no sandbox or crash recovery',
                      'No actual X bookmarks were imported']}


if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
