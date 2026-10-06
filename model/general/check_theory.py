#!/usr/bin/env python3
"""general independent rational verification. Writes only beside this file.
Grid agreement corroborates proofs; it does not prove them or establish novelty.
"""
from fractions import Fraction as Q
from dataclasses import dataclass, replace, asdict
from itertools import product
from pathlib import Path
from collections import Counter
import json, hashlib

ROOT=Path(__file__).resolve().parent
@dataclass(frozen=True)
class P:
    V: Q=Q(10); c: Q=Q(6); b: Q=Q(2); h: Q=Q(3)
    B: Q=Q(5); k: Q=Q(1,2); F: Q=Q(0)
    a0: Q=Q(0); r0: Q=Q(0); a1: Q=Q(5); r1: Q=Q(1)
@dataclass(frozen=True)
class Outcome:
    x: int; mode: str; q: Q; p: object; A: Q; W: Q; pi: Q; G: Q; O: Q; alt: int

def outside(z,x):
    R=z.B-z.F-z.k*x
    opts=[(Q(0),Q(0),-1)]
    if z.r0<=R: opts.append((z.a0-z.r0,z.r0,0))
    if x and z.r1<=R: opts.append((z.a1-z.r1,z.r1,1))
    return max(opts,key=lambda v:(v[0],-v[1],-v[2]))

def out(z,x,q=None,p=None):
    O,r,j=outside(z,x); K=z.F+z.k*x
    if q is None: return Outcome(x,'fallback',Q(0),None,O-K,O-K,Q(0),O-K,O,j)
    A=z.V-p-K; W=A-z.h*q; pi=p-z.c+z.b*q
    return Outcome(x,'trade',Q(q),p,A,W,pi,W+pi,O,j)

def solve_cont(z,x,d=Q(0),cap=None,continuous=False):
    """Offer optimization over exact affine vertices; no classification formula."""
    O,_,_=outside(z,x); R=z.B-z.F-z.k*x
    if cap is not None: R=min(R,cap)
    qs={Q(0),Q(1)}
    if continuous and d*z.h:
        kink=(z.V-O-R)/(d*z.h)
        if 0<=kink<=1: qs.add(kink)
    offers=[]
    for q in qs:
        ceiling=min(R,z.V-O-d*z.h*q)
        profit=ceiling-z.c+z.b*q
        if ceiling>=0 and profit>=0: offers.append((profit,-q,ceiling))
    if not offers: return out(z,x)
    profit,nq,p=max(offers)
    return out(z,x,-nq,p)

def cell_cont(z,x,d):
    """Theorem 1 disjoint algebraic cells, implemented separately."""
    O,_,_=outside(z,x); R=z.B-z.F-z.k*x; m=z.V-O
    u=min(R,m); v=min(R,m-d*z.h); C=z.c-z.b
    good=u>=z.c
    bad=v>=C
    if good and (not bad or z.b<=u-v): return out(z,x,0,u)
    if bad and (not good or z.b>u-v): return out(z,x,1,v)
    return out(z,x)

def eq(z,f,d,cont=solve_cont,**kw):
    a=cont(z,0,d,**kw)
    if z.F+z.k>z.B: return a
    b=cont(z,1,d,**kw)
    objective=lambda v:v.A-f*z.h*v.q
    return b if objective(b)>objective(a) else a

def full(z,cont=solve_cont,**kw):
    return [eq(z,f,d,cont,**kw) for f,d in ((0,0),(0,1),(1,0),(1,1))]

def mask(z,os): return ''.join('1' if z.h*o.q==0 else '0' for o in os)
def region(z):
    O,_,_=outside(z,1); R=z.B-z.k; C=z.c-z.b
    return z.F==0 and outside(z,0)[0]==0 and C<R<z.B<z.c and z.V-z.h>z.B and z.r1<=R and z.V-z.h-C<O<z.V-R

def enc(o):
    if hasattr(o,'__dataclass_fields__'): return {k:enc(v) for k,v in asdict(o).items()}
    if isinstance(o,Q): return str(o)
    if isinstance(o,dict): return {str(k):enc(v) for k,v in o.items()}
    if isinstance(o,(list,tuple)): return [enc(v) for v in o]
    return o

COUNTS=Counter(); WIT={}; MASKS=Counter()
def check_global(z):
    a=full(z); b=full(z,cell_cont)
    assert a==b,(z,a,b)
    COUNTS['global_parameter_vectors']+=1
    COUNTS['global_allocation_comparisons']+=4
    assert a[3].W>=max(o.W for o in a)
    if z.h*a[0].q==0: assert z.h*a[3].q==0
    for d in (0,1):
        for x in (0,1):
            if z.F+z.k*x>z.B: continue
            o=solve_cont(z,x,d)
            assert o.G==o.W+o.pi
            if o.mode=='trade':
                assert o.p<=z.B-z.F-z.k*x and o.pi>=0
                assert z.V-o.p-d*z.h*o.q>=o.O
        af=eq(z,0,d); rf=eq(z,1,d)
        assert z.h*rf.q<=z.h*af.q
    m=mask(z,a); MASKS[m]+=1
    WIT.setdefault('mask_'+m,{'parameters':z,'outcomes':a})

def global_grid():
    # Factorial structural grid: varies cash, costs, harm, capital, fixed cost,
    # value and technology affordability, including zero costs and equality.
    for V,c,b,h,B,k,F,technology in product(
        (Q(3),Q(6)),(Q(0),Q(2),Q(4)),(Q(0),Q(1),Q(2)),
        (Q(0),Q(1),Q(3)),(Q(0),Q(2),Q(4),Q(6)),
        (Q(0),Q(1),Q(3)),(Q(0),Q(1)),range(6)):
        if b>c or F>B: continue
        tech=((0,0,0,0),(0,0,4,1),(4,1,6,2),(5,3,7,4),(3,0,4,0),(1,2,3,5))[technology]
        check_global(P(V,c,b,h,B,k,F,*map(Q,tech)))
    # Manuscript Grid II, including its boundary and out-of-region points.
    for B,O in product((Q(i,8) for i in range(24,65)),(Q(i,8) for i in range(73))):
        check_global(replace(P(),B=B,a1=O+1))
    for z in (P(), replace(P(),V=Q(-1),a0=Q(-2),a1=Q(-3)), replace(P(),k=Q(3,2),a0=Q(3),a1=Q(4),r1=Q(0))):
        check_global(z)
    WIT['refusal_can_undo_protection']={'parameters':replace(P(),k=Q(3,2),a0=Q(3),a1=Q(4),r1=Q(0)), 'outcomes':full(replace(P(),k=Q(3,2),a0=Q(3),a1=Q(4),r1=Q(0)))}

def extended_global(z):
    for f,g in product((Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)),repeat=2):
        assert eq(z,f,g)==eq(z,f,g,cell_cont)
        COUNTS['global_weighted_comparisons']+=1
    if z.F+z.k>z.B: return
    for f,g0,g1 in product((Q(0),Q(1,2),Q(1)),repeat=3):
        oracle=[solve_cont(z,0,g0),solve_cont(z,1,g1)]
        formula=[cell_cont(z,0,g0),cell_cont(z,1,g1)]
        pick=lambda a:a[1] if a[1].A-f*z.h*a[1].q>a[0].A-f*z.h*a[0].q else a[0]
        assert pick(oracle)==pick(formula)
        COUNTS['global_contingent_comparisons']+=1

def extra_global():
    import random
    rng=random.Random(3406)
    for _ in range(12000):
        c=Q(rng.randrange(0,33),4)
        z=P(V=Q(rng.randrange(0,61),4),c=c,b=Q(rng.randrange(0,int(4*c)+1),4),
            h=Q(rng.randrange(0,41),4),B=Q(rng.randrange(0,41),4),
            k=Q(rng.randrange(0,25),4),F=Q(rng.randrange(0,9),4),
            a0=Q(rng.randrange(0,41),4),r0=Q(rng.randrange(0,25),4),
            a1=Q(rng.randrange(0,49),4),r1=Q(rng.randrange(0,25),4))
        if z.F<=z.B:
            check_global(z)
            if _%31==0: extended_global(z)
    z=replace(P(),k=Q(3,2),a0=Q(3),a1=Q(7),r1=Q(0))
    check_global(z)
    WIT['refusal_can_harm_baseline']={'parameters':z,'outcomes':full(z)}
    assert set(MASKS)<=set(('0000','0001','0010','0011','0101','0111','1011','1111'))

def liquidity_grid():
    for V,c,b,h,B,k,O in product((Q(8),Q(10)),(Q(4),Q(6)),(Q(1),Q(2),Q(3)),
            (Q(1),Q(3),Q(5)),(Q(3),Q(4),Q(5)),(Q(0),Q(1,2),Q(1),Q(2),Q(3)),
            (Q(i,2) for i in range(19))):
        C=c-b; R=B-k
        if not (C<=B<c and V-h>B and R>=0): continue
        z=P(V,c,b,h,B,k,a1=O,r1=Q(0))
        os=full(z)
        predicted=''.join('1' if ((R<C or O>V-d*h-C) and O>V-B-f*h+k) else '0'
            for f,d in ((0,0),(0,1),(1,0),(1,1)))
        assert mask(z,os)==predicted,(z,os,predicted)
        COUNTS['liquidity_vectors']+=1
        # Piecewise cell derivative checks use an exact small increment and
        # only compare unchanged active action/ceiling branches (below).

def region_points():
    for V,c,b,h,B,k,O in product((Q(8),Q(10)),(Q(4),Q(6)),(Q(1),Q(2),Q(3)),
            (Q(1),Q(3),Q(5)),(Q(3),Q(4),Q(5)),(Q(1,4),Q(1,2),Q(3,4)),
            (Q(i,4) for i in range(1,28))):
        z=P(V,c,b,h,B,k,a1=O,r1=Q(0))
        if region(z): yield z

def institutions_grid():
    for z in region_points():
        O=outside(z,1)[0]; C=z.c-z.b; R=z.B-z.k
        t=z.V-z.B+z.k-O; s=R-C
        fi=t/z.h; ga=(t+s)/z.h
        fs=sorted({Q(0),fi, (fi+1)/2,Q(1)})
        gs=sorted({Q(0),fi,ga,(ga+1)/2,Q(1)})
        for f,g in product(fs,gs):
            e=eq(z,f,g)
            assert (e.q==0)==(f>fi and g>ga)
            if g*z.h<=t: assert e.x==0
            elif g*z.h<=t+s: assert e.x==1 and e.q==1
            else: assert e.x==int(f*z.h>t)
            COUNTS['weighted_institutions']+=1
        for y,u in product((Q(0),Q(1,4),Q(1,2),Q(1)),repeat=2):
            aa0=solve_cont(z,0,0); rr0=solve_cont(z,0,1)
            aa1=solve_cont(z,1,0); rr1=solve_cont(z,1,1)
            A0=(1-u)*aa0.A+u*rr0.A; W0=(1-u)*aa0.W+u*rr0.W
            A1=(1-u)*aa1.A+u*rr1.A; W1=(1-u)*aa1.W+u*rr1.W
            xa=int(A1>A0); xr=int(W1>W0)
            expected_q=(1-y)*((1-xa)+xa*(1-u))+y*((1-xr)+xr*(1-u))
            assert expected_q==1-y*u
            COUNTS['public_lotteries']+=1
        for f,d0,d1 in product((0,1),repeat=3):
            e0=solve_cont(z,0,d0); e1=solve_cont(z,1,d1)
            e=e1 if e1.A-f*z.h*e1.q>e0.A-f*z.h*e0.q else e0
            assert (e.q==0)==(f==1 and d1==1)
            COUNTS['state_contingent_arrangements']+=1
        for T in {Q(0),t,(t+(z.h-t))/2,z.h-t,t+Q(1,100)}:
            e0=solve_cont(z,0,1); e1=solve_cont(z,1,1)
            agency_build=e1.A+T>e0.A
            residents_accept=e1.W-T>=e0.W
            assert agency_build==(T>t)
            assert residents_accept==(T<=z.h-t)
            COUNTS['transfer_checks']+=1

def price_grid():
    for z in region_points():
        O=outside(z,1)[0]; C=z.c-z.b; H=z.V-z.h-C
        threshold=z.V-z.h-O+z.k
        caps={C,z.B,(C+z.B)/2}
        if C<=threshold<=z.B:
            caps|={threshold,(C+threshold)/2,(threshold+z.B)/2}
        prev=None
        for cap in sorted(caps):
            os=full(z,cap=cap); rr=os[3]
            assert rr.x==int(cap>threshold) and (rr.q==0)==(cap>threshold)
            assert rr.W==max(z.V-z.h-cap,O-z.k)
            assert rr.G==(O-z.k if cap>threshold else H)
            assert all(o.q==1 for o in os[:3])
            if prev:
                assert prev.W>=rr.W and prev.G>=rr.G # lower cap weakly improves both
            prev=rr
            COUNTS['price_cap_cases']+=1
        assert (eq(z,1,1,cap=C).x==1)==(O>H+z.k)
    z=replace(P(),a1=Q(17,4)) # O=13/4
    WIT['price_transition']={'parameters':z,'threshold':Q(17,4),
        'monopoly':full(z),'cost_price':full(z,cap=Q(4)),
        'threshold_outcomes':full(z,cap=Q(17,4))}

def private_cost_grid():
    # Two support points; exact integration and explicit ex-ante investment.
    for b,h,B,k,O,Clo,Chi,prob in product((Q(2),Q(3)),(Q(2),Q(3),Q(4)),
            (Q(4),Q(5)),(Q(1,2),Q(1)),(Q(i,2) for i in range(1,14)),
            (Q(3,2),Q(5,2),Q(7,2)),(Q(7,2),Q(4),Q(9,2)),
            (Q(1,4),Q(1,2),Q(3,4))):
        V=Q(10); R=B-k
        if not (0<=Clo<=Chi<=R and Clo+b>B and V-h>B and V-h-R<O<V-R): continue
        pars=[P(V,C+b,b,h,B,k,a1=O,r1=Q(0)) for C in (Clo,Chi)]
        weights=(prob,1-prob); t=V-B+k-O; cut=V-h-O
        F=sum(w for C,w in zip((Clo,Chi),weights) if C<=cut)
        for f,d in product((Q(0),Q(1,4),Q(1,2),Q(3,4),Q(1)),(0,1)):
            states=[[solve_cont(z,x,d) for z in pars] for x in (0,1)]
            us=[sum(w*(o.A-f*h*o.q) for w,o in zip(weights,ss)) for ss in states]
            x=int(us[1]>us[0]); q=sum(w*o.q for w,o in zip(weights,states[x]))
            predx=0 if d==0 else int(h*(f+(1-f)*F)>t)
            assert x==predx
            assert q==(F if predx else 1)
            if d==1:
                expected={name:sum(w*getattr(o,name) for w,o in zip(weights,states[x]))
                          for name in ('A','W','pi','G')}
                rent=sum(w*(cut-C) for C,w in zip((Clo,Chi),weights) if C<=cut)
                meanC=prob*Clo+(1-prob)*Chi
                formula=({'A':O-k+h*F,'W':O-k,'pi':rent,'G':O-k+rent} if x else
                         {'A':V-B,'W':V-B-h,'pi':B-meanC,'G':V-h-meanC})
                assert expected==formula
            COUNTS['private_cost_allocation_checks']+=1
        for z in pars:
            assert solve_cont(z,1,1).W==O-k
    lo=replace(P(),c=Q(11,2),b=Q(3)); hi=replace(lo,c=Q(15,2))
    WIT['private_cost_mean_failure']={'low':lo,'high':hi,'each_probability':Q(1,2),
        'resident_built_low':solve_cont(lo,1,1),'resident_built_high':solve_cont(hi,1,1),
        'mean_complete_information':full(replace(lo,c=Q(13,2)))}

def derivative_grid():
    # At fixed O and actions, differentiate price and all payoffs exactly.
    eps=Q(1,1000)
    for B,h,O,k in product((Q(3),Q(5),Q(8),Q(12)),(Q(1),Q(3),Q(6)),
            (Q(i,2) for i in range(17)),(Q(0),Q(1,2),Q(2))):
        z=replace(P(),B=B,h=h,a1=O+1,k=k)
        for x,d in product((0,1),repeat=2):
            a=solve_cont(z,x,d)
            if a.mode!='trade': continue
            R=z.B-z.k*x; m=z.V-a.O-d*z.h*a.q
            if R==m: continue
            cash=R<m
            for name in ('B','k','h','b','a1'):
                zz=replace(z,**{name:getattr(z,name)+eps})
                if zz.b>zz.c or zz.F+zz.k*x>zz.B: continue
                o=solve_cont(zz,x,d)
                if o.mode!=a.mode or o.q!=a.q or outside(zz,x)[2]!=outside(z,x)[2]: continue
                RR=zz.B-zz.k*x; mm=zz.V-o.O-d*zz.h*o.q
                if RR==mm or (RR<mm)!=cash: continue
                Op=(o.O-a.O)/eps
                pp={'B':int(cash),'k':-x*int(cash),'h':-d*a.q*int(not cash),
                    'b':Q(0),'a1':-Op*int(not cash)}[name]
                kp=x if name=='k' else 0
                hh=a.q if name=='h' else 0
                bb=a.q if name=='b' else 0
                assert (o.p-a.p)/eps==pp
                assert (o.W-a.W)/eps==-pp-kp-hh
                assert (o.pi-a.pi)/eps==pp+bb
                assert (o.G-a.G)/eps==bb-kp-hh
                COUNTS['fixed_cell_derivatives']+=1
                COUNTS['derivatives_cash' if cash else 'derivatives_participation']+=1

def targeted_boundaries():
    # Positive-profit versions of the two nonmonotone-protection witnesses.
    for O,expected in ((Q(4),'0010'),(Q(7),'1011')):
        z=replace(P(),k=Q(3,2),a0=Q(11,4),a1=O,r1=Q(0))
        os=full(z)
        assert mask(z,os)==expected
        for o in os:
            if o.mode=='trade': assert o.pi>0
        WIT['strict_'+expected]={'parameters':z,'outcomes':os}
        COUNTS['targeted_boundary_cases']+=1
    for k,expected in ((Q(1,2),'0001'),(Q(3,2),'0011')):
        z=replace(P(),k=k)
        assert mask(z,full(z))==expected
        COUNTS['targeted_boundary_cases']+=1
    for k,protect in ((Q(1,2),True),(Q(3,2),False)):
        z=replace(P(),k=k,a1=Q(17,4))
        assert (eq(z,1,1).q==0)==protect
        COUNTS['targeted_boundary_cases']+=1
    for B,protect in ((Q(3),True),(Q(5),False)):
        z=replace(P(),B=B,a1=Q(1))
        assert all((o.q==0)==protect for o in full(z))
        COUNTS['targeted_boundary_cases']+=1
    # T4 monotonicity in capital on a fixed-affordable-O, no-legacy slice.
    for h,O in product((Q(1),Q(2),Q(3),Q(4)),(Q(i,4) for i in range(33))):
        last=True
        for k in (Q(i,8) for i in range(41)):
            z=replace(P(),h=h,k=k,a1=O,r1=Q(0))
            protected=eq(z,1,1).q==0
            assert not protected or last
            last=protected
            COUNTS['capital_monotonicity_cases']+=1
    for z in region_points():
        O=outside(z,1)[0]; t=z.V-z.B+z.k-O; s=z.B-z.k-(z.c-z.b)
        fi=t/z.h; ga=(t+s)/z.h
        for alpha,beta in product((Q(1),Q(2)),repeat=2):
            infimum=alpha*fi+beta*ga
            for n in (Q(2),Q(4),Q(8)):
                f=fi+(1-fi)/n; g=ga+(1-ga)/n
                assert eq(z,f,g).q==0
                assert infimum<alpha*f+beta*g<alpha+beta
                assert (alpha*f+beta*g-infimum)==(alpha*(1-fi)+beta*(1-ga))/n
                COUNTS['conditional_cost_frontier_cases']+=1

if __name__=='__main__':
    global_grid()
    extra_global()
    liquidity_grid()
    institutions_grid()
    price_grid()
    private_cost_grid()
    derivative_grid()
    targeted_boundaries()
    (ROOT/'CHECKS.json').write_text(json.dumps(enc({'counts':COUNTS,'masks':MASKS,'witnesses':WIT}),indent=2)+'\n')
    print(json.dumps(enc({'counts':COUNTS,'masks':MASKS}),indent=2))
