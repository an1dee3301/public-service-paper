#!/usr/bin/env python3
"""Lead check, 6 Oct 2026: full characterisation of the Section 5.1-5.2 game with F=0, no legacy service (O_0=0)
and an operable built alternative of net value O (assumed affordable after building).
(1) brute(): the rules exactly as Section 5.2 prints them.  (2) lemma(): the 'priced slack' closed form.
(3) classify every grid point by which of the four allocations end with q=0, and how (harmless incumbent / fallback).
(4) test closed-form descriptions of the set where joint resident rights are the only protecting allocation.
Exact rational arithmetic throughout."""
from fractions import Fraction as F
from itertools import product
from collections import Counter
import random, json

def brute(V,c,b,h,B,k,O,x,d):
    R=B-k*x; Ox=O if x else F(0); C=c-b
    best=None
    for q in (0,1):
        p=min(R, V-Ox-d*h*q)
        if p<0: continue
        prof=p-c+b*q
        if prof<0: continue
        if best is None or prof>best[0] or (prof==best[0] and q==0): best=(prof,q,p)
    if best is None: return ('F',None,Ox-k*x,Ox-k*x)          # fallback: agency score, resident welfare
    prof,q,p=best
    return ('T',q,V-p-k*x,V-p-h*q-k*x)

def lemma(V,c,b,h,B,k,O,x,d):
    R=B-k*x; Ox=O if x else F(0); C=c-b
    P0=min(R,V-Ox); s=d*min(h,max(F(0),R-(V-Ox-h))); P1=P0-s
    if P0<0: return ('F',None,Ox-k*x,Ox-k*x)
    if s>=b:
        if P0>=c: return ('T',0,V-P0-k*x,V-P0-k*x)
        return ('F',None,Ox-k*x,Ox-k*x)
    if P1>=C and P1>=0: return ('T',1,V-P1-k*x,V-P1-h-k*x)
    # s<b: harmless never preferred unless harmful infeasible because price negative
    return ('F',None,Ox-k*x,Ox-k*x)

def equilibrium(V,c,b,h,B,k,O,inv,d,f=brute):
    """inv: 0 agency invests, 1 residents invest. Tie: no build."""
    o0=f(V,c,b,h,B,k,O,0,d); o1=f(V,c,b,h,B,k,O,1,d)
    i=3 if inv else 2
    x=1 if o1[i]>o0[i] else 0
    o=(o0,o1)[x]
    return x,o

def pattern(V,c,b,h,B,k,O):
    out=[]
    for inv,d in ((0,0),(1,0),(0,1),(1,1)):           # neither, financing only, refusal only, joint
        x,o=equilibrium(V,c,b,h,B,k,O,inv,d)
        out.append(('H' if (o[0]=='T' and o[1]==1) else ('N' if o[0]=='T' else 'f'))+str(x))
    return tuple(out)

def prop2(V,c,b,h,B,k,O):
    C=c-b
    return C<B-k and B<c and V-h>B and V-h-C<O<V-(B-k)

def setT(V,c,b,h,B,k,O):
    """Joint rights uniquely protect and the incumbent keeps serving, harmless (threat region)."""
    C=c-b
    s0=min(h,max(F(0),B-(V-h))); s1=min(h,max(F(0),B-k-(V-O-h)))
    P00=min(B,V); P10=P00-s0; P01=min(B-k,V-O)
    return s0<b<=s1 and P01>=c and P10>=C and P10<=P01+k<P10+h

def run():
    res={}
    # (1)-(2): lemma == brute on a wide rational sample, including b=0 excluded (b>0 maintained)
    random.seed(7); n=0; bad=0
    def rf(lo,hi): return F(random.randint(lo*4,hi*4),4)
    for _ in range(200000):
        V=rf(1,14); c=rf(1,12); b=rf(0,12);
        if b==0 or b>c: continue
        h=rf(0,10); B=rf(0,16); k=rf(0,6); O=rf(0,14)
        if k>B: continue
        for x,d in product((0,1),(0,1)):
            n+=1
            if brute(V,c,b,h,B,k,O,x,d)!=lemma(V,c,b,h,B,k,O,x,d): bad+=1
    res['lemma_vs_brute']={'states':n,'mismatch':bad}
    # (3)-(4): patterns
    pats=Counter(); onlyjoint=0; inP2=0; inT=0; other=[]; p2_notonly=0; T_notonly=0
    random.seed(11); m=0
    for _ in range(400000):
        V=rf(2,14); c=rf(1,12); b=rf(0,12)
        if b==0 or b>c: continue
        h=rf(0,10); B=rf(0,16); k=rf(0,6); O=rf(0,14)
        if k>B or k==0: continue
        m+=1
        pt=pattern(V,c,b,h,B,k,O); pats[pt]+=1
        oj = pt[0][0]=='H' and pt[1][0]=='H' and pt[2][0]=='H' and pt[3][0]!='H'
        a=prop2(V,c,b,h,B,k,O); t=setT(V,c,b,h,B,k,O)
        if a and not oj: p2_notonly+=1
        if t and not oj: T_notonly+=1
        if oj:
            onlyjoint+=1
            if a: inP2+=1
            elif t: inT+=1
            else:
                if len(other)<400: other.append((pt,[str(z) for z in (V,c,b,h,B,k,O)]))
    res['sample']=m; res['only_joint']=onlyjoint; res['of_which_prop2']=inP2; res['of_which_T']=inT
    res['only_joint_unexplained']=onlyjoint-inP2-inT; res['prop2_but_not_only_joint']=p2_notonly; res['T_but_not_only_joint']=T_notonly
    res['unexplained_patterns']=Counter(str(o[0]) for o in other).most_common(8)
    res['unexplained_examples']=other[:12]
    res['patterns']=[(str(kk),v) for kk,v in pats.most_common(25)]
    # worked example for T
    ex=dict(V=F(10),c=F(6),b=F(2),h=F(3),B=F(8),k=F(1,2),O=F(3))
    res['T_example']={'pattern':pattern(**ex),'states':{f'x{x}d{d}':[str(z) for z in brute(x=x,d=d,**ex)] for x in (0,1) for d in (0,1)}}
    json.dump(res,open('closed_form/characterise_out.json','w'),indent=1,default=str); print(json.dumps(res,indent=1,default=str))
run()
