"""independent independent finite-action backward induction. Written before lead code read.
All money/value inputs may be Fraction or integer common-denomination units.
No floats used. Run this file for boundary and rational-grid checks.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent

def continuation(V,c,b,h,R,O,d, *, harmless_tie=True, trade_zero=True):
    # Enumerate condition-specific accepted endpoint offers, then abstention.
    offers=[]
    for q in (0,1):
        cap=min(R,V-O-d*h*q)
        if cap < 0:
            continue
        p=cap
        profit=p-c+b*q
        if profit<0 or (profit==0 and not trade_zero):
            continue
        offers.append((profit, -q if harmless_tie else q, q,p))
    if not offers:
        return dict(kind='f',q=0,p=None,A=O,W=O,profit=0)
    profit,_,q,p=max(offers)
    return dict(kind='H' if q else 'N',q=q,p=p,A=V-p,W=V-p-h*q,profit=profit)

def equilibrium(t,i,d, *, build_tie=False, harmless_tie=True, trade_zero=True):
    V,c,b,h,B,k,O=t
    options=[]
    for x in (0,1):
        if k*x>B:
            continue
        z=continuation(V,c,b,h,B-k*x,O*x,d,
                       harmless_tie=harmless_tie,trade_zero=trade_zero)
        z=dict(z,x=x,A=z['A']-k*x,W=z['W']-k*x)
        options.append(z)
    key='W' if i else 'A'
    return max(options,key=lambda z:(z[key],z['x'] if build_tie else -z['x']))

def outcomes(t,**ties):
    return [equilibrium(t,i,d,**ties) for i,d in ((0,0),(1,0),(0,1),(1,1))]

def target(t,**ties):
    z=outcomes(t,**ties)
    return all(a['q']==1 for a in z[:3]) and z[3]['q']==0

def primitive_case(t):
    V,c,b,h,B,k,O=t
    if not (c>=b>0 and h>=0 and B>=k>=0 and O>=0):
        return None
    C=c-b
    n0=min(B,V); m0=min(B,V-h)
    n1=min(B-k,V-O); m1=min(B-k,V-O-h)
    H0=m0>=C and n0-m0<b
    if H0 and C<=n1<c and m1<C and V-m0-h<O-k<=V-m0:
        return 'F'
    if H0 and n1>=c and n1-m1>=b and m0<=n1+k<m0+h:
        return 'T'
    if n0>=c and n0-m0>=b and m1>=C and n1-m1<b and n0-h<=m1+k<n0:
        return 'D'
    return None

def slack_cont(V,c,b,h,R,O,d):
    P=min(R,V-O)
    s=min(h,max(0,R-(V-O-h))) if d else 0
    if s>=b:
        return ('N',P) if P>=c else ('f',None)
    return ('H',P-s) if P-s>=c-b else ('f',None)

def prop2(t):
    V,c,b,h,B,k,O=t; C=c-b
    return C<B-k<B<c and V-h>B and V-h-C<O<V-(B-k)

def encode(x):
    if isinstance(x,Q): return str(x)
    raise TypeError(type(x))

def run():
    # Deliberately includes b=0, k=0, zero cost/profit/harm, V<h, O<k,
    # O>V (negative ceilings), budget endpoints and infeasible builds.
    count=0; eligible=0; b0=0; counts=dict(F=0,T=0,D=0)
    for V,c,b,h,B,k,O in product(range(5),range(4),range(4),range(5),range(5),range(4),range(6)):
        if b>c: continue
        t=(V,c,b,h,B,k,O); count+=1
        actual=target(t)
        if b==0:
            b0+=1
            assert not actual, t
        if k<=B and b>0:
            eligible+=1
            label=primitive_case(t)
            assert bool(label)==actual,(t,label,outcomes(t))
            if label: counts[label]+=1
        elif k>B:
            assert not actual,t
    # Continuation lemma, integer lattice including nonpositive willingness to pay.
    lc=0
    for V,c,b,h,R,O,d in product(range(6),range(5),range(5),range(6),range(6),range(8),(0,1)):
        if b>c: continue
        z=continuation(V,c,b,h,R,O,d)
        assert (z['kind'],z['p'])==slack_cont(V,c,b,h,R,O,d),(V,c,b,h,R,O,d,z)
        lc+=1
    rational_count=0
    for B,k,O in product([Q(n,2) for n in range(0,25)],
                         [Q(n,3) for n in range(0,10)],
                         [Q(n,4) for n in range(0,25)]):
        t=(Q(10),Q(6),Q(2),Q(3),B,k,O)
        assert target(t)==bool(primitive_case(t)),t
        rational_count+=1
    examples={name:outcomes(tuple(Q(v) for v in t)) for name,t in {
        'F':(10,6,2,3,5,Q(1,2),4),
        'T':(10,6,2,3,8,Q(1,2),3),
        'D':(10,6,2,3,9,Q(1,2),0)}.items()}
    report=dict(parameter_grid=count,eligible_positive_b_feasible_build=eligible,
                zero_b_points=b0,case_counts=counts,lemma_states=lc,
                mixed_denominator_points=rational_count,examples=examples,
                mismatches=0)
    (HERE/'independent_checks.json').write_text(json.dumps(report,indent=2,default=encode)+'\n')
    print(json.dumps(report,indent=2,default=encode))

if __name__=='__main__': run()
