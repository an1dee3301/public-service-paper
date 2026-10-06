#!/usr/bin/env python3
"""Exact, synthetic finite-game checks; no empirical calibration or estimation.

Run from any directory. Standard library only. Writes the named model outputs;
never reads or modifies raw research data. See model/MANIFEST.md for the released checking map.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path


def q(value):
    return Q(str(value))


@dataclass(frozen=True)
class Parameters:
    V: Q = Q(10)
    c: Q = Q(6)
    b: Q = Q(2)
    h: Q = Q(3)
    B: Q = Q(5)
    k: Q = Q(1, 2)
    a0: Q = Q(0)
    r0: Q = Q(0)
    a1: Q = Q(5)
    r1: Q = Q(1)
    F: Q = Q(0)

    def __post_init__(self):
        assert all(v >= 0 for v in self.__dict__.values())
        assert self.c >= self.b, "Review removal saves at most total service cost."


def make(**kwargs):
    return Parameters(**{k: q(v) for k, v in kwargs.items()})


def fallback(p, x):
    """Retain the legacy option after investment; shutdown is always available."""
    K = p.F + p.k * x
    if K > p.B:
        return None
    options = [(Q(0), Q(0), Q(0), "shutdown")]
    if p.r0 <= p.B - K:
        options.append((p.a0 - p.r0, -p.r0, p.a0, "non_ai"))
    if x and p.r1 <= p.B - K:
        options.append((p.a1 - p.r1, -p.r1, p.a1, "fallback"))
    # Higher net value, then lower cash cost; shutdown wins exact zero ties.
    selected = max(enumerate(options), key=lambda z: (z[1][0], z[1][1], -z[0]))[1]
    return dict(O=selected[0], expense=-selected[1], value=selected[2], mode=selected[3])


def solve_state(p, x, resident_acceptance):
    """Backward-induction solution. Trade at zero profit; q=0 on profit ties."""
    alt = fallback(p, x)
    if alt is None:
        return None
    K = p.F + p.k * x
    R = p.B - K
    offers = []
    for burden in (0, 1):
        price = min(R, p.V - alt["O"] - int(resident_acceptance) * p.h * burden)
        profit = price - p.c + p.b * burden
        if price >= 0 and profit >= 0:
            offers.append((profit, -burden, price, burden))
    if offers:
        profit, _, price, burden = max(offers)
        value, expense, mode = p.V, price, "incumbent"
        operating = p.c - p.b * burden
    else:
        profit, price, burden = Q(0), Q(0), 0
        value, expense, mode = alt["value"], alt["expense"], alt["mode"]
        operating = expense
    agency = value - expense - K
    resident = agency - p.h * burden
    global_welfare = value - operating - K - p.h * burden
    return dict(x=x, resident_acceptance=bool(resident_acceptance), K=K, R=R,
                O=alt["O"], mode=mode, q=burden, price=price, expense=expense,
                value=value, operating=operating, agency=agency, resident=resident,
                profit=profit, global_welfare=global_welfare)


def solve_investment(p, resident_acceptance=False, resident_investment=False,
                     capacity_available=True, rebate=False):
    states = [solve_state(p, x, resident_acceptance)
              for x in ((0, 1) if capacity_available else (0,))]
    states = [s for s in states if s is not None]
    if not states:
        return None
    objective = "resident" if resident_investment else "agency"
    # Rebate option only for slack-budget comparison or a separately fixed cap;
    # it does NOT solve rebate-induced changes to the statutory spending cap.
    return max(states, key=lambda s: (s[objective] + (s["profit"] if rebate else 0), -s["x"]))


def resource_benchmark(p):
    """Planner can procure at avoidable cost, with the same cash constraint.

    This is a complete-contract/resource benchmark, not a decentralized
    equilibrium; it includes the non-AI/capacity/shutdown alternatives.
    """
    choices = []
    for x in (0, 1):
        alt = fallback(p, x)
        if alt is None:
            continue
        K = p.F + p.k * x
        choices.append(dict(welfare=alt["O"] - K, x=x, mode=alt["mode"], q=0))
        for burden in (0, 1):
            cost = p.c - p.b * burden
            if cost <= p.B - K:
                choices.append(dict(welfare=p.V - cost - p.h * burden - K,
                                    x=x, mode="incumbent", q=burden))
    return max(choices, key=lambda s: (s["welfare"], -s["x"], -s["q"])) if choices else None


def no_adoption_value(p):
    # Give opting out access to the same technology for building a fallback,
    # without imposing the adopted institution's governance overhead.
    outside = replace(p, F=Q(0))
    return max(fallback(outside, x)["O"] - outside.k * x
               for x in (0, 1) if fallback(outside, x) is not None)


def adoption(p, chosen, early_net_gain, objective="agency"):
    """Optional prehistory: anticipated early benefit less integration cost.

    The no-AI early benefit is normalized to zero. Strict gain is necessary;
    opt out at a tie. This does not infer an observed subsidy/lock-in trap.
    """
    outside = no_adoption_value(p)
    value = q(early_net_gain) + chosen[objective]
    return dict(adopt=value > outside, value=value, outside=outside,
                threshold=outside - chosen[objective])


def verify_state(p, state):
    assert state is not None
    x, d = state["x"], state["resident_acceptance"]
    alt = fallback(p, x)
    assert state["K"] + state["expense"] <= p.B
    assert state["resident"] + state["profit"] == state["global_welfare"]
    assert state["agency"] - p.h * state["q"] == state["resident"]
    assert state["profit"] >= 0
    # Independently enumerate rational price grids PLUS every acceptance/cap
    # boundary. Linear profits ensure no missing interior price can improve.
    candidate_prices = {Q(i, 4) for i in range(int(4 * p.B) + 1)}
    candidate_prices.add(state["R"])
    for burden in (0, 1):
        candidate_prices.add(p.V - alt["O"] - int(d) * p.h * burden)
    alternatives = [(Q(0), -2, Q(0), None)]  # abstention loses zero-profit tie
    for burden, price in product((0, 1), candidate_prices):
        if not (0 <= price <= state["R"]):
            continue
        decision_value = p.V - price - int(d) * p.h * burden
        if decision_value < alt["O"]:
            continue
        profit = price - p.c + p.b * burden
        alternatives.append((profit, -burden, price, burden))
    best = max(alternatives)
    assert best[0] == state["profit"], (p, state, best)
    if best[3] is None:
        assert state["mode"] != "incumbent"
    else:
        assert state["mode"] == "incumbent"
        assert (best[3], best[2]) == (state["q"], state["price"])


def serial(value):
    if isinstance(value, Q):
        return int(value) if value.denominator == 1 else float(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def illustrate():
    rows = []
    def add(name, p, institution, state, note):
        assert state is not None
        verify_state(p, state)
        rows.append(dict(scenario=name, institution=institution,
                         parameters=serial(p.__dict__), **serial(state), note=note))

    base = make()
    configs = [
        ("commercial", False, False, False),
        ("capacity_authority_only", False, False, True),
        ("resident_acceptance_only", True, True, False),
        ("joint_resident_control", True, True, True),
        ("resident_financing_only", False, True, True),
        ("resident_acceptance_agency_financing", True, False, True),
    ]
    for title, accept, invest, available in configs:
        add("budget_complementarity", base, title,
            solve_investment(base, accept, invest, available),
            "Synthetic common parameters; investment endogenous; no-build at investment ties.")
    add("budget_complementarity", base, "capacity_forced_for_factorial_comparison",
        solve_state(base, 1, False), "Forced x=1 is a diagnostic, not the agency equilibrium.")
    nominal = replace(base, F=q(.2))
    add("budget_complementarity", nominal, "nominal_portability_fee",
        solve_investment(nominal, False, False, False),
        "A legal label changes no feasible action; the fee only spends budget.")

    slack = replace(base, B=q(20))
    for title, accept, invest, available in configs[:4]:
        add("slack_budget", slack, title, solve_investment(slack, accept, invest, available),
            "Rights can remove q without capacity when harmless provision is financeable.")

    under = make(V=10, c=6, b=2, h=5, B=20, k=8, a1=8, r1=1)
    add("fixed_acceptance_investment_wedge", under, "agency_investor",
        solve_investment(under), "Agency does not buy x: fiscal return 7 is below cost 8.")
    add("fixed_acceptance_investment_wedge", under, "resident_investor",
        solve_investment(under, False, True),
        "Resident control of financing buys x: avoidance of harm 5 reverses the comparison.")

    over = replace(base, F=q(2))
    add("governance_cost_reversal", over, "costly_joint_resident_control",
        solve_investment(over, True, True),
        "High governance overhead lowers welfare below commercial baseline; adoption optional.")
    low_quality = replace(base, a1=q(2))
    add("low_fallback_quality", low_quality, "joint_resident_control",
        solve_investment(low_quality, True, True),
        "A poor alternative does not warrant investment; institutional superiority is absent.")

    q_high_b = make(V=10, c=6, b=4, h=1, B=20, k=6, a1=4, r1=1)
    add("efficient_review_removal", q_high_b, "resident_acceptance_only",
        solve_investment(q_high_b, True, True, False),
        "Resident authority can accept q when its resource saving exceeds its modeled harm.")

    rent = make(V=10, c=3, b=1, h=0, B=30, k=1, a1=4, r1=1)
    for rebated in (False, True):
        s = solve_investment(rent, False, False, True, rebate=rebated)
        add("introductory_competition", rent,
            "full_rebate" if rebated else "no_rebate", s,
            ("Rebate equals continuation profit; total agency/resident value is reported separately."
             if rebated else "Capacity saves national procurement rents but has a real resource cost."))
        rows[-1]["introductory_rebate"] = serial(s["profit"] if rebated else Q(0))
        rows[-1]["lifecycle_agency"] = serial(s["agency"] + (s["profit"] if rebated else 0))
        rows[-1]["lifecycle_resident"] = serial(s["resident"] + (s["profit"] if rebated else 0))
        rows[-1]["lifecycle_supplier_profit"] = serial(Q(0) if rebated else s["profit"])
    return rows


def run_checks():
    state_checks = 0
    # 3,072 candidate states (2,816 feasible) cover infeasible capital, payment
    # ceilings, weak/strong outside options, zero profit, ties and legacy fallback.
    for B, k, a1, h, c, b in product((2, 5, 9, 20), (0, 1, 6),
                                     (0, 3, 9, 13), (0, 1, 3, 8), (3, 6), (0, 2)):
        p = make(B=B, k=k, a1=a1, h=h, c=c, b=b, a0=2, r0=1)
        for x, d in product((0, 1), (False, True)):
            s = solve_state(p, x, d)
            if s is None:
                assert p.F + p.k * x > p.B
                continue
            verify_state(p, s)
            state_checks += 1
        for d, investor in product((False, True), repeat=2):
            best = solve_investment(p, d, investor)
            if best is None:
                continue
            metric = "resident" if investor else "agency"
            for x in (0, 1):
                s = solve_state(p, x, d)
                if s:
                    assert best[metric] >= s[metric]
            s0, s1 = solve_state(p, 0, d), solve_state(p, 1, d)
            if s0 and s1:
                da = s1["agency"] - s0["agency"]
                dr = s1["resident"] - s0["resident"]
                assert dr == da + p.h * (s0["q"] - s1["q"])
            assert resource_benchmark(p)["welfare"] >= best["resident"]

    base = make()
    commercial = solve_investment(base, capacity_available=False)
    authority = solve_investment(base)
    rights = solve_investment(base, True, True, False)
    joint = solve_investment(base, True, True)
    forced = solve_state(base, 1, False)
    assert (commercial["resident"], rights["resident"], forced["resident"], joint["resident"]) == (2, 2, 2, Q(7, 2))
    assert (authority["x"], joint["x"]) == (0, 1)
    assert joint["global_welfare"] - commercial["global_welfare"] == Q(1, 2)
    assert solve_investment(base, True, False)["x"] == 0
    assert solve_investment(base, False, True)["x"] == 0
    # Complete contracts can replicate every decision right in this model:
    # institutions with identical rights, costs and technology have identical
    # solution inputs and outputs. There is deliberately no ownership flag.

    rent = make(V=10, c=3, b=1, h=0, B=30, k=1, a1=4, r1=1)
    assert solve_investment(rent)["x"] == 1
    assert solve_investment(rent, rebate=True)["x"] == 0
    assert adoption(base, commercial, 0)["adopt"]
    assert not adoption(base, commercial, 0, "resident")["adopt"]
    assert not adoption(base, joint, 0, "resident")["adopt"]  # tie: opt out
    assert adoption(base, joint, 1, "resident")["adopt"]
    return state_checks


def sensitivity():
    rows = []
    for B, k, a1, F in product((4, 5, 6, 8, 12), (0, .5, 2, 5), (2, 5, 8), (0, .5, 2)):
        p = make(B=B, k=k, a1=a1, F=F)
        commercial = solve_investment(replace(p, F=Q(0)), capacity_available=False)
        joint = solve_investment(p, True, True)
        if joint is None:
            continue
        rows.append(dict(B=B, k=k, a1=a1, governance_cost=F,
                         commercial_resident=serial(commercial["resident"]),
                         joint_resident=serial(joint["resident"]),
                         resident_difference=serial(joint["resident"] - commercial["resident"]),
                         commercial_global=serial(commercial["global_welfare"]),
                         joint_global=serial(joint["global_welfare"]),
                         joint_x=joint["x"], joint_q=joint["q"], joint_mode=joint["mode"]))
    return rows


def main():
    checked = run_checks()
    rows = illustrate()
    sens = sensitivity()
    counts = {"joint_better": sum(r["resident_difference"] > 0 for r in sens),
              "equal": sum(r["resident_difference"] == 0 for r in sens),
              "joint_worse": sum(r["resident_difference"] < 0 for r in sens)}
    output = Path(__file__).resolve().parents[1] / "data/processed/ai_dependence/model"
    output.mkdir(parents=True, exist_ok=True)
    result = dict(status="all exact assertions passed", empirical=False,
                  arithmetic="fractions.Fraction; output decimals for display only",
                  checked_states=checked, sensitivity_rows=len(sens),
                  sensitivity_ranking_counts=counts,
                  limitations=["Synthetic parameters; grid counts are not probabilities.",
                               "No measured population, estimated parameter or AI-specific theorem.",
                               "Competition rebate comparison requires unchanged feasibility; demonstrated under slack budgets."],
                  illustrations=rows)
    (output / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    with (output / "sensitivity.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sens[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sens)
    columns = ["scenario", "institution", "x", "q", "mode", "price", "K", "O",
               "agency", "resident", "profit", "global_welfare"]
    with (output / "illustrations.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Synthetic model validation", "", "No observations or calibrated estimates.", "",
             f"All assertions passed for {checked:,} exact continuation states.",
             f"The declared sensitivity grid has {len(sens)} rows: {counts}.",
             "Counts summarize this arbitrary grid, not a probability distribution.", "",
             "| Scenario / institution | x | q | Mode | Resident | Supplier | Global |",
             "|---|---:|---:|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['scenario']} / {row['institution']} | {row['x']} | {row['q']} | "
                     f"{row['mode']} | {row['resident']} | {row['profit']} | {row['global_welfare']} |")
    lines += ["", "The full-rebate row above reports continuation payoffs. Its lifetime agency/resident",
              "payoff adds the recorded rebate; lifetime supplier profit is zero. See validation.json.", ""]
    (output / "VALIDATION.md").write_text("\n".join(lines))
    print(json.dumps({k: result[k] for k in ("status", "checked_states", "sensitivity_rows", "sensitivity_ranking_counts")}))


if __name__ == "__main__":
    main()
