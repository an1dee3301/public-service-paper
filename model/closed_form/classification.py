#!/usr/bin/env python3
"""Lead check, 6 Oct 2026. Closed form for the set J where, among the four allocations, joint resident rights are the only
one that ends without the harmful condition (F=0, O_0=0, built alternative operable and affordable, b>0, k>0).
Tests J == (Case 1F or 1T or 2) and D against the brute-force equilibrium of characterise.py on a rational sample."""
from fractions import Fraction as F
import random, json, importlib.util, sys, io, contextlib
spec=importlib.util.spec_from_file_location('ch','closed_form/characterise.py')
src=open('closed_form/characterise.py').read().rsplit('\nrun()',1)[0]
ns={}; exec(src,ns); pattern=ns['pattern']; prop2=ns['prop2']

def cells(V,c,b,h,B,k,O):
    C=c-b; Z=F(0)
    R=(B,B-k); Ox=(Z,O)
    P0=[min(R[x],V-Ox[x]) for x in (0,1)]
    s=[min(h,max(Z,R[x]-(V-Ox[x]-h))) for x in (0,1)]
    P1=[P0[x]-s[x] for x in (0,1)]
    def typ(x):                       # resident acceptance
        if P0[x]<0: return 'f'
        if s[x]>=b: return 'N' if P0[x]>=c else 'f'
        return 'H' if P1[x]>=C else 'f'
    t=[typ(0),typ(1)]
    def A1(x): return V-P0[x]-k*x if t[x]=='N' else (V-P1[x]-k*x if t[x]=='H' else Ox[x]-k*x)
    # agency acceptance
    h0=[P0[x]>=C and P0[x]>=0 for x in (0,1)]
    A0=[V-P0[x]-k*x if h0[x] else Ox[x]-k*x for x in (0,1)]
    W0=[A0[x]-(h if h0[x] else 0) for x in (0,1)]
    xa=1 if A0[1]>A0[0] else 0; xr=1 if W0[1]>W0[0] else 0
    D=h0[xa] and h0[xr]
    c1F=t[0]=='H' and t[1]=='f' and (V-P1[0]-h < O-k <= V-P1[0])
    c1T=t[0]=='H' and t[1]=='N' and (P1[0] <= P0[1]+k < P1[0]+h)
    a0=A1(0)
    c2 =t[0] in 'Nf' and t[1]=='H' and (a0 < V-P1[1]-k <= a0+h)
    return D,c1F,c1T,c2,t

def run():
    random.seed(23); rf=lambda lo,hi: F(random.randint(lo*4,hi*4),4)
    n=0; J=0; mism=0; cnt={'1F':0,'1T':0,'2':0}; p2=0; p2in1F=0; ex={}
    for _ in range(400000):
        V=rf(2,14); c=rf(1,12); b=rf(0,12)
        if b==0 or b>c: continue
        h=rf(0,10); B=rf(0,16); k=rf(0,6); O=rf(0,14)
        if k>B or k==0: continue
        n+=1
        pt=pattern(V,c,b,h,B,k,O)
        oj = pt[0][0]=='H' and pt[1][0]=='H' and pt[2][0]=='H' and pt[3][0]!='H'
        D,c1F,c1T,c2,t=cells(V,c,b,h,B,k,O)
        pred=D and (c1F or c1T or c2)
        if pred!=oj: mism+=1
        if oj:
            J+=1
            key='1F' if c1F else ('1T' if c1T else '2')
            cnt[key]+=1
            if key not in ex or (key=='2' and len(ex.get('2list',[]))<3):
                ex.setdefault(key,[str(z) for z in (V,c,b,h,B,k,O)]+[str(pt)])
        if prop2(V,c,b,h,B,k,O):
            p2+=1; p2in1F+= (c1F and D)
    out=dict(sample=n,J=J,mismatch=mism,by_case=cnt,prop2_points=p2,prop2_inside_case_1F=p2in1F,examples=ex)
    json.dump(out,open('closed_form/theorem_J_out.json','w'),indent=1); print(json.dumps(out,indent=1))
run()
