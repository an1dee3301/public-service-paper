"""Lead (independent solver) independent checks, 4 Oct 2026. Exact fractions.
(1) independent solver H1 item M13: competition + unreliable fallback.
(2) Shared budget vs earmarked reserve at the same total resources (H1 item M1)."""
from fractions import Fraction as Fr
from itertools import product

def cont(V,c,b,h,R,K,O,d):
    """Monopoly continuation: returns (q, A, W, profit)."""
    best=None
    for q in (0,1):
        p=min(R, V-O-d*h*q)
        prof=p-c+b*q
        if p>=0 and prof>=0 and (best is None or prof>best[0]): best=(prof,q,p)
    if best is None: return (0, O-K, O-K, Fr(0))
    prof,q,p=best
    return (q, V-p-K, V-p-h*q-K, prof)

def solve(V,c,b,h,B,k,O1,mode):
    out={}
    for inv,d in product("AR",(0,1)):
        res=[]
        for x in (0,1):
            R = B-k*x if mode=="shared" else B-k      # earmark: operating cash is B-k in both states
            res.append(cont(V,c,b,h,R,k*x,O1*x,d))
        i = 1 if inv=="A" else 2
        x = 1 if res[1][i]>res[0][i] else 0            # tie -> no build
        out[(inv,d)]=(x,)+res[x]
    return out

# ---- (2) grid over Corollary 1 region
n=tot=holds_sh=holds_em=pred_ok=0
lost=[]
rng=[Fr(i,4) for i in range(0,49)]
for V in (Fr(10),Fr(12)):
  for c,b,h,B,k,O1 in product(rng[4:33:4],rng[0:17:4],rng[0:25:2],rng[4:33:2],rng[1:9],rng[0:49]):
    C=c-b
    if not (b<=c and C<B-k<B<c and V-h>B and V-h-C<O1<V-(B-k)): continue
    tot+=1
    sh=solve(V,c,b,h,B,k,O1,"shared"); em=solve(V,c,b,h,B,k,O1,"earmark")
    pat=lambda s: s[("R",1)][1]==0 and all(s[a][1]==1 for a in s if a!=("R",1))
    holds_sh+=pat(sh); e=pat(em); holds_em+=e
    pred = O1 > V-h-B+2*k
    pred_ok += (e==pred)
    # earmark alone: no-build resident payoff rises by exactly k, harm unchanged
    assert em[("A",0)][1]==1 and em[("A",0)][3]-sh[("A",0)][3]==k
    if not e: lost.append((V,c,b,h,B,k,O1))
print("region points",tot,"| shared pattern holds",holds_sh,"| earmark pattern holds",holds_em,"| earmark==predicted threshold",pred_ok)
print("example lost point (V,c,b,h,B,k,O1):",[str(x) for x in lost[0]] if lost else None)
w=dict(V=Fr(10),c=Fr(6),b=Fr(2),h=Fr(3),B=Fr(5),k=Fr(1,2),O1=Fr(4))
for m in ("shared","earmark"):
    s=solve(mode=m,**w); print(m,{f"{a[0]}inv/{'R' if a[1] else 'A'}acc":(v[0],v[1],str(v[3])) for a,v in s.items()})

# ---- (1) M13: two suppliers at cost, fallback works with prob rho, refusal commits before outcome known
def comp(V,c,b,h,B,k,a1,r1,rho):
    C=c-b; Orho=max(Fr(0),rho*a1-r1); out={}
    for inv,d in product("AR",(0,1)):
        res=[]
        for x in (0,1):
            R=B-k*x; O=Orho*x; K=k*x
            # harmless infeasible (B<c). Harmful trades at cost C iff acceptable and affordable.
            ok = C<=R and (V-C-d*h >= O)
            res.append((1,V-C-K,V-C-h-K) if ok else (0,O-K,O-K))
        i=1 if inv=="A" else 2
        x=1 if res[1][i]>res[0][i] else 0
        out[(inv,d)]=(x,res[x][0],res[x][2])
    return out
for rho in (Fr(1),Fr(9,10),Fr(17,20),Fr(19,20)):
    s=comp(Fr(10),Fr(6),Fr(2),Fr(3),Fr(5),Fr(1,2),Fr(5),Fr(1),rho)
    print("competition, rho",rho,{f"{a[0]}inv/{'R' if a[1] else 'A'}acc":(v[0],v[1],str(v[2])) for a,v in s.items()})
# monopoly with reliability alone
for rho in (Fr(9,10),Fr(17,20)):
    s=solve(Fr(10),Fr(6),Fr(2),Fr(3),Fr(5),Fr(1,2),max(Fr(0),rho*5-1),"shared")
    print("monopoly, rho",rho,"joint:",(s[("R",1)][0],s[("R",1)][1],str(s[("R",1)][3])))
