"""Exact certificates for the report; changed rules are scope attacks, not refutations."""
from solver import *
from itertools import product

witnesses={
 'F_trade_zero':((10,6,2,3,Q(17,4),Q(1,4),Q(13,4)),dict(trade_zero=False)),
 'F_build_tie':((10,6,2,3,5,Q(1,2),Q(11,2)),dict(build_tie=True)),
 'T_build_tie':((10,6,2,3,8,Q(1,2),Q(7,2)),dict(build_tie=True)),
 'T_condition_tie':((10,6,2,3,8,Q(1,2),Q(3,2)),dict(harmless_tie=False)),
 'D_condition_tie':((10,6,2,3,9,Q(1,2),0),dict(harmless_tie=False)),
 'D_trade_zero':((10,6,2,3,9,Q(13,4),3),dict(trade_zero=False)),
}
result={}
for name,(t,change) in witnesses.items():
    assert target(t) and not target(t,**change),(name,t)
    result[name]=dict(parameters=t,changed_rule=change,baseline=outcomes(t),changed=outcomes(t,**change))
strict={
 'T':(10,6,2,3,8,Q(1,2),Q(13,4)),
 'D':(10,6,2,3,Q(19,2),1,Q(1,4)),
}
for name,t in strict.items():
    for build,harmless,zero in product((False,True),repeat=3):
        assert target(t,build_tie=build,harmless_tie=harmless,trade_zero=zero),(name,t)
# The physical alternative a1=9,r1=5 is unaffordable with B=5,k=1/2.
# Actual O1 is therefore zero, not the nominal a1-r1=4.
nominal=(10,6,2,3,5,Q(1,2),4)
actual=nominal[:-1]+(0,)
assert target(nominal) and not target(actual)
# k=0 is a valid extension; no drain, but fallback and threat can survive.
for t in [(10,6,2,3,5,0,4),(10,6,2,3,6,0,3)]:
    assert target(t)
# Reject-at-indifference: no maximum in the resident continuation at B=8,O=0.
# Harmless profit is 2; harmful feasible p<7 has profit<3, with improving offers.
for den in range(2,21):
    p=7-Q(1,den)
    assert p-4>2 and p<7
    p_next=(p+7)/2
    assert p_next<7 and p_next-4>p-4
(HERE/'boundary_certificates.json').write_text(json.dumps(dict(witnesses=result,
 strict_examples= strict,strict_tie_combinations_per_example=8,
 affordability=dict(nominal=outcomes(nominal),actual=outcomes(actual)),
 status='all assertions passed'),indent=2,default=encode)+'\n')
print(json.dumps({name:dict(parameters=z['parameters'],
 baseline=[a['kind']+str(a['x']) for a in z['baseline']],
 changed=[a['kind']+str(a['x']) for a in z['changed']]) for name,z in result.items()},indent=2,default=encode))
