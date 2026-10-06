"""Figure R1: where joint resident rights remove the harm, in (k, O1) space, at the worked values.
Bounds are those printed in Sections 5.3, 5.4 and 5.7 of candidate C; nothing new is derived here.
V=10, c=6, b=2, h=3, B=5 -> C=4, H=V-h-C=3. Region of Proposition 2: 0<k<B-C, H<O1<V-(B-k).
"""
from fractions import Fraction as F
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
V,c,b,h,B=10,6,2,3,5; C=c-b; H=V-h-C
k=np.linspace(0,B-C,400)
upper=V-(B-k); shared=np.full_like(k,H); earmark=np.maximum(H,V-h-B+2*k); comp=H+k
fig,ax=plt.subplots(figsize=(6.4,4.4),dpi=200)
ax.fill_between(k,shared,upper,color="#e3e3e3",linewidth=0)
ax.fill_between(k,shared,earmark,color="#b5b5b5",linewidth=0)
ax.plot(k,upper,"k-",lw=1.2); ax.plot(k,shared,"k-",lw=1.2)
ax.plot(k,earmark,"k--",lw=1.1); ax.plot(k,comp,"k:",lw=1.6)
ax.plot([0.5],[4],"ko",ms=5); ax.annotate("worked example",(0.5,4),xytext=(0.47,4.12),fontsize=8,ha="right")
ax.text(0.02,5.1,r"upper bound $O_1=V-(B-k)$",fontsize=8,rotation=13)
ax.text(0.02,2.84,r"lower bound, shared account: $O_1=V-h-C$",fontsize=8)
ax.annotate("two suppliers pricing at cost:\nprotection needs $O_1>V-h-C+k$",(0.3,3.3),xytext=(0.05,3.75),fontsize=8,arrowprops=dict(arrowstyle="-",lw=.6))
ax.annotate("separate fallback account:\nprotection needs\n$O_1>\\max\\{V-h-C,\\;V-h-B+2k\\}$\n(dark band is lost)",(0.85,3.7),xytext=(0.55,4.5),fontsize=8,arrowprops=dict(arrowstyle="-",lw=.6))
ax.text(0.5,5.9,"joint resident rights remove the harm (Proposition 2)",fontsize=8.5,ha="center")
ax.set_xlim(0,B-C); ax.set_ylim(2.6,6.2)
ax.set_xlabel(r"fallback investment $k$   (cash constraint $k<B-C$)"); ax.set_ylabel(r"value of the fallback, $O_1=a_1-r_1$")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
fig.tight_layout(); fig.savefig("fig_region.png"); fig.savefig("fig_region.pdf"); fig.savefig("fig_region.eps")
# exact checks of the statements made in the caption
assert H==3 and F(1,2)*2+V-h-B==H           # earmark and shared bounds coincide at k=1/2
assert H+F(1,2)<4<V-(B-F(1,2))              # worked point protected under competition too
# exact areas of the protected set in (k,O1) at the worked V,h,B,C (piecewise-linear bounds, integrated by hand)
A_shared=F(5,2); A_earmark=A_shared-F(1,4); A_comp=A_shared-F(1,2)
print({"area_shared":str(A_shared),"area_earmark":str(A_earmark),"area_competition":str(A_comp)})
