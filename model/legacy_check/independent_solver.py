#!/usr/bin/env python3
"""Independent re-implementation of the finite game in Sections 5.1-5.3 of
manuscript 0.8, written from the manuscript text only, in exact rational
arithmetic (fractions.Fraction). Standard library only.

Usage:
    python3 independent_solver.py [path/to/dir/containing/check_ai_dependence_model.py]

Without a path it runs the self-contained checks (worked example, Corollary 1,
surplus sign). With a path it also compares against the program under review and
writes disagreements.csv and results.json next to this file.

Game as read from the text (section references are to the manuscript):
  5.1  K_x = F + k x; R_x = B - K_x; x with K_x > B is not available.
       Alternatives: shutdown (value 0, cost 0); legacy (a0, r0) if r0 <= R_x;
       new (a1, r1) if x = 1 and r1 <= R_x. O_x = best net value.
       Fallback choice: max net value, then min expenditure, shutdown on an
       exact zero tie. Incumbent: A = V-p-K, W = A-hq, pi = p-c+bq,
       G = V-(c-bq)-hq-K. Fallback: A = W = G = O-K, pi = 0.
  5.2  Stage 1 investment authority picks x (agency: max A; residents: max W;
       x = 0 on ties). Stage 2 supplier offers (p, q), p >= 0, p <= R_x, or
       declines. Stage 3 acceptance authority accepts iff
       V - p - d h q >= O_x (acceptance at indifference); else fallback.
       Supplier: greatest nonnegative profit (trade at zero profit), q = 0 on
       equal-profit ties, declines if no nonnegative-profit acceptable offer.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

ZERO = Fr(0)
MUTATE = None   # set only by the mutation test: deliberately wrong tie rules
KEYS = ("V", "c", "b", "h", "B", "k", "a0", "r0", "a1", "r1", "F")
EXAMPLE = dict(V=Fr(10), c=Fr(6), b=Fr(2), h=Fr(3), B=Fr(5), k=Fr(1, 2),
               a0=ZERO, r0=ZERO, a1=Fr(5), r1=Fr(1), F=ZERO)
# (investment by residents, acceptance by residents)
ALLOCATIONS = {"neither": (False, False), "financing_only": (True, False),
               "refusal_only": (False, True), "both": (True, True)}


# ---------------------------------------------------------------- stage 3 --
def best_alternative(P, x):
    """Acceptance-stage outside option at capacity x, or None if x unaffordable."""
    spent = P["F"] + P["k"] * x
    if spent > P["B"]:
        return None
    cash = P["B"] - spent
    menu = [("shutdown", ZERO, ZERO)]            # (label, gross value, running cost)
    if P["r0"] <= cash:
        menu.append(("non_ai", P["a0"], P["r0"]))
    if x == 1 and P["r1"] <= cash:
        menu.append(("fallback", P["a1"], P["r1"]))
    top = max(v - r for _, v, r in menu)
    tied = [m for m in menu if m[1] - m[2] == top]
    cheapest = min(r for _, _, r in tied)
    tied = [m for m in tied if m[2] == cheapest]
    # shutdown on an exact zero tie; any residual tie (legacy vs new with equal
    # net value and cost) is payoff-irrelevant; take the first listed.
    label, value, cost = tied[0]
    return dict(spent=spent, cash=cash, O=top, label=label, value=value, cost=cost)


def accepts(P, d, O, p, q):
    return P["V"] - p - (P["h"] * q if d else ZERO) >= O


# ---------------------------------------------------------------- stage 2 --
def supplier_offer(P, d, alt):
    """Supplier's optimal (profit, q, p) or None to decline.

    For each q the acceptable, affordable price set is an interval
    {p : 0 <= p <= cash, V - p - d h q >= O}. Profit is strictly increasing in
    p, so the optimum is the interval's upper end. The upper end is found among
    the constraint breakpoints and then confirmed by a perturbation test
    (no acceptable affordable price above it), without assuming the closed form.
    """
    best = None
    for q in (0, 1):
        harm = P["h"] * q if d else ZERO
        breakpoints = {ZERO, alt["cash"], P["V"] - alt["O"] - harm}
        ok = [p for p in breakpoints
              if ZERO <= p <= alt["cash"] and accepts(P, d, alt["O"], p, q)]
        if not ok:
            continue
        p = max(ok)
        eps = Fr(1, 10**9)
        assert not (p + eps <= alt["cash"] and accepts(P, d, alt["O"], p + eps, q))
        profit = p - (P["c"] - P["b"] * q)
        if profit < 0 or (MUTATE == "decline_at_zero" and profit == 0):
            continue
        # strict improvement needed to move from q=0 to q=1 (q=0 on ties)
        if best is None or profit > best[0] or (MUTATE == "q_tie_to_1" and profit == best[0]):
            best = (profit, q, p)
    return best


# ---------------------------------------------------------------- stage 1 --
def continuation(P, x, d):
    alt = best_alternative(P, x)
    if alt is None:
        return None
    K = alt["spent"]
    offer = supplier_offer(P, d, alt)
    if offer is not None:
        profit, q, p = offer
        A = P["V"] - p - K
        W = A - P["h"] * q
        G = P["V"] - (P["c"] - P["b"] * q) - P["h"] * q - K
        mode = "incumbent"
    else:
        profit, q, p = ZERO, 0, ZERO
        A = W = G = alt["O"] - K
        mode = alt["label"]
    assert W + profit == G
    assert K + (p if offer else alt["cost"]) <= P["B"]
    return dict(x=x, d=d, q=q, price=p, profit=profit, agency=A, resident=W,
                surplus=G, mode=mode, O=alt["O"])


def equilibrium(P, invest_res, accept_res, capacity=True, force_x=None):
    d = 1 if accept_res else 0
    xs = (force_x,) if force_x is not None else ((0, 1) if capacity else (0,))
    best = None
    for x in xs:
        s = continuation(P, x, d)
        if s is None:
            continue
        score = s["resident"] if invest_res else s["agency"]
        if best is None or score > best[0] or (MUTATE == "build_on_tie" and score == best[0]):  # x = 0 kept on ties
            best = (score, s)
    return None if best is None else best[1]


# ------------------------------------------------------------- the region --
def in_region(P, require_operable=True):
    C = P["c"] - P["b"]
    O0 = best_alternative(P, 0)
    alt1 = best_alternative(P, 1)
    if O0 is None or alt1 is None:
        return False
    O1 = alt1["O"]
    ok = (P["F"] == 0 and O0["O"] == 0 and C < P["B"] - P["k"] < P["B"] < P["c"]
          and P["V"] - P["h"] > P["B"] and P["V"] - P["h"] - C < O1 < P["V"] - (P["B"] - P["k"]))
    if require_operable:
        ok = ok and P["r1"] <= P["B"] - P["k"] and alt1["label"] == "fallback"
    return ok


# ------------------------------------------------------------ random draws --
def rat(rng, lo, hi, coarse):
    """Rational in [lo, hi]; coarse draws use denominators 1, 2, 4 (tie-rich)."""
    den = rng.choice((1, 2, 4)) if coarse else rng.randint(1, 60)
    lo_n, hi_n = -(-lo * den // 1), hi * den // 1
    if hi_n < lo_n:
        return Fr(lo)
    return Fr(rng.randint(int(lo_n), int(hi_n)), den)


def rat_open(rng, lo, hi):
    """Rational strictly inside (lo, hi)."""
    t = Fr(rng.randint(1, 999), 1000)
    return lo + (hi - lo) * t


def draw_general(rng):
    coarse = rng.random() < 0.5
    V = rat(rng, 0, 20, coarse)
    c = rat(rng, 0, 15, coarse)
    b = rat(rng, 0, c, coarse)
    P = dict(V=V, c=c, b=b, h=rat(rng, 0, 10, coarse), B=rat(rng, 0, 15, coarse),
             k=rat(rng, 0, 5, coarse), F=ZERO if rng.random() < 0.6 else rat(rng, 0, 3, coarse),
             a1=rat(rng, 0, 12, coarse), r1=rat(rng, 0, 5, coarse), a0=ZERO, r0=ZERO)
    if rng.random() < 0.5:
        P["a0"], P["r0"] = rat(rng, 0, 8, coarse), rat(rng, 0, 5, coarse)
    return P


def draw_region(rng):
    """Constructive draw strictly inside the Corollary 1 region (incl. r1 <= B-k)."""
    C = rat_open(rng, Fr(0), Fr(8)) if rng.random() < 0.9 else ZERO
    h = rat_open(rng, Fr(0), Fr(10))
    m = rat_open(rng, C, C + h)                       # m = B - k, C < m < C + h
    k = rat_open(rng, Fr(0), Fr(4))
    B = m + k
    b = B - C + rat_open(rng, Fr(0), Fr(5))           # c = C + b > B
    c = C + b
    V = B + h + rat_open(rng, Fr(0), Fr(10))          # V - h > B
    O1 = rat_open(rng, V - h - C, V - m)              # nonempty since m < C + h
    r1 = rat_open(rng, Fr(0), m) if rng.random() < 0.9 else m   # operable
    P = dict(V=V, c=c, b=b, h=h, B=B, k=k, F=ZERO, a1=O1 + r1, r1=r1, a0=ZERO, r0=ZERO)
    u = rng.random()                                   # ways to have O0 = 0
    if u < 0.2:
        P["r0"] = rat_open(rng, Fr(0), Fr(5)); P["a0"] = P["r0"] * rat_open(rng, Fr(0), Fr(1))
    elif u < 0.35:
        P["r0"] = B + rat_open(rng, Fr(0), Fr(3)); P["a0"] = P["r0"] + rat_open(rng, Fr(0), Fr(5))
    assert in_region(P), P
    return P


# ------------------------------------------------------------- comparisons --
FIELDS = ("x", "q", "price", "resident", "profit", "agency", "mode")


def compare_one(M, P, rows, tag, draw_id):
    """Compare the four allocations plus the two no-capacity configurations."""
    theirs_p = M.Parameters(**P)
    configs = [(n, inv, acc, True) for n, (inv, acc) in ALLOCATIONS.items()]
    configs += [("nocap_agency_accept", False, False, False),
                ("nocap_resident_accept", True, True, False)]
    out = {}
    for name, inv, acc, cap in configs:
        mine = equilibrium(P, inv, acc, cap)
        theirs = M.solve_investment(theirs_p, acc, inv, cap)
        if mine is None or theirs is None:
            agree = (mine is None) == (theirs is None)
            diff = [] if agree else ["feasibility"]
        else:
            diff = [f for f in FIELDS if mine[f] != theirs[f]]
            if mine["surplus"] != theirs["global_welfare"]:
                diff.append("surplus")
        out[name] = not diff
        if diff:
            rows.append(dict(sample=tag, draw=draw_id, config=name, fields=";".join(diff),
                             **{k: str(P[k]) for k in KEYS},
                             mine=None if mine is None else {f: str(mine[f]) for f in FIELDS},
                             theirs=None if theirs is None else {f: str(theirs[f]) for f in FIELDS}))
    return out


def prop2_check(P):
    """Returns (ok, details). Uses only the independent solver."""
    r = {n: equilibrium(P, *a) for n, a in ALLOCATIONS.items()}
    ok = (r["neither"]["q"] == 1 and r["financing_only"]["q"] == 1
          and r["refusal_only"]["q"] == 1 and r["both"]["q"] == 0
          and r["both"]["x"] == 1 and r["both"]["mode"] == "fallback")
    # "resident acceptance authority without capacity" read as capacity unavailable
    nocap = equilibrium(P, True, True, capacity=False)
    ok_nocap = nocap["q"] == 1
    # forced capacity under agency acceptance still q=1 (text after the proof)
    forced = continuation(P, 1, 0)
    ok_forced = forced["q"] == 1
    # the financing-only no-build is an exact investment tie (Delta W = 0)
    tie = continuation(P, 1, 0)["resident"] == continuation(P, 0, 0)["resident"]
    C = P["c"] - P["b"]
    O1 = P["a1"] - P["r1"]
    dG = r["both"]["surplus"] - r["neither"]["surplus"]
    formula = O1 - P["k"] - (P["V"] - C - P["h"])
    return dict(prop2=ok, nocap=ok_nocap, forced=ok_forced, fin_tie=tie,
                dG_formula=(dG == formula),
                sign_claim=((dG > 0) == (O1 > P["V"] - P["h"] - C + P["k"])),
                dG_neg=dG < 0, dG_zero=dG == 0,
                welfare_gain=r["both"]["resident"] - r["neither"]["resident"])


def coverage(P, cov):
    """Count the tie/boundary situations a draw exercises (all x, d)."""
    for x in (0, 1):
        alt = best_alternative(P, x)
        if alt is None:
            continue
        cov["states"] += 1
        if alt["O"] == 0 and any(v - r == 0 for v, r in
                                 [(P["a0"], P["r0"])] * (P["r0"] <= alt["cash"])
                                 + [(P["a1"], P["r1"])] * (x == 1 and P["r1"] <= alt["cash"])):
            cov["fallback_zero_tie"] += 1
        for d in (0, 1):
            prof = {}
            for q in (0, 1):
                acc = P["V"] - alt["O"] - (P["h"] * q if d else ZERO)
                p = min(alt["cash"], acc)
                if p >= 0:
                    prof[q] = p - P["c"] + P["b"] * q
                    if prof[q] >= 0:
                        cov["cash_binds" if alt["cash"] < acc else "accept_binds" if acc < alt["cash"] else "both_bind"] += 1
            if 0 in prof and 1 in prof and prof[0] == prof[1] >= 0:
                cov["q_profit_tie"] += 1
            if prof and max(prof.values()) == 0:
                cov["zero_profit_trade"] += 1
    for inv, acc in ALLOCATIONS.values():
        a, b = continuation(P, 0, int(acc)), continuation(P, 1, int(acc))
        if a and b and (a["resident"] if inv else a["agency"]) == (b["resident"] if inv else b["agency"]):
            cov["investment_tie"] += 1


def mutation_test(M, n=4000):
    """Deliberately break one tie rule in this solver; count detected draws."""
    global MUTATE
    out = {}
    for mut in ("q_tie_to_1", "decline_at_zero", "build_on_tie"):
        MUTATE = mut
        rng = random.Random(99)
        hit = 0
        for i in range(n):
            P = draw_general(rng) if i % 2 else draw_region(rng)
            rows = []
            compare_one(M, P, rows, "mut", i)
            hit += bool(rows)
        out[mut] = f"{hit}/{n}"
    MUTATE = None
    return out


def main():
    here = Path(__file__).resolve().parent
    M = None
    if len(sys.argv) > 1:
        sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
        import check_ai_dependence_model as M  # noqa: E402
    res = {}

    # (a) worked example
    ex = {}
    for n, a in ALLOCATIONS.items():
        s = equilibrium(EXAMPLE, *a)
        ex[n] = {f: str(s[f]) for f in ("x", "q", "price", "resident", "profit", "surplus", "mode")}
    res["worked_example"] = ex
    assert [ex[n]["resident"] for n in ALLOCATIONS] == ["2", "2", "2", "7/2"]
    assert [ex[n]["surplus"] for n in ALLOCATIONS] == ["3", "3", "3", "7/2"]
    assert [ex[n]["profit"] for n in ALLOCATIONS] == ["1", "1", "1", "0"]
    res["worked_example_F2_both"] = str(equilibrium(dict(EXAMPLE, F=Fr(2)), True, True)["resident"])
    res["worked_example_B20"] = {n: {f: str(equilibrium(dict(EXAMPLE, B=Fr(20)), *a)[f])
                                     for f in ("x", "q", "resident", "surplus")}
                                 for n, a in ALLOCATIONS.items()}

    rng = random.Random(20260930)
    disagreements, agree_counts = [], {}
    samples = [("general", draw_general, 15000), ("region", draw_region, 10000)]
    prop = dict(n=0, prop2=0, nocap=0, forced=0, fin_tie=0, dG_formula=0, sign_claim=0,
                dG_neg=0, dG_zero=0)
    general_in_region = 0
    from collections import Counter
    cov = Counter()
    for tag, drawer, n in samples:
        cnt = {}
        for i in range(n):
            P = drawer(rng)
            coverage(P, cov)
            if M is not None:
                for cfg, ok in compare_one(M, P, disagreements, tag, i).items():
                    t = cnt.setdefault(cfg, [0, 0]); t[0] += ok; t[1] += 1
            if in_region(P):
                general_in_region += tag == "general"
                chk = prop2_check(P)
                prop["n"] += 1
                for key in prop:
                    if key != "n":
                        prop[key] += bool(chk[key])
                if not chk["prop2"]:
                    disagreements.append(dict(sample=tag, draw=i, config="PROP2_FAIL", fields="",
                                              **{k: str(P[k]) for k in KEYS}, mine=None, theirs=None))
        agree_counts[tag] = cnt
    res["agreement"] = agree_counts
    res["coverage_counts"] = dict(cov)
    res["prop2"] = prop
    res["general_draws_inside_region"] = general_in_region

    # Operability condition: what happens in the displayed inequalities without r1 <= B-k
    rng2 = random.Random(7)
    fail = total = 0
    for _ in range(3000):
        P = draw_region(rng2)
        m = P["B"] - P["k"]
        O1 = P["a1"] - P["r1"]
        P["r1"] = m + rat_open(rng2, Fr(0), Fr(3)); P["a1"] = O1 + P["r1"]
        total += 1
        fail += equilibrium(P, True, True)["q"] == 1
    res["without_operability_r1_gt_B_minus_k"] = dict(draws=total, joint_rights_leave_q1=fail)

    # Boundary draws: region with O1 exactly at the lower bound (excluded, strict)
    rng3 = random.Random(11)
    lower = upper = 0
    for _ in range(2000):
        P = draw_region(rng3)
        C = P["c"] - P["b"]
        P["a1"] = P["V"] - P["h"] - C + P["r1"]
        lower += equilibrium(P, True, True)["q"] == 0
        P["a1"] = P["V"] - (P["B"] - P["k"]) + P["r1"]
        upper += equilibrium(P, False, True)["q"] == 1
    res["boundary_O1_eq_lower_both_gives_q0"] = f"{lower}/2000"
    res["boundary_O1_eq_upper_refusal_only_gives_q1"] = f"{upper}/2000"

    if M is not None:
        res["mutation_test_draws_detected"] = mutation_test(M)
        with (here / "disagreements.csv").open("w", newline="") as fh:
            cols = ["sample", "draw", "config", "fields", *KEYS, "mine", "theirs"]
            w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            for row in disagreements:
                w.writerow({**row, "mine": json.dumps(row["mine"]), "theirs": json.dumps(row["theirs"])})
        res["n_disagreement_rows"] = len(disagreements)
    (here / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
