#!/usr/bin/env python3
"""extensions independent Fraction checks. Writes only beside this file; no project imports.
Direct optimization and closed-form continuation are separate implementations.
Run: python3 check_extensions.py
"""
from fractions import Fraction as Q
from itertools import product
from collections import Counter
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
Z=Q(0); ONE=Q(1)
def clip(y,lo=Z,hi=ONE): return max(lo,min(hi,y))
def slack(V,h,R,O,q=ONE):
    return min(h*q,max(Z,R-(V-O-h*q)))
def record(V,c,b,h,K,O,p=None,q=Z):
    if p is None:
        return dict(kind='f',q=Z,p=None,A=O-K,W=O-K,profit=Z,G=O-K)
    A=V-p-K
    return dict(kind='N' if q==0 else 'H',q=q,p=p,A=A,W=A-h*q,
                profit=p-c+b*q,G=V-c+b*q-h*q-K)
def direct(V,c,b,h,R,O,K,d,mode):
    # Independent endpoint/kink optimization or cost-menu selection.
    if mode=='competition':
        bids=[]
        for q in (Z,ONE):
            p=c-b*q
            if p<=R and V-p-d*h*q>=O:
                bids.append((V-p-d*h*q,-q,p,q))
        if not bids: return record(V,c,b,h,K,O)
        _,_,p,q=max(bids)
        return record(V,c,b,h,K,O,p,q)
    qs={Z,ONE}
    if mode=='continuous' and d*h:
        qs.update(q for q in ((V-O-R)/(d*h),(V-O)/(d*h)) if 0<=q<=1)
    bids=[]
    for q in qs:
        p=min(R,V-O-d*h*q)
        profit=p-c+b*q
        if p>=0 and profit>=0:
            bids.append((profit,-q,p,q))
    if not bids: return record(V,c,b,h,K,O)
    _,_,p,q=max(bids)
    return record(V,c,b,h,K,O,p,q)
def formula(V,c,b,h,R,O,K,d,mode):
    P=min(R,V-O)
    s=slack(V,h,R,O) if d else Z
    if mode=='competition':
        # Slack determines cost feasibility; buyer selects the cost menu.
        ok0=P>=c
        ok1=P-s>=c-b
        if ok0 and (not ok1 or d*h>=b): q=Z
        elif ok1: q=ONE
        else: return record(V,c,b,h,K,O)
        return record(V,c,b,h,K,O,c-b*q,q)
    if mode=='continuous':
        if not d or b>h: q=ONE
        else: q=clip((V-O-R)/h) # b<=h, b>0 and h>0
        p=P-(slack(V,h,R,O,q) if d else Z)
        if p<0 or p<c-b*q: return record(V,c,b,h,K,O)
        return record(V,c,b,h,K,O,p,q)
    q=Z if s>=b else ONE
    p=P-(s if q else Z)
    if p<0 or p<c-b*q: return record(V,c,b,h,K,O)
    return record(V,c,b,h,K,O,p,q)
def solve(params,mode='binary',reserve=False):
    V,c,b,h,B,k,F,a0,r0,a1,r1=map(Q,params)
    assert V>=0 and c>=b>0 and h>0 and B>=F>=0 and k>=0
    states={}
    for x in (0,1):
        K=F+k*x
        if K>B: continue
        R=B-F-k if reserve else B-K
        if R<0: continue
        alternatives=[(Z,Z)]
        if r0<=R: alternatives.append((a0-r0,r0))
        if x and r1<=R: alternatives.append((a1-r1,r1))
        O=max(v for v,r in alternatives)
        for d in (0,1):
            got=direct(V,c,b,h,R,O,K,d,mode)
            expected=formula(V,c,b,h,R,O,K,d,mode)
            assert got==expected,(params,mode,reserve,x,d,got,expected)
            assert got['W']+got['profit']==got['G']
            if got['p'] is not None:
                assert 0<=got['p']<=R and V-got['p']-d*h*got['q']>=O
            states[x,d]=dict(got,R=R,O=O,P=min(R,V-O),s=slack(V,h,R,O))
    if (0,0) not in states: return None
    eq={}
    for inv,d in product((0,1),repeat=2):
        metric='W' if inv else 'A'
        x=int((1,d) in states and states[1,d][metric]>states[0,d][metric])
        eq[inv,d]=dict(states[x,d],x=x)
    unique=(eq[1,1]['q']==0 and all(eq[p]['q']>0 for p in ((0,0),(1,0),(0,1))))
    case=None
    DA=all(eq[p]['q']>0 for p in ((0,0),(1,0)))
    if (1,1) in states:
        u,v=states[0,1],states[1,1]
        delta=v['A']-u['A']
        if DA and u['q']>0 and v['q']==0 and -h*u['q']<delta<=0:
            case='F' if v['kind']=='f' else 'T'
        if DA and u['q']==0 and v['q']>0 and 0<delta<=h*v['q']:
            case='D'
    assert unique==(case is not None),(params,mode,reserve,eq,case)
    # Restrictions proved in report, checked over whole family.
    if reserve: assert case!='D',(params,states)
    if mode=='continuous' and (1,1) in states:
        if states[1,1]['O']>=states[0,1]['O']: assert case!='D'
        if case=='T': assert states[1,1]['P']==states[1,1]['R'] and b<=h
    if mode=='competition': assert case!='T',(params,states)
    return dict(case=case,eq=eq,states=states)

def serial(obj):
    if isinstance(obj,Q): return str(obj)
    if isinstance(obj,dict): return {str(k):serial(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)): return [serial(v) for v in obj]
    return obj

def run():
    counts={}; examples={}; witnesses={}
    def check_family(name,rows,mode='binary',reserve=False):
        ct=Counter()
        for row in rows:
            ans=solve(row,mode,reserve)
            if ans is None: ct['infeasible_institution']+=1; continue
            ct['scenarios']+=1
            ct[ans['case'] or 'not_unique']+=1
            if ans['case']:
                witnesses.setdefault(name,{}) .setdefault(ans['case'],serial(dict(parameters=row,result=ans)))
        counts[name]=dict(ct)
    # Boundary-rich Cartesian lattice: actual operating costs determine O_x.
    base=list(product([Q(0),Q(4),Q(10)], [Q(4),Q(6)], [Q(1),Q(2)],
                      [Q(1),Q(2),Q(3)], [Q(0),Q(4),Q(5),Q(6),Q(8),Q(9)],
                      [Q(0),Q(1,2),Q(2),Q(6)], [Q(0),Q(3),Q(4),Q(12)]))
    def base_rows():
        for V,c,b,h,B,k,O in base:
            yield (V,c,b,h,B,k,Z,Z,Z,O,Z)
    check_family('binary_boundaries',base_rows())
    check_family('continuous_boundaries',base_rows(),'continuous')
    check_family('competition_boundaries',base_rows(),'competition')
    check_family('reserve_boundaries',base_rows(),reserve=True)
    def legacy_rows():
        for B,k,a0,r0,a1,r1 in product(map(Q,[4,5,6,8,9]),[Q(1,2),Q(2)],
                                     map(Q,[1,3,5,10]),[Z,Q(1),Q(4),Q(5)],
                                     map(Q,[0,4,5,12]),[Z,Q(1),Q(5)]):
            if a0>r0 and r0<=B:
                yield (Q(10),Q(6),Q(2),Q(3),B,k,Z,a0,r0,a1,r1)
    check_family('legacy',legacy_rows())
    check_family('legacy_continuous',legacy_rows(),'continuous')
    check_family('legacy_competition',legacy_rows(),'competition')
    check_family('legacy_reserve',legacy_rows(),reserve=True)
    def overhead_rows():
        for B,k,F,O in product([Q(1),Q(5),Q(6),Q(8),Q(10)],
                              [Z,Q(1,2),Q(2)], [Q(1,4),Q(1),Q(2)],
                              [Z,Q(3),Q(4),Q(12)]):
            if F<=B: yield (10,6,2,3,B,k,F,0,0,O,0)
    check_family('overhead',overhead_rows())
    # Independent closed-form Table 2 row 3, row 6 and reserve bounds in Prop 2.
    ct=Counter()
    for B,k,O,h,b in product([Q(n,4) for n in range(17,24)],
                            [Q(n,4) for n in range(1,8)],
                            [Q(n,4) for n in range(1,29)],
                            [Q(1),Q(2),Q(3),Q(4)], [Q(1),Q(2),Q(3)]):
        V=Q(10);c=Q(6);C=c-b;R=B-k;H=V-h-C
        if not (C<R<B<c and V-h>B and H<O<V-R): continue
        row=(V,c,b,h,B,k,Z,Z,Z,O,Z)
        for mode,reserve,condition in (
            ('continuous',False,O>max(H,V-R-h*(c-R)/b)),
            ('competition',False,O>H+k),
            ('binary',True,O>max(H,V-h-B+2*k))):
            ans=solve(row,mode,reserve)
            assert (ans['case'] is not None)==condition,(row,mode,reserve,ans)
            ct[mode+('_reserve' if reserve else '')]+=1
    counts['printed_region_thresholds']=dict(ct)
    # Named examples: parameters V,c,b,h,B,k,F,a0,r0,a1,r1.
    spec={
        'legacy_F':((10,6,2,3,5,Q(1,2),0,2,1,5,1),'binary',False,'F'),
        'legacy_T':((10,6,2,3,8,Q(1,2),0,Q(5,4),1,4,1),'binary',False,'T'),
        'legacy_D':((10,6,2,3,9,Q(1,2),0,Q(5,4),1,0,0),'binary',False,'D'),
        'legacy_lost_after_build':((10,6,2,3,5,Q(1,2),0,9,5,0,0),'binary',False,'D'),
        'overhead_F':((10,6,2,3,Q(21,4),Q(1,2),Q(1,4),0,0,5,1),'binary',False,'F'),
        'overhead_T':((10,6,2,3,Q(33,4),Q(1,2),Q(1,4),0,0,3,0),'binary',False,'T'),
        'overhead_D':((10,6,2,3,Q(37,4),Q(1,2),Q(1,4),0,0,0,0),'binary',False,'D'),
        'continuous_F':((10,6,2,3,5,Q(1,2),0,0,0,5,1),'continuous',False,'F'),
        'continuous_T_boundary':((10,6,2,3,8,Q(1,2),0,0,0,Q(5,2),0),'continuous',False,'T'),
        'continuous_D_attempt_fails':((10,6,2,3,10,Q(1,2),0,0,0,0,0),'continuous',False,None),
        'continuous_D_legacy_loss':((10,6,2,3,5,Q(1,2),0,9,5,0,0),'continuous',False,'D'),
        'continuous_partial_boundary':((10,6,2,3,5,Q(1,2),0,0,0,Q(13,4),0),'continuous',False,None),
        'competition_F':((10,6,2,3,5,Q(1,2),0,0,0,5,1),'competition',False,'F'),
        'competition_D':((10,6,2,3,Q(25,4),Q(1,2),0,0,0,0,0),'competition',False,'D'),
        'competition_build_tie':((10,6,2,3,5,Q(1,2),0,0,0,Q(7,2),0),'competition',False,None),
        'reserve_F':((10,6,2,3,5,Q(1,2),0,0,0,5,1),'binary',True,'F'),
        'reserve_T':((10,6,2,3,Q(17,2),Q(1,2),0,0,0,3,0),'binary',True,'T'),
    }
    for name,(row,mode,reserve,case) in spec.items():
        ans=solve(row,mode,reserve)
        assert ans['case']==case,(name,ans)
        examples[name]=serial(dict(parameters=row,mode=mode,reserve=reserve,result=ans))
    report=dict(status='PASS',counts=counts,examples=examples,first_grid_witnesses=witnesses,
                limitations='Finite exact checks, not proof. Competition outside row 6 uses the explicit cost-menu selection completion. No external literature or empirical validation.')
    (OUT/'CHECK_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',counts=counts),indent=2))
if __name__=='__main__': run()
