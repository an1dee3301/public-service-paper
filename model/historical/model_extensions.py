#!/usr/bin/env python3
"""Model extensions for Sections 5.2-5.4 of the working draft: phase diagram over (B, O1),
surplus condition, top-up benchmark.  Independent exact-rational re-implementation of the
stated game (Fractions, standard library) plus matplotlib for the figure.
Synthetic parameters only; no data, no network.  Run from any directory:
    python3 model_extensions.py            (writes outputs beside this file)
Optionally cross-checks against econ/scripts/check_ai_dependence_model.py if found.
"""
from __future__ import annotations
import csv, random, sys, json
from fractions import Fraction as Q
from pathlib import Path
from dataclasses import dataclass, replace

HERE = Path(__file__).resolve().parent

@dataclass(frozen=True)
class P:
    V: Q = Q(10); c: Q = Q(6); b: Q = Q(2); h: Q = Q(3); B: Q = Q(5); k: Q = Q(1, 2)
    a0: Q = Q(0); r0: Q = Q(0); a1: Q = Q(5); r1: Q = Q(1); F: Q = Q(0)
    @property
    def C(self): return self.c - self.b
    @property
    def O1(self): return max(Q(0), self.a1 - self.r1)

def fallback(p, x, R):
    """Best affordable alternative given remaining cash R: (net value O, cash expense, gross value)."""
    opts = [(Q(0), Q(0), Q(0), 3)]                       # shutdown (wins exact ties, index 3 = lowest priority sign trick below)
    opts = [(Q(0), Q(0), Q(0))]
    if p.r0 <= R: opts.append((p.a0 - p.r0, p.r0, p.a0))
    if x and p.r1 <= R: opts.append((p.a1 - p.r1, p.r1, p.a1))
    # max net value, then min expenditure; shutdown (index 0) preferred on exact tie
    best = max(enumerate(opts), key=lambda z: (z[1][0], -z[1][1], -z[0]))[1]
    return best

def state(p, x, d, q_forced_zero=False):
    """Continuation game. x investment, d=1 resident acceptance. Returns dict or None if infeasible."""
    K = p.F + p.k * x
    if K > p.B: return None
    R = p.B - K
    O, exp_fb, val_fb = fallback(p, x, R)
    offers = []
    for q in ((0,) if q_forced_zero else (0, 1)):
        price = min(R, p.V - O - d * p.h * q)          # binding of cash and acceptance ceilings
        profit = price - p.c + p.b * q
        if price >= 0 and profit >= 0:
            offers.append((profit, -q, price, q))       # tie -> q=0
    if offers:
        profit, _, price, q = max(offers)
        gross, spend, oper = p.V, price, p.c - p.b * q
    else:
        profit, price, q = Q(0), Q(0), 0
        gross, spend, oper = val_fb, exp_fb, exp_fb
    A = gross - spend - K
    return dict(x=x, q=q, price=price, profit=profit, A=A, W=A - p.h * q,
                G=gross - oper - K - p.h * q, fallback_used=not offers)

def solve(p, invest_res, accept_res, capacity=True, q_forced_zero=False):
    cand = [state(p, x, int(accept_res), q_forced_zero) for x in ((0, 1) if capacity else (0,))]
    cand = [s for s in cand if s is not None]
    key = 'W' if invest_res else 'A'
    return max(cand, key=lambda s: (s[key], -s['x']))      # no build on ties

ALLOC = {'none': (False, False), 'financing_only': (True, False),
         'refusal_only': (False, True), 'both': (True, True)}   # (invest_res, accept_res)

def all_alloc(p):
    return {n: solve(p, *v) for n, v in ALLOC.items()}

def in_region(p):
    C = p.C
    return (p.F == 0 and p.a0 - p.r0 == 0 and C < p.B - p.k < p.B < p.c and p.V - p.h > p.B
            and p.V - p.h - C < p.O1 < p.V - (p.B - p.k) and p.r1 + p.k <= p.B)

def topup_outcomes(p):
    """Institution (a): budget top-up T=max(0,c-B) plus enforceable no-removal clause (q=0), agency holds both rights.
    Variants: fallback available to the buyer or not.  Outside money T is a transfer; residents' W counts all payments."""
    T = max(Q(0), p.c - p.B)
    pt = replace(p, B=p.B + T)
    with_fb = solve(pt, False, False, True, True)
    no_fb = solve(pt, False, False, False, True)
    clause_only = solve(p, False, False, True, True)     # clause, no top-up
    return T, with_fb, no_fb, clause_only

def classify(res, tol=Q(0)):
    W = {n: s['W'] for n, s in res.items()}
    top = max(W.values())
    if top <= W['none']: return 'neither helps'
    fin, ref, both = W['financing_only'] == top, W['refusal_only'] == top, W['both'] == top
    if fin and ref: return 'either right alone suffices'
    if fin: return 'financing alone suffices'
    if ref: return 'refusal alone suffices'
    return 'both required'

def grid(Bs, O1s, base):
    rows = []
    for B in Bs:
        for O1 in O1s:
            p = replace(base, B=B, a1=O1 + base.r1)
            res = all_alloc(p)
            T, twf, tnf, clo = topup_outcomes(p)
            r = dict(B=float(B), O1=float(O1), in_prop2_region=in_region(p), region_class=classify(res))
            for n, s in res.items():
                r['W_' + n] = float(s['W']); r['q_' + n] = s['q']; r['G_' + n] = float(s['G']); r['x_' + n] = s['x']
            r['dG_both_vs_none'] = float(res['both']['G'] - res['none']['G'])
            r['dW_both_vs_none'] = float(res['both']['W'] - res['none']['W'])
            r['topup_T'] = float(T); r['W_topup_fallback'] = float(twf['W']); r['G_topup_fallback'] = float(twf['G'])
            r['W_topup_nofallback'] = float(tnf['W']); r['W_clause_only'] = float(clo['W']); r['G_clause_only'] = float(clo['G'])
            r['topup_minus_both_W'] = float(twf['W'] - res['both']['W'])
            r['clause_only_minus_both_W'] = float(clo['W'] - res['both']['W'])
            rows.append(r)
    return rows

def crosscheck():
    """Compare with the author's program on random states if it can be found; returns (n_checked, n_mismatch) or None."""
    for anc in HERE.parents:
        f = anc / 'econ' / 'scripts' / 'check_ai_dependence_model.py'
        if f.exists():
            sys.path.insert(0, str(f.parent)); break
    else: return None
    import check_ai_dependence_model as M
    rnd = random.Random(7); n = bad = 0
    for _ in range(3000):
        kw = dict(V=rnd.randint(4, 20), c=rnd.randint(1, 10), h=rnd.randint(0, 6), B=rnd.randint(1, 12),
                  k=Q(rnd.randint(0, 6), 4), a1=rnd.randint(0, 10), r1=rnd.randint(0, 3), F=rnd.choice([0, 0, 1]))
        kw['b'] = rnd.randint(0, kw['c'])
        mine = replace(P(), **{k: Q(v) for k, v in kw.items()})
        theirs = M.Parameters(**{k: Q(v) for k, v in kw.items()}, a0=Q(0), r0=Q(0)) if False else\
                 replace(M.make(), **{k: Q(v) for k, v in kw.items()})
        for (ir, ar) in ALLOC.values():
            a = solve(mine, ir, ar)
            b_ = M.solve_investment(theirs, ar, ir, True)
            n += 1
            if b_ is None or (a['q'], a['W'], a['profit'], a['x']) != (b_['q'], b_['resident'], b_['profit'], b_['x']): bad += 1
    return n, bad

def main():
    base = P()
    out = {}
    # ---- Task 1: worked example -------------------------------------------------
    ex = all_alloc(base)
    T, twf, tnf, clo = topup_outcomes(base)
    out['example'] = {n: dict(q=s['q'], W=float(s['W']), profit=float(s['profit']), G=float(s['G']), x=s['x']) for n, s in ex.items()}
    out['example_topup'] = dict(T=float(T), W_with_fallback=float(twf['W']), W_no_fallback=float(tnf['W']),
                                G_with_fallback=float(twf['G']), x=twf['x'], W_clause_only=float(clo['W']), x_clause_only=clo['x'],
                                W_topup_if_donor_pays=float(twf['W'] + T))
    # ---- Task 2: phase grid -------------------------------------------------------
    Bs = [Q(3) + Q(i, 8) for i in range(0, 8 * 5 + 1)]           # 3.000 .. 8.000 step 0.125
    O1s = [Q(i, 8) for i in range(0, 8 * 9 + 1)]                # 0 .. 9 step 0.125
    rows = grid(Bs, O1s, base)
    with open(HERE / 'phase_grid.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    from collections import Counter
    cnt = Counter(r['region_class'] for r in rows)
    cnt_reg = Counter(r['region_class'] for r in rows if r['in_prop2_region'])
    out['grid_n'] = len(rows); out['class_counts'] = dict(cnt); out['class_counts_in_region'] = dict(cnt_reg)
    out['n_region'] = sum(r['in_prop2_region'] for r in rows)
    out['joint_lowers_W_vs_none'] = sum(r['dW_both_vs_none'] < 0 for r in rows)
    out['joint_lowers_G_vs_none_all'] = sum(r['dG_both_vs_none'] < 0 for r in rows)
    reg = [r for r in rows if r['in_prop2_region']]
    out['region_joint_lowers_G'] = sum(r['dG_both_vs_none'] < 0 for r in reg)
    out['region_joint_raises_G'] = sum(r['dG_both_vs_none'] > 0 for r in reg)
    # what does joint control do overall?  changed-outcome points
    ch = [r for r in rows if r['dW_both_vs_none'] != 0]
    out['n_joint_changes_W'] = len(ch)
    out['changed_lowers_G'] = sum(r['dG_both_vs_none'] < 0 for r in ch)
    out['changed_G_equal'] = sum(r['dG_both_vs_none'] == 0 for r in ch)
    # analytic check inside region
    bad = [r for r in reg if abs(r['dG_both_vs_none'] - (r['O1'] - float(base.k) - (float(base.V) - float(base.C) - float(base.h)))) > 1e-12]
    out['analytic_formula_mismatches_in_region'] = len(bad)
    # top-up vs joint over grid
    def rng(key, sel): v = [r[key] for r in sel]; return (min(v), max(v))
    out['topup_minus_both_W_all'] = rng('topup_minus_both_W', rows)
    out['topup_minus_both_W_region'] = rng('topup_minus_both_W', reg)
    out['clause_only_minus_both_W_all'] = rng('clause_only_minus_both_W', rows)
    out['clause_only_minus_both_W_region'] = rng('clause_only_minus_both_W', reg)
    out['topup_lt_joint_count'] = sum(r['topup_minus_both_W'] < 0 for r in rows)
    out['topup_gt_joint_count'] = sum(r['topup_minus_both_W'] > 0 for r in rows)
    out['topup_gt_joint_region'] = sum(r['topup_minus_both_W'] > 0 for r in reg)
    out['topup_eq_joint_region'] = sum(r['topup_minus_both_W'] == 0 for r in reg)
    nf = [r['W_topup_nofallback'] - r['W_both'] for r in reg]
    out['topup_nofallback_minus_both_region'] = (min(nf), max(nf))
    out['topup_nofallback_lt_joint_region'] = sum(v < 0 for v in nf)
    out['clause_only_eq_joint_region'] = sum(r['clause_only_minus_both_W'] == 0 for r in reg)
    out['topup_T_region'] = rng('topup_T', reg)
    # ---- Task 3: sampling for the surplus claim ----------------------------------
    rnd = random.Random(20260930)
    def draw_params():
        V = Q(rnd.randint(500, 2000), 100); c = Q(rnd.randint(100, int(V * 100)), 100)
        b = Q(rnd.randint(0, int(c * 100)), 100); h = Q(rnd.randint(0, 1000), 100)
        B = Q(rnd.randint(0, int(V * 100)), 100); k = Q(rnd.randint(0, 300), 100)
        return dict(V=V, c=c, b=b, h=h, B=B, k=k)
    schemes = {}
    # S1: unconditional rejection sampling, O1 ~ U[0, V]
    n_draw = 400000; reg1 = low1 = eq1 = 0
    for _ in range(n_draw):
        d = draw_params(); O1 = Q(rnd.randint(0, int(d['V'] * 100)), 100)
        p = replace(P(), **d, a1=O1 + 1, r1=Q(1))
        if in_region(p):
            reg1 += 1
            dG = solve(p, True, True)['G'] - solve(p, False, False)['G']
            low1 += dG < 0; eq1 += dG == 0
    schemes['S1_reject_all_params_O1~U[0,V]'] = dict(draws=n_draw, region=reg1, lowers=low1, share=low1 / reg1 if reg1 else None)
    # S2: parameters as in S1 (region-feasible B, V-h>B..) but O1 uniform inside the region interval
    reg2 = low2 = 0; n2 = 0
    while reg2 < 20000 and n2 < 3000000:
        n2 += 1
        d = draw_params(); p0 = replace(P(), **d, r1=Q(1))
        C = p0.C; lo, hi = p0.V - p0.h - C, p0.V - (p0.B - p0.k)
        if not (C < p0.B - p0.k < p0.B < p0.c and p0.V - p0.h > p0.B and lo < hi and p0.B - p0.k >= 1): continue
        O1 = lo + (hi - lo) * Q(rnd.randint(1, 9999), 10000)
        p = replace(p0, a1=O1 + 1)
        if not in_region(p): continue
        reg2 += 1
        dG = solve(p, True, True)['G'] - solve(p, False, False)['G']
        low2 += dG < 0
        assert dG == O1 - p.k - (p.V - p.C - p.h)
    schemes['S2_parameter-region_then_O1~U(interval)'] = dict(draws=n2, region=reg2, lowers=low2, share=low2 / reg2)
    # S3: the grid itself
    schemes['S3_(B,O1)_grid_inside_region'] = dict(region=len(reg), lowers=out['region_joint_lowers_G'], share=out['region_joint_lowers_G'] / len(reg))
    # analytic share for the example, uniform O1: k / (h + C - B + k)
    L = base.h + base.C - base.B + base.k
    schemes['analytic_example_B=5_uniform_O1'] = dict(share=float(min(Q(1), base.k / L)), interval_length=float(L))
    out['surplus_schemes'] = schemes
    xc = crosscheck(); out['crosscheck_vs_author_program(n_states,n_mismatch)'] = xc
    with open(HERE / 'model_extensions_results.json', 'w') as f: json.dump(out, f, indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))
    make_figures(rows, base)

def make_figures(rows, base):
    import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    Bs = sorted({r['B'] for r in rows}); O1s = sorted({r['O1'] for r in rows})
    idx = {(r['B'], r['O1']): r for r in rows}
    cls = ['neither helps', 'financing alone suffices', 'refusal alone suffices', 'either right alone suffices', 'both required']
    cols = ['#e8e8e8', '#0072B2', '#E69F00', '#009E73', '#CC79A7']   # Okabe-Ito
    Z = np.array([[cls.index(idx[(B, O)]['region_class']) for B in Bs] for O in O1s])
    fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.6), gridspec_kw=dict(width_ratios=[1.25, 1]))
    a = ax[0]
    dB = Bs[1] - Bs[0]; dO = O1s[1] - O1s[0]
    ext = [Bs[0] - dB / 2, Bs[-1] + dB / 2, O1s[0] - dO / 2, O1s[-1] + dO / 2]
    a.imshow(Z, origin='lower', extent=ext, aspect='auto', cmap=ListedColormap(cols), vmin=-.5, vmax=4.5, interpolation='nearest')
    V, c, h, k, C = map(float, (base.V, base.c, base.h, base.k, base.C))
    a.axvline(c, color='k', lw=1, ls='--'); a.axvline(C + k, color='k', lw=1, ls=':')
    xs = np.array(Bs); a.plot(xs, V - xs + k, color='k', lw=1.2); a.axhline(V - h - C, color='k', lw=1.2)
    a.plot(float(base.B), float(base.O1), marker='*', ms=15, mfc='white', mec='k')
    a.annotate('paper example\n(B=5, O1=4)', (5, 4), (5.35, 1.7), fontsize=9, arrowprops=dict(arrowstyle='-', lw=.8))
    a.text(c + .05, 8.6, 'B = c', fontsize=8); a.text(C + k + .05, 8.6, 'B = C+k', fontsize=8)
    a.text(3.1, V - h - C + .1, 'O1 = V-h-C', fontsize=8); a.text(6.3, V - 6.3 + k + .1, 'O1 = V-B+k', fontsize=8, rotation=-35)
    a.set_xlim(ext[0], ext[1]); a.set_ylim(ext[2], ext[3])
    a.set_xlabel('Budget B'); a.set_ylabel('Value of the new alternative, O1 (net of running cost)')
    a.set_title('Which rights raise resident welfare above the no-rights outcome', fontsize=11)
    a.legend(handles=[Patch(fc=cols[i], ec='k', lw=.4, label=cls[i]) for i in range(5)], loc='upper right', fontsize=8, framealpha=.95)
    # panel b: surplus sign of joint rights vs none, and top-up vs joint
    b = ax[1]
    D = np.array([[idx[(B, O)]['dG_both_vs_none'] for B in Bs] for O in O1s])
    S = np.sign(D).astype(int)   # -1,0,1
    reg = np.array([[idx[(B, O)]['in_prop2_region'] for B in Bs] for O in O1s])
    cm = ListedColormap(['#D55E00', '#f5f5f5', '#56B4E9'])
    b.imshow(S, origin='lower', extent=ext, aspect='auto', cmap=cm, vmin=-1.5, vmax=1.5, interpolation='nearest')
    b.contour(Bs, O1s, reg.astype(float), levels=[.5], colors='k', linewidths=1.3)
    b.plot(float(base.B), float(base.O1), marker='*', ms=15, mfc='white', mec='k')
    b.set_xlabel('Budget B'); b.set_ylabel('O1'); b.set_title('Total surplus: joint rights vs no rights\n(black outline = Corollary 1 region)', fontsize=11)
    b.legend(handles=[Patch(fc='#D55E00', label='joint rights lower total surplus'), Patch(fc='#f5f5f5', ec='k', lw=.4, label='no change'),
                      Patch(fc='#56B4E9', label='joint rights raise total surplus')], loc='upper right', fontsize=8, framealpha=.95)
    fig.text(0.01, 0.005, 'Synthetic parameters V=10, c=6, b=2, h=3, k=0.5, r1=1, F=0, no legacy service. Exact enumeration, grid step 0.125.', fontsize=8)
    fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(HERE / 'phase_diagram.png', dpi=170); plt.close(fig)
    # figure 2: top-up minus joint-rights, resident welfare
    fig, a = plt.subplots(figsize=(7.2, 5.4))
    Dt = np.array([[idx[(B, O)]['topup_minus_both_W'] for B in Bs] for O in O1s])
    im = a.imshow(Dt, origin='lower', extent=ext, aspect='auto', cmap='viridis', interpolation='nearest')
    a.contour(Bs, O1s, reg.astype(float), levels=[.5], colors='w', linewidths=1.3)
    a.plot(float(base.B), float(base.O1), marker='*', ms=15, mfc='white', mec='k')
    plt.colorbar(im, label='resident welfare: top-up + clause minus joint rights')
    a.set_xlabel('Budget B'); a.set_ylabel('O1'); a.set_title('Top-up (to B = c) with no-removal clause vs joint rights', fontsize=11)
    fig.tight_layout(); fig.savefig(HERE / 'topup_vs_joint.png', dpi=170); plt.close(fig)

if __name__ == '__main__':
    main()
