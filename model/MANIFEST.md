# Statement, table and figure manifest

Allocation order in independent and robustness solvers: agency both, financing only, refusal only, joint. General welfare solver order: agency both, refusal only, financing only, joint; the comparison explicitly reorders these. Monetary computations use integers or fractions, with decimal display only.

| Object | Checking file and entry point | What is reproduced | Reference coverage |
|---|---|---|---|
| Solution lemma, Section 5.2 | `independent/solver.py:continuation`, `equilibrium`; `econ/scripts/check_ai_dependence_model.py:verify_state` | Feasible condition-specific offer endpoints, zero-profit and condition ties, investment comparison | Present; independently checked |
| Lemma 1 | `independent/solver.py:slack_cont`, `run`; `closed_form/characterise.py:lemma`, `brute`; `independent/audit.py` | Price-ceiling identity and exact continuation agreement including negative ceilings | Present |
| Theorem 1 | `independent/solver.py:primitive_case`, `target`; `independent/audit.py`; `closed_form/classification.py:cells` | F/T/D iff classification, finite rational samples, strict and boundary examples | Present |
| Corollary 1 | `independent/solver.py:prop2`; `independent/audit.py`; `institutions/solver.py:region` | Liquidity-gap region inside F and four-allocation pattern | Present |
| Theorem 2 | `general/check_theory.py:check_global`, `global_grid`, `extra_global` | Joint welfare weakly exceeds each other allocation on exact general-domain grids with legacy and overhead | Present in the 6 October reference |
| Proposition 1 | `general/check_theory.py:price_grid`; `check_printed.py:compare` | Strict price threshold, equality/no-build, welfare and total surplus; O1=13/4 example | Present in the 6 October reference |
| Table 1a | `independent/solver.py:outcomes`; `check_printed.py:compare` | All parameter and welfare cells; strict F/T/D examples | Present; numbers parsed from reference |
| Table 1 | `institutions/solver.py`; `check_printed.py:compare` | Condition and welfare in six institutions, transfer boundary and outside funding accounting | Present; numeric q/welfare cells parsed |
| Table 2, row 1 | `institutions/solver.py:continuation`, `solve`, `Table2_row1` checks | Partial internalisation threshold, equality included | Present; printed formula read against code |
| Table 2, row 2 | `institutions/solver.py:Table2_row2` checks | Conditional cash-capped Nash offers including limiting endpoint weights | Present; printed formula read against code |
| Table 2, row 3 | `institutions/solver.py:Table2_row3`; `extensions/check_extensions.py:direct`, `formula` | All affine continuous-intensity vertices; deterrence threshold and smallest-intensity ties | Present; printed formula read against code |
| Table 2, row 4 | `institutions/solver.py:Table2_row4` checks | Minimal borrowing, capped credit, interest in both objectives | Present; D<c−B domain |
| Table 2, row 5 | `institutions/solver.py:Table2_row5` checks | Expected net fallback under irrevocable refusal; effective value threshold | Present; ex-post failure revelation is a different protocol |
| Table 2, row 6 | `institutions/solver.py:Table2_row6`; `extensions/check_extensions.py` | Cost-price competing suppliers, investment threshold H+k | Present; outside-region selection uses explicit completion |
| Table 2, row 7 | `institutions/solver.py:Table2_row7_sufficient_region` checks | Sufficient transformed region under enforced partial clause; full clause benchmark | Present; no iff claim |
| Figure 2, investment/value region | `region/fig_region.py`; `institutions/solver.py:integral`; `check_printed.py` | Original figure PNG/PDF/EPS; exact areas 5/2, 9/4, 2 and bounds | Present; caption areas compared |
| Phase diagram (two panels) | `phase/fig_cases.py:arrangement`, `classify`, `validate_lattices`, `main` | Exact affine vertices, equality ownership, independent classifications, PDF/EPS/PNG | Present in the 6 October reference |
| Table A1 | `check_printed.py:compare` | Both grid ranges, steps, dimensions and region counts | Present; every numeric cell compared |
| Table A2 and surrounding counts | `check_printed.py:protection`, `welfare`, `compare`; `historical/model_extensions.py` | Minimal rights counts under both criteria; agreement and difference counts | Present |
| Table A3 | `historical/model_extensions.py:main`; `check_printed.py:compare` | Grid counts, exact analytic fraction, both deterministic sampling schemes and reported rounded percentages | Present; generation algorithm retained |
| Table A4, panels A/B | `institutions/solver.py`; `historical/model_extensions.py:topup_outcomes`; `check_printed.py:compare` | q, welfare, profits, surplus, outside payer and both investment-tie accounts | Present; every numeric result cell compared |
| Table A5 | `institutions/solver.py`; `general/check_theory.py:full`; `check_printed.py:compare` | Six variant rows; q/welfare, caps and investor alignment | Present |
| Extensions in theorem discussion | `extensions/check_extensions.py` | Recomputed affordability/slack, continuous/competitive failures, no drain with refundable reserve | Present; finite checks accompany proofs elsewhere |
| Noncomposition thresholds | `institutions/solver.py:noncomposition_*` checks | 4/5, 17/20 and 9/10 boundaries for separately specified combined games | Present |
| Separate-account historical count | `historical/reserve_checks.py` | Original 61,583 region points, shared/reserve outcomes and predicted-bound agreement | Present; original count regenerated |
| Consolidation historical count | `historical/consolidation.py` | 288,756 = binary comparisons plus continuous-baseline comparisons; expanded total retained separately | Not printed in the 6 October reference; retained as a historical check |
| Legacy implementation agreement | `historical/model_extensions.py:crosscheck` | Deterministic 3,000 parameter draws × four allocations = 12,000 comparisons | Present |

The manuscript's empirical counts and citations have no mathematical regeneration mapping here. Documentary materials are catalogued separately in the root pointer register. No evidence or contribution gate is passed by assembling or running this package.
