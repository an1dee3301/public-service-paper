#!/usr/bin/env python3
"""Stage-0 timing extension of the post-deployment game (referee fix 8, M3).

Exact rational arithmetic (fractions.Fraction), standard library only, synthetic
parameters only. Imports the author's program unchanged from econ/scripts/
and reuses its fallback() and solve_state().

Timeline (one renewal term, the original game's single period):
  t0   Prior contract (p0, q=0) is running, p0 <= B - k. The investor may build the
       fallback now (ex ante), cost k.
  t1   With probability pi a cost shock makes the old harmless configuration cost c
       per term (the region's B < c); the supplier then announces renewal terms
       (p_a, q_a) with notice N. With probability 1 - pi nothing happens and the
       prior terms renew (supplier profit normalised to zero, c_old = p0).
  t2   If not built ex ante and the activation lag satisfies L <= N, the investor may
       build now (after notice); the fallback is operable when the change binds.
       If L > N a fallback started now is not operable when the change binds, so
       this action is not available (binary operability, as in the task).
  t3   Supplier may revise its announced terms only in the buyer's favour
       (p <= p_a and q <= q_a) or decline to renew; adverse revisions would need a
       fresh notice and would bind only in a later term (outside the model).
  t4   The acceptance holder accepts or invokes the best operable alternative
       (fallback if operable, else legacy / shutdown, O0 = 0 in the region).

Payoffs in the shock state are exactly the original game's (V, c, b, h, B, k, a1, r1).
Capital k is charged to the renewal-term budget (R = B - k, as in the original;
'renewal' convention) or, as a robustness check, to the prior term's slack
(R = B; 'prior' convention). Tie rules are the original's, plus: no ex-ante build on
ties (wait), and among supplier announcements with equal profit, trade beats no
trade, then q = 0, then the higher price (the original's offer ordering).
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import replace
from functools import lru_cache
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "econ" / "scripts" / "check_ai_dependence_model.py"
if not SRC.is_file():
    raise FileNotFoundError(f"Expected source model at {SRC}")
sys.path.insert(0, str(SRC.parent))
import check_ai_dependence_model as M  # noqa: E402

ALLOC = {  # name: (resident acceptance d, resident investor)
    "none": (False, False),
    "financing_only": (False, True),
    "refusal_only": (True, False),
    "both": (True, True),
}


# ---------------------------------------------------------------- continuation
def cont(p, x, d, cap=None, capital="renewal"):
    """Renewal-term continuation with capacity x, acceptance d and an optional cap
    (p_a, q_a) from the announcement. With cap=None and capital='renewal' this is
    exactly M.solve_state (checked in run_checks)."""
    pb = p if capital == "renewal" else replace(p, k=Q(0))  # budget-side parameters
    alt = M.fallback(pb, x)
    if alt is None:
        return None
    R = pb.B - (pb.F + pb.k * x)
    K = p.F + p.k * x  # welfare cost of capital, whoever's budget pays it
    offers = []
    for burden in (0, 1):
        if cap is not None and burden > cap[1]:
            continue
        price = min(R, p.V - alt["O"] - int(d) * p.h * burden)
        if cap is not None:
            price = min(price, cap[0])
        profit = price - p.c + p.b * burden
        if price >= 0 and profit >= 0:
            offers.append((profit, -burden, price, burden))
    if offers:
        profit, _, price, burden = max(offers)
        value, expense, mode, operating = p.V, price, "incumbent", p.c - p.b * burden
    else:
        profit, price, burden = Q(0), Q(0), 0
        value, expense, mode = alt["value"], alt["expense"], alt["mode"]
        operating = expense
    agency = value - expense - K
    return dict(x=x, q=burden, price=price, profit=profit, mode=mode, O=alt["O"],
                agency=agency, resident=agency - p.h * burden,
                global_welfare=value - operating - K - p.h * burden)


def _kinks(p, d, capital):
    pts = {Q(0), p.B, p.c, p.c - p.b}
    for x, burden in product((0, 1), (0, 1)):
        s = cont(p, x, d, None, capital)
        if s is None:
            continue
        pb = p if capital == "renewal" else replace(p, k=Q(0))
        R = pb.B - (pb.F + pb.k * x)
        pts.add(min(R, p.V - s["O"] - int(d) * p.h * burden))
    return sorted(v for v in pts if 0 <= v <= p.B)


@lru_cache(maxsize=None)
def after_notice(p, d, inv, capital, verify=False):
    """Shock state, nothing built ex ante, L <= N: announcement, build decision,
    favourable-only revision, acceptance. Returns (outcome, announcement)."""
    def outcome(pa, qa):
        opts = [s for s in (cont(p, 0, d, (pa, qa), capital), cont(p, 1, d, (pa, qa), capital)) if s]
        return max(opts, key=lambda s: (s[inv], -s["x"]))  # no build on ties

    def diff(pa, qa):
        s0, s1 = cont(p, 0, d, (pa, qa), capital), cont(p, 1, d, (pa, qa), capital)
        return None if s1 is None else s1[inv] - s0[inv]

    kinks = _kinks(p, d, capital)
    cands = set(kinks)
    for qa in (0, 1):  # exact crossing points of the investor's build/no-build payoffs
        for u, v in zip(kinks, kinks[1:]):
            du, dv = diff(u, qa), diff(v, qa)
            if du is not None and dv is not None and du != dv and (du > 0) != (dv > 0):
                cands.add(u + (v - u) * du / (du - dv))
    best = None
    for pa, qa in product(sorted(cands), (0, 1)):
        s = outcome(pa, qa)
        key = (s["profit"], s["mode"] == "incumbent", -s["q"], s["price"])
        if best is None or key > best[0]:
            best = (key, s, (pa, qa))
    if verify:  # independent 1/16 price grid must not beat the exact candidates
        for pa, qa in product([Q(i, 16) for i in range(int(16 * p.B) + 1)], (0, 1)):
            assert outcome(pa, qa)["profit"] <= best[1]["profit"], (p, d, inv, pa, qa)
    return best[1], best[2]


def solve_timing(p, alloc, regime, pi, p0, capital="renewal", verify=False, ante_p=None):
    """regime: 'static' (original game), 'L>N' (ex-ante build only), 'L<=N'
    (ex-ante build or build after notice). Returns the shock-state outcome and
    the investor's expected payoff; build timing in 'build'."""
    d, res_inv = ALLOC[alloc]
    inv = "resident" if res_inv else "agency"
    if regime == "static":
        s = M.solve_investment(p, d, res_inv) if capital == "renewal" else max(
            [t for t in (cont(p, 0, d, None, capital), cont(p, 1, d, None, capital)) if t],
            key=lambda t: (t[inv], -t["x"]))
        return dict(s, build="ex_ante" if s["x"] else "none", expected=s[inv])
    assert p0 <= p.B - p.k, "prior price must be affordable after building"
    # supplier sees capacity before announcing; ante_p lets the gap variant give the
    # ex-ante fallback full quality while the after-notice one is degraded; False = no ex-ante option
    ante = None if ante_p is False else cont(ante_p or p, 1, d, None, capital)
    if regime == "L>N":
        wait, ann = cont(p, 0, d, None, capital), None
    else:
        wait, ann = after_notice(p, d, inv, capital, verify)
    e_wait = pi * wait[inv] + (1 - pi) * (p.V - p0)
    e_ante = None if ante is None else pi * ante[inv] + (1 - pi) * (p.V - p0 - p.k)
    if e_ante is not None and e_ante > e_wait:
        return dict(ante, build="ex_ante", expected=e_ante, announcement=None)
    return dict(wait, build="after_notice" if wait["x"] else "none",
                expected=e_wait, announcement=ann)


# ---------------------------------------------------------------- grid
def point(B, O1, **kw):
    return M.make(B=B, a1=O1 + 1, r1=1, **kw)


def in_prop2(p):
    C, O1 = p.c - p.b, p.a1 - p.r1
    return (p.F == 0 and p.a0 - p.r0 <= 0 and C < p.B - p.k < p.B < p.c and p.V - p.h > p.B
            and p.V - p.h - C < O1 < p.V - (p.B - p.k) and p.r1 + p.k <= p.B)


def pattern(res):
    return (res["none"]["q"], res["financing_only"]["q"], res["refusal_only"]["q"], res["both"]["q"]) == (1, 1, 1, 0)


PIS = (Q(1), Q(3, 4), Q(1, 2), Q(1, 4), Q(1, 8))
SCEN = [("static", Q(1), "renewal")]
SCEN += [(r, pi, "renewal") for r in ("L>N", "L<=N") for pi in PIS]
SCEN += [("static", Q(1), "prior")]
SCEN += [(r, pi, "prior") for r in ("L>N", "L<=N") for pi in (Q(1), Q(1, 2))]
SCEN = list(dict.fromkeys(SCEN))


def grid():
    Bs = [Q(3) + Q(i, 8) for i in range(41)]
    O1s = [Q(i, 8) for i in range(73)]
    rows = []
    for B, O1 in product(Bs, O1s):
        p = point(B, O1)
        p0 = min(Q(4), p.B - p.k)
        r2 = in_prop2(p)
        for regime, pi, capital in SCEN:
            res = {a: solve_timing(p, a, regime, pi, p0, capital) for a in ALLOC}
            row = dict(regime=regime, pi=str(pi), capital=capital, B=str(B), O1=str(O1),
                       in_prop2_region=int(r2), pattern_holds=int(pattern(res)),
                       both_build=res["both"]["build"])
            for a in ALLOC:
                row[f"q_{a}"] = res[a]["q"]
                row[f"W_{a}"] = str(res[a]["resident"])
                row[f"G_{a}"] = str(res[a]["global_welfare"])
            rows.append(row)
    return rows


def summarise(rows):
    out = []
    for regime, pi, capital in SCEN:
        sub = [r for r in rows if (r["regime"], r["pi"], r["capital"]) == (regime, str(pi), capital)]
        reg = [r for r in sub if r["in_prop2_region"]]
        pat = [r for r in sub if r["pattern_holds"]]
        out.append(dict(regime=regime, pi=str(pi), capital=capital, grid_points=len(sub),
                        prop2_points=len(reg),
                        prop2_points_pattern_survives=sum(r["pattern_holds"] for r in reg),
                        pattern_points_total=len(pat),
                        pattern_points_outside_prop2=sum(1 for r in pat if not r["in_prop2_region"])))
    return out


# ---------------------------------------------------------------- checks
def run_checks():
    n = 0
    # 1. With no announcement cap, cont() equals the author's solve_state.
    for B, k, a1, h, c, b in product((2, 5, 9, 20), (0, 1, 6), (0, 3, 9, 13), (0, 1, 3, 8), (3, 6), (0, 2)):
        p = M.make(B=B, k=k, a1=a1, h=h, c=c, b=b, a0=2, r0=1)
        for x, d in product((0, 1), (False, True)):
            s, t = M.solve_state(p, x, d), cont(p, x, d)
            assert (s is None) == (t is None)
            if s:
                for f in ("q", "price", "profit", "agency", "resident", "global_welfare", "mode"):
                    assert s[f] == t[f], (p, x, d, f)
                n += 1
    # 2. Analytic statements at every Corollary 1 grid point (renewal capital).
    Bs = [Q(3) + Q(i, 8) for i in range(41)]
    O1s = [Q(i, 8) for i in range(73)]
    region = [(B, O1) for B, O1 in product(Bs, O1s) if in_prop2(point(B, O1))]
    assert len(region) == 187
    for (B, O1), pi in product(region, PIS):
        p = point(B, O1)
        V, h, C, k = p.V, p.h, p.c - p.b, p.k
        p0 = p.B - k
        res = {r: {a: solve_timing(p, a, r, pi, p0, verify=(pi == 1 and r == "L<=N")) for a in ALLOC}
               for r in ("L>N", "L<=N")}
        # (i) single rights never remove q=1 in either timing regime
        for r in res:
            assert all(res[r][a]["q"] == 1 for a in ("none", "financing_only", "refusal_only"))
        # (ii) ex-ante only: joint rights protect iff O1 > V-h-B+k/pi
        assert (res["L>N"]["both"]["q"] == 0) == (O1 > V - h - B + k / pi), (B, O1, pi)
        # (iii) after-notice feasible: joint rights protect iff O1 > V-h-C+k (any pi)
        assert (res["L<=N"]["both"]["q"] == 0) == (O1 > V - h - C + k), (B, O1, pi)
        # (iv) in the band the supplier's announced harmful price equals V-h-O1+k
        if O1 <= V - h - C + k:
            s = res["L<=N"]["both"]
            assert s["q"] == 1 and s["price"] == V - h - O1 + k and s["resident"] == O1 - k
        # (v) resident welfare under joint rights never falls below the static game's
        stat = M.solve_investment(p, True, True)
        if pi == 1:
            assert res["L>N"]["both"]["resident"] == stat["resident"]
            assert res["L<=N"]["both"]["resident"] == stat["resident"]
        # (vi) p0 cancels: a different prior price leaves every choice unchanged
        for r in res:
            alt = solve_timing(p, "both", r, pi, Q(0))
            assert (alt["q"], alt["build"]) == (res[r]["both"]["q"], res[r]["both"]["build"])
        n += 1
    # 3. Pattern region in the Corollary 1 budget band (C < B-k < B < c, V-h > B,
    #    r1+k <= B, F=0, O0=0) for every O1 on the grid: the four-cell pattern holds iff
    #      static : V-h-C < O1 <= V-B+k
    #      L>N    : max(V-h-C, V-h-B+k/pi) < O1 <= min(V-C, V-B+k/pi)
    #      L<=N   : V-h-C+k < O1 <= V-C
    for B, O1 in product(Bs, O1s):
        p = point(B, O1)
        V, h, C, k = p.V, p.h, p.c - p.b, p.k
        if not (C < B - k < B < p.c and V - h > B and p.r1 + k <= B):
            continue
        for pi in PIS:
            got = {r: pattern({a: solve_timing(p, a, r, pi, B - k) for a in ALLOC})
                   for r in ("static", "L>N", "L<=N")}
            assert got["static"] == (V - h - C < O1 <= V - B + k), (B, O1)
            assert got["L>N"] == (max(V - h - C, V - h - B + k / pi) < O1 <= min(V - C, V - B + k / pi)), (B, O1, pi)
            assert got["L<=N"] == (V - h - C + k < O1 <= V - C), (B, O1, pi)
            n += 1
    return n


# ---------------------------------------------------------------- example tables
def example():
    base = M.make()  # V=10,c=6,b=2,h=3,B=5,k=1/2,a1=5,r1=1
    p0 = Q(4)
    rows = []
    for regime, pi in [("static", Q(1))] + [(r, pi) for r in ("L>N", "L<=N") for pi in (Q(1), Q(1, 2), Q(1, 4), Q(1, 5))]:
        for a in ALLOC:
            s = solve_timing(base, a, regime, pi, p0, verify=(regime == "L<=N"))
            rows.append(dict(table="example", regime=regime, pi=str(pi), variant="", allocation=a,
                             build=s["build"], q=s["q"], price=str(s["price"]), mode=s["mode"],
                             W_shock=str(s["resident"]), profit=str(s["profit"]),
                             G_shock=str(s["global_welfare"]), expected_investor=str(s["expected"])))
    # band point O1 = 3.25 (inside Corollary 1, inside the surplus-reducing band)
    band = point(Q(5), Q(13, 4))
    for regime in ("static", "L>N", "L<=N"):
        s = solve_timing(band, "both", regime, Q(1, 2) if regime != "static" else Q(1), p0, verify=True)
        rows.append(dict(table="band_O1_3.25", regime=regime, pi="1/2" if regime != "static" else "1",
                         variant="", allocation="both", build=s["build"], q=s["q"], price=str(s["price"]),
                         mode=s["mode"], W_shock=str(s["resident"]), profit=str(s["profit"]),
                         G_shock=str(s["global_welfare"]), expected_investor=str(s["expected"])))
    # gap variant: L > N and a fallback started after notice serves share theta of a
    # 365-day term (shutdown during the gap); O1 and r1 scale by theta.
    for N, L in ((30, 30), (30, 60), (30, 120), (60, 120), (30, 240)):
        theta = max(Q(0), 1 - Q(max(0, L - N), 365))
        g = replace(base, a1=base.a1 * theta, r1=base.r1 * theta)
        s = solve_timing(g, "both", "L<=N", Q(1), p0, ante_p=False)  # after notice only, degraded
        rows.append(dict(table="gap_variant", regime="after_notice_only_partial", pi="1",
                         variant=f"N={N},L={L},theta={theta}", allocation="both", build=s["build"],
                         q=s["q"], price=str(s["price"]), mode=s["mode"], W_shock=str(s["resident"]),
                         profit=str(s["profit"]), G_shock=str(s["global_welfare"]),
                         expected_investor=str(s["expected"])))
    # keep-prior-terms benchmark: an enforceable right to reject the change and keep
    # (p0, q=0) for the renewal term, supplier cannot exit before the term ends.
    rows.append(dict(table="keep_prior_terms", regime="no_supplier_exit", pi="1", variant="p0=4",
                     allocation="any_holder_of_the_right", build="none", q=0, price="4",
                     mode="incumbent", W_shock=str(base.V - p0), profit=str(p0 - base.c),
                     G_shock=str(base.V - base.c), expected_investor=""))
    s = solve_timing(base, "none", "static", Q(1), p0)
    rows.append(dict(table="keep_prior_terms", regime="supplier_may_exit_at_renewal", pi="1",
                     variant="p0=4 (right held by agency; reduces to refusal)", allocation="none",
                     build=s["build"], q=s["q"], price=str(s["price"]), mode=s["mode"],
                     W_shock=str(s["resident"]), profit=str(s["profit"]),
                     G_shock=str(s["global_welfare"]), expected_investor=str(s["expected"])))
    return rows


def main():
    n = run_checks()
    rows = grid()
    summ = summarise(rows)
    ex = example()
    with (HERE / "timing_grid.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with (HERE / "timing_results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(summ)
    with (HERE / "timing_example.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ex[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(ex)
    print(json.dumps(dict(status="all exact assertions passed", checks=n), indent=1))
    for s in summ:
        print(s)
    for r in ex:
        print(r)


if __name__ == "__main__":
    main()
