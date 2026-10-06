#!/usr/bin/env python3
"""Historical independent exact solver. Written before opening the earlier derivation.

No third-party modules or imports from other workers. Continuous monopoly
optimization uses all breakpoints of piecewise-affine profit, not a q grid.
Run from any directory: python3 /absolute/path/to/solver.py
Only writes results.json beside this script.
"""
from fractions import Fraction as Q
from dataclasses import dataclass, replace
from itertools import product
from pathlib import Path
import json


@dataclass(frozen=True)
class Game:
    V: Q
    c: Q
    b: Q
    h: Q
    B: Q
    k: Q
    a: Q
    r: Q

    @property
    def H(self):
        return self.V - self.h - self.c + self.b

    @property
    def O(self):
        return self.a - self.r

    def region(self):
        return (self.c-self.b < self.B-self.k < self.B < self.c
                and self.V-self.h > self.B and self.r <= self.B-self.k
                and self.H < self.O < self.V-self.B+self.k)


@dataclass(frozen=True)
class Outcome:
    W: Q
    q: Q
    p: Q
    profit: Q
    fallback: bool


def continuation(g, P, O, institution='monopoly', beta=Q(1), continuous=False):
    """Resident acceptance. Capital absent here; accepted zero profit trades.

    O is a feasible refusal value, including shutdown. For cost competition,
    select the affordable service with maximal resident utility, q=0 on ties.
    Nash bargaining uses supplier share beta of surplus above disagreement,
    capped by P; supplier selects q, minimum q on profit ties.
    """
    assert P >= 0 and O >= 0
    qs = {Q(0), Q(1)}
    if continuous:
        assert institution == 'monopoly'
        # Cash/acceptance kink and zero-profit boundaries on both pieces.
        if g.h:
            qs.add((g.V-O-P)/g.h)
        if g.b:
            qs.add((g.c-P)/g.b)
        if g.b != g.h:
            qs.add((g.c-g.V+O)/(g.b-g.h))
        if g.h:
            qs.add((g.V-O)/g.h)  # nonnegative accepted price boundary
        qs = {q for q in qs if 0 <= q <= 1}
    bids = []
    for q in sorted(qs):
        cost = g.c-g.b*q
        cap = min(P, g.V-g.h*q-O)
        if cap < cost or cap < 0:
            continue
        if institution == 'competition':
            p = cost
        elif institution == 'bargaining':
            surplus = g.V-g.h*q-cost-O
            p = cost + min(beta*surplus, P-cost)
        else:
            p = cap
        bids.append(Outcome(g.V-p-g.h*q, q, p, p-cost, False))
    if not bids:
        return Outcome(O, Q(0), Q(0), Q(0), True)
    if institution == 'competition':
        return max(bids, key=lambda z: (z.W, -z.q))
    return max(bids, key=lambda z: (z.profit, -z.q))


def joint(g, institution='monopoly', beta=Q(1), rho=Q(1),
          cap=None, returned=False, lapse=False, continuous=False):
    """Compare continuations; no build on an exact investment tie.

    Returned/lapsing reserves have operating cash B-k in both states.
    Lapse takes k from residents even when no build: investment increment 0.
    All losses unobserved before a binding refusal; r paid in either outcome.
    """
    P0 = g.B-g.k if returned or lapse else g.B
    P1 = g.B-g.k
    if cap is not None:
        P0, P1 = min(P0, cap), min(P1, cap)
    assert g.k+g.r <= g.B
    Oe = max(Q(0), rho*g.a-g.r)
    out0 = continuation(g, P0, Q(0), institution, beta, continuous)
    out1 = continuation(g, P1, Oe, institution, beta, continuous)
    W0 = out0.W-(g.k if lapse else 0)
    W1 = out1.W-g.k
    build = W1 > W0
    chosen = out1 if build else out0
    return dict(build=build, protect=chosen.q == 0, q=chosen.q,
                W0=W0, W1=W1, W=W1 if build else W0,
                normalized_W0=W0+(g.k if lapse else 0),
                Oe=Oe, kappa=Q(0) if lapse else g.k,
                P1=P1, after_build=out1)


def predicted(g, result, continuous=False):
    barrier = g.H
    if continuous:
        barrier = max(barrier, g.V-result['P1']-
                      g.h*(g.c-result['P1'])/g.b)
    return result['Oe'] > max(barrier, result['normalized_W0']+result['kappa'])


def serialize(z):
    if isinstance(z, Q):
        return str(z)
    if isinstance(z, Outcome):
        return {k: serialize(v) for k, v in vars(z).items()}
    if isinstance(z, dict):
        return {k: serialize(v) for k, v in z.items()}
    if isinstance(z, (tuple, list)):
        return [serialize(v) for v in z]
    return z


def debt_continuation(g, R, O, D, interest):
    """Offer-stage incremental credit; interest after service, principal once."""
    bids = []
    for q in [Q(0), Q(1)]:
        willingness = g.V-g.h*q-O
        if willingness < 0:
            continue
        if willingness <= R:
            p = willingness
        else:
            p = R+min(D,(willingness-R)/(1+interest))
        cost = g.c-g.b*q
        if p >= cost:
            W = g.V-g.h*q-p-interest*max(Q(0),p-R)
            bids.append(Outcome(W,q,p,p-cost,False))
    return max(bids,key=lambda z:(z.profit,-z.q)) if bids else Outcome(O,Q(0),Q(0),Q(0),True)


def run():
    checked, failed = {}, []
    # Grid is defined independently of the lead. Exact base region filter.
    grids = product([Q(8), Q(10), Q(12)], [Q(4), Q(6)],
                    [Q(1), Q(2), Q(3)], [Q(1), Q(2), Q(3), Q(4)],
                    [Q(i, 2) for i in range(4, 12)],
                    [Q(1,4), Q(1,2), Q(3,4), Q(1)],
                    [Q(i,4) for i in range(1,29)], [Q(0), Q(1)])
    region_count = 0
    for vals in grids:
        g = Game(*vals)
        if not g.region():
            continue
        region_count += 1
        C = g.c-g.b
        cases = [('baseline', {}), ('returned', dict(returned=True)),
                 ('lapsing', dict(lapse=True)), ('competition',dict(institution='competition'))]
        cases += [('bargaining',dict(institution='bargaining', beta=beta))
                  for beta in [Q(0), Q(1,12), Q(1,10), Q(1,2), Q(1)]]
        cases += [('cap',dict(cap=p)) for p in [C,(C+g.B-g.k)/2,g.B-g.k]]
        for name, kwargs in cases:
            for rho in [Q(0),Q(1,2),Q(4,5),Q(17,20),Q(9,10),Q(1)]:
                res = joint(g, rho=rho, **kwargs)
                checked[name] = checked.get(name,0)+1
                if res['protect'] != predicted(g,res):
                    failed.append(dict(kind=name,g=vars(g),rho=rho,kwargs=kwargs,result=res))
        # Added after the late lead Addendum 2, without opening its code.
        cont_cases = [('continuous_baseline',{}),
                      ('continuous_returned',dict(returned=True)),
                      ('continuous_lapsing',dict(lapse=True))]
        cont_cases += [('continuous_cap',dict(cap=p))
                       for p in [C,(C+g.B-g.k)/2,g.B-g.k]]
        for name,kwargs in cont_cases:
            for rho in [Q(0),Q(1,2),Q(4,5),Q(17,20),Q(9,10),Q(1)]:
                res = joint(g,rho=rho,continuous=True,**kwargs)
                checked[name] = checked.get(name,0)+1
                if res['protect'] != predicted(g,res,True):
                    failed.append(dict(kind=name,g=vars(g),rho=rho,result=res))

    g = Game(Q(10),Q(6),Q(2),Q(3),Q(5),Q(1,2),Q(5),Q(1))
    assert g.region()
    worked = {}
    for name, kwargs in [
        ('baseline_rho_9_10',dict(rho=Q(9,10))),
        ('competition_rho_9_10',dict(institution='competition',rho=Q(9,10))),
        ('competition_rho_19_20',dict(institution='competition',rho=Q(19,20))),
        ('continuous_rho_17_20',dict(continuous=True,rho=Q(17,20))),
        ('continuous_rho_43_50',dict(continuous=True,rho=Q(43,50))),
        ('bargaining_beta_1_12_rho_17_20',dict(institution='bargaining',beta=Q(1,12),rho=Q(17,20))),
        ('bargaining_beta_1_10_rho_17_20',dict(institution='bargaining',beta=Q(1,10),rho=Q(17,20))),
        ('cap_17_4',dict(cap=Q(17,4))),
        ('lapse_rho_81_100',dict(lapse=True,rho=Q(81,100))),
    ]:
        worked[name] = joint(g,**kwargs)
    assert worked['competition_rho_9_10']['build'] is False
    assert worked['continuous_rho_17_20']['q'] == Q(3,4)
    assert worked['continuous_rho_43_50']['protect'] is True
    assert worked['bargaining_beta_1_12_rho_17_20']['build'] is False
    assert worked['bargaining_beta_1_10_rho_17_20']['protect'] is True

    # Boundary tests choose Oe exactly at each binding bound by solving for rho.
    boundaries = []
    for label, kwargs, iscont in [
        ('binary_deterrence',{},False),
        ('competition_investment',dict(institution='competition'),False),
        ('bargaining_investment',dict(institution='bargaining',beta=Q(1,12)),False),
        ('continuous_deterrence',dict(continuous=True),True),
        ('cap_investment',dict(cap=Q(17,4)),False)]:
        ref = joint(g, **kwargs)
        first = g.H if not iscont else max(g.H,g.V-ref['P1']-g.h*(g.c-ref['P1'])/g.b)
        bound = max(first,ref['W0']+ref['kappa'])
        for delta in [Q(-1,100),Q(0),Q(1,100)]:
            rho = (bound+delta+g.r)/g.a
            res = joint(g,rho=rho,**kwargs)
            assert res['protect'] == (delta>0)
            boundaries.append(dict(label=label,bound=bound,delta=delta,result=res))

    # Stress witnesses INSIDE the base Proposition 2 region, changing protocol.
    # Continuous intensity: binary lemma false even with rho=1 for another base point.
    gc = replace(g,h=Q(4),a=Q(13,4))  # O1=9/4 > H=2; Hc=5/2
    assert gc.region()
    cont_false = joint(gc,continuous=True)
    assert predicted(gc,cont_false) and not cont_false['protect']

    # Partial clause theta=1/10; keep base parameters in Prop 2 region.
    gp = replace(g,b=Q(9,5),h=Q(27,10))
    partial = joint(gp,rho=Q(81,100))  # Oe=61/20; actual H'=31/10
    original_H_prediction = partial['Oe'] > max(g.H,partial['W0']+g.k)
    assert original_H_prediction and not partial['protect']

    # The lead's Nash table omits max(H,...). Its lone investment bound can
    # pass although mutually acceptable harmful trade remains available.
    nash_table = joint(g,institution='bargaining',beta=Q(1),rho=Q(3,4))
    nash_investment_bound = g.H+g.k-min(g.H,g.B-g.c+g.b)
    assert nash_table['Oe'] > nash_investment_bound
    assert not nash_table['protect'] and nash_table['Oe'] <= g.H

    # Limited credit can be included in the abstraction if harmless supply
    # remains unaffordable, the fallback needs no debt, and interest is nonnegative.
    debt_checks = 0
    for D, interest, rho in product([Q(0),Q(1,4),Q(3,4)],
                                   [Q(0),Q(1,5),Q(1)],
                                   [Q(i,100) for i in range(70,101)]):
        assert g.B+D < g.c
        Oe = max(Q(0),rho*g.a-g.r)
        d0 = debt_continuation(g,g.B,Q(0),D,interest)
        d1 = debt_continuation(g,g.B-g.k,Oe,D,interest)
        build = d1.W-g.k > d0.W
        actual = (d1 if build else d0).q == 0
        assert actual == (Oe>max(g.H,d0.W+g.k))
        debt_checks += 1

    # Public success/failure before offers; avoid r on failure as row 5 states.
    rho = Q(9,10)
    good = continuation(g,g.B-g.k,g.O)
    bad = continuation(g,g.B-g.k,Q(0))
    no_build = continuation(g,g.B,Q(0))
    W1 = rho*good.W+(1-rho)*bad.W-g.k
    revealed = dict(build=W1>no_build.W, W0=no_build.W,W1=W1,
                    expected_harm=(1-rho)*g.h, success=good,failure=bad,
                    putative_Oe=rho*g.a-g.r)
    assert revealed['build'] and revealed['expected_harm'] == Q(3,10)

    # Zero interest borrowing D=5 permits the monopolist to prefer harmless trade.
    # D=1 merely makes it affordable: the monopolist still prefers harmful trade.
    borrow = continuation(g,g.B+Q(5),Q(0))
    assert borrow.q == 0 and not borrow.fallback

    # Still B<c, but a cap below C rules out harmful service even without fallback.
    infeasible_cap = continuation(g,Q(7,2),Q(0))
    assert infeasible_cap.fallback
    witnesses = dict(continuous_binary_statement_false=dict(game=vars(gc),result=cont_false),
                     partial_original_H_false=dict(base_game=vars(g),transformed=vars(gp),result=partial),
                     nash_table_missing_H=dict(investment_bound=nash_investment_bound,result=nash_table),
                     revealed_failure=revealed, borrowing=borrow,cap_below_cost=infeasible_cap)
    result = serialize(dict(region_points=region_count,checks=checked,
                            total_checks=sum(checked.values()), mismatches=failed,
                            limited_debt_checks=debt_checks,
                            worked=worked,boundaries=boundaries,witnesses=witnesses))
    Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['region_points','checks','total_checks','mismatches']},indent=2))
    print('Worked cases and protocol witnesses written to results.json')
    assert not failed


if __name__ == '__main__':
    run()
