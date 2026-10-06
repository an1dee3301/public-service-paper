"""Replication, ties, scope attacks. Imports only the independent solver.
Lead functions are inspected via AST and loaded without their run() side effects.
Reported lattice calculations use exact integer quarter-units, never floats.
"""
import ast,json,random
from itertools import product
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from solver import continuation,equilibrium,outcomes,target,primitive_case,prop2,slack_cont,encode
HERE=Path(__file__).resolve().parent
LEAD=HERE.parent/'closed_form'

def load_functions(path,names,ns):
    tree=ast.parse(path.read_text())
    selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns)
    return ns

lead=load_functions(LEAD/'classification.py',{'cells'},{'F':Q})['cells']
counts=Counter(); sampled=0; p2=0; raw_lemma=0
random.seed(23)
rf=lambda lo,hi:random.randint(lo*4,hi*4)
for _ in range(400000):
    V,c,b=rf(2,14),rf(1,12),rf(0,12)
    if b==0 or b>c:continue
    h,B,k,O=rf(0,10),rf(0,16),rf(0,6),rf(0,14)
    if k>B or k==0:continue
    t=(V,c,b,h,B,k,O);sampled+=1
    label=primitive_case(t);actual=target(t)
    d,f,th,dr,types=lead(*t)
    assert bool(label)==actual==bool(d and (f or th or dr)),t
    if label:counts[label]+=1
    if prop2(t):
        p2+=1;assert label=='F',t
sample=dict(points=sampled,by_case=dict(counts),joint_only=sum(counts.values()),prop2=p2,mismatches=0)
print('seed23',sample,flush=True)

random.seed(7)
for _ in range(200000):
    V,c,b=rf(1,14),rf(1,12),rf(0,12)
    if b==0 or b>c:continue
    h,B,k,O=rf(0,10),rf(0,16),rf(0,6),rf(0,14)
    if k>B:continue
    for x,d in product((0,1),(0,1)):
        z=continuation(V,c,b,h,B-k*x,O*x,d)
        assert (z['kind'],z['p'])==slack_cont(V,c,b,h,B-k*x,O*x,d)
        raw_lemma+=1
print('seed7 lemma states',raw_lemma,flush=True)

lc=Counter(); total=0; feasible=0; p2=0; invalid=0; boundary_counts=Counter()
for B,k,O in product(range(81),range(1,25),range(49)):
    total+=1
    if k>B:
        invalid+=1;continue
    feasible+=1
    t=(40,24,8,12,B,k,O)
    label=primitive_case(t)
    assert bool(label)==target(t),t
    if label:
        lc[label]+=1
        for key,kwargs in [('build_at_tie',dict(build_tie=True)),
                           ('harm_at_condition_tie',dict(harmless_tie=False)),
                           ('decline_at_zero_profit',dict(trade_zero=False))]:
            if not target(t,**kwargs):boundary_counts[(label,key)]+=1
    if prop2(t):p2+=1;assert label=='F'
lattice=dict(total_points=total,feasible_points=feasible,excluded_k_gt_B=invalid,
             joint_only=sum(lc.values()),by_case=dict(lc),prop2=p2,
             points_losing_unique_joint_under_one_changed_tie={str(k):v for k,v in boundary_counts.items()},mismatches=0)
print('lattice',lattice,flush=True)

named={
'F':(10,6,2,3,5,Q(1,2),4),
'T_note':(10,6,2,3,8,Q(1,2),3),
'D_note':(10,6,2,3,9,Q(1,2),0),
'T_strict':(10,6,2,3,8,Q(1,2),Q(13,4)),
'D_strict':(10,6,2,3,Q(19,2),1,0),
'F_without_agency_condition':(10,6,2,3,5,2,Q(9,2)),
'unaffordable_nominal_alternative':(10,6,2,3,5,Q(1,2),0),
'negative_harmful_ceiling':(1,1,1,3,2,1,0),
'zero_b':(10,6,0,3,8,Q(1,2),3),
'zero_k_T':(10,6,2,3,6,0,3),
'O_below_k_D':(10,6,2,3,Q(19,2),1,Q(1,4)),
'T_resource_loss':(10,6,2,3,8,Q(5,4),Q(7,2)),
}
# First exact counterexample to robustness under each changed tie, per case.
found={}
for B,k,O in product(range(16,45),range(0,17),range(0,33)):
    if k>B:continue
    t=(40,24,8,12,B,k,O)
    label=primitive_case(t)
    if not label:continue
    for tie,kwargs in [('build_tie',dict(build_tie=True)),('harm_tie',dict(harmless_tie=False)),('zero_profit_decline',dict(trade_zero=False))]:
        key=label+'_'+tie
        if key not in found and not target(t,**kwargs):
            unscaled=tuple(Q(x,4) for x in t)
            found[key]=dict(parameters=unscaled,baseline=outcomes(unscaled),changed=outcomes(unscaled,**kwargs))
# Missing equality cases not hit at worked V,c,b,h are not inferred impossible.
report=dict(seed23=sample,seed7_lemma_states=raw_lemma,lattice=lattice,
            named={name:dict(parameters=t,case=primitive_case(t),outcomes=outcomes(t)) for name,t in named.items()},tie_counterexamples=found)
(HERE/'audit_results.json').write_text(json.dumps(report,indent=2,default=encode)+'\n')
print('tie witnesses',json.dumps({k:v['parameters'] for k,v in found.items()},default=encode),flush=True)
