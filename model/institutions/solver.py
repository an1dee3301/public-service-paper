"""institutions independent reconstruction from region §§5.1–5.7, no earlier code imported.
Run: python3 solver.py. All outputs remain beside this file.
Finite exact checks supplement the derivations in the accompanying derivations.
Continuous q uses all vertices of the piecewise-linear profit function.
"""
from fractions import Fraction as Q
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
import json

@dataclass(frozen=True)
class P:
    V: Q=Q(10); c: Q=Q(6); b: Q=Q(2); h: Q=Q(3)
    B: Q=Q(5); k: Q=Q(1,2); O: Q=Q(4); r: Q=Q(1)
    @property
    def C(self): return self.c-self.b
    @property
    def H(self): return self.V-self.h-self.C
    @property
    def t(self): return self.V-self.B+self.k-self.O

def region(p):
    return (p.C < p.B-p.k < p.B < p.c and p.V-p.h > p.B
            and p.r <= p.B-p.k and p.H < p.O < p.V-p.B+p.k)

def continuation(p,x,d,mode='base',lam=Q(0),beta=Q(1),D=Q(0),interest=Q(0),
                 forced_q=None,external=False):
    K=Q(0) if external else p.k*x
    R=p.B-K
    if mode=='reserve': R=p.B-p.k
    if R<0: return None
    O=max(Q(0),p.O) if x and p.r<=R else Q(0)
    fallback=dict(x=x,q=Q(0),p=None,A=O-K,W=O-K,profit=Q(0),G=O-K,
                  service='fallback' if O>0 else 'shutdown')
    z=Q(1) if d else lam
    qs={Q(0),Q(1)} if forced_q is None else {Q(forced_q)}
    if mode=='continuous':
        # cash/acceptance intersection; endpoints sufficient on each affine piece
        if z*p.h: qs.add((p.V-O-R)/(z*p.h))
    choices=[]
    for q in qs:
        if not 0<=q<=1: continue
        cost=p.c-p.b*q
        willingness=p.V-O-z*p.h*q
        if mode=='credit':
            ceiling=min(R+D, willingness if willingness<=R else (willingness+interest*R)/(1+interest))
        elif mode=='nash':
            if willingness<cost or R<cost: continue
            ceiling=min(R,cost+beta*(willingness-cost))
        elif mode=='competition':
            if willingness<cost or R<cost: continue
            ceiling=cost
        else: ceiling=min(R,willingness)
        if ceiling<0 or ceiling<cost: continue
        repayment=interest*max(Q(0),ceiling-R) if mode=='credit' else Q(0)
        A=p.V-ceiling-K-repayment
        W=A-p.h*q
        profit=ceiling-cost
        choices.append(dict(x=x,q=q,p=ceiling,A=A,W=W,profit=profit,G=W+profit,service='incumbent'))
    if not choices: return fallback
    if mode=='competition':
        # Buyer chooses its best cost-priced offer, then harmless on ties.
        return max(choices,key=lambda y:(y['A']-z*p.h*y['q'],-y['q']))
    return max(choices,key=lambda y:(y['profit'],-y['q']))

def solve(p,f,d,**kw):
    ys=[continuation(p,x,d,**kw) for x in (0,1)]
    ys=[y for y in ys if y is not None]
    lam=kw.get('lam',Q(0))
    return max(ys,key=lambda y:(y['W'] if f else y['A']-lam*p.h*y['q'],-y['x']))

def pattern(p,**kw):
    ys=[solve(p,f,d,**kw) for f,d in ((0,0),(1,0),(0,1),(1,1))]
    return all(y['q']>0 for y in ys[:3]) and ys[3]['q']==0

checks={}; fails=[]
def check(name, actual, expected, p=None, detail=None):
    checks[name]=checks.get(name,0)+1
    if actual!=expected:
        fails.append(dict(check=name,actual=actual,expected=expected,parameters=p.__dict__ if p else None,detail=detail))

points=[]
for c,b,gap_fraction,k_fraction,h,slack,ofrac in product(
    map(Q,[4,6]),map(Q,[1,2]),[Q(1,3),Q(2,3)],
    [Q(1,4),Q(1,2),Q(3,4)],map(Q,[1,3,5]),map(Q,[1,3]),
    [Q(1,8),Q(1,4),Q(1,2),Q(3,4),Q(7,8)]):
    C=c-b; B=C+gap_fraction*b; k=k_fraction*(B-C); V=B+h+slack
    H=V-h-C; upper=V-B+k
    O=H+ofrac*(upper-H)
    p=P(V,c,b,h,B,k,O,Q(1,4))
    if region(p): points.append(p)
base=P(); points.append(base)

for p in points:
    check('Proposition2',pattern(p),True,p)
    for x,d in product((0,1),repeat=2):
        y=continuation(p,x,d)
        check('resource_identity',y['W']+y['profit'],y['G'],p)
        # Independently enumerate feasible prices below/at/above thresholds.
        R=p.B-p.k*x; O=p.O*x
        profits=[]
        for q in (Q(0),Q(1)):
            threshold=p.V-O-d*p.h*q
            for price in {Q(0),R,threshold,min(R,threshold),min(R,threshold)-Q(1,100),min(R,threshold)+Q(1,100)}:
                if 0<=price<=R and p.V-price-d*p.h*q>=O:
                    profits.append(price-p.c+p.b*q)
        check('Proposition1_price_deviations',y['profit'],max([Q(0)]+profits),p)
    # reserve equation independently compared with solver
    check('separate_accounts',pattern(p,mode='reserve'),p.O>max(p.H,p.V-p.h-p.B+2*p.k),p)
    for lam in [Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1),min(Q(1),p.t/p.h)]:
        check('Table2_row1',pattern(p,lam=lam),lam*p.h<=p.t,p)
    for beta in [Q(0),Q(1,12),Q(1,4),Q(1,2),Q(1)]:
        check('Table2_row2',pattern(p,mode='nash',beta=beta),p.O-p.H-p.k+min(beta*p.H,p.B-p.C)>0,p)
    threshold=max(p.H,p.V-(p.B-p.k)-p.h*(p.c-(p.B-p.k))/p.b)
    check('Table2_row3',pattern(p,mode='continuous'),p.O>threshold,p)
    for df,i in product([Q(0),Q(1,4),Q(3,4)],[Q(0),Q(1,2),Q(2)]):
        D=df*(p.c-p.B)
        check('Table2_row4',pattern(p,mode='credit',D=D,interest=i),min((1+i)*D,p.V-p.h-p.B)<=p.t,p)
    for rho in [Q(0),Q(1,2),Q(4,5),Q(9,10),Q(1)]:
        Oe=rho*(p.O+p.r)-p.r
        check('Table2_row5',pattern(replace(p,O=Oe)),Oe>p.H,p)
    check('Table2_row6',pattern(p,mode='competition'),p.O>p.H+p.k,p)
    for theta,v in product([Q(0),Q(1,4),Q(1,2),Q(3,4)],[Q(0),Q(1,8)]):
        transformed=replace(p,b=(1-theta)*p.b,h=(1-theta)*p.h,B=p.B-v)
        if region(transformed):
            check('Table2_row7_sufficient_region',pattern(transformed),True,p)
    # Mandatory clause; adoption cost common across build states.
    clause=solve(p,0,0,forced_q=0)
    check('Table1_clause_region',clause['W'],p.O-p.k,p)
    check('clause_voluntary_nonadoption',clause['A']<p.V-p.B,True,p)
    for v in [Q(0),p.B/2,p.B]:
        cp=replace(p,B=p.B-v)
        value=solve(cp,0,0,forced_q=0)['A']-v
        predicted=p.O-p.k-v if p.k+v+p.r<=p.B else -v
        check('clause_adoption_cost',value,predicted,p)

worked={}
for f,d in ((0,0),(1,0),(0,1),(1,1)):
    worked[f'rights_{f}{d}']=solve(base,f,d)
worked['Table1_joint']=solve(base,1,1)
worked['Table1_topup_resident_borne']=solve(replace(base,B=base.c),0,0,forced_q=0)
worked['Table1_clause']=solve(base,0,0,forced_q=0)
worked['Table1_outside_fallback']=continuation(base,1,1,external=True)
worked['Table1_aligned']=solve(base,1,1)
worked['Table1_refusal_only']=solve(base,0,1)
for key,target in zip(['Table1_joint','Table1_topup_resident_borne','Table1_clause','Table1_outside_fallback','Table1_aligned','Table1_refusal_only'],[Q(7,2),Q(4),Q(7,2),Q(4),Q(7,2),Q(2)]):
    check(key,worked[key]['W'],target,base)
check('Table1_transfer_strict_threshold',base.O>base.V-base.B+base.k-base.h/2,False,base)
for rho in [Q(4,5),Q(17,20),Q(9,10),Q(19,20),Q(1)]:
    p=replace(base,O=rho*5-1)
    check('noncomposition_competition',pattern(p,mode='competition'),rho>Q(9,10),p)
    check('noncomposition_continuous',pattern(p,mode='continuous'),rho>Q(17,20),p)
    check('noncomposition_nash',pattern(p,mode='nash',beta=Q(1,12)),rho>Q(17,20),p)

# Extend Table 1 benchmark comparisons to all sampled region vectors.
for p in points:
    check('Table1_topup_grid',solve(replace(p,B=p.c),0,0,forced_q=0)['W'],max(p.V-p.c,p.O-p.k),p)
    check('Table1_external_grid',continuation(p,1,1,external=True)['W'],p.O,p)
    check('Table1_aligned_grid',solve(p,1,1)['W'],p.O-p.k,p)
    check('Table1_refusal_grid',solve(p,0,1)['W'],p.V-p.B-p.h,p)
    loss=(p.V-p.B)-(p.O-p.k)
    gain=(p.O-p.k)-(p.V-p.B-p.h)
    check('Table1_transfer_grid',loss<gain,p.O>p.V-p.B+p.k-p.h/2,p)

# Integral of affine lines, exact antiderivative, no floating quadrature.
def integral(a,b,lo,hi): return a*(hi*hi-lo*lo)/2+b*(hi-lo)
areas={
    'baseline':integral(Q(1),Q(2),Q(0),Q(1)),
    'reserve':integral(Q(1),Q(2),Q(0),Q(1,2))+integral(Q(-1),Q(3),Q(1,2),Q(1)),
    'competition':integral(Q(0),Q(2),Q(0),Q(1))}
for key,target in zip(areas,[Q(5,2),Q(9,4),Q(2)]): check('Figure1_'+key,areas[key],target)
# Direct witness to the more useful investment threshold.
p=replace(base,O=Q(13,4))
worked['crowding_out_baseline']=solve(p,1,1)
worked['crowding_out_competition']=solve(p,1,1,mode='competition')
worked['continuous_worked']=solve(base,1,1,mode='continuous')
worked['reserve_worked']=solve(base,1,1,mode='reserve')
worked['nash_beta_zero']=solve(base,1,1,mode='nash',beta=Q(0))
# Interior counterexample to using row 7 as an iff rather than sufficient condition:
worked['full_clause']=solve(base,0,0,forced_q=0)
output=dict(region_points=len(points),checks=checks,total_checks=sum(checks.values()),failures=fails,worked=worked,figure_areas=areas,
 assumptions=['Risk neutral expected utility for row 5','Continuous q scales cost saving and harm linearly; smallest q on profit ties',
 'Minimal borrowing max(0,p-R), both objectives pay interest after service','Nash price bargaining conditional on supplier-chosen q; inherited cash cap',
 'Top-up row charges residents all 6; donor grant is a distinct convention'])
Path(__file__).with_name('RESULTS.json').write_text(json.dumps(output,indent=2,default=str)+'\n')
print(json.dumps(dict(region_points=len(points),total_checks=sum(checks.values()),counts=checks,failures=len(fails)),indent=2))
if fails: print(json.dumps(fails[:5],indent=2,default=str))
